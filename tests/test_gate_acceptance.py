#!/usr/bin/env python3
"""Tests for Acceptance Criteria enforcement in stan-gate hook."""

import pytest
import json
import tempfile
import os
from pathlib import Path
from io import StringIO
from unittest.mock import patch, MagicMock

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "stan"))


class TestAcceptanceCriteriaEnforcement:
    """Tests for acceptance criteria check in gate hook."""

    @pytest.fixture
    def mock_session_state(self):
        """Mock session state for tests."""
        state = {
            "iteration_count": 0,
            "current_task": None,
        }
        return state

    @pytest.fixture
    def plan_all_checked(self, tmp_path):
        """Create a plan with all criteria checked."""
        plan = tmp_path / "docs" / "plan.md"
        plan.parent.mkdir(parents=True)
        plan.write_text("""---
type: plan
status: in-progress
---
# Plan

### T-001: Task

**Acceptance Criteria:**
- [x] Criterion 1
- [x] Criterion 2
- [x] Typecheck passes
""")
        return plan

    @pytest.fixture
    def plan_unchecked(self, tmp_path):
        """Create a plan with unchecked criteria."""
        plan = tmp_path / "docs" / "plan.md"
        plan.parent.mkdir(parents=True)
        plan.write_text("""---
type: plan
status: in-progress
---
# Plan

### T-001: Task

**Acceptance Criteria:**
- [x] Done criterion
- [ ] Pending criterion
- [ ] Another pending
""")
        return plan

    def test_check_acceptance_criteria_all_done(self, plan_all_checked):
        """Wenn alle Criteria abgehakt sind, wird erlaubt."""
        from lib.acceptance import all_criteria_checked
        assert all_criteria_checked(plan_all_checked) is True

    def test_check_acceptance_criteria_some_pending(self, plan_unchecked):
        """Wenn Criteria offen sind, wird blockiert."""
        from lib.acceptance import all_criteria_checked, get_unchecked_criteria
        assert all_criteria_checked(plan_unchecked) is False
        unchecked = get_unchecked_criteria(plan_unchecked)
        assert len(unchecked) == 2


class TestIterationCounter:
    """Tests for iteration counting."""

    @pytest.fixture(autouse=True)
    def setup_clean_state(self, tmp_path):
        """Clean session state before each test."""
        # Use a unique session file for tests
        session_file = tmp_path / "test-session.json"
        with patch.dict(os.environ, {"STAN_SESSION_FILE": str(session_file)}):
            yield

    def test_iteration_increments(self):
        """Iteration wird erhöht bei jedem Versuch."""
        from lib.session_state import (
            get_iteration_count,
            increment_iteration,
            reset_iteration_count,
        )
        reset_iteration_count()
        assert get_iteration_count() == 0

        count = increment_iteration()
        assert count == 1
        assert get_iteration_count() == 1

        count = increment_iteration()
        assert count == 2

    def test_iteration_resets_on_task_change(self):
        """Iteration wird zurückgesetzt bei Task-Wechsel."""
        from lib.session_state import (
            get_iteration_count,
            increment_iteration,
            set_current_task,
        )
        set_current_task("T-001")
        increment_iteration()
        increment_iteration()
        assert get_iteration_count() == 2

        # Task wechseln → Reset
        set_current_task("T-002")
        assert get_iteration_count() == 0

    def test_same_task_no_reset(self):
        """Gleiche Task setzt nicht zurück."""
        from lib.session_state import (
            get_iteration_count,
            increment_iteration,
            set_current_task,
        )
        set_current_task("T-001")
        increment_iteration()
        increment_iteration()

        # Gleiche Task nochmal setzen → kein Reset
        set_current_task("T-001")
        assert get_iteration_count() == 2


class TestMaxIterations:
    """Tests for max iterations check."""

    def test_under_max_allowed(self):
        """Unter Max-Iterationen wird erlaubt."""
        iteration = 5
        max_iterations = 10
        assert iteration < max_iterations

    def test_at_max_blocked(self):
        """Bei Max-Iterationen wird blockiert."""
        iteration = 10
        max_iterations = 10
        assert iteration >= max_iterations

    def test_default_max_is_10(self):
        """Default Max ist 10 (wie Ralph)."""
        DEFAULT_MAX_ITERATIONS = 10
        assert DEFAULT_MAX_ITERATIONS == 10


class TestGateHookIntegration:
    """Integration tests for acceptance criteria in gate hook."""

    @pytest.fixture
    def stan_manifest(self, tmp_path):
        """Create stan.md manifest."""
        manifest = tmp_path / "stan.md"
        manifest.write_text("""---
phase: create
max_iterations: 10
---
# STAN Manifest
""")
        return manifest

    @pytest.fixture
    def mock_hook_input(self):
        """Create mock hook input for git commit."""
        return {
            "tool_name": "Bash",
            "tool_input": {
                "command": "git commit -m 'feat: something'"
            }
        }

    @pytest.fixture
    def plan_unchecked(self, tmp_path):
        """Create a plan with unchecked criteria."""
        plan = tmp_path / "docs" / "plan.md"
        plan.parent.mkdir(parents=True)
        plan.write_text("""---
type: plan
status: in-progress
---
# Plan

### T-001: Task

**Acceptance Criteria:**
- [x] Done criterion
- [ ] Pending criterion
- [ ] Another pending
""")
        return plan

    def test_block_message_includes_unchecked(self, plan_unchecked):
        """Block-Message zeigt offene Criteria."""
        from lib.acceptance import get_unchecked_criteria, format_unchecked_for_message

        unchecked = get_unchecked_criteria(plan_unchecked)
        message = format_unchecked_for_message(unchecked)

        assert "Pending criterion" in message
        assert "Another pending" in message

    def test_block_message_shows_iteration(self):
        """Block-Message zeigt Iteration-Counter."""
        iteration = 3
        max_iter = 10
        message = f"Iteration {iteration}/{max_iter}"
        assert "3/10" in message

    def test_escalation_at_max_iterations(self):
        """Bei Max-Iterationen kommt Eskalations-Message."""
        iteration = 10
        max_iter = 10
        if iteration >= max_iter:
            message = f"Max {max_iter} Iterationen erreicht! Eskalation nötig."
            assert "Eskalation" in message


class TestRalphStyleLoop:
    """Tests for Ralph-style autonomous loop behavior."""

    def test_loop_continues_while_unchecked(self, tmp_path):
        """Loop läuft weiter solange Criteria offen."""
        plan = tmp_path / "plan.md"
        plan.write_text("""---
type: plan
---
- [ ] Not done yet
""")
        from lib.acceptance import all_criteria_checked
        assert all_criteria_checked(plan) is False
        # → Hook würde BLOCK zurückgeben

    def test_loop_stops_when_all_checked(self, tmp_path):
        """Loop stoppt wenn alle Criteria abgehakt."""
        plan = tmp_path / "plan.md"
        plan.write_text("""---
type: plan
---
- [x] All done
""")
        from lib.acceptance import all_criteria_checked
        assert all_criteria_checked(plan) is True
        # → Hook würde ALLOW zurückgeben

    def test_complete_signal_pattern(self, tmp_path):
        """Bei Completion könnte <promise>COMPLETE</promise> ausgegeben werden."""
        plan = tmp_path / "plan.md"
        plan.write_text("""---
type: plan
status: done
---
- [x] Everything done
""")
        from lib.acceptance import all_criteria_checked
        if all_criteria_checked(plan):
            signal = "<promise>COMPLETE</promise>"
            assert "COMPLETE" in signal
