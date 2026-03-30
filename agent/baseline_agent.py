"""Baseline agent for testing PromptGym."""

import json
from typing import Optional

import requests


class BaselineAgent:
    """Baseline agent with multiple prompt strategies."""

    BASE_URL = "http://localhost:7860"

    # Prompt strategies
    NAIVE = "NAIVE"
    STRUCTURED = "STRUCTURED"
    CHAIN_OF_THOUGHT = "CHAIN_OF_THOUGHT"
    ROLE_PLAY = "ROLE_PLAY"

    def __init__(self, base_url: str = BASE_URL):
        """Initialize agent."""
        self.base_url = base_url

    def run_episode(self, difficulty: str = "easy", strategy: str = NAIVE) -> dict:
        """
        Run single episode.
        
        Args:
            difficulty: Task difficulty
            strategy: Prompt strategy to use
            
        Returns:
            Episode summary with metrics
        """
        # Reset environment
        reset_response = requests.post(
            f"{self.base_url}/reset",
            json={"difficulty": difficulty},
        ).json()

        session_id = reset_response["session_id"]
        observation = reset_response["observation"]

        total_reward = 0.0
        steps = []

        # Run episode (max 5 steps)
        for step_num in range(5):
            # Generate prompt based on strategy
            prompt = self._generate_prompt(observation, strategy)

            # Execute step
            step_response = requests.post(
                f"{self.base_url}/step",
                json={"session_id": session_id, "action": prompt},
            ).json()

            observation = step_response["observation"]
            reward = step_response["reward"]
            done = step_response["done"]

            total_reward += reward
            steps.append({
                "step": step_num + 1,
                "reward": reward,
                "output_length": len(step_response["info"]["llm_output"].split()),
            })

            if done:
                break

        return {
            "session_id": session_id,
            "difficulty": difficulty,
            "strategy": strategy,
            "total_reward": total_reward,
            "steps": len(steps),
            "step_details": steps,
        }

    def run_full_benchmark(self) -> dict:
        """
        Run full benchmark across all difficulties and strategies.
        
        Returns:
            Benchmark results table
        """
        difficulties = ["easy", "medium", "hard"]
        strategies = [self.NAIVE, self.STRUCTURED, self.CHAIN_OF_THOUGHT, self.ROLE_PLAY]

        results = []
        for difficulty in difficulties:
            for strategy in strategies:
                try:
                    episode = self.run_episode(difficulty, strategy)
                    results.append({
                        "difficulty": difficulty,
                        "strategy": strategy,
                        "total_reward": episode["total_reward"],
                        "steps": episode["steps"],
                    })
                except Exception as e:
                    print(f"Error in {difficulty}/{strategy}: {e}")

        return results

    def _generate_prompt(self, observation: dict, strategy: str) -> str:
        """Generate prompt based on strategy."""
        task_description = observation.get("task_description", "")
        input_data = observation.get("input_data", "")
        task_type = observation.get("task_type", "")

        if strategy == self.NAIVE:
            return f"Task: {task_description}\nData: {input_data}\nResponse:"

        elif strategy == self.STRUCTURED:
            return f"""Task: {task_description}
Input Data:
{input_data}

Instructions:
1. Understand the task clearly
2. Extract relevant information
3. Structure your response logically
4. Provide a clear final answer

Response:"""

        elif strategy == self.CHAIN_OF_THOUGHT:
            return f"""Task: {task_description}

Let me think through this step by step:

Input Data:
{input_data}

Step 1: Understanding the task
Step 2: Identifying key information
Step 3: Processing and analysis
Step 4: Generating response

Response:"""

        elif strategy == self.ROLE_PLAY:
            if task_type == "summarization":
                role = "a professional technical writer"
            elif task_type == "json_extraction":
                role = "a data extraction specialist"
            else:
                role = "a problem-solving expert"

            return f"""You are {role}.

Task: {task_description}

Input Data:
{input_data}

Please solve this task using your expertise.

Response:"""

        else:
            # Default to naive
            return f"Task: {task_description}\nData: {input_data}\nResponse:"


def main():
    """Run baseline agent benchmark."""
    print("Starting PromptGym Baseline Agent...")
    print("=" * 60)

    agent = BaselineAgent()

    try:
        # Run full benchmark
        results = agent.run_full_benchmark()

        # Print results table
        print("\nBenchmark Results:")
        print("-" * 60)
        print(f"{'Difficulty':<12} {'Strategy':<20} {'Reward':<10} {'Steps':<6}")
        print("-" * 60)

        for result in results:
            print(
                f"{result['difficulty']:<12} "
                f"{result['strategy']:<20} "
                f"{result['total_reward']:<10.4f} "
                f"{result['steps']:<6}"
            )

        print("-" * 60)

        # Calculate averages by difficulty
        print("\nAverage Reward by Difficulty:")
        for difficulty in ["easy", "medium", "hard"]:
            rewards = [
                r["total_reward"]
                for r in results
                if r["difficulty"] == difficulty
            ]
            avg_reward = sum(rewards) / len(rewards) if rewards else 0
            print(f"  {difficulty}: {avg_reward:.4f}")

    except Exception as e:
        print(f"Error running benchmark: {e}")


if __name__ == "__main__":
    main()
