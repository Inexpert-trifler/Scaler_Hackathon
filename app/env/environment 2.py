"""Core environment implementation for PromptGym with OpenEnv compatibility."""

from __future__ import annotations

import logging
import random
from typing import Any, Optional

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from app.env.grader import grade_output
from app.env.tasks import get_tasks
from app.utils.llm_executor import run_prompt

logger = logging.getLogger(__name__)


class PromptGymEnv(gym.Env):
    """
    PromptGym Environment - OpenEnv compatible.

    Task: Agent generates prompts to solve tasks, grader evaluates output quality.
    """

    metadata = {"render_modes": ["human"]}

    def __init__(
        self,
        llm_provider: str = "mock",
        max_steps: int = 5,
        difficulty_weights: Optional[list[float]] = None,
    ):
        """
        Initialize PromptGymEnv.

        Args:
            llm_provider: "mock" or "openai"
            max_steps: Maximum steps per episode
            difficulty_weights: Weights for [EASY, MEDIUM, HARD] sampling
        """
        super().__init__()

        self.llm_provider = llm_provider
        self.max_steps = max_steps
        self.difficulty_weights = difficulty_weights or [0.33, 0.33, 0.34]

        # Define action and observation spaces
        self.action_space = spaces.Dict(
            {
                "prompt": spaces.Text(max_length=1000),
            }
        )

        self.observation_space = spaces.Dict(
            {
                "task_description": spaces.Text(max_length=500),
                "input_data": spaces.Text(max_length=2000),
                "step": spaces.Box(low=0, high=max_steps, shape=(1,), dtype=np.int32),
                "previous_scores": spaces.Box(
                    low=0.0, high=1.0, shape=(max_steps,), dtype=np.float32
                ),
            }
        )

        # Environment state
        self.current_task: dict[str, Any] | None = None
        self.step_count = 0
        self.previous_scores: list[float] = []
        self.episode_reward = 0.0
        self.previous_prompts: list[str] = []

    def reset(
        self, seed: Optional[int] = None, options: Optional[dict] = None
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """
        Reset the environment and load a new task.

        Returns:
            observation: Dict matching observation_space
            info: Additional info dictionary
        """
        super().reset(seed=seed, options=options)

        # Sample task based on difficulty weights
        self.current_task = self._sample_task()
        self.step_count = 0
        self.previous_scores = []
        self.episode_reward = 0.0
        self.previous_prompts = []

        obs = self._get_observation()
        info = {
            "task_difficulty": self.current_task.get("difficulty", "UNKNOWN"),
            "task_description": self.current_task.get("task_description", ""),
        }

        logger.info(f"Reset environment. Task: {info['task_difficulty']}")
        return obs, info

    def step(
        self, action: dict[str, Any]
    ) -> tuple[dict[str, Any], float, bool, bool, dict[str, Any]]:
        """
        Execute one step of the environment.

        Args:
            action: Dict with 'prompt' key

        Returns:
            observation, reward, terminated, truncated, info
        """
        if self.current_task is None:
            raise RuntimeError("Environment not initialized. Call reset() first.")

        # Validate action
        prompt = action.get("prompt")
        if not prompt or not isinstance(prompt, str):
            raise ValueError("Action must include a non-empty 'prompt' string.")

        if len(prompt) > 1000:
            raise ValueError("Prompt exceeds maximum length of 1000 characters.")

        # Execute prompt via LLM
        try:
            output = run_prompt(
                prompt, str(self.current_task.get("input_data", "")), self.llm_provider
            )
        except Exception as e:
            logger.error(f"Error executing prompt: {str(e)}")
            output = f"Error: {str(e)}"

        # Grade output
        score = grade_output(self.current_task, output)
        self.previous_scores.append(score)
        self.previous_prompts.append(prompt)
        self.episode_reward += score
        self.step_count += 1

        # Determine termination conditions
        terminated = self.step_count >= self.max_steps
        truncated = False  # Can be True for time limits, etc.

        # Prepare info
        info = {
            "score": score,
            "output": output,
            "step": self.step_count,
            "episode_reward": self.episode_reward,
            "task_difficulty": self.current_task.get("difficulty", "UNKNOWN"),
        }

        obs = self._get_observation()

        logger.debug(f"Step {self.step_count}: score={score:.3f}, total_reward={self.episode_reward:.3f}")

        return obs, float(score), terminated, truncated, info

    def _get_observation(self) -> dict[str, Any]:
        """Get current observation matching observation_space."""
        # Pad scores to max_steps
        padded_scores = np.zeros(self.max_steps, dtype=np.float32)
        for i, score in enumerate(self.previous_scores):
            if i < self.max_steps:
                padded_scores[i] = score

        return {
            "task_description": str(self.current_task.get("task_description", "")),
            "input_data": str(self.current_task.get("input_data", "")),
            "step": np.array([self.step_count], dtype=np.int32),
            "previous_scores": padded_scores,
        }

    def _sample_task(self) -> dict[str, Any]:
        """Sample a task based on difficulty weights."""
        tasks = get_tasks()

        # Group by difficulty
        easy_tasks = [t for t in tasks if t.get("difficulty") == "EASY"]
        medium_tasks = [t for t in tasks if t.get("difficulty") == "MEDIUM"]
        hard_tasks = [t for t in tasks if t.get("difficulty") == "HARD"]

        # Weighted selection
        difficulty = np.random.choice(
            ["EASY", "MEDIUM", "HARD"], p=self.difficulty_weights
        )

        if difficulty == "EASY" and easy_tasks:
            return random.choice(easy_tasks)
        elif difficulty == "MEDIUM" and medium_tasks:
            return random.choice(medium_tasks)
        elif difficulty == "HARD" and hard_tasks:
            return random.choice(hard_tasks)
        else:
            # Fallback to any task
            return random.choice(tasks)

    def state(self) -> dict[str, Any]:
        """Return the current environment state (for API compatibility)."""
        if self.current_task is None:
            return {"error": "Environment not initialized. Call reset() first."}

        return {
            "task_description": self.current_task.get("task_description"),
            "input_data": self.current_task.get("input_data"),
            "expected_output": self.current_task.get("expected_output"),
            "previous_prompts": self.previous_prompts,
            "previous_scores": self.previous_scores,
            "step_count": self.step_count,
            "episode_reward": self.episode_reward,
            "task_difficulty": self.current_task.get("difficulty"),
        }

    def render(self, mode: str = "human") -> None:
        """Optional rendering for visualization."""
        if not self.current_task:
            print("Environment not initialized")
            return

        print("\n" + "=" * 60)
        print(f"Task: {self.current_task.get('task_description')}")
        print(f"Difficulty: {self.current_task.get('difficulty')}")
        print(f"Step: {self.step_count}/{self.max_steps}")
        if self.previous_scores:
            avg_score = np.mean(self.previous_scores)
            print(f"Average Score: {avg_score:.3f}")
        print("=" * 60)

    def close(self) -> None:
        """Cleanup resources."""
        pass

    def get_metrics(self) -> dict[str, Any]:
        """Get environment metrics for monitoring."""
        return {
            "step_count": self.step_count,
            "max_steps": self.max_steps,
            "episode_reward": self.episode_reward,
            "previous_scores": self.previous_scores,
            "average_score": float(np.mean(self.previous_scores))
            if self.previous_scores
            else 0.0,
        }
