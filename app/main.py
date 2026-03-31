"""FastAPI application for PromptGym backend."""

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.env import PromptGymEnv
from app.schemas import (
    HealthResponse,
    ResetRequest,
    ResetResponse,
    StepRequest,
    StepResponse,
)
from app.session import SessionManager

logger = logging.getLogger(__name__)

# Module-level environment singleton
_env: Optional[PromptGymEnv] = None


def get_env() -> PromptGymEnv:
    """Get or initialize the environment."""
    global _env
    if _env is None:
        _env = PromptGymEnv()
    return _env


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    global _env
    _env = PromptGymEnv()
    
    banner = """
    ╔══════════════════════════════════════════════════════╗
    ║     🎯 PromptGym Backend Started Successfully 🎯     ║
    ╚══════════════════════════════════════════════════════╝
    """
    print(banner)
    logger.info(f"Started PromptGym on {settings.HOST}:{settings.PORT}")
    logger.info(f"LLM Mode: {settings.LLM_MODE}")
    logger.info(f"Use Torch Scorer: {settings.USE_TORCH_SCORER}")
    
    yield
    
    logger.info("PromptGym Backend shutting down")


app = FastAPI(
    title="PromptGym",
    description="LLM training backend",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware for HuggingFace Spaces
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        llm_mode=settings.LLM_MODE,
        version="1.0.0"
    )

@app.get("/")
async def root():
    return {"message": "PromptGym API is running"}


@app.post("/reset", response_model=ResetResponse)
async def reset(request: ResetRequest):
    """Reset environment and start new episode."""
    try:
        env = get_env()
        response = env.reset(difficulty=request.difficulty, session_id=request.session_id)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Reset error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/step", response_model=StepResponse)
async def step(request: StepRequest):
    """Execute one step in environment."""
    try:
        env = get_env()
        response = env.step(request.session_id, request.action)
        return response
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logger.error(f"Step error: {e}")
        # Return failed step (reward=0.0) but keep episode alive
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/state/{session_id}")
async def get_state(session_id: str):
    """Get current session state."""
    try:
        env = get_env()
        state = env.state(session_id)
        return state
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logger.error(f"State error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/tasks/{difficulty}")
async def get_tasks(difficulty: str):
    """Get all tasks for difficulty."""
    try:
        env = get_env()
        tasks = env.task_loader.list_tasks(difficulty)
        return {
            "difficulty": difficulty,
            "count": len(tasks),
            "tasks": [{"id": t.get("id"), "type": t.get("type")} for t in tasks],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Tasks error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/leaderboard")
async def get_leaderboard():
    """Get leaderboard of all completed sessions."""
    try:
        sessions_dict = SessionManager.get_all_sessions()
        leaderboard = [
            {
                "session_id": s.session_id,
                "total_reward": s.total_reward,
                "steps": s.step_count,
                "difficulty": s.difficulty,
                "done": s.done,
            }
            for s in sessions_dict.values()
        ]
        leaderboard.sort(key=lambda x: x["total_reward"], reverse=True)
        return {"leaderboard": leaderboard, "total_sessions": len(leaderboard)}
    except Exception as e:
        logger.error(f"Leaderboard error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/delete/{session_id}")
async def delete_session(session_id: str):
    """Delete a session."""
    try:
        SessionManager.delete_session(session_id)
        return {"status": "deleted", "session_id": session_id}
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logger.error(f"Delete error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
