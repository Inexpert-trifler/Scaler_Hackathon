"""PromptGym environment implementing openenv-core Environment pattern."""

from __future__ import annotations
import os
import sys
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import PromptAction, PromptObservation, PromptState
from app.config import settings
from app.tasks.loader import TaskLoader
from app.grader import Grader
from openenv.core.env_server import Environment

class PromptGymEnvironment(Environment[PromptAction, PromptObservation, PromptState]):
    """Standardized PromptGym environment for OpenEnv validation."""

    def __init__(self):
        super().__init__()
        self.task_loader = TaskLoader()
        self.grader = Grader()
        self.current_task = None
        self.difficulty = "easy"
        self.step_count = 0
        self.total_reward = 0.0

    def reset(self, difficulty: str = "EASY", **kwargs) -> PromptObservation:
        self.difficulty = difficulty.lower()
        self.current_task = self.task_loader.get_task(self.difficulty)
        self.step_count = 0
        self.total_reward = 0.0
        
        return PromptObservation(
            task_description=self.current_task["task_description"],
            input_data=self.current_task["input_data"],
            task_type=self.current_task["type"],
            difficulty=self.difficulty,
            step=0,
            max_steps=settings.MAX_STEPS
        )

    def step(self, action: PromptAction, **kwargs) -> PromptObservation:
        from server.app import mock_execute
        self.step_count += 1
        output = mock_execute(action.prompt, self.current_task)
        score, signals = self.grader.grade(output, self.current_task)
        self.total_reward += score
        
        done = self.step_count >= settings.MAX_STEPS or score >= settings.REWARD_THRESHOLD
        
        return PromptObservation(
            task_description=self.current_task["task_description"],
            input_data=self.current_task["input_data"],
            task_type=self.current_task["type"],
            difficulty=self.difficulty,
            step=self.step_count,
            max_steps=settings.MAX_STEPS,
            last_llm_output=output,
            last_score=score,
            grader_signals=signals,
            done=done,
            reward=score
        )

    @property
    def state(self) -> PromptState:
        return PromptState(
            task_id=self.current_task.get("id", "") if self.current_task else "",
            difficulty=self.difficulty,
            total_reward=self.total_reward,
            best_reward=self.total_reward,
            done=self.step_count >= settings.MAX_STEPS,
            task_description=self.current_task["task_description"] if self.current_task else ""
        )
