#!/usr/bin/env python3
"""
STAN Task Schema - JSONL-based task storage with hash IDs.

Source of Truth: .stan/tasks.jsonl
Inspired by beads (vendor/beads/) architecture.
"""

import json
import hashlib
import uuid
import os
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional


# Valid task statuses
VALID_STATUSES = {"pending", "in_progress", "done", "blocked"}

# Valid phases
VALID_PHASES = {"define", "plan", "create"}

# Task ID prefix
TASK_ID_PREFIX = "t-"


@dataclass
class Task:
    """A single task in the JSONL task system."""

    id: str
    subject: str
    description: str = ""
    status: str = "pending"
    phase: str = "create"
    dependencies: list[str] = field(default_factory=list)
    acceptance_criteria: list[str] = field(default_factory=list)
    owner: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        """Validate task on creation."""
        self.validate()

    def validate(self) -> list[str]:
        """Validate task fields. Returns list of errors (empty if valid)."""
        errors = []

        # Required fields
        if not self.id:
            errors.append("id is required")
        elif not self.id.startswith(TASK_ID_PREFIX):
            errors.append(f"id must start with '{TASK_ID_PREFIX}'")

        if not self.subject:
            errors.append("subject is required")

        # Valid status
        if self.status not in VALID_STATUSES:
            errors.append(f"status must be one of: {VALID_STATUSES}")

        # Valid phase
        if self.phase not in VALID_PHASES:
            errors.append(f"phase must be one of: {VALID_PHASES}")

        # Dependencies must be list of strings
        if not isinstance(self.dependencies, list):
            errors.append("dependencies must be a list")
        elif not all(isinstance(d, str) for d in self.dependencies):
            errors.append("dependencies must be strings")

        # Acceptance criteria must be list of strings
        if not isinstance(self.acceptance_criteria, list):
            errors.append("acceptance_criteria must be a list")
        elif not all(isinstance(ac, str) for ac in self.acceptance_criteria):
            errors.append("acceptance_criteria must be strings")

        if errors:
            raise ValueError(f"Task validation failed: {errors}")

        return errors

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string (one line for JSONL)."""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        """Create Task from dictionary."""
        # Handle missing optional fields
        return cls(
            id=data["id"],
            subject=data["subject"],
            description=data.get("description", ""),
            status=data.get("status", "pending"),
            phase=data.get("phase", "create"),
            dependencies=data.get("dependencies", []),
            acceptance_criteria=data.get("acceptance_criteria", []),
            owner=data.get("owner"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "Task":
        """Create Task from JSON string."""
        return cls.from_dict(json.loads(json_str))

    def mark_updated(self):
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now().isoformat()

    def is_ready(self, all_tasks: dict[str, "Task"]) -> bool:
        """Check if task is ready (pending with no open blockers)."""
        if self.status != "pending":
            return False

        # Check all dependencies are done
        for dep_id in self.dependencies:
            dep_task = all_tasks.get(dep_id)
            if dep_task is None:
                # Missing dependency - treat as blocking
                return False
            if dep_task.status != "done":
                return False

        return True


def generate_task_id(existing_ids: set[str] = None) -> str:
    """
    Generate a unique hash-based task ID.

    Format: t-xxxx (4-6 chars, collision-free)
    Uses UUID + hash for uniqueness across worktrees/agents.
    """
    if existing_ids is None:
        existing_ids = set()

    # Try progressively longer hashes until unique
    for length in range(4, 8):
        # Generate UUID-based hash
        unique_str = str(uuid.uuid4())
        hash_bytes = hashlib.sha256(unique_str.encode()).hexdigest()
        task_id = f"{TASK_ID_PREFIX}{hash_bytes[:length]}"

        if task_id not in existing_ids:
            return task_id

    # Fallback: full 8-char hash (extremely unlikely to need this)
    return f"{TASK_ID_PREFIX}{hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:8]}"


def get_tasks_file() -> Path:
    """Get the path to .stan/tasks.jsonl."""
    cwd = Path(os.getcwd())
    return cwd / ".stan" / "tasks.jsonl"


def load_tasks() -> dict[str, Task]:
    """
    Load all tasks from .stan/tasks.jsonl.

    Returns:
        Dict mapping task ID to Task object.
    """
    tasks_file = get_tasks_file()
    tasks = {}

    if not tasks_file.exists():
        return tasks

    with open(tasks_file, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            try:
                data = json.loads(line)
                task = Task.from_dict(data)
                tasks[task.id] = task
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                # Log error but continue loading other tasks
                print(f"Warning: Failed to parse task on line {line_num}: {e}")

    return tasks


def save_tasks(tasks: dict[str, Task]):
    """
    Save all tasks to .stan/tasks.jsonl.

    Overwrites the file with current state.
    """
    tasks_file = get_tasks_file()

    # Ensure .stan directory exists
    tasks_file.parent.mkdir(parents=True, exist_ok=True)

    with open(tasks_file, "w", encoding="utf-8") as f:
        for task in tasks.values():
            f.write(task.to_json() + "\n")


def add_task(task: Task) -> Task:
    """Add a new task to the JSONL file."""
    tasks = load_tasks()

    # Validate ID doesn't exist
    if task.id in tasks:
        raise ValueError(f"Task with ID {task.id} already exists")

    tasks[task.id] = task
    save_tasks(tasks)
    return task


def update_task(task_id: str, **updates) -> Task:
    """
    Update an existing task.

    Args:
        task_id: The task ID to update
        **updates: Fields to update (status, description, etc.)

    Returns:
        Updated Task object
    """
    tasks = load_tasks()

    if task_id not in tasks:
        raise ValueError(f"Task {task_id} not found")

    task = tasks[task_id]

    # Apply updates
    for key, value in updates.items():
        if hasattr(task, key):
            setattr(task, key, value)

    task.mark_updated()
    task.validate()

    save_tasks(tasks)
    return task


def get_task(task_id: str) -> Optional[Task]:
    """Get a single task by ID."""
    tasks = load_tasks()
    return tasks.get(task_id)


def get_ready_tasks(phase: Optional[str] = None) -> list[Task]:
    """
    Get all tasks that are ready to work on.

    Args:
        phase: Optional filter by phase (define, plan, create)

    Returns:
        List of ready tasks (pending with no open blockers)
    """
    tasks = load_tasks()
    ready = []

    for task in tasks.values():
        if task.is_ready(tasks):
            if phase is None or task.phase == phase:
                ready.append(task)

    return ready


def get_blocked_tasks() -> list[tuple[Task, list[str]]]:
    """
    Get all blocked tasks with their blockers.

    Returns:
        List of (task, [blocker_ids]) tuples
    """
    tasks = load_tasks()
    blocked = []

    for task in tasks.values():
        if task.status == "pending" and task.dependencies:
            blockers = []
            for dep_id in task.dependencies:
                dep_task = tasks.get(dep_id)
                if dep_task is None or dep_task.status != "done":
                    blockers.append(dep_id)

            if blockers:
                blocked.append((task, blockers))

    return blocked


def create_task(
    subject: str,
    description: str = "",
    phase: str = "create",
    dependencies: list[str] = None,
    acceptance_criteria: list[str] = None,
    owner: Optional[str] = None,
) -> Task:
    """
    Create a new task with auto-generated hash ID.

    Convenience function that generates ID and adds to JSONL.
    """
    tasks = load_tasks()
    existing_ids = set(tasks.keys())

    task_id = generate_task_id(existing_ids)

    task = Task(
        id=task_id,
        subject=subject,
        description=description,
        phase=phase,
        dependencies=dependencies or [],
        acceptance_criteria=acceptance_criteria or [],
        owner=owner,
    )

    return add_task(task)


def delete_task(task_id: str) -> bool:
    """
    Delete a task from the JSONL file.

    Returns:
        True if deleted, False if not found
    """
    tasks = load_tasks()

    if task_id not in tasks:
        return False

    del tasks[task_id]
    save_tasks(tasks)
    return True


def get_tasks_by_status(status: str) -> list[Task]:
    """Get all tasks with a specific status."""
    tasks = load_tasks()
    return [t for t in tasks.values() if t.status == status]


def get_tasks_by_phase(phase: str) -> list[Task]:
    """Get all tasks in a specific phase."""
    tasks = load_tasks()
    return [t for t in tasks.values() if t.phase == phase]
