#!/usr/bin/env python3
"""Tests for Feature Completion (T-035).

TDD: Tests written before implementation.
"""

import pytest
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


class TestCompleteCommandExists:
    """Tests for /stan complete command."""

    def test_complete_command_exists(self):
        """Complete command file should exist."""
        cmd_file = PROJECT_ROOT / "commands" / "stan" / "complete.md"
        assert cmd_file.exists(), f"Complete command not found: {cmd_file}"

    def test_complete_command_has_trigger_words(self):
        """Complete command should mention trigger words."""
        cmd_file = PROJECT_ROOT / "commands" / "stan" / "complete.md"
        content = cmd_file.read_text()

        # Should mention trigger words
        has_triggers = (
            "fertig" in content.lower() or
            "finish" in content.lower() or
            "complete" in content.lower()
        )
        assert has_triggers, "Complete command should mention trigger words"

    def test_complete_command_mentions_confirmation(self):
        """Complete command should mention confirmation before completing."""
        cmd_file = PROJECT_ROOT / "commands" / "stan" / "complete.md"
        content = cmd_file.read_text()

        # Should ask for confirmation
        has_confirmation = (
            "confirm" in content.lower() or
            "ask" in content.lower() or
            "sure" in content.lower()
        )
        assert has_confirmation, "Complete command should ask for confirmation"


class TestCompletedDirectory:
    """Tests for .stan/completed/ directory handling."""

    def test_complete_command_mentions_completed_directory(self):
        """Complete command should mention .stan/completed/."""
        cmd_file = PROJECT_ROOT / "commands" / "stan" / "complete.md"
        content = cmd_file.read_text()

        assert ".stan/completed" in content or "completed/" in content, \
            "Complete command should mention completed directory"

    def test_complete_command_describes_package_move(self):
        """Complete command should describe moving all 3 documents."""
        cmd_file = PROJECT_ROOT / "commands" / "stan" / "complete.md"
        content = cmd_file.read_text()

        # Should mention prd, plan, and tasks
        assert "prd" in content.lower(), "Should mention PRD"
        assert "plan" in content.lower(), "Should mention Plan"
        assert "tasks" in content.lower(), "Should mention Tasks"


class TestFeatureNaming:
    """Tests for feature naming in completed files."""

    def test_complete_command_uses_feature_name(self):
        """Complete command should use feature name, not date."""
        cmd_file = PROJECT_ROOT / "commands" / "stan" / "complete.md"
        content = cmd_file.read_text()

        # Should mention feature name in filename
        has_feature_name = (
            "feature" in content.lower() or
            "prd-" in content or
            "-feature" in content.lower()
        )
        assert has_feature_name, "Complete command should use feature name in filename"

    def test_complete_command_adds_frontmatter_date(self):
        """Complete command should add completed_at to frontmatter."""
        cmd_file = PROJECT_ROOT / "commands" / "stan" / "complete.md"
        content = cmd_file.read_text()

        # Should mention frontmatter update
        assert "frontmatter" in content.lower() or "status" in content.lower(), \
            "Complete command should update frontmatter"


class TestNewFilesFromTemplates:
    """Tests for creating new files from templates."""

    def test_complete_command_creates_new_files(self):
        """Complete command should create new files from templates."""
        cmd_file = PROJECT_ROOT / "commands" / "stan" / "complete.md"
        content = cmd_file.read_text()

        # Should mention creating new files
        has_new_files = (
            "template" in content.lower() or
            "new" in content.lower() or
            "create" in content.lower()
        )
        assert has_new_files, "Complete command should create new files from templates"


class TestOptionalLearningsPromotion:
    """Tests for optional learnings promotion."""

    def test_complete_command_mentions_learnings(self):
        """Complete command should mention optional learnings promotion."""
        cmd_file = PROJECT_ROOT / "commands" / "stan" / "complete.md"
        content = cmd_file.read_text()

        # Should mention learnings (optional)
        assert "learning" in content.lower() or "graphiti" in content.lower(), \
            "Complete command should mention learnings promotion"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
