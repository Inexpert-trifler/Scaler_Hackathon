"""Session management for PromptGym."""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


@dataclass
class SessionState:
    """State of a single session."""

    session_id: str
    current_task: dict
    step_count: int = 0
    last_reward: float = 0.0
    total_reward: float = 0.0
    done: bool = False
    difficulty: str = "easy"
    history: List[dict] = field(default_factory=list)


class SessionManager:
    """In-memory session management."""

    _sessions: Dict[str, SessionState] = {}

    @classmethod
    def create_session(
        cls, task: dict, difficulty: str, session_id: Optional[str] = None
    ) -> SessionState:
        """Create a new session."""
        if session_id is None:
            session_id = str(uuid4())

        session = SessionState(
            session_id=session_id, current_task=task, difficulty=difficulty
        )
        cls._sessions[session_id] = session
        logger.debug(f"Created session {session_id}")
        return session

    @classmethod
    def get_session(cls, session_id: str) -> SessionState:
        """Get existing session or raise KeyError."""
        if session_id not in cls._sessions:
            raise KeyError(f"Session not found: {session_id}")
        return cls._sessions[session_id]

    @classmethod
    def update_session(
        cls,
        session_id: str,
        reward: float,
        done: bool,
        prompt: str,
        output: str,
    ) -> SessionState:
        """Update session with step result."""
        session = cls.get_session(session_id)

        session.step_count += 1
        session.last_reward = reward
        session.total_reward += reward
        session.done = done

        session.history.append(
            {
                "step": session.step_count,
                "prompt": prompt,
                "output": output,
                "reward": reward,
            }
        )

        return session

    @classmethod
    def delete_session(cls, session_id: str) -> None:
        """Delete a session."""
        if session_id in cls._sessions:
            del cls._sessions[session_id]
            logger.debug(f"Deleted session {session_id}")

    @classmethod
    def list_sessions(cls) -> List[str]:
        """List all active session IDs."""
        return list(cls._sessions.keys())

    @classmethod
    def get_all_sessions(cls) -> Dict[str, SessionState]:
        """Get all sessions."""
        return dict(cls._sessions)

    @classmethod
    def clear_all(cls) -> None:
        """Clear all sessions (for testing)."""
        cls._sessions.clear()
