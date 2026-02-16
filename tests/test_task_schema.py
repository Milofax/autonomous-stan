#!/usr/bin/env python3
"""Tests for STAN Task Schema (T-047)."""

import json
import os
import sys
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch

# Path configured in conftest.py

from task_schema import (
    Task,
    VALID_STATUSES,
    VALID_PHASES,
    TASK_ID_PREFIX,
    generate_task_id,
    load_tasks,
    save_tasks,
    add_task,
    update_task,
    get_task,
    get_ready_tasks,
    get_blocked_tasks,
    create_task,
    delete_task,
    get_tasks_by_status,
    get_tasks_by_phase,
)


class TestTask:
    """Tests for Task dataclass."""

    def test_create_valid_task(self):
        """Test creating a valid task."""
        task = Task(
            id="t-abcd",
            subject="Test task",
            description="A test task",
        )
        assert task.id == "t-abcd"
        assert task.subject == "Test task"
        assert task.status == "pending"
        assert task.phase == "create"

    def test_task_requires_id_prefix(self):
        """Test that task ID must start with prefix."""
        with pytest.raises(ValueError, match="must start with"):
            Task(id="abcd", subject="Test")

    def test_task_requires_subject(self):
        """Test that subject is required."""
        with pytest.raises(ValueError, match="subject is required"):
            Task(id="t-abcd", subject="")

    def test_task_validates_status(self):
        """Test that status must be valid."""
        with pytest.raises(ValueError, match="status must be one of"):
            Task(id="t-abcd", subject="Test", status="invalid")

    def test_task_validates_phase(self):
        """Test that phase must be valid."""
        with pytest.raises(ValueError, match="phase must be one of"):
            Task(id="t-abcd", subject="Test", phase="invalid")

    def test_task_to_dict(self):
        """Test converting task to dict."""
        task = Task(id="t-abcd", subject="Test")
        d = task.to_dict()
        assert d["id"] == "t-abcd"
        assert d["subject"] == "Test"
        assert "created_at" in d

    def test_task_to_json(self):
        """Test converting task to JSON."""
        task = Task(id="t-abcd", subject="Test")
        json_str = task.to_json()
        data = json.loads(json_str)
        assert data["id"] == "t-abcd"

    def test_task_from_dict(self):
        """Test creating task from dict."""
        data = {"id": "t-abcd", "subject": "Test", "status": "in_progress"}
        task = Task.from_dict(data)
        assert task.id == "t-abcd"
        assert task.status == "in_progress"

    def test_task_from_json(self):
        """Test creating task from JSON."""
        json_str = '{"id": "t-abcd", "subject": "Test"}'
        task = Task.from_json(json_str)
        assert task.id == "t-abcd"

    def test_task_is_ready_no_deps(self):
        """Test is_ready with no dependencies."""
        task = Task(id="t-abcd", subject="Test", status="pending")
        assert task.is_ready({}) is True

    def test_task_is_ready_with_done_deps(self):
        """Test is_ready with all dependencies done."""
        dep = Task(id="t-0001", subject="Dep", status="done")
        task = Task(id="t-abcd", subject="Test", dependencies=["t-0001"])
        assert task.is_ready({"t-0001": dep}) is True

    def test_task_not_ready_with_pending_deps(self):
        """Test is_ready with pending dependencies."""
        dep = Task(id="t-0001", subject="Dep", status="pending")
        task = Task(id="t-abcd", subject="Test", dependencies=["t-0001"])
        assert task.is_ready({"t-0001": dep}) is False

    def test_task_not_ready_if_not_pending(self):
        """Test is_ready returns False if task is not pending."""
        task = Task(id="t-abcd", subject="Test", status="in_progress")
        assert task.is_ready({}) is False


class TestGenerateTaskId:
    """Tests for task ID generation."""

    def test_generate_task_id_format(self):
        """Test that generated ID has correct format."""
        task_id = generate_task_id()
        assert task_id.startswith(TASK_ID_PREFIX)
        assert len(task_id) >= 5  # t- + at least 3 chars

    def test_generate_task_id_unique(self):
        """Test that generated IDs are unique."""
        ids = {generate_task_id() for _ in range(100)}
        assert len(ids) == 100

    def test_generate_task_id_avoids_existing(self):
        """Test that generation avoids existing IDs."""
        existing = {"t-aaaa", "t-bbbb"}
        task_id = generate_task_id(existing)
        assert task_id not in existing


class TestTaskStorage:
    """Tests for JSONL storage functions."""

    @pytest.fixture
    def temp_stan_dir(self):
        """Create a temporary .stan directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stan_dir = Path(tmpdir) / ".stan"
            stan_dir.mkdir()
            with patch("task_schema.get_tasks_file", return_value=stan_dir / "tasks.jsonl"):
                yield stan_dir

    def test_load_tasks_empty(self, temp_stan_dir):
        """Test loading from non-existent file."""
        tasks = load_tasks()
        assert tasks == {}

    def test_save_and_load_tasks(self, temp_stan_dir):
        """Test saving and loading tasks."""
        task = Task(id="t-abcd", subject="Test task")
        save_tasks({"t-abcd": task})

        loaded = load_tasks()
        assert "t-abcd" in loaded
        assert loaded["t-abcd"].subject == "Test task"

    def test_add_task(self, temp_stan_dir):
        """Test adding a task."""
        task = Task(id="t-abcd", subject="Test")
        result = add_task(task)
        assert result.id == "t-abcd"

        loaded = load_tasks()
        assert "t-abcd" in loaded

    def test_add_task_duplicate_fails(self, temp_stan_dir):
        """Test that adding duplicate ID fails."""
        task1 = Task(id="t-abcd", subject="Test 1")
        add_task(task1)

        task2 = Task(id="t-abcd", subject="Test 2")
        with pytest.raises(ValueError, match="already exists"):
            add_task(task2)

    def test_update_task(self, temp_stan_dir):
        """Test updating a task."""
        task = Task(id="t-abcd", subject="Test")
        add_task(task)

        updated = update_task("t-abcd", status="in_progress")
        assert updated.status == "in_progress"

        loaded = get_task("t-abcd")
        assert loaded.status == "in_progress"

    def test_update_task_not_found(self, temp_stan_dir):
        """Test updating non-existent task fails."""
        with pytest.raises(ValueError, match="not found"):
            update_task("t-nonexistent", status="done")

    def test_get_task(self, temp_stan_dir):
        """Test getting a single task."""
        task = Task(id="t-abcd", subject="Test")
        add_task(task)

        result = get_task("t-abcd")
        assert result.subject == "Test"

    def test_get_task_not_found(self, temp_stan_dir):
        """Test getting non-existent task returns None."""
        result = get_task("t-nonexistent")
        assert result is None

    def test_delete_task(self, temp_stan_dir):
        """Test deleting a task."""
        task = Task(id="t-abcd", subject="Test")
        add_task(task)

        result = delete_task("t-abcd")
        assert result is True
        assert get_task("t-abcd") is None

    def test_delete_task_not_found(self, temp_stan_dir):
        """Test deleting non-existent task returns False."""
        result = delete_task("t-nonexistent")
        assert result is False

    def test_create_task_auto_id(self, temp_stan_dir):
        """Test creating task with auto-generated ID."""
        task = create_task(subject="Auto ID test")
        assert task.id.startswith(TASK_ID_PREFIX)
        assert len(task.id) >= 5

    def test_get_ready_tasks(self, temp_stan_dir):
        """Test getting ready tasks."""
        # Add some tasks
        t1 = Task(id="t-0001", subject="Ready task", status="pending")
        t2 = Task(id="t-0002", subject="In progress", status="in_progress")
        t3 = Task(id="t-0003", subject="Blocked", status="pending", dependencies=["t-0001"])
        add_task(t1)
        add_task(t2)
        add_task(t3)

        ready = get_ready_tasks()
        ready_ids = [t.id for t in ready]
        assert "t-0001" in ready_ids
        assert "t-0002" not in ready_ids  # in_progress
        assert "t-0003" not in ready_ids  # blocked

    def test_get_ready_tasks_by_phase(self, temp_stan_dir):
        """Test getting ready tasks filtered by phase."""
        t1 = Task(id="t-0001", subject="Create task", phase="create")
        t2 = Task(id="t-0002", subject="Plan task", phase="plan")
        add_task(t1)
        add_task(t2)

        ready = get_ready_tasks(phase="create")
        assert len(ready) == 1
        assert ready[0].id == "t-0001"

    def test_get_blocked_tasks(self, temp_stan_dir):
        """Test getting blocked tasks with blockers."""
        t1 = Task(id="t-0001", subject="Blocker", status="pending")
        t2 = Task(id="t-0002", subject="Blocked", dependencies=["t-0001"])
        add_task(t1)
        add_task(t2)

        blocked = get_blocked_tasks()
        assert len(blocked) == 1
        task, blockers = blocked[0]
        assert task.id == "t-0002"
        assert "t-0001" in blockers

    def test_get_tasks_by_status(self, temp_stan_dir):
        """Test getting tasks by status."""
        t1 = Task(id="t-0001", subject="Pending", status="pending")
        t2 = Task(id="t-0002", subject="Done", status="done")
        add_task(t1)
        add_task(t2)

        pending = get_tasks_by_status("pending")
        assert len(pending) == 1
        assert pending[0].id == "t-0001"

    def test_get_tasks_by_phase(self, temp_stan_dir):
        """Test getting tasks by phase."""
        t1 = Task(id="t-0001", subject="Define", phase="define")
        t2 = Task(id="t-0002", subject="Create", phase="create")
        add_task(t1)
        add_task(t2)

        define_tasks = get_tasks_by_phase("define")
        assert len(define_tasks) == 1
        assert define_tasks[0].id == "t-0001"


class TestJsonlFormat:
    """Tests for JSONL file format."""

    @pytest.fixture
    def temp_stan_dir(self):
        """Create a temporary .stan directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stan_dir = Path(tmpdir) / ".stan"
            stan_dir.mkdir()
            with patch("task_schema.get_tasks_file", return_value=stan_dir / "tasks.jsonl"):
                yield stan_dir

    def test_jsonl_one_task_per_line(self, temp_stan_dir):
        """Test that each task is on a separate line."""
        t1 = Task(id="t-0001", subject="Task 1")
        t2 = Task(id="t-0002", subject="Task 2")
        save_tasks({"t-0001": t1, "t-0002": t2})

        tasks_file = temp_stan_dir / "tasks.jsonl"
        lines = tasks_file.read_text().strip().split("\n")
        assert len(lines) == 2

    def test_jsonl_valid_json_per_line(self, temp_stan_dir):
        """Test that each line is valid JSON."""
        t1 = Task(id="t-0001", subject="Task 1")
        t2 = Task(id="t-0002", subject="Task 2")
        save_tasks({"t-0001": t1, "t-0002": t2})

        tasks_file = temp_stan_dir / "tasks.jsonl"
        for line in tasks_file.read_text().strip().split("\n"):
            data = json.loads(line)
            assert "id" in data
            assert "subject" in data
