#!/usr/bin/env python3
"""Session State Management for STAN hooks."""

import json
import os
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Any, Optional

# Session file location
SESSION_DIR = Path("/tmp")


def _get_session_id() -> str:
    """Generate a session ID based on CWD and parent PID."""
    cwd = os.getcwd()
    ppid = os.getppid()
    key = f"{cwd}:{ppid}"
    return hashlib.md5(key.encode()).hexdigest()[:12]


def get_session_file() -> Path:
    """Get path to current session state file."""
    session_id = _get_session_id()
    return SESSION_DIR / f"stan-session-{session_id}.json"


def _load_state() -> dict:
    """Load session state from file."""
    session_file = get_session_file()
    if not session_file.exists():
        return _create_default_state()

    try:
        with open(session_file, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return _create_default_state()


def _save_state(state: dict) -> None:
    """Save session state to file."""
    session_file = get_session_file()
    with open(session_file, "w") as f:
        json.dump(state, f, indent=2, default=str)


def _create_default_state() -> dict:
    """Create default session state."""
    return {
        "session_id": _get_session_id(),
        "started_at": datetime.now().isoformat(),
        "test_history": [],
        "pending_learnings": [],
        "error_counts": {},
        "last_error_type": None,
        "iteration_count": 0,
        "current_task": None,
    }


def get(key: str, default: Any = None) -> Any:
    """Get a value from session state."""
    state = _load_state()
    return state.get(key, default)


def set(key: str, value: Any) -> None:
    """Set a value in session state."""
    state = _load_state()
    state[key] = value
    _save_state(state)


def record_test_result(command: str, exit_code: int) -> dict:
    """
    Record a test result and detect red-to-green transitions.

    Args:
        command: The test command that was run
        exit_code: Exit code (0 = passed, non-zero = failed)

    Returns:
        Dict with 'passed' and 'red_to_green' keys
    """
    state = _load_state()
    history = state.get("test_history", [])

    passed = exit_code == 0

    # Check for red-to-green
    red_to_green = False
    if passed and history:
        # Look for previous run of same command
        for prev in reversed(history):
            if prev.get("command") == command:
                if not prev.get("passed"):
                    red_to_green = True
                break

    # Add to history
    history.append({
        "command": command,
        "exit_code": exit_code,
        "passed": passed,
        "timestamp": datetime.now().isoformat(),
    })

    # Keep last 100 entries
    state["test_history"] = history[-100:]
    _save_state(state)

    return {
        "passed": passed,
        "red_to_green": red_to_green,
    }


def get_last_test_result(command: Optional[str] = None) -> Optional[dict]:
    """
    Get the last test result.

    Args:
        command: Optional command to filter by

    Returns:
        Last test result or None
    """
    history = get("test_history", [])
    if not history:
        return None

    if command:
        for entry in reversed(history):
            if entry.get("command") == command:
                return entry
        return None

    return history[-1]


def add_pending_learning(content: str, context: str = "") -> None:
    """
    Add a pending learning to be saved later.

    Args:
        content: Learning content
        context: Additional context
    """
    state = _load_state()
    pending = state.get("pending_learnings", [])

    pending.append({
        "content": content,
        "context": context,
        "timestamp": datetime.now().isoformat(),
        "saved": False,
    })

    state["pending_learnings"] = pending
    _save_state(state)


def get_pending_learnings() -> list[dict]:
    """Get all pending (unsaved) learnings."""
    pending = get("pending_learnings", [])
    return [l for l in pending if not l.get("saved")]


def mark_learning_saved(index: int) -> None:
    """Mark a learning as saved."""
    state = _load_state()
    pending = state.get("pending_learnings", [])

    if 0 <= index < len(pending):
        pending[index]["saved"] = True
        state["pending_learnings"] = pending
        _save_state(state)


def clear_pending_learnings() -> None:
    """Clear all pending learnings."""
    state = _load_state()
    state["pending_learnings"] = []
    _save_state(state)


def save_pending_learnings() -> int:
    """Speichere alle pending Learnings in Local Storage und lösche sie aus Session.

    Returns:
        Anzahl der gespeicherten Learnings.
    """
    # Import hier um zirkuläre Imports zu vermeiden
    import learnings

    pending = get_pending_learnings()
    if not pending:
        return 0

    for p in pending:
        learnings.save_learning(
            content=p["content"],
            context=p["context"],
            source="auto"
        )

    clear_pending_learnings()
    return len(pending)


def increment_error(error_type: str) -> int:
    """
    Increment error counter for a type.

    Args:
        error_type: Type of error

    Returns:
        New count for this error type
    """
    state = _load_state()
    counts = state.get("error_counts", {})

    counts[error_type] = counts.get(error_type, 0) + 1
    state["error_counts"] = counts
    state["last_error_type"] = error_type
    _save_state(state)

    return counts[error_type]


def get_error_count(error_type: str) -> int:
    """Get error count for a type."""
    counts = get("error_counts", {})
    return counts.get(error_type, 0)


def reset_error_count(error_type: str) -> None:
    """Reset error count for a type."""
    state = _load_state()
    counts = state.get("error_counts", {})

    if error_type in counts:
        del counts[error_type]
        state["error_counts"] = counts
        _save_state(state)


def reset_all_errors() -> None:
    """Reset all error counts."""
    state = _load_state()
    state["error_counts"] = {}
    state["last_error_type"] = None
    _save_state(state)


def get_iteration_count() -> int:
    """Get current iteration count."""
    return get("iteration_count", 0)


def increment_iteration() -> int:
    """
    Increment iteration counter.

    Returns:
        New iteration count
    """
    state = _load_state()
    count = state.get("iteration_count", 0) + 1
    state["iteration_count"] = count
    _save_state(state)
    return count


def reset_iteration_count() -> None:
    """Reset iteration counter (e.g., when task changes)."""
    state = _load_state()
    state["iteration_count"] = 0
    _save_state(state)


def set_current_task(task_id: str | None) -> None:
    """
    Set current task being worked on.

    Resets iteration count when task changes.
    """
    state = _load_state()
    current = state.get("current_task")

    if current != task_id:
        state["current_task"] = task_id
        state["iteration_count"] = 0  # Reset on task change
        _save_state(state)


def get_current_task() -> str | None:
    """Get current task ID."""
    return get("current_task")
