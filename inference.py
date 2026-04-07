"""Inference module for PromptGym - Hackathon submission entry point."""

import os
import textwrap
import time
from typing import List, Optional

import requests
from openai import OpenAI

from client import PromptGymEnv
from models import PromptAction

# LLM Configuration per Hackathon rules
HF_TOKEN = os.getenv("HF_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")

# Env configuration
ENV_API_URL = os.getenv("OPENENV_URL", "http://localhost:7860")

TEMPERATURE = 0.7
MAX_TOKENS = 500
SUCCESS_SCORE_THRESHOLD = 0.5


def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    
    # We must sanitize action string so it doesn't break the single line format
    action_str = repr(action).replace('\n', '\\n')
    
    print(
        f"[STEP] step={step} action={action_str} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


def get_model_prompt(client: OpenAI, task_desc: str, input_data: str, difficulty: str) -> str:
    system_prompt = "You are an expert prompt engineer. Your job is to create the perfect prompt to solve a specific task."
    
    user_prompt = textwrap.dedent(f"""
        Task Description: {task_desc}
        Input Data: {input_data}
        Difficulty: {difficulty}
        
        Write a single, highly effective prompt that will guide an LLM to perfectly solve this task for the given input data.
        Return ONLY the prompt string itself, nothing else. No quotes, no intro text.
    """).strip()
    
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        text = (completion.choices[0].message.content or "").strip()
        return text if text else f"Please process the input data '{input_data}' according to the task description."
    except Exception as exc:
        print(f"[DEBUG] Model request failed: {exc}", flush=True)
        return f"Process this: {input_data} based on {task_desc}"


def run_episode(env_client: PromptGymEnv, openai_client: OpenAI, difficulty: str, task_idx: int) -> dict:
    task_name = f"promptgym-{difficulty.lower()}-{task_idx}"
    benchmark = "promptgym"
    log_start(task=task_name, env=benchmark, model=MODEL_NAME)
    
    rewards: List[float] = []
    steps_taken = 0
    success = False
    
    try:
        observation = env_client.reset(difficulty=difficulty)
        
        # The promptgym environment is basically a single-step environment per task.
        steps_taken = 1
        
        # Generate the action using the required OpenAI client
        prompt = get_model_prompt(
            openai_client, 
            observation.task_description, 
            observation.input_data, 
            difficulty
        )
        
        action = PromptAction(prompt=prompt)
        try:
            result_obs = env_client.step(action)
            reward = float(result_obs.reward)
            done = result_obs.done
            error = None
        except Exception as e:
            reward = 0.0
            done = True
            error = str(e)
            
        rewards.append(reward)
        log_step(step=1, action=prompt, reward=reward, done=done, error=error)
        
        score = reward
        success = score >= SUCCESS_SCORE_THRESHOLD
        
    except Exception as e:
        score = 0.0
        success = False
        print(f"[DEBUG] Episode error: {e}", flush=True)
        
    log_end(success=success, steps=steps_taken, score=score, rewards=rewards)
    return {"difficulty": difficulty, "task_idx": task_idx, "score": score, "success": success}


def main():
    print(f"[DEBUG] Checking if environment server at {ENV_API_URL} is ready...", flush=True)
    # Wait for the environment server to be ready
    for _ in range(30):
        try:
            requests.get(f"{ENV_API_URL}/health", timeout=2)
            break
        except Exception:
            time.sleep(1)
            
    env_client = PromptGymEnv(base_url=ENV_API_URL)
    
    # Initialize OpenAI client 
    client_kwargs = {"api_key": HF_TOKEN}
    if API_BASE_URL:
        client_kwargs["base_url"] = API_BASE_URL
        
    openai_client = OpenAI(**client_kwargs)

    # In openenv.yaml, we declared 3 tasks for EASY, 3 for MEDIUM, 3 for HARD
    tasks_per_level = 3
    
    for difficulty in ["EASY", "MEDIUM", "HARD"]:
        for task_idx in range(tasks_per_level):
            run_episode(env_client, openai_client, difficulty, task_idx + 1)


if __name__ == "__main__":
    main()
