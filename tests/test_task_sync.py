#!/usr/bin/env python3
"""Tests for STAN Task Sync (T-050, T-051)."""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import pytest

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude/hooks/stan/lib"))

from task_schema import Task, save_tasks
from task_sync import (
    TaskSyncState,
    STAN_TO_CLAUDE_STATUS,
    CLAUDE_TO_STAN_STATUS,
    prepare_claude_task_params,
    sync_to_claude_tasks,
    register_claude_task,
    sync_from_claude_task,
    sync_task_completion,
    get_sync_instructions,
    get_pending_tasks_for_sync,
    clear_sync_state,
    get_sync_state,
    save_sync_state,
)


class TestTaskSyncState:
    """Tests for TaskSyncState class."""

    def test_create_empty_state(self):
        """Test creating empty sync state."""
        state = TaskSyncState()
        assert state.stan_to_claude == {}
        assert state.claude_to_stan == {}
        assert state.synced_at is None

    def test_add_mapping(self):
        """Test adding task mapping."""
        state = TaskSyncState()
        state.add_mapping("t-abcd", "1")

        assert state.get_claude_id("t-abcd") == "1"
        assert state.get_stan_id("1") == "t-abcd"

    def test_get_nonexistent_mapping(self):
        """Test getting nonexistent mapping returns None."""
        state = TaskSyncState()

        assert state.get_claude_id("t-none") is None
        assert state.get_stan_id("999") is None

    def test_mark_synced(self):
        """Test marking sync time."""
        state = TaskSyncState()
        state.mark_synced()

        assert state.synced_at is not None

    def test_to_dict(self):
        """Test converting to dict."""
        state = TaskSyncState()
        state.add_mapping("t-abcd", "1")
        state.mark_synced()

        d = state.to_dict()

        assert d["stan_to_claude"] == {"t-abcd": "1"}
        assert d["claude_to_stan"] == {"1": "t-abcd"}
        assert "synced_at" in d

    def test_from_dict(self):
        """Test creating from dict."""
        data = {
            "stan_to_claude": {"t-abcd": "1"},
            "claude_to_stan": {"1": "t-abcd"},
            "synced_at": "2026-01-24T10:00:00",
        }

        state = TaskSyncState.from_dict(data)

        assert state.get_claude_id("t-abcd") == "1"
        assert state.synced_at == "2026-01-24T10:00:00"


class TestStatusMapping:
    """Tests for status mappings."""

    def test_stan_to_claude_pending(self):
        """Test pending maps correctly."""
        assert STAN_TO_CLAUDE_STATUS["pending"] == "pending"

    def test_stan_to_claude_in_progress(self):
        """Test in_progress maps correctly."""
        assert STAN_TO_CLAUDE_STATUS["in_progress"] == "in_progress"

    def test_stan_to_claude_done(self):
        """Test done maps to completed."""
        assert STAN_TO_CLAUDE_STATUS["done"] == "completed"

    def test_stan_to_claude_blocked(self):
        """Test blocked maps to pending."""
        assert STAN_TO_CLAUDE_STATUS["blocked"] == "pending"

    def test_claude_to_stan_completed(self):
        """Test completed maps to done."""
        assert CLAUDE_TO_STAN_STATUS["completed"] == "done"


class TestPrepareClaudeTaskParams:
    """Tests for preparing Claude Task parameters."""

    def test_basic_params(self):
        """Test basic task parameter preparation."""
        task = Task(id="t-abcd", subject="Test task")
        params = prepare_claude_task_params(task, {})

        assert "[t-abcd]" in params["subject"]
        assert "Test task" in params["subject"]
        assert "activeForm" in params

    def test_params_with_description(self):
        """Test params include description."""
        task = Task(id="t-abcd", subject="Test", description="Detailed desc")
        params = prepare_claude_task_params(task, {})

        assert "Detailed desc" in params["description"]

    def test_params_with_acceptance_criteria(self):
        """Test params include acceptance criteria."""
        task = Task(
            id="t-abcd",
            subject="Test",
            acceptance_criteria=["AC1", "AC2"],
        )
        params = prepare_claude_task_params(task, {})

        assert "Acceptance Criteria:" in params["description"]
        assert "- AC1" in params["description"]
        assert "- AC2" in params["description"]


class TestSyncToClaudeTasks:
    """Tests for syncing STAN tasks to Claude Tasks."""

    def test_sync_pending_tasks(self):
        """Test syncing pending tasks."""
        t1 = Task(id="t-0001", subject="Pending", status="pending")
        t2 = Task(id="t-0002", subject="Done", status="done")
        tasks = {"t-0001": t1, "t-0002": t2}

        # Clear any existing state
        with patch("task_sync.get_sync_state", return_value=TaskSyncState()):
            result = sync_to_claude_tasks(tasks)

        # Only pending task should be synced
        assert len(result) == 1
        assert result[0]["stan_id"] == "t-0001"

    def test_sync_in_progress_tasks(self):
        """Test syncing in_progress tasks."""
        task = Task(id="t-abcd", subject="Working", status="in_progress")
        tasks = {"t-abcd": task}

        with patch("task_sync.get_sync_state", return_value=TaskSyncState()):
            result = sync_to_claude_tasks(tasks)

        assert len(result) == 1
        assert result[0]["stan_id"] == "t-abcd"

    def test_skip_already_synced(self):
        """Test skipping already synced tasks."""
        task = Task(id="t-abcd", subject="Test", status="pending")
        tasks = {"t-abcd": task}

        # Create state with existing mapping
        state = TaskSyncState()
        state.add_mapping("t-abcd", "1")

        with patch("task_sync.get_sync_state", return_value=state):
            result = sync_to_claude_tasks(tasks)

        assert len(result) == 0

    def test_skip_done_tasks(self):
        """Test skipping done tasks."""
        task = Task(id="t-abcd", subject="Done", status="done")
        tasks = {"t-abcd": task}

        with patch("task_sync.get_sync_state", return_value=TaskSyncState()):
            result = sync_to_claude_tasks(tasks)

        assert len(result) == 0


class TestRegisterClaudeTask:
    """Tests for registering Claude Task mappings."""

    def test_register_mapping(self):
        """Test registering a new mapping."""
        with patch("task_sync.get_sync_state", return_value=TaskSyncState()) as mock_get:
            with patch("task_sync.save_sync_state") as mock_save:
                register_claude_task("t-abcd", "1")

                # Verify save was called
                mock_save.assert_called_once()
                saved_state = mock_save.call_args[0][0]
                assert saved_state.get_claude_id("t-abcd") == "1"


class TestSyncFromClaudeTask:
    """Tests for syncing from Claude Task changes."""

    @pytest.fixture
    def temp_stan_dir(self):
        """Create a temporary .stan directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stan_dir = Path(tmpdir) / ".stan"
            stan_dir.mkdir()
            tasks_file = stan_dir / "tasks.jsonl"

            with patch("task_schema.get_tasks_file", return_value=tasks_file):
                with patch("task_generator.regenerate_tasks_md"):
                    yield stan_dir

    def test_sync_completion(self, temp_stan_dir):
        """Test syncing task completion."""
        # Create a task
        task = Task(id="t-abcd", subject="Test", status="in_progress")
        save_tasks({"t-abcd": task})

        # Create sync state with mapping
        state = TaskSyncState()
        state.add_mapping("t-abcd", "1")

        with patch("task_sync.get_sync_state", return_value=state):
            result = sync_from_claude_task("1", "completed")

        assert result is not None
        assert result.status == "done"

    def test_sync_unknown_mapping(self, temp_stan_dir):
        """Test syncing with unknown Claude Task ID."""
        with patch("task_sync.get_sync_state", return_value=TaskSyncState()):
            result = sync_from_claude_task("999", "completed")

        assert result is None


class TestSyncTaskCompletion:
    """Tests for direct task completion."""

    @pytest.fixture
    def temp_stan_dir(self):
        """Create a temporary .stan directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stan_dir = Path(tmpdir) / ".stan"
            stan_dir.mkdir()
            tasks_file = stan_dir / "tasks.jsonl"

            with patch("task_schema.get_tasks_file", return_value=tasks_file):
                with patch("task_generator.regenerate_tasks_md"):
                    yield stan_dir

    def test_complete_task(self, temp_stan_dir):
        """Test completing a task directly."""
        task = Task(id="t-abcd", subject="Test", status="pending")
        save_tasks({"t-abcd": task})

        result = sync_task_completion("t-abcd")

        assert result is not None
        assert result.status == "done"

    def test_complete_nonexistent_task(self, temp_stan_dir):
        """Test completing nonexistent task returns None."""
        result = sync_task_completion("t-nonexistent")
        assert result is None


class TestGetPendingTasksForSync:
    """Tests for getting pending tasks."""

    def test_get_pending_unsynced(self):
        """Test getting pending unsynced tasks."""
        t1 = Task(id="t-0001", subject="Pending", status="pending")
        t2 = Task(id="t-0002", subject="Synced", status="pending")
        tasks = {"t-0001": t1, "t-0002": t2}

        # t-0002 is already synced
        state = TaskSyncState()
        state.add_mapping("t-0002", "2")

        with patch("task_sync.load_tasks", return_value=tasks):
            with patch("task_sync.get_sync_state", return_value=state):
                result = get_pending_tasks_for_sync()

        assert len(result) == 1
        assert result[0].id == "t-0001"


class TestGetSyncInstructions:
    """Tests for sync instructions."""

    def test_instructions_format(self):
        """Test sync instructions format."""
        task = Task(id="t-abcd", subject="Test task", status="pending")

        with patch("task_sync.load_tasks", return_value={"t-abcd": task}):
            with patch("task_sync.get_sync_state", return_value=TaskSyncState()):
                instructions = get_sync_instructions()

        assert "[STAN]" in instructions
        assert "t-abcd" in instructions

    def test_no_tasks_message(self):
        """Test message when no tasks to sync."""
        with patch("task_sync.load_tasks", return_value={}):
            with patch("task_sync.get_sync_state", return_value=TaskSyncState()):
                instructions = get_sync_instructions()

        assert "No tasks to sync" in instructions
