#!/usr/bin/env python3
"""Tests for /stan create Loop Logic (T-042).

TDD: Tests written before implementation.
"""

import pytest
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


class TestCreateCommandExists:
    """Tests for /stan create command structure."""

    def test_create_command_exists(self):
        """Create command file should exist."""
        cmd_file = PROJECT_ROOT / ".claude" / "commands" / "stan" / "create.md"
        assert cmd_file.exists(), f"Create command not found: {cmd_file}"

    def test_create_command_has_loop_section(self):
        """Create command should have execution loop section."""
        cmd_file = PROJECT_ROOT / ".claude" / "commands" / "stan" / "create.md"
        content = cmd_file.read_text()

        # Check for loop-related content
        assert "loop" in content.lower() or "execution" in content.lower(), \
            "Create command should have loop/execution section"

    def test_create_command_has_iteration_logic(self):
        """Create command should reference iteration counter."""
        cmd_file = PROJECT_ROOT / ".claude" / "commands" / "stan" / "create.md"
        content = cmd_file.read_text()

        # Check for iteration-related content
        assert "iteration" in content.lower() or "max_iterations" in content.lower(), \
            "Create command should reference iterations"

    def test_create_command_has_acceptance_criteria_check(self):
        """Create command should check acceptance criteria."""
        cmd_file = PROJECT_ROOT / ".claude" / "commands" / "stan" / "create.md"
        content = cmd_file.read_text()

        # Check for acceptance criteria references
        assert "acceptance" in content.lower() or "criteria" in content.lower(), \
            "Create command should reference acceptance criteria"


class TestLoopInstructions:
    """Tests for loop execution instructions."""

    def test_has_task_selection_logic(self):
        """Create command should have task selection logic (next ready task)."""
        cmd_file = PROJECT_ROOT / ".claude" / "commands" / "stan" / "create.md"
        content = cmd_file.read_text()

        # Should mention selecting/getting next task
        has_task_logic = (
            "next task" in content.lower() or
            "ready task" in content.lower() or
            "pending task" in content.lower() or
            "select task" in content.lower()
        )
        assert has_task_logic, "Create command should have task selection logic"

    def test_has_success_path(self):
        """Create command should describe success path."""
        cmd_file = PROJECT_ROOT / ".claude" / "commands" / "stan" / "create.md"
        content = cmd_file.read_text()

        # Should mention success/completion
        has_success = (
            "success" in content.lower() or
            "complete" in content.lower() or
            "done" in content.lower() or
            "finish" in content.lower()
        )
        assert has_success, "Create command should describe success path"

    def test_has_failure_path(self):
        """Create command should describe failure path."""
        cmd_file = PROJECT_ROOT / ".claude" / "commands" / "stan" / "create.md"
        content = cmd_file.read_text()

        # Should mention failure/error handling
        has_failure = (
            "fail" in content.lower() or
            "error" in content.lower() or
            "stop" in content.lower() or
            "max" in content.lower()
        )
        assert has_failure, "Create command should describe failure path"

    def test_has_perspective_shift_mention(self):
        """Create command should mention perspective shift at max iterations."""
        cmd_file = PROJECT_ROOT / ".claude" / "commands" / "stan" / "create.md"
        content = cmd_file.read_text()

        # Should mention perspective shift or similar
        has_perspective = (
            "perspective" in content.lower() or
            "approach" in content.lower() or
            "stuck" in content.lower() or
            "think" in content.lower()
        )
        assert has_perspective, "Create command should mention perspective shift"

    def test_has_completion_signal(self):
        """Create command should have completion signal."""
        cmd_file = PROJECT_ROOT / ".claude" / "commands" / "stan" / "create.md"
        content = cmd_file.read_text()

        # Should mention completion signal
        assert "COMPLETE" in content or "completion" in content.lower(), \
            "Create command should have completion signal"


class TestIterationCounterIntegration:
    """Tests for iteration counter from session state."""

    def test_session_state_has_iteration_functions(self):
        """Session state should have iteration counter functions."""
        import sys
        sys.path.insert(0, str(PROJECT_ROOT / ".claude" / "hooks" / "stan" / "lib"))

        import importlib
        import session_state
        importlib.reload(session_state)

        # Check functions exist
        assert hasattr(session_state, 'get_iteration_count'), \
            "session_state should have get_iteration_count"
        assert hasattr(session_state, 'increment_iteration'), \
            "session_state should have increment_iteration"
        assert hasattr(session_state, 'reset_iteration_count'), \
            "session_state should have reset_iteration_count"

    def test_iteration_counter_increments(self, tmp_path):
        """Iteration counter should increment correctly."""
        import sys
        sys.path.insert(0, str(PROJECT_ROOT / ".claude" / "hooks" / "stan" / "lib"))

        import importlib
        import session_state
        importlib.reload(session_state)

        from unittest.mock import patch

        stan_dir = tmp_path / ".stan"
        stan_dir.mkdir()

        with patch('os.getcwd', return_value=str(tmp_path)):
            with patch.object(session_state, 'get_session_file',
                            return_value=stan_dir / "session.json"):
                # Reset and verify
                session_state.reset_iteration_count()
                assert session_state.get_iteration_count() == 0

                # Increment
                session_state.increment_iteration()
                assert session_state.get_iteration_count() == 1

                session_state.increment_iteration()
                assert session_state.get_iteration_count() == 2


class TestMaxIterationsCheck:
    """Tests for max iterations enforcement."""

    def test_get_max_iterations_exists(self):
        """stan_gate should have get_max_iterations function."""
        import sys
        sys.path.insert(0, str(PROJECT_ROOT / ".claude" / "hooks" / "stan" / "pre-tool-use"))

        import importlib
        import stan_gate
        importlib.reload(stan_gate)

        assert hasattr(stan_gate, 'get_max_iterations'), \
            "stan_gate should have get_max_iterations function"

    def test_default_max_iterations_is_10(self):
        """Default max iterations should be 10 (like Ralph)."""
        import sys
        sys.path.insert(0, str(PROJECT_ROOT / ".claude" / "hooks" / "stan" / "pre-tool-use"))

        import importlib
        import stan_gate
        importlib.reload(stan_gate)

        assert stan_gate.DEFAULT_MAX_ITERATIONS == 10, \
            "Default max iterations should be 10"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
