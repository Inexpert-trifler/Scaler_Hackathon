"""Task loading and management."""

import json
import random
from pathlib import Path
from typing import Dict, List, Optional


class TaskLoader:
    """Loads and manages tasks from JSON files."""

    def __init__(self):
        """Initialize TaskLoader and load all tasks."""
        self.tasks_dir = Path(__file__).parent
        self.tasks: Dict[str, List[Dict]] = {}
        self._load_tasks()
        self.validate_tasks()

    def _load_tasks(self) -> None:
        """Load all task JSON files."""
        difficulties = ["easy", "medium", "hard"]
        for difficulty in difficulties:
            filepath = self.tasks_dir / f"{difficulty}.json"
            if not filepath.exists():
                raise FileNotFoundError(f"Task file not found: {filepath}")
            with open(filepath, "r") as f:
                self.tasks[difficulty] = json.load(f)

    def validate_tasks(self) -> None:
        """Validate that all tasks have required keys."""
        required_keys = {
            "easy": ["id", "type", "difficulty", "task_description", "input_data", "expected_output", "keywords"],
            "medium": ["id", "type", "difficulty", "task_description", "input_data", "expected_output", "required_keys", "keywords"],
            "hard": ["id", "type", "difficulty", "task_description", "input_data", "expected_output", "answer_variants", "keywords"],
        }

        for difficulty, tasks_list in self.tasks.items():
            required = required_keys.get(difficulty, [])
            for idx, task in enumerate(tasks_list):
                missing = [key for key in required if key not in task]
                if missing:
                    raise ValueError(
                        f"Task {difficulty}[{idx}] (id={task.get('id')}) missing keys: {missing}"
                    )

    def get_task(self, difficulty: str) -> Dict:
        """Get a random task of the given difficulty."""
        if difficulty not in self.tasks:
            raise ValueError(f"Invalid difficulty: {difficulty}")
        return random.choice(self.tasks[difficulty])

    def get_task_by_id(self, task_id: str) -> Optional[Dict]:
        """Get a specific task by ID."""
        for tasks_list in self.tasks.values():
            for task in tasks_list:
                if task.get("id") == task_id:
                    return task
        return None

    def list_tasks(self, difficulty: str) -> List[Dict]:
        """Get all tasks of a given difficulty."""
        if difficulty not in self.tasks:
            raise ValueError(f"Invalid difficulty: {difficulty}")
        return self.tasks[difficulty]
