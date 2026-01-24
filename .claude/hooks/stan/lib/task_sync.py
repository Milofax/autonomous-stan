#!/usr/bin/env python3
"""
STAN Task Sync - Synchronization between JSONL and Claude Tasks.

Session Start: JSONL → Claude Tasks
Runtime: Claude Tasks → JSONL
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional

from task_schema import (
    Task,
    load_tasks,
    save_tasks,
    get_task,
    update_task,
    VALID_STATUSES,
)
from task_generator import regenerate_tasks_md


# Mapping from STAN status to Claude Tasks status
STAN_TO_CLAUDE_STATUS = {
    "pending": "pending",
    "in_progress": "in_progress",
    "done": "completed",
    "blocked": "pending",  # Claude Tasks doesn't have blocked, use pending
}

# Mapping from Claude Tasks status to STAN status
CLAUDE_TO_STAN_STATUS = {
    "pending": "pending",
    "in_progress": "in_progress",
    "completed": "done",
}


class TaskSyncState:
    """
    Tracks the mapping between STAN Task IDs and Claude Task IDs.

    Stored in session state for persistence across operations.
    """

    def __init__(self):
        self.stan_to_claude: dict[str, str] = {}  # t-abcd -> "1"
        self.claude_to_stan: dict[str, str] = {}  # "1" -> t-abcd
        self.synced_at: Optional[str] = None

    def add_mapping(self, stan_id: str, claude_id: str):
        """Add a mapping between STAN and Claude task IDs."""
        self.stan_to_claude[stan_id] = claude_id
        self.claude_to_stan[claude_id] = stan_id

    def get_claude_id(self, stan_id: str) -> Optional[str]:
        """Get Claude Task ID for a STAN Task ID."""
        return self.stan_to_claude.get(stan_id)

    def get_stan_id(self, claude_id: str) -> Optional[str]:
        """Get STAN Task ID for a Claude Task ID."""
        return self.claude_to_stan.get(claude_id)

    def mark_synced(self):
        """Mark the current time as last sync."""
        self.synced_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "stan_to_claude": self.stan_to_claude,
            "claude_to_stan": self.claude_to_stan,
            "synced_at": self.synced_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TaskSyncState":
        """Create from dictionary."""
        state = cls()
        state.stan_to_claude = data.get("stan_to_claude", {})
        state.claude_to_stan = data.get("claude_to_stan", {})
        state.synced_at = data.get("synced_at")
        return state


def get_sync_state() -> TaskSyncState:
    """
    Get the current sync state from session.

    Returns new empty state if not found.
    """
    try:
        import session_state
        data = session_state.get("task_sync_state", {})
        return TaskSyncState.from_dict(data)
    except Exception:
        return TaskSyncState()


def save_sync_state(state: TaskSyncState):
    """Save sync state to session."""
    try:
        import session_state
        session_state.set("task_sync_state", state.to_dict())
    except Exception:
        pass  # Fail silently if session not available


def prepare_claude_task_params(task: Task, all_tasks: dict[str, Task]) -> dict:
    """
    Prepare parameters for TaskCreate from a STAN Task.

    Returns dict suitable for Claude TaskCreate tool.
    """
    # Build blockedBy list from dependencies
    blocked_by = []
    sync_state = get_sync_state()

    for dep_id in task.dependencies:
        claude_id = sync_state.get_claude_id(dep_id)
        if claude_id:
            blocked_by.append(claude_id)

    # Build description with acceptance criteria
    description = task.description or ""
    if task.acceptance_criteria:
        if description:
            description += "\n\n"
        description += "Acceptance Criteria:\n"
        for ac in task.acceptance_criteria:
            description += f"- {ac}\n"

    return {
        "subject": f"[{task.id}] {task.subject}",
        "description": description,
        "activeForm": f"Working on {task.subject}",
        # blockedBy would be set after all tasks are created
    }


def sync_to_claude_tasks(tasks: Optional[dict[str, Task]] = None) -> list[dict]:
    """
    Sync STAN Tasks to Claude Tasks at session start.

    Creates Claude Tasks for all pending/in_progress STAN tasks.

    Args:
        tasks: Optional dict of tasks. If None, loads from JSONL.

    Returns:
        List of dicts with TaskCreate parameters for each task.
        The caller (skill) should execute these with the TaskCreate tool.
    """
    if tasks is None:
        tasks = load_tasks()

    sync_state = get_sync_state()
    tasks_to_create = []

    for task in tasks.values():
        # Only sync pending and in_progress tasks
        if task.status not in ("pending", "in_progress"):
            continue

        # Skip if already synced
        if sync_state.get_claude_id(task.id):
            continue

        params = prepare_claude_task_params(task, tasks)
        tasks_to_create.append({
            "stan_id": task.id,
            "params": params,
        })

    return tasks_to_create


def register_claude_task(stan_id: str, claude_id: str):
    """
    Register the mapping after a Claude Task is created.

    Call this after TaskCreate returns with the new task ID.
    """
    sync_state = get_sync_state()
    sync_state.add_mapping(stan_id, claude_id)
    save_sync_state(sync_state)


def sync_from_claude_task(claude_id: str, new_status: str) -> Optional[Task]:
    """
    Sync a Claude Task status change back to JSONL.

    Args:
        claude_id: The Claude Task ID that changed
        new_status: The new Claude Task status (pending, in_progress, completed)

    Returns:
        Updated Task if found, None otherwise
    """
    sync_state = get_sync_state()
    stan_id = sync_state.get_stan_id(claude_id)

    if not stan_id:
        return None

    # Map Claude status to STAN status
    stan_status = CLAUDE_TO_STAN_STATUS.get(new_status)
    if not stan_status:
        return None

    # Update STAN task
    try:
        updated_task = update_task(stan_id, status=stan_status)

        # Regenerate markdown
        regenerate_tasks_md()

        return updated_task
    except ValueError:
        return None


def sync_task_completion(stan_id: str) -> Optional[Task]:
    """
    Mark a STAN task as done and sync.

    Convenience function for when a task is completed.
    """
    try:
        updated_task = update_task(stan_id, status="done")
        regenerate_tasks_md()
        return updated_task
    except ValueError:
        return None


def get_sync_instructions() -> str:
    """
    Get instructions for syncing tasks at session start.

    Returns markdown instructions for the /stan create skill.
    """
    tasks = load_tasks()
    tasks_to_sync = sync_to_claude_tasks(tasks)

    if not tasks_to_sync:
        return "[STAN] No tasks to sync. All tasks are already done or synced."

    lines = []
    lines.append("[STAN] Syncing tasks to Claude Tasks...")
    lines.append("")
    lines.append("Create the following Claude Tasks:")
    lines.append("")

    for item in tasks_to_sync:
        stan_id = item["stan_id"]
        params = item["params"]
        lines.append(f"- {stan_id}: {params['subject']}")

    lines.append("")
    lines.append("After creating each task, register the mapping with:")
    lines.append("```python")
    lines.append("from task_sync import register_claude_task")
    lines.append("register_claude_task(stan_id, claude_task_id)")
    lines.append("```")

    return "\n".join(lines)


def get_pending_tasks_for_sync() -> list[Task]:
    """
    Get list of pending tasks that need to be synced.

    Returns tasks that are pending/in_progress and not yet synced.
    """
    tasks = load_tasks()
    sync_state = get_sync_state()
    result = []

    for task in tasks.values():
        if task.status in ("pending", "in_progress"):
            if not sync_state.get_claude_id(task.id):
                result.append(task)

    return result


def clear_sync_state():
    """Clear the sync state (for testing or reset)."""
    save_sync_state(TaskSyncState())
