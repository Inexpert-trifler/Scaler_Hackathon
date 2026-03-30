"""PromptGym environment implementing openenv-core Environment pattern."""

from __future__ import annotations

import random
from typing import Optional
from datetime import datetime, timezone
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import PromptAction, PromptObservation, PromptState
from app.config import settings
from app.env.tasks import get_tasks_by_difficulty
from app.env.grader import grade_output

# Import openenv Environment base
from openenv.core.env_server import Environment


class PromptGymEnvironment(Environment[PromptAction, PromptObservation, PromptState]):
    """PromptGym environment for optimizing LLM prompts across multiple tasks."""

    def __init__(self):
        """Initialize the PromptGym environment."""
        super().__init__()
        self.current_task: Optional[dict] = None
        self.current_difficulty: Optional[str] = None
        self.max_steps = settings.MAX_STEPS
        self.step_count = 0
        self.episode_reward = 0.0
        self.task_scores = {}
        self._episode_id: Optional[str] = None
        
    def reset(
        self,
        *,
        difficulty: str = "EASY",
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        **kwargs
    ) -> PromptObservation:
        """
        Reset the environment for a new episode.

        Args:
            difficulty: Task difficulty ("EASY", "MEDIUM", "HARD")
            seed: Random seed for reproducibility
            episode_id: Episode identifier
            **kwargs: Additional arguments

        Returns:
            PromptObservation with initial task state
        """
        if seed is not None:
            random.seed(seed)
        
        self.current_difficulty = difficulty.upper()
        self.step_count = 0
        self.episode_reward = 0.0
        self.task_scores = {}
        self._episode_id = episode_id or self._generate_episode_id()
        
        # Get a random task of the specified difficulty
        tasks = get_tasks_by_difficulty(self.current_difficulty)
        if not tasks:
            raise ValueError(f"No tasks available for difficulty: {self.current_difficulty}")
        
        self.current_task = random.choice(tasks)
        
        # Determine task type from difficulty
        task_type_map = {
            "EASY": "summarization",
            "MEDIUM": "json_extraction",
            "HARD": "reasoning",
        }
        task_type = task_type_map.get(self.current_difficulty, "summarization")
        
        # Create observation with all required fields
        observation = PromptObservation(
            task_description=str(self.current_task.get("task_description", "")),
            input_data=str(self.current_task.get("input_data", "")),
            task_type=task_type,
            difficulty=self.current_difficulty.lower(),
            step=0,
            max_steps=self.max_steps,
            done=False,
            reward=0.0,
            last_llm_output="",
            last_score=0.0,
            grader_signals={},
            message="New task initialized",
        )
        
        return observation

    def step(
        self,
        action: PromptAction,
        *,
        timeout_s: Optional[float] = None,
        **kwargs
    ) -> PromptObservation:
        """
        Execute one step of environment.

        Args:
            action: PromptAction containing prompt to execute
            timeout_s: Timeout for execution (currently unused for mock)
            **kwargs: Additional arguments

        Returns:
            PromptObservation with task result and reward
        """
        # Auto-reset if no task is loaded
        if self.current_task is None:
            self.reset(difficulty="EASY")
        
        self.step_count += 1
        
        # Execute prompt (mock or real)
        output = self._execute_prompt(action.prompt, self.current_task)
        
        # Grade the output
        task_reward = grade_output(self.current_task, output)
        self.episode_reward += task_reward
        
        # Check if episode is done
        done = self.step_count >= self.max_steps
        
        # Determine task type from difficulty
        task_type_map = {
            "EASY": "summarization",
            "MEDIUM": "json_extraction",
            "HARD": "reasoning",
        }
        task_type = task_type_map.get(self.current_difficulty, "summarization")
        
        # Create observation with all required fields
        observation = PromptObservation(
            task_description=str(self.current_task.get("task_description", "")),
            input_data=str(self.current_task.get("input_data", "")),
            task_type=task_type,
            difficulty=self.current_difficulty.lower(),
            step=self.step_count,
            max_steps=self.max_steps,
            done=done,
            reward=task_reward,
            last_llm_output=output,
            last_score=task_reward,
            grader_signals={},
            message=f"Step {self.step_count} completed with reward {task_reward:.3f}",
        )
        
        return observation

    @property
    def state(self) -> PromptState:
        """
        Get the current state of the environment.

        Returns:
            PromptState with current episode and step information
        """
        return PromptState(
            task_id=self._task_to_id(self.current_task),
            episode_id=self._episode_id or self._generate_episode_id(),
            step_count=self.step_count,
            difficulty=self.current_difficulty.lower() if self.current_difficulty else "easy",
            total_reward=self.episode_reward,
            best_reward=self.episode_reward,  # Since we're tracking single-step rewards
            done=self.step_count >= self.max_steps,
            task_description=str(self.current_task.get("task_description", "")) if self.current_task else "",
        )

    def _execute_prompt(self, prompt: str, task: dict) -> str:
        """
        Execute a prompt against the task.

        In mock mode, returns simulated output based on prompt quality.
        In production, would call actual LLM.

        Args:
            prompt: The prompt to execute
            task: The task dictionary

        Returns:
            Simulated or actual LLM output
        """
        mode = settings.LLM_MODE.lower()
        
        if mode == "mock":
            return self._mock_execute(prompt, task)
        elif mode == "openai":
            return self._openai_execute(prompt, task)
        else:
            return self._mock_execute(prompt, task)

    def _mock_execute(self, prompt: str, task: dict) -> str:
        """
        Mock LLM execution with quality tiers based on prompt quality.

        Args:
            prompt: The prompt to execute
            task: The task dictionary

        Returns:
            Simulated output
        """
        difficulty = str(task.get("difficulty", "")).upper()
        expected = str(task.get("expected_output", ""))
        input_data = str(task.get("input_data", ""))
        
        # Analyze prompt quality
        quality_score = self._analyze_prompt_quality(
            prompt, input_data, difficulty
        )
        
        # Generate output based on quality tier
        if quality_score >= 0.8:
            # High quality prompt -> return expected output
            return expected
        elif quality_score >= 0.6:
            # Medium quality -> partial/slightly modified output
            if difficulty == "EASY":
                # For summaries, truncate or simplify
                words = expected.split()
                truncated = " ".join(words[: len(words) // 2 + 1])
                return truncated
            elif difficulty == "MEDIUM":
                # For JSON, return with slight modifications
                return expected.replace('"', "'")
            else:
                # For reasoning, return without full explanation
                return str(expected).split()[0] if expected else ""
        else:
            # Low quality -> random or incomplete output
            return "Unable to provide accurate output"

    def _analyze_prompt_quality(
        self, prompt: str, input_data: str, difficulty: str
    ) -> float:
        """
        Analyze prompt quality heuristically.

        Args:
            prompt: The prompt to analyze
            input_data: The input data context
            difficulty: Task difficulty level

        Returns:
            Quality score between 0.0 and 1.0
        """
        score = 0.5  # Base score
        
        # Check prompt length (longer is generally better)
        if len(prompt) > 50:
            score += 0.15
        if len(prompt) > 100:
            score += 0.10
        
        # Check if prompt contains task context
        if input_data.lower() in prompt.lower():
            score += 0.10
        
        # Check for instruction clarity keywords
        clarity_keywords = [
            "step", "format", "structure", "specific", "clearly",
            "concise", "detailed", "example",
        ]
        for keyword in clarity_keywords:
            if keyword.lower() in prompt.lower():
                score += 0.05
        
        # Check for good engineering patterns
        if ":" in prompt:  # Likely contains examples or structure
            score += 0.05
        
        return min(1.0, score)

    def _openai_execute(self, prompt: str, task: dict) -> str:
        """
        Execute prompt using OpenAI API.

        Args:
            prompt: The prompt to execute
            task: The task dictionary

        Returns:
            LLM output (stub for now)
        """
        # Placeholder for OpenAI integration
        return self._mock_execute(prompt, task)

    def _task_to_id(self, task: Optional[dict]) -> str:
        """Convert task to ID."""
        if not task:
            return "unknown"
        
        description = str(task.get("task_description", ""))
        difficulty = str(task.get("difficulty", ""))
        
        # Create a simple ID from task description
        desc_hash = str(hash(description) % 10000).lstrip("-")
        return f"{difficulty}_{desc_hash}"

    def _generate_episode_id(self) -> str:
        """Generate a unique episode ID."""
        timestamp = datetime.now(timezone.utc).isoformat()
        return f"episode_{timestamp}"
