"""Baseline agent implementations for PromptGym."""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


class BaselineAgent:
    """Simple template-based baseline agent."""

    TEMPLATES = {
        "EASY": [
            "Summarize the following text in one sentence: {input}",
            "Create a brief summary of the key points: {input}",
            "Condense this into a single sentence: {input}",
        ],
        "MEDIUM": [
            "Convert the following text to JSON format: {input}",
            "Parse this into a JSON object with relevant fields: {input}",
            "Extract information and format as JSON: {input}",
        ],
        "HARD": [
            "Solve this step-by-step: {input}",
            "Work through this problem with clear steps: {input}",
            "Calculate and explain: {input}",
        ],
    }

    def get_action(self, state: dict[str, Any]) -> dict[str, str]:
        """Generate action based on task description."""
        task_desc = state.get("task_description", "").upper()
        input_data = state.get("input_data", "")

        # Identify difficulty from task description
        difficulty = self._identify_difficulty(task_desc)

        # Get appropriate template
        if difficulty in self.TEMPLATES:
            templates = self.TEMPLATES[difficulty]
            template = templates[0]  # Use first template
        else:
            template = "Complete the following task: {input}"

        prompt = template.format(input=input_data)
        return {"prompt": prompt}

    def _identify_difficulty(self, task_desc: str) -> str:
        """Identify task difficulty from description."""
        task_lower = task_desc.lower()

        if "json" in task_lower or "convert" in task_lower:
            return "MEDIUM"
        elif "reason" in task_lower or "solve" in task_lower or "calculate" in task_lower:
            return "HARD"
        else:
            return "EASY"


class AdaptiveBaselineAgent:
    """
    Adaptive agent that learns which prompt patterns work best.

    Tracks prompt effectiveness and adapts strategy over time.
    """

    def __init__(self, num_variations: int = 3):
        """Initialize adaptive agent."""
        self.num_variations = num_variations
        self.prompt_history: list[str] = []
        self.score_history: list[float] = []
        self.best_prompts: dict[str, str] = {}
        self.current_episode_scores: list[float] = []

    def get_action(self, state: dict[str, Any], step: int = 1) -> dict[str, str]:
        """
        Generate adaptive action based on history.

        Strategy:
        - Iteration 1-2: Try different prompt styles
        - Iteration 3+: Refine best performer
        """
        task_desc = state.get("task_description", "").upper()
        input_data = state.get("input_data", "")
        difficulty = self._identify_difficulty(task_desc)

        # If we have found a good prompt, use variations of it
        if step > 2 and difficulty in self.best_prompts:
            prompt = self._mutate_prompt(self.best_prompts[difficulty])
        else:
            # Try different strategies
            strategy_idx = (step - 1) % self.num_variations
            prompt = self._generate_prompt(difficulty, input_data, strategy_idx)

        return {"prompt": prompt}

    def update(self, difficulty: str, prompt: str, score: float) -> None:
        """Update agent with feedback."""
        self.prompt_history.append(prompt)
        self.score_history.append(score)
        self.current_episode_scores.append(score)

        # Track best prompt per difficulty
        if difficulty not in self.best_prompts:
            self.best_prompts[difficulty] = prompt
        else:
            best_score = self._get_score_for_prompt(self.best_prompts[difficulty])
            if score > best_score:
                self.best_prompts[difficulty] = prompt

    def reset_episode(self) -> None:
        """Reset episode-specific state."""
        self.current_episode_scores = []

    def _generate_prompt(self, difficulty: str, input_data: str, strategy: int) -> str:
        """Generate prompt based on difficulty and strategy."""
        strategies = {
            "EASY": [
                f"Summarize this in one sentence: {input_data}",
                f"Create a brief summary: {input_data}",
                f"One-line summary of: {input_data}",
            ],
            "MEDIUM": [
                f"Convert to JSON format: {input_data}",
                f"Parse as JSON: {input_data}",
                f"Format as JSON object: {input_data}",
            ],
            "HARD": [
                f"Solve step-by-step: {input_data}",
                f"Work through this calculation: {input_data}",
                f"Step-by-step solution: {input_data}",
            ],
        }

        if difficulty in strategies:
            prompts = strategies[difficulty]
            return prompts[strategy % len(prompts)]
        else:
            return f"Complete this task: {input_data}"

    def _mutate_prompt(self, prompt: str) -> str:
        """Create slight variation of a prompt."""
        variations = [
            lambda p: p + " Respond clearly.",
            lambda p: p + " Be concise.",
            lambda p: "Carefully " + p,
        ]

        idx = len(self.prompt_history) % len(variations)
        return variations[idx](prompt)

    def _identify_difficulty(self, task_desc: str) -> str:
        """Identify task difficulty."""
        task_lower = task_desc.lower()
        if "json" in task_lower or "convert" in task_lower:
            return "MEDIUM"
        elif "reason" in task_lower or "solve" in task_lower or "calculate" in task_lower:
            return "HARD"
        else:
            return "EASY"

    def _get_score_for_prompt(self, prompt: str) -> float:
        """Get best score for a given prompt."""
        if prompt not in self.prompt_history:
            return 0.0
        idx = self.prompt_history.index(prompt)
        return self.score_history[idx] if idx < len(self.score_history) else 0.0

    def get_stats(self) -> dict[str, Any]:
        """Get agent statistics."""
        return {
            "total_prompts": len(self.prompt_history),
            "average_score": float(np.mean(self.score_history))
            if self.score_history
            else 0.0,
            "max_score": float(np.max(self.score_history))
            if self.score_history
            else 0.0,
            "best_prompts": self.best_prompts,
        }


def baseline_agent(state: dict[str, Any]) -> dict[str, str]:
    """
    Simple baseline agent function for compatibility.

    Returns a basic prompt for the given task.
    """
    agent = BaselineAgent()
    return agent.get_action(state)
