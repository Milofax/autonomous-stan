#!/usr/bin/env python3
"""Tests for Task Priority Default Rule (T-045).

TDD: Tests written before implementation.
"""

import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


class TestTaskPriorityRuleFile:
    """Tests for .claude/rules/stan/task-priority.md"""

    def test_rule_file_exists(self):
        """Rule file must exist."""
        rule_file = PROJECT_ROOT / ".claude" / "rules" / "stan" / "task-priority.md"
        assert rule_file.exists(), f"Rule file not found: {rule_file}"

    def test_rule_file_has_pith_header(self):
        """Rule file should have PITH header."""
        rule_file = PROJECT_ROOT / ".claude" / "rules" / "stan" / "task-priority.md"
        content = rule_file.read_text()
        assert "#PITH:1.2" in content, "Missing PITH header"

    def test_rule_defines_pending_as_required(self):
        """Rule must define pending (·) as REQUIRED."""
        rule_file = PROJECT_ROOT / ".claude" / "rules" / "stan" / "task-priority.md"
        content = rule_file.read_text().lower()
        # Must mention pending and required together
        assert "pending" in content and "required" in content, \
            "Rule must define pending as required"

    def test_rule_defines_parked_as_optional(self):
        """Rule must define parked (~) as optional."""
        rule_file = PROJECT_ROOT / ".claude" / "rules" / "stan" / "task-priority.md"
        content = rule_file.read_text().lower()
        assert "parked" in content and "optional" in content, \
            "Rule must define parked as optional"

    def test_rule_warns_against_optional_labeling(self):
        """Rule must warn against labeling required tasks as optional."""
        rule_file = PROJECT_ROOT / ".claude" / "rules" / "stan" / "task-priority.md"
        content = rule_file.read_text().lower()
        # Should mention not calling things optional/enhancement
        assert "optional" in content or "enhancement" in content, \
            "Rule must warn against optional labeling"

    def test_rule_has_status_definitions(self):
        """Rule must define all status symbols."""
        rule_file = PROJECT_ROOT / ".claude" / "rules" / "stan" / "task-priority.md"
        content = rule_file.read_text()
        # Check for status symbols
        assert "·" in content or "pending" in content.lower(), "Missing pending status"
        assert "►" in content or "in_progress" in content.lower() or "in-progress" in content.lower(), "Missing in-progress status"
        assert "✓" in content or "done" in content.lower() or "completed" in content.lower(), "Missing done status"
        assert "~" in content or "parked" in content.lower(), "Missing parked status"


class TestCreateCommandHasRule:
    """Tests for /stan create command including the rule."""

    def test_create_command_exists(self):
        """Create command must exist."""
        cmd_file = PROJECT_ROOT / "commands" / "stan" / "create.md"
        assert cmd_file.exists(), f"Create command not found: {cmd_file}"

    def test_create_command_mentions_required_tasks(self):
        """Create command must mention that pending tasks are required."""
        cmd_file = PROJECT_ROOT / "commands" / "stan" / "create.md"
        content = cmd_file.read_text().lower()
        # Should mention required/must/mandatory for pending tasks
        assert "required" in content or "must" in content or "mandatory" in content, \
            "Create command must mention required tasks"

    def test_create_command_warns_against_optional(self):
        """Create command should warn against calling things optional."""
        cmd_file = PROJECT_ROOT / "commands" / "stan" / "create.md"
        content = cmd_file.read_text().lower()
        # Should have some warning about not calling things optional
        assert "never" in content or "not" in content, \
            "Create command should have warnings"


class TestTasksFileHasLegend:
    """Tests for status legend in docs/tasks.md."""

    def test_tasks_file_exists(self):
        """Tasks file must exist."""
        tasks_file = PROJECT_ROOT / "docs" / "tasks.md"
        assert tasks_file.exists(), f"Tasks file not found: {tasks_file}"

    def test_tasks_file_has_status_legend(self):
        """Tasks file should have a status legend section."""
        tasks_file = PROJECT_ROOT / "docs" / "tasks.md"
        content = tasks_file.read_text().lower()
        # Should have legend or status explanation
        assert "legend" in content or "status" in content, \
            "Tasks file should have status legend"

    def test_tasks_file_explains_pending_is_required(self):
        """Tasks file legend should explain pending = required."""
        tasks_file = PROJECT_ROOT / "docs" / "tasks.md"
        content = tasks_file.read_text().lower()
        # Should explain that pending means required
        assert ("pending" in content and "required" in content) or \
               ("·" in content and "required" in content), \
            "Tasks file should explain pending = required"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
