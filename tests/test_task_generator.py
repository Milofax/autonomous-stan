#!/usr/bin/env python3
"""Tests for STAN Task Generator (T-049)."""

import sys
from pathlib import Path
from unittest.mock import patch
import tempfile
import pytest

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude/hooks/stan/lib"))

from task_schema import Task, save_tasks
from task_generator import (
    get_status_symbol,
    format_task,
    format_phase_section,
    generate_summary_table,
    generate_tasks_md,
    write_tasks_md,
    get_ready_tasks_summary,
    STATUS_SYMBOLS,
    PHASE_NAMES,
)


class TestStatusSymbols:
    """Tests for status symbol mapping."""

    def test_pending_symbol(self):
        """Test pending status symbol."""
        assert get_status_symbol("pending") == "·"

    def test_in_progress_symbol(self):
        """Test in_progress status symbol."""
        assert get_status_symbol("in_progress") == "►"

    def test_done_symbol(self):
        """Test done status symbol."""
        assert get_status_symbol("done") == "✓"

    def test_blocked_symbol(self):
        """Test blocked status symbol."""
        assert get_status_symbol("blocked") == "⏸"

    def test_unknown_symbol(self):
        """Test unknown status returns ?."""
        assert get_status_symbol("unknown") == "?"


class TestFormatTask:
    """Tests for single task formatting."""

    def test_format_basic_task(self):
        """Test formatting a basic task."""
        task = Task(id="t-abcd", subject="Test task", status="pending")
        output = format_task(task, {})

        assert "### · t-abcd: Test task" in output
        assert "**Status:** pending" in output

    def test_format_task_with_description(self):
        """Test formatting task with description."""
        task = Task(
            id="t-abcd",
            subject="Test task",
            description="A detailed description",
        )
        output = format_task(task, {})

        assert "**Description:** A detailed description" in output

    def test_format_task_with_owner(self):
        """Test formatting task with owner."""
        task = Task(id="t-abcd", subject="Test", owner="agent-1")
        output = format_task(task, {})

        assert "**Owner:** agent-1" in output

    def test_format_task_with_dependencies(self):
        """Test formatting task with dependencies."""
        task = Task(id="t-abcd", subject="Test", dependencies=["t-0001", "t-0002"])
        output = format_task(task, {})

        assert "**Depends on:** t-0001, t-0002" in output

    def test_format_task_with_acceptance_criteria_pending(self):
        """Test formatting pending task with acceptance criteria."""
        task = Task(
            id="t-abcd",
            subject="Test",
            acceptance_criteria=["AC1", "AC2"],
            status="pending",
        )
        output = format_task(task, {})

        assert "- [ ] AC1" in output
        assert "- [ ] AC2" in output

    def test_format_task_with_acceptance_criteria_done(self):
        """Test formatting done task with acceptance criteria (checked)."""
        task = Task(
            id="t-abcd",
            subject="Test",
            acceptance_criteria=["AC1", "AC2"],
            status="done",
        )
        output = format_task(task, {})

        assert "- [x] AC1" in output
        assert "- [x] AC2" in output

    def test_format_task_ends_with_separator(self):
        """Test that formatted task ends with separator."""
        task = Task(id="t-abcd", subject="Test")
        output = format_task(task, {})

        assert output.strip().endswith("---")


class TestFormatPhaseSection:
    """Tests for phase section formatting."""

    def test_format_empty_phase(self):
        """Test formatting empty phase returns empty string."""
        output = format_phase_section("create", [], {})
        assert output == ""

    def test_format_phase_header(self):
        """Test phase header format."""
        task = Task(id="t-abcd", subject="Test", phase="create")
        output = format_phase_section("create", [task], {"t-abcd": task})

        assert "## Phase: CREATE" in output

    def test_format_phase_counts(self):
        """Test phase header shows task counts."""
        t1 = Task(id="t-0001", subject="Done task", status="done", phase="create")
        t2 = Task(id="t-0002", subject="Pending task", status="pending", phase="create")
        tasks = [t1, t2]
        all_tasks = {t.id: t for t in tasks}

        output = format_phase_section("create", tasks, all_tasks)

        assert "(1/2)" in output  # 1 done out of 2 total


class TestGenerateSummaryTable:
    """Tests for summary table generation."""

    def test_summary_table_header(self):
        """Test summary table has header row."""
        task = Task(id="t-abcd", subject="Test", phase="create")
        output = generate_summary_table({"t-abcd": task})

        assert "| Phase |" in output
        assert "| Pending |" in output

    def test_summary_table_counts(self):
        """Test summary table shows correct counts."""
        t1 = Task(id="t-0001", subject="Pending", status="pending", phase="create")
        t2 = Task(id="t-0002", subject="Done", status="done", phase="create")
        tasks = {"t-0001": t1, "t-0002": t2}

        output = generate_summary_table(tasks)

        # CREATE phase should have 1 pending, 0 in_progress, 1 done, 0 blocked, 2 total
        assert "| CREATE | 1 | 0 | 1 | 0 | 2 |" in output


class TestGenerateTasksMd:
    """Tests for full markdown generation."""

    def test_generate_header(self):
        """Test generated markdown has header."""
        output = generate_tasks_md({})

        assert "# STAN Tasks" in output
        assert "AUTO-GENERATED" in output
        assert "DO NOT EDIT" in output

    def test_generate_status_legend(self):
        """Test generated markdown has status legend."""
        output = generate_tasks_md({})

        assert "## Status Legend" in output
        assert "| `·` | pending |" in output

    def test_generate_no_tasks_message(self):
        """Test message when no tasks exist."""
        output = generate_tasks_md({})

        assert "No tasks found" in output
        assert "/stan plan" in output

    def test_generate_with_tasks(self):
        """Test generating markdown with tasks."""
        t1 = Task(id="t-0001", subject="Task 1", phase="define")
        t2 = Task(id="t-0002", subject="Task 2", phase="create")
        tasks = {"t-0001": t1, "t-0002": t2}

        output = generate_tasks_md(tasks)

        assert "t-0001" in output
        assert "Task 1" in output
        assert "t-0002" in output
        assert "Task 2" in output

    def test_generate_groups_by_phase(self):
        """Test tasks are grouped by phase."""
        t1 = Task(id="t-0001", subject="Define task", phase="define")
        t2 = Task(id="t-0002", subject="Create task", phase="create")
        tasks = {"t-0001": t1, "t-0002": t2}

        output = generate_tasks_md(tasks)

        # DEFINE should come before CREATE
        define_pos = output.find("Phase: DEFINE")
        create_pos = output.find("Phase: CREATE")
        assert define_pos < create_pos


class TestWriteTasksMd:
    """Tests for writing tasks.md file."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create .stan directory
            stan_dir = Path(tmpdir) / ".stan"
            stan_dir.mkdir()

            # Create docs directory
            docs_dir = Path(tmpdir) / "docs"
            docs_dir.mkdir()

            # Patch the file paths
            with patch("task_generator.get_docs_tasks_file", return_value=docs_dir / "tasks.md"):
                with patch("task_schema.get_tasks_file", return_value=stan_dir / "tasks.jsonl"):
                    yield tmpdir

    def test_write_creates_file(self, temp_project):
        """Test that write_tasks_md creates the file."""
        tasks = {"t-abcd": Task(id="t-abcd", subject="Test")}
        result = write_tasks_md(tasks)

        assert result.exists()
        assert result.name == "tasks.md"

    def test_write_content(self, temp_project):
        """Test that written content is correct."""
        tasks = {"t-abcd": Task(id="t-abcd", subject="Test task")}
        result = write_tasks_md(tasks)

        content = result.read_text()
        assert "Test task" in content
        assert "AUTO-GENERATED" in content


class TestGetReadyTasksSummary:
    """Tests for ready tasks summary."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            stan_dir = Path(tmpdir) / ".stan"
            stan_dir.mkdir()

            with patch("task_schema.get_tasks_file", return_value=stan_dir / "tasks.jsonl"):
                with patch("task_generator.load_tasks") as mock_load:
                    yield mock_load

    def test_no_ready_tasks(self, temp_project):
        """Test message when no ready tasks."""
        temp_project.return_value = {}

        output = get_ready_tasks_summary()

        assert "No ready tasks" in output

    def test_ready_tasks_count(self, temp_project):
        """Test ready tasks count in output."""
        t1 = Task(id="t-0001", subject="Task 1", status="pending")
        t2 = Task(id="t-0002", subject="Task 2", status="pending")
        temp_project.return_value = {"t-0001": t1, "t-0002": t2}

        output = get_ready_tasks_summary()

        assert "2 tasks" in output

    def test_ready_tasks_format(self, temp_project):
        """Test ready tasks are formatted correctly."""
        task = Task(id="t-abcd", subject="Test task", phase="create")
        temp_project.return_value = {"t-abcd": task}

        output = get_ready_tasks_summary()

        assert "t-abcd" in output
        assert "Test task" in output
        assert "[create]" in output

    def test_ready_tasks_instructions(self, temp_project):
        """Test ready tasks shows instructions."""
        task = Task(id="t-abcd", subject="Test", status="pending")
        temp_project.return_value = {"t-abcd": task}

        output = get_ready_tasks_summary()

        assert "/stan create" in output
