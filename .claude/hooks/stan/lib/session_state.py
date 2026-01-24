#!/usr/bin/env python3
"""
STAN Session State - Persistent state for a session

Storage location: .stan/session.json (in project directory)
Persists across sessions for continuity.
"""

import json
import hashlib
import os
from pathlib import Path
from datetime import datetime
from typing import Any, Optional


def get_session_file() -> Path:
    """Get session file path in .stan/ directory."""
    cwd = Path(os.getcwd())
    stan_dir = cwd / ".stan"
    # Create .stan directory if it doesn't exist
    stan_dir.mkdir(exist_ok=True)
    return stan_dir / "session.json"


def get_old_session_file() -> Path:
    """Get old-style session file path in /tmp/ (for migration)."""
    cwd = os.getcwd()
    cwd_hash = hashlib.md5(cwd.encode()).hexdigest()[:8]
    return Path(f"/tmp/claude-stan-session-{cwd_hash}.json")


def migrate_session():
    """Migrate session data from old /tmp/ location to .stan/."""
    old_file = get_old_session_file()
    new_file = get_session_file()

    # Only migrate if old exists and new doesn't
    if old_file.exists() and not new_file.exists():
        try:
            old_data = json.loads(old_file.read_text())
            new_file.write_text(json.dumps(old_data, indent=2))
            old_file.unlink()  # Remove old file after successful migration
        except (json.JSONDecodeError, IOError):
            pass  # Ignore errors, just use new location


def load_session() -> dict:
    """Load session state or create new one. Migrates old sessions automatically."""
    # Try to migrate old session from /tmp/ if it exists
    migrate_session()

    session_file = get_session_file()

    if session_file.exists():
        try:
            with open(session_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    # Neue Session
    return {
        "created_at": datetime.now().isoformat(),
        "cwd": os.getcwd(),
        "test_history": [],
        "pending_learnings": [],
        "error_counts": {},
        "phase_changes": []
    }


def save_session(state: dict):
    """Speichere Session State."""
    session_file = get_session_file()
    state["last_updated"] = datetime.now().isoformat()
    with open(session_file, "w") as f:
        json.dump(state, f, indent=2)


def get(key: str, default: Any = None) -> Any:
    """Hole Wert aus Session."""
    state = load_session()
    return state.get(key, default)


def set(key: str, value: Any):
    """Setze Wert in Session."""
    state = load_session()
    state[key] = value
    save_session(state)


def append_to(key: str, value: Any):
    """Füge Wert zu Liste hinzu."""
    state = load_session()
    if key not in state:
        state[key] = []
    state[key].append(value)
    save_session(state)


def record_test_result(command: str, exit_code: int):
    """Speichere Test-Ergebnis und erkenne ROT→GRÜN."""
    state = load_session()
    history = state.get("test_history", [])

    result = {
        "command": command,
        "exit_code": exit_code,
        "timestamp": datetime.now().isoformat(),
        "passed": exit_code == 0
    }

    # Check for ROT→GRÜN
    red_to_green = False
    if exit_code == 0 and history:
        # Finde letzten Test mit gleichem Command
        for prev in reversed(history):
            if prev["command"] == command:
                if not prev["passed"]:
                    red_to_green = True
                break

    result["red_to_green"] = red_to_green
    history.append(result)

    # Behalte nur letzte 20 Einträge
    state["test_history"] = history[-20:]
    save_session(state)

    return result


def add_pending_learning(content: str, context: str):
    """Füge pending Learning hinzu (muss vor Commit gespeichert werden)."""
    state = load_session()
    pending = state.get("pending_learnings", [])

    pending.append({
        "content": content,
        "context": context,
        "created_at": datetime.now().isoformat()
    })

    state["pending_learnings"] = pending
    save_session(state)


def get_pending_learnings() -> list:
    """Hole alle pending Learnings."""
    return get("pending_learnings", [])


def clear_pending_learnings():
    """Lösche alle pending Learnings (nach Speichern)."""
    set("pending_learnings", [])


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
    """Zähle Fehler hoch, return neue Anzahl."""
    state = load_session()
    counts = state.get("error_counts", {})
    counts[error_type] = counts.get(error_type, 0) + 1
    state["error_counts"] = counts
    save_session(state)
    return counts[error_type]


def get_error_count(error_type: str) -> int:
    """Hole aktuelle Fehleranzahl."""
    counts = get("error_counts", {})
    return counts.get(error_type, 0)


def reset_error_count(error_type: str):
    """Setze Fehleranzahl zurück."""
    state = load_session()
    counts = state.get("error_counts", {})
    if error_type in counts:
        del counts[error_type]
    state["error_counts"] = counts
    save_session(state)


def clear_session():
    """Lösche Session-Datei."""
    session_file = get_session_file()
    if session_file.exists():
        session_file.unlink()


def get_iteration_count() -> int:
    """Get current iteration count."""
    return get("iteration_count", 0)


def increment_iteration() -> int:
    """Increment iteration counter."""
    state = load_session()
    count = state.get("iteration_count", 0) + 1
    state["iteration_count"] = count
    save_session(state)
    return count


def reset_iteration_count():
    """Reset iteration counter."""
    set("iteration_count", 0)


def set_current_task(task_id: str | None):
    """Set current task, reset iteration on change."""
    state = load_session()
    current = state.get("current_task")
    if current != task_id:
        state["current_task"] = task_id
        state["iteration_count"] = 0
        save_session(state)


def get_current_task() -> str | None:
    """Get current task ID."""
    return get("current_task")
