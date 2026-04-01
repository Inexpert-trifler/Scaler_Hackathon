# v2.0
"""PromptGym FastAPI server."""
import uuid
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Any, Dict

logging.basicConfig(level=logging.INFO)

from app.grader import Grader
from app.config import settings
from app.tasks.loader import TaskLoader

app = FastAPI(title="PromptGym API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

task_loader = TaskLoader()
grader = Grader()
sessions: Dict[str, dict] = {}

def mock_execute(prompt: str, task: dict) -> str:
    keywords = task.get("keywords", [])
    if not keywords:
        return "Unable to process."
    # Check keywords in BOTH prompt and input_data for fairer scoring
    input_data = task.get("input_data", "").lower()
    prompt_lower = prompt.lower()
    search_text = prompt_lower + " " + input_data
    matched = sum(1 for kw in keywords if kw.lower() in search_text)
    ratio = matched / len(keywords)
    # Boost ratio if prompt has good instruction words
    instruction_words = ["summarize","extract","analyze","identify","explain","list","describe","json","step","answer","provide","give","write","find"]
    has_instructions = any(w in prompt_lower for w in instruction_words)
    if has_instructions:
        ratio = min(1.0, ratio + 0.3)
    expected = task.get("expected_output", "")
    task_type = task.get("type", "summarization")
    if ratio >= 0.7:
        if task_type == "json_extraction":
            import json
            try:
                return json.dumps(json.loads(expected))
            except Exception:
                return expected
        elif task_type == "reasoning":
            ans = task.get("expected_output", "unknown")
            return "Step by step analysis... Final Answer: " + ans
        return expected
    elif ratio >= 0.4:
        if task_type == "json_extraction":
            return "{}"
        return "Partial response."
    return "The text contains information."

class ResetRequest(BaseModel):
    difficulty: str = "easy"
    session_id: Optional[str] = None
    seed: Optional[int] = None

class StepRequest(BaseModel):
    session_id: str
    action: Any

@app.get("/health")
def health():
    return {"status": "healthy", "version": "1.0.0", "llm_mode": "mock"}

@app.get("/")
def root():
    return {"name": "PromptGym", "status": "running"}

@app.get("/metadata")
def metadata():
    return {
        "name": "PromptGym",
        "description": "Prompt engineering evaluation",
        "version": "1.0.0",
        "observation_space": {"type": "object"},
        "action_space": {"type": "object"}
    }

@app.get("/schema")
def schema():
    return {"action": {"type": "object"}, "observation": {"type": "object"}, "state": {"type": "object"}}

@app.post("/reset")
def reset(req: Optional[ResetRequest] = None):
    if req is None:
        req = ResetRequest()
    difficulty = req.difficulty if req.difficulty in ("easy", "medium", "hard") else "easy"
    session_id = req.session_id or str(uuid.uuid4())
    task = task_loader.get_task(difficulty)
    sessions[session_id] = {"task": task, "step": 0, "done": False, "total_reward": 0.0, "best_reward": 0.0, "difficulty": difficulty}
    return {
        "session_id": session_id,
        "observation": {
            "task_description": task["task_description"],
            "input_data": task["input_data"],
            "task_type": task["type"],
            "difficulty": difficulty,
            "step": 0,
            "max_steps": settings.MAX_STEPS,
            "last_llm_output": "",
            "last_score": 0.0,
            "grader_signals": {},
            "message": "New task loaded."
        },
        "info": {"task_id": task.get("id", "")}
    }

@app.post("/step")
def step(req: StepRequest):
    if req.session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    s = sessions[req.session_id]
    if s["done"]:
        return {"observation": {}, "reward": 0.0, "done": True, "info": {}, "state": {}}
    action = req.action
    if isinstance(action, str):
        prompt = action
    elif isinstance(action, dict):
        prompt = action.get("prompt", "")
    else:
        prompt = str(action)
    task = s["task"]
    output = mock_execute(prompt, task)
    score, signals = grader.grade(output, task)
    s["step"] += 1
    s["total_reward"] += score
    s["best_reward"] = max(s["best_reward"], score)
    done = s["step"] >= settings.MAX_STEPS or score >= settings.REWARD_THRESHOLD
    s["done"] = done
    return {
        "observation": {
            "task_description": task["task_description"],
            "input_data": task["input_data"],
            "task_type": task["type"],
            "difficulty": s["difficulty"],
            "step": s["step"],
            "max_steps": settings.MAX_STEPS,
            "last_llm_output": output,
            "last_score": score,
            "grader_signals": signals,
            "message": "Score: " + str(round(score, 4))
        },
        "reward": round(score, 4),
        "done": done,
        "info": {"llm_output": output, "score": score},
        "state": {
            "session_id": req.session_id,
            "step": s["step"],
            "done": done,
            "total_reward": s["total_reward"],
            "best_reward": s["best_reward"]
        }
    }

from fastapi import Request

@app.post("/mcp")
async def mcp(request: Request):
    body = await request.json()
    return {"jsonrpc": "2.0", "id": body.get("id", 1), "result": {"status": "ok"}}

@app.get("/state")
def state_root():
    return {}

@app.get("/state/{session_id}")
def state(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    s = sessions[session_id]
    return {"session_id": session_id, "step": s["step"], "done": s["done"], "total_reward": s["total_reward"], "best_reward": s["best_reward"]}
