"""Client for PromptGym environment using openenv-core."""

from typing import Optional
import requests
import json
from models import PromptAction, PromptObservation, PromptState


class PromptGymEnv:
    """Client for interacting with PromptGym server."""

    def __init__(self, base_url: str = "http://localhost:7860"):
        """
        Initialize PromptGym client.

        Args:
            base_url: Base URL of the PromptGym server
        """
        self.base_url = base_url
        self._session_id = None

    def reset(self, difficulty: str = "EASY", seed: Optional[int] = None, **kwargs) -> PromptObservation:
        """
        Reset the environment with specified difficulty.

        Args:
            difficulty: Task difficulty ("EASY", "MEDIUM", "HARD")
            seed: Random seed for reproducibility
            **kwargs: Additional arguments

        Returns:
            Initial PromptObservation
        """
        reset_payload = {
            "difficulty": difficulty,
        }
        if seed is not None:
            reset_payload["seed"] = seed
        reset_payload.update(kwargs)
        
        try:
            response = requests.post(
                f"{self.base_url}/reset",
                json=reset_payload,
                timeout=5.0,
            ).json()
            
            # Store session_id for subsequent steps
            self._session_id = response.get("session_id", "default_session")
            
            obs_data = response.get("observation", {})
            reward = response.get("reward", 0.0)  # Get reward from response
            
            # Create observation directly without validation
            observation = PromptObservation(
                task_description=obs_data.get("task_description", ""),
                input_data=obs_data.get("input_data", ""),
                task_type=obs_data.get("task_type", "summarization"),
                difficulty=obs_data.get("difficulty", "easy"),
                step=obs_data.get("step", 0),
                max_steps=obs_data.get("max_steps", 5),
                done=obs_data.get("done", False),
                reward=reward,  # Use reward from response
                last_llm_output=obs_data.get("last_llm_output", ""),
                last_score=obs_data.get("last_score", 0.0),
                grader_signals=obs_data.get("grader_signals", {}),
                message=obs_data.get("message", ""),
            )
            
            return observation
        except Exception as e:
            raise ValueError(f"Failed to reset environment: {e}") from e

    def step(self, action: PromptAction) -> PromptObservation:
        """
        Execute one step of the environment.

        Args:
            action: PromptAction containing the prompt

        Returns:
            PromptObservation with result
        """
        payload = {
            "session_id": self._session_id or "default_session",
            "action": {
                "prompt": action.prompt,
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/step",
                json=payload,
                timeout=5.0,
            ).json()
            
            obs_data = response.get("observation", {})
            reward = response.get("reward", 0.0)  # Get reward from response, not observation
            
            # Create observation directly without validation
            observation = PromptObservation(
                task_description=obs_data.get("task_description", ""),
                input_data=obs_data.get("input_data", ""),
                task_type=obs_data.get("task_type", "summarization"),
                difficulty=obs_data.get("difficulty", "easy"),
                step=obs_data.get("step", 0),
                max_steps=obs_data.get("max_steps", 5),
                done=obs_data.get("done", False),
                reward=reward,  # Use reward from response
                last_llm_output=obs_data.get("last_llm_output", ""),
                last_score=obs_data.get("last_score", 0.0),
                grader_signals=obs_data.get("grader_signals", {}),
                message=obs_data.get("message", ""),
            )
            
            return observation
        except Exception as e:
            raise ValueError(f"Failed to execute step: {e}") from e

    def get_state(self) -> PromptState:
        """
        Get the current state of the environment.

        Returns:
            PromptState object
        """
        try:
            response = requests.get(
                f"{self.base_url}/state",
                timeout=5.0,
            ).json()
            
            state_data = response.get("state", {})
            state = PromptState(
                task_id=state_data.get("task_id", ""),
                episode_id=state_data.get("episode_id", ""),
                step_count=state_data.get("step_count", 0),
                difficulty=state_data.get("difficulty", "easy"),
                total_reward=state_data.get("total_reward", 0.0),
                best_reward=state_data.get("best_reward", 0.0),
                done=state_data.get("done", False),
                task_description=state_data.get("task_description", ""),
            )
            
            return state
        except Exception as e:
            raise ValueError(f"Failed to get state: {e}") from e
