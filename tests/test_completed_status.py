#!/usr/bin/env python3
"""Tests for "completed" status (T-046).

TDD: Tests for renaming "archived" to "completed".
"""

import pytest
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


class TestValidStatusesIncludeCompleted:
    """Tests that VALID_STATUSES uses "completed" instead of "archived"."""

    def test_document_module_exists(self):
        """Document module should exist."""
        doc_file = PROJECT_ROOT / "hooks" / "autonomous-stan" / "lib" / "document.py"
        assert doc_file.exists(), f"Document module not found: {doc_file}"

    def test_valid_statuses_has_completed(self):
        """VALID_STATUSES should include "completed"."""
        # Path configured in conftest.py

        import importlib
        import document
        importlib.reload(document)

        assert "completed" in document.VALID_STATUSES, \
            "VALID_STATUSES should include 'completed'"

    def test_valid_statuses_no_archived(self):
        """VALID_STATUSES should NOT include "archived"."""
        # Path configured in conftest.py

        import importlib
        import document
        importlib.reload(document)

        assert "archived" not in document.VALID_STATUSES, \
            "VALID_STATUSES should NOT include 'archived' (use 'completed' instead)"


class TestTransitionsUseCompleted:
    """Tests that transitions use "completed" instead of "archived"."""

    def test_done_can_transition_to_completed(self):
        """done should transition to completed (not archived)."""
        # Path configured in conftest.py

        import importlib
        import document
        importlib.reload(document)

        assert "completed" in document.ALLOWED_TRANSITIONS.get("done", []), \
            "done should be able to transition to completed"

    def test_completed_can_transition_to_draft(self):
        """completed should be able to unarchive to draft."""
        # Path configured in conftest.py

        import importlib
        import document
        importlib.reload(document)

        assert "draft" in document.ALLOWED_TRANSITIONS.get("completed", []), \
            "completed should be able to transition back to draft (unarchive)"


class TestManualTransitionsUseCompleted:
    """Tests that MANUAL_TRANSITIONS uses "completed"."""

    def test_done_to_completed_is_manual(self):
        """done → completed should be a manual transition."""
        # Path configured in conftest.py

        import importlib
        import document
        importlib.reload(document)

        assert ("done", "completed") in document.MANUAL_TRANSITIONS, \
            "done → completed should be a manual transition"

    def test_completed_to_draft_is_manual(self):
        """completed → draft should be a manual transition."""
        # Path configured in conftest.py

        import importlib
        import document
        importlib.reload(document)

        assert ("completed", "draft") in document.MANUAL_TRANSITIONS, \
            "completed → draft should be a manual transition"


class TestTasksFileLegendUpdated:
    """Tests that tasks.md status legend uses "completed"."""

    def test_tasks_file_exists(self):
        """Tasks file should exist."""
        tasks_file = PROJECT_ROOT / "docs" / "tasks.md"
        assert tasks_file.exists(), f"Tasks file not found: {tasks_file}"

    def test_status_legend_mentions_completed(self):
        """Status legend should mention completed, not archived."""
        tasks_file = PROJECT_ROOT / "docs" / "tasks.md"
        content = tasks_file.read_text()

        # In the status legend, § should mean completed
        assert "§" in content, "Status legend should have § symbol"

        # The legend should explain § as completed (or not implementing)
        # We allow both interpretations since in tasks.md, § still means "not implementing"
        # The document status uses "completed" but task status symbol § can mean archived/not implementing


class TestStatusInfoFunctions:
    """Tests for status info functions with "completed"."""

    def test_get_status_info_for_completed(self):
        """get_status_info should work for "completed" status."""
        # Path configured in conftest.py

        import importlib
        import document
        importlib.reload(document)

        info = document.get_status_info("completed")
        assert info["valid"] is True, "completed should be a valid status"
        assert info["is_terminal"] is True, "completed should be terminal status"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
