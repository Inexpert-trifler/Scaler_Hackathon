"""Main PromptGym environment."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

from app.config import settings
from app.executor import LLMExecutor
from app.grader import Grader
from app.schemas import Observation, ResetResponse, StepResponse
from app.session import SessionManager
from app.tasks.loader import TaskLoader

logger = logging.getLogger(__name__)

# Try to import torch scorer
try:
    from scorer.reward_model import TorchRewardScorer, pretrain_on_synthetic_data
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("Scorer module not available")


class PromptGymEnv:
    """Main environment orchestrating all components."""

    def __init__(self):
        """Initialize environment."""
        self.task_loader = TaskLoader()
        self.grader = Grader()
        self.executor = LLMExecutor(mode=settings.LLM_MODE)

        self.torch_scorer = None
        if settings.USE_TORCH_SCORER and TORCH_AVAILABLE:
            self.torch_scorer = TorchRewardScorer()
            pretrain_on_synthetic_data(self.torch_scorer)

        # Ensure logs directory exists
        Path(settings.LOG_FILE).parent.mkdir(parents=True, exist_ok=True)

        logger.info(
            f"PromptGymEnv initialized (LLM: {settings.LLM_MODE}, "
            f"Torch: {settings.USE_TORCH_SCORER})"
        )

    def reset(self, difficulty: str = "easy", session_id: str = None) -> ResetResponse:
        """
        Reset environment and start new episode.
        
        Args:
            difficulty: Task difficulty ("easy", "medium", "hard")
            session_id: Optional session ID (generated if not provided)
            
        Returns:
            ResetResponse with observation and session info
        """
        task = self.task_loader.get_task(difficulty)
        session = SessionManager.create_session(task, difficulty, session_id)

        observation = self._make_observation(task, session)
        info = {"task_id": task.get("id"), "task_type": task.get("type")}

        return ResetResponse(
            observation=observation, info=info, session_id=session.session_id
        )

    def step(self, session_id: str, action: str) -> StepResponse:
        """
        Execute one step.
        
        Args:
            session_id: Session ID
            action: Prompt action
            
        Returns:
            StepResponse with observation, reward, done, and info
        """
        session = SessionManager.get_session(session_id)
        task = session.current_task

        # Execute prompt
        output = self.executor.execute(action, task)

        # Grade output
        score, signals = self.grader.grade(output, task)

        # Optionally blend with torch scorer
        if self.torch_scorer:
            torch_score = self.torch_scorer.score(action, output, task)
            score = TorchRewardScorer.blend_with_grader(score, torch_score)

        # Determine done
        done = session.step_count + 1 >= settings.MAX_STEPS or score >= settings.REWARD_THRESHOLD

        # Update session
        SessionManager.update_session(session_id, score, done, action, output)
        session = SessionManager.get_session(session_id)

        # Log to JSONL
        self._log_step(session, task, action, output, score, signals, done)

        # Build response
        observation = self._make_observation(task, session)
        info = {
            "llm_output": output,
            "score": score,
            "signals": signals,
            "step": session.step_count,
            "task_id": task.get("id"),
        }

        return StepResponse(observation=observation, reward=score, done=done, info=info)

    def state(self, session_id: str):
        """Get current session state."""
        from app.schemas import StateResponse
        session = SessionManager.get_session(session_id)
        observation = self._make_observation(session.current_task, session)
        return StateResponse(
            session_id=session_id,
            observation=observation,
            last_reward=session.last_reward,
            total_reward=session.total_reward,
            step=session.step_count,
            done=session.done,
        )

    def _make_observation(self, task: dict, session) -> Observation:
        """Build observation."""
        return Observation(
            task_description=task.get("task_description", ""),
            input_data=task.get("input_data", ""),
            task_type=task.get("type", ""),
            step=session.step_count,
            max_steps=settings.MAX_STEPS,
            difficulty=session.difficulty,
        )

    def _log_step(
        self,
        session,
        task: dict,
        prompt: str,
        output: str,
        score: float,
        signals: dict,
        done: bool,
    ) -> None:
        """Log step to JSONL file."""
        try:
            record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "session_id": session.session_id,
                "step": session.step_count,
                "difficulty": session.difficulty,
                "task_id": task.get("id"),
                "prompt_length": len(prompt.split()),
                "output_length": len(output.split()),
                "score": score,
                "signals": signals,
                "done": done,
            }
            with open(settings.LOG_FILE, "a") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            logger.error(f"Error logging step: {e}")
