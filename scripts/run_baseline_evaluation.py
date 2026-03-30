"""Baseline evaluation script for PromptGym."""

import logging
import sys
from typing import Any

import numpy as np

from app.agent.baseline_agent import AdaptiveBaselineAgent
from app.env.environment import PromptGymEnv
from app.env.tasks import get_tasks_by_difficulty

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def run_episode(
    env: PromptGymEnv, agent: AdaptiveBaselineAgent, episode: int
) -> dict[str, Any]:
    """
    Run a single evaluation episode.

    Returns:
        metrics: Episode metrics
    """
    obs, info = env.reset()
    difficulty = info.get("task_difficulty", "UNKNOWN")
    episode_reward = 0.0
    step_count = 0

    for step in range(1, env.max_steps + 1):
        try:
            # Get agent action
            action = agent.get_action(obs, step=step)

            # Execute step
            obs, reward, terminated, truncated, step_info = env.step(action)

            # Update agent
            agent.update(difficulty, action["prompt"], reward)
            episode_reward += reward
            step_count = step

            logger.debug(
                f"Episode {episode}, Step {step}: "
                f"prompt_len={len(action['prompt'])}, "
                f"score={reward:.3f}, "
                f"cumulative={episode_reward:.3f}"
            )

            if terminated or truncated:
                break

        except Exception as e:
            logger.error(f"Error in episode {episode}, step {step}: {str(e)}")
            break

    agent.reset_episode()

    return {
        "episode": episode,
        "difficulty": difficulty,
        "episode_reward": episode_reward,
        "steps": step_count,
        "avg_step_reward": episode_reward / step_count if step_count > 0 else 0.0,
    }


def evaluate_baseline(
    num_episodes: int = 50, llm_provider: str = "mock"
) -> dict[str, Any]:
    """
    Run comprehensive baseline agent evaluation.

    Args:
        num_episodes: Number of episodes to run
        llm_provider: LLM provider to use ("mock" or "openai")

    Returns:
        evaluation_results: Comprehensive evaluation metrics
    """
    logger.info(f"Starting baseline evaluation ({num_episodes} episodes)")
    logger.info(f"LLM Provider: {llm_provider}")

    # Initialize environment and agent
    env = PromptGymEnv(llm_provider=llm_provider, max_steps=5, difficulty_weights=[0.33, 0.33, 0.34])
    agent = AdaptiveBaselineAgent(num_variations=3)

    # Tracking
    episode_rewards = []
    difficulty_performance = {"EASY": [], "MEDIUM": [], "HARD": []}
    difficulty_episodes = {"EASY": 0, "MEDIUM": 0, "HARD": 0}

    # Run episodes
    for ep in range(num_episodes):
        metrics = run_episode(env, agent, ep + 1)

        episode_rewards.append(metrics["episode_reward"])
        difficulty = metrics["difficulty"]
        difficulty_performance[difficulty].append(metrics["episode_reward"])
        difficulty_episodes[difficulty] += 1

        # Progress logging
        if (ep + 1) % 10 == 0 or ep == 0:
            current_avg = np.mean(episode_rewards)
            logger.info(f"Progress: {ep + 1}/{num_episodes} episodes. Avg reward: {current_avg:.3f}")

    # Compile results
    overall_avg = np.mean(episode_rewards) if episode_rewards else 0.0
    overall_std = np.std(episode_rewards) if episode_rewards else 0.0
    overall_max = np.max(episode_rewards) if episode_rewards else 0.0
    overall_min = np.min(episode_rewards) if episode_rewards else 0.0

    results = {
        "total_episodes": num_episodes,
        "llm_provider": llm_provider,
        "overall": {
            "average_reward": float(overall_avg),
            "std_dev": float(overall_std),
            "max_reward": float(overall_max),
            "min_reward": float(overall_min),
        },
        "by_difficulty": {},
        "agent_stats": agent.get_stats(),
    }

    # Per-difficulty metrics
    for difficulty in ["EASY", "MEDIUM", "HARD"]:
        scores = difficulty_performance[difficulty]
        if scores:
            results["by_difficulty"][difficulty] = {
                "episodes": len(scores),
                "average_reward": float(np.mean(scores)),
                "std_dev": float(np.std(scores)),
                "max_reward": float(np.max(scores)),
                "min_reward": float(np.min(scores)),
            }
        else:
            results["by_difficulty"][difficulty] = {
                "episodes": 0,
                "average_reward": 0.0,
                "std_dev": 0.0,
                "max_reward": 0.0,
                "min_reward": 0.0,
            }

    env.close()
    return results


def print_results(results: dict[str, Any]) -> None:
    """Pretty-print evaluation results."""
    print("\n" + "=" * 70)
    print("PromptGym BASELINE EVALUATION RESULTS")
    print("=" * 70)

    print(f"\nConfiguration:")
    print(f"  Total Episodes: {results['total_episodes']}")
    print(f"  LLM Provider: {results['llm_provider']}")

    print(f"\nOverall Performance:")
    overall = results["overall"]
    print(f"  Average Reward: {overall['average_reward']:.4f} ± {overall['std_dev']:.4f}")
    print(f"  Max Reward: {overall['max_reward']:.4f}")
    print(f"  Min Reward: {overall['min_reward']:.4f}")

    print(f"\nPerformance by Difficulty:")
    for difficulty in ["EASY", "MEDIUM", "HARD"]:
        metrics = results["by_difficulty"][difficulty]
        if metrics["episodes"] > 0:
            print(
                f"  {difficulty:6s} (n={metrics['episodes']:2d}): "
                f"Avg={metrics['average_reward']:.4f}, "
                f"Max={metrics['max_reward']:.4f}, "
                f"Min={metrics['min_reward']:.4f}"
            )
        else:
            print(f"  {difficulty:6s}: No episodes")

    print(f"\nAgent Statistics:")
    stats = results["agent_stats"]
    print(f"  Total Prompts Generated: {stats['total_prompts']}")
    print(f"  Average Prompt Effectiveness: {stats['average_score']:.4f}")
    print(f"  Best Achieved Score: {stats['max_score']:.4f}")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate PromptGym baseline agent")
    parser.add_argument(
        "--episodes", type=int, default=50, help="Number of episodes to run"
    )
    parser.add_argument(
        "--provider",
        type=str,
        choices=["mock", "openai"],
        default="mock",
        help="LLM provider to use",
    )

    args = parser.parse_args()

    try:
        results = evaluate_baseline(num_episodes=args.episodes, llm_provider=args.provider)
        print_results(results)
    except KeyboardInterrupt:
        logger.info("Evaluation interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}", exc_info=True)
        sys.exit(1)
