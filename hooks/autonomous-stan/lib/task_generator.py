#!/usr/bin/env python3
"""
STAN Task Generator - Generate docs/tasks.md from .stan/tasks.jsonl

The generated markdown is READ-ONLY. Source of truth is the JSONL file.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional

# Import from task_schema (same directory)
from task_schema import (
    Task,
    load_tasks,
    get_tasks_file,
    VALID_PHASES,
)


# Status symbols
STATUS_SYMBOLS = {
    "pending": "·",
    "in_progress": "►",
    "done": "✓",
    "parked": "~",
    "archived": "§",
    "blocked": "⏸",
}

# Phase display names
PHASE_NAMES = {
    "define": "DEFINE",
    "plan": "PLAN",
    "create": "CREATE",
}


def get_status_symbol(status: str) -> str:
    """Get the display symbol for a status."""
    return STATUS_SYMBOLS.get(status, "?")


def get_docs_tasks_file() -> Path:
    """Get the path to docs/tasks.md."""
    cwd = Path(os.getcwd())
    return cwd / "docs" / "tasks.md"


def format_task(task: Task, all_tasks: dict[str, Task]) -> str:
    """
    Format a single task as markdown.

    Returns multi-line markdown string for the task.
    """
    lines = []

    # Task header with status symbol
    symbol = get_status_symbol(task.status)
    lines.append(f"### {symbol} {task.id}: {task.subject}")
    lines.append("")

    # Description
    if task.description:
        lines.append(f"**Description:** {task.description}")
        lines.append("")

    # Status
    lines.append(f"**Status:** {task.status}")

    # Owner (if assigned)
    if task.owner:
        lines.append(f"**Owner:** {task.owner}")

    # Dependencies
    if task.dependencies:
        dep_str = ", ".join(task.dependencies)
        lines.append(f"**Depends on:** {dep_str}")

    lines.append("")

    # Acceptance Criteria
    if task.acceptance_criteria:
        lines.append("**Acceptance Criteria:**")
        for ac in task.acceptance_criteria:
            # Mark as checked if task is done
            checkbox = "[x]" if task.status == "done" else "[ ]"
            lines.append(f"- {checkbox} {ac}")
        lines.append("")

    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def format_phase_section(phase: str, tasks: list[Task], all_tasks: dict[str, Task]) -> str:
    """
    Format all tasks in a phase as a markdown section.
    """
    if not tasks:
        return ""

    lines = []
    phase_name = PHASE_NAMES.get(phase, phase.upper())

    # Count stats
    done_count = sum(1 for t in tasks if t.status == "done")
    total_count = len(tasks)

    lines.append(f"## Phase: {phase_name} ({done_count}/{total_count})")
    lines.append("")

    # Sort tasks: in_progress first, then pending, then blocked, then done
    status_order = {"in_progress": 0, "pending": 1, "blocked": 2, "done": 3}
    sorted_tasks = sorted(tasks, key=lambda t: (status_order.get(t.status, 4), t.id))

    for task in sorted_tasks:
        lines.append(format_task(task, all_tasks))

    return "\n".join(lines)


def generate_summary_table(all_tasks: dict[str, Task]) -> str:
    """Generate a summary table of tasks by phase and status."""
    lines = []
    lines.append("## Summary")
    lines.append("")
    lines.append("| Phase | Pending | In Progress | Done | Blocked | Total |")
    lines.append("|-------|---------|-------------|------|---------|-------|")

    for phase in VALID_PHASES:
        phase_tasks = [t for t in all_tasks.values() if t.phase == phase]
        if not phase_tasks:
            continue

        pending = sum(1 for t in phase_tasks if t.status == "pending")
        in_progress = sum(1 for t in phase_tasks if t.status == "in_progress")
        done = sum(1 for t in phase_tasks if t.status == "done")
        blocked = sum(1 for t in phase_tasks if t.status == "blocked")
        total = len(phase_tasks)

        phase_name = PHASE_NAMES.get(phase, phase.upper())
        lines.append(f"| {phase_name} | {pending} | {in_progress} | {done} | {blocked} | {total} |")

    lines.append("")
    return "\n".join(lines)


def generate_tasks_md(tasks: Optional[dict[str, Task]] = None) -> str:
    """
    Generate the complete docs/tasks.md content from JSONL tasks.

    Args:
        tasks: Optional dict of tasks. If None, loads from .stan/tasks.jsonl

    Returns:
        Complete markdown string for docs/tasks.md
    """
    if tasks is None:
        tasks = load_tasks()

    lines = []

    # Header with warning
    lines.append("# STAN Tasks")
    lines.append("")
    lines.append("> **AUTO-GENERATED** from `.stan/tasks.jsonl` - DO NOT EDIT DIRECTLY")
    lines.append(">")
    lines.append(f"> Last generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # Status legend
    lines.append("## Status Legend")
    lines.append("")
    lines.append("| Symbol | Status | Meaning |")
    lines.append("|--------|--------|---------|")
    lines.append("| `·` | pending | **Required** - Waiting to start |")
    lines.append("| `►` | in_progress | Currently being worked on |")
    lines.append("| `✓` | done | Completed |")
    lines.append("| `~` | parked | Optional - Deliberately deferred |")
    lines.append("| `§` | archived | Not implementing |")
    lines.append("| `⏸` | blocked | Blocked by dependencies |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Summary table
    if tasks:
        lines.append(generate_summary_table(tasks))
        lines.append("---")
        lines.append("")

    # Tasks by phase
    for phase in ["define", "plan", "create"]:
        phase_tasks = [t for t in tasks.values() if t.phase == phase]
        if phase_tasks:
            lines.append(format_phase_section(phase, phase_tasks, tasks))

    # No tasks message
    if not tasks:
        lines.append("## No Tasks")
        lines.append("")
        lines.append("No tasks found in `.stan/tasks.jsonl`.")
        lines.append("")
        lines.append("Use `/stan plan` to create tasks from your PRD.")
        lines.append("")

    return "\n".join(lines)


def write_tasks_md(tasks: Optional[dict[str, Task]] = None) -> Path:
    """
    Generate and write docs/tasks.md from JSONL tasks.

    Args:
        tasks: Optional dict of tasks. If None, loads from .stan/tasks.jsonl

    Returns:
        Path to the written file
    """
    content = generate_tasks_md(tasks)
    output_file = get_docs_tasks_file()

    # Ensure docs directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    output_file.write_text(content, encoding="utf-8")
    return output_file


def regenerate_tasks_md() -> Path:
    """
    Convenience function to regenerate docs/tasks.md from current JSONL.

    Returns:
        Path to the written file
    """
    return write_tasks_md()


def get_ready_tasks_summary() -> str:
    """
    Get a formatted summary of ready tasks for display.

    Used by /stan ready skill.
    """
    tasks = load_tasks()
    ready = []

    for task in tasks.values():
        if task.is_ready(tasks):
            ready.append(task)

    if not ready:
        return "[STAN] No ready tasks. All tasks are either done or blocked."

    lines = []
    lines.append(f"[STAN] Ready Tasks ({len(ready)} tasks):")
    lines.append("")

    for task in sorted(ready, key=lambda t: t.id):
        phase_tag = f"[{task.phase}]"
        lines.append(f"  {task.id}  {task.subject:<40} {phase_tag}")

    lines.append("")
    lines.append("Use `/stan create` to start working on these tasks.")

    return "\n".join(lines)
