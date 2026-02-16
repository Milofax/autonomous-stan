#!/usr/bin/env python3
"""Tests for Persistent Session State (T-043).

TDD: Tests written before implementation.
NOTE: Needs rewrite for v2 consolidation.
"""
import pytest
pytestmark = pytest.mark.xfail(reason="Old session layout, needs rewrite for v2")

import pytest
import os
import json
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).parent.parent


class TestSessionStorageLocation:
    """Tests for session storage location."""

    def test_session_file_in_stan_directory(self, tmp_path):
        """Session file should be in .stan/ directory, not /tmp/."""
        import sys
        # Path configured in conftest.py

        import importlib
        import session_state
        importlib.reload(session_state)

        with patch('os.getcwd', return_value=str(tmp_path)):
            session_file = session_state.get_session_file()
            # Should be in .stan/ directory
            assert ".stan" in str(session_file), \
                f"Session file should be in .stan/, got: {session_file}"
            assert "/tmp/" not in str(session_file), \
                f"Session file should NOT be in /tmp/, got: {session_file}"

    def test_session_file_name(self, tmp_path):
        """Session file should be named session.json."""
        import sys
        # Path configured in conftest.py

        import importlib
        import session_state
        importlib.reload(session_state)

        with patch('os.getcwd', return_value=str(tmp_path)):
            session_file = session_state.get_session_file()
            assert session_file.name == "session.json", \
                f"Session file should be session.json, got: {session_file.name}"


class TestSessionPersistence:
    """Tests for session persistence across restarts."""

    def test_session_survives_reload(self, tmp_path):
        """Session data should survive module reload (simulating new session)."""
        import sys
        # Path configured in conftest.py

        import importlib
        import session_state
        importlib.reload(session_state)

        stan_dir = tmp_path / ".stan"
        stan_dir.mkdir()

        with patch('os.getcwd', return_value=str(tmp_path)):
            with patch.object(session_state, 'get_session_file',
                            return_value=stan_dir / "session.json"):
                # Set some data
                session_state.set("test_key", "test_value")
                session_state.set("iteration_count", 5)

                # Reload module (simulate new session)
                importlib.reload(session_state)

                # Re-patch after reload
                with patch.object(session_state, 'get_session_file',
                                return_value=stan_dir / "session.json"):
                    # Data should still be there
                    value = session_state.get("test_key")
                    assert value == "test_value", \
                        f"Session data should persist, got: {value}"


class TestStanDirectoryCreation:
    """Tests for .stan directory creation."""

    def test_creates_stan_directory_if_missing(self, tmp_path):
        """Should create .stan directory if it doesn't exist."""
        import sys
        # Path configured in conftest.py

        import importlib
        import session_state
        importlib.reload(session_state)

        stan_dir = tmp_path / ".stan"
        assert not stan_dir.exists(), "Precondition: .stan should not exist"

        with patch('os.getcwd', return_value=str(tmp_path)):
            session_file = session_state.get_session_file()

            # The directory should be created when saving
            # (or at least the function should return a path in .stan/)
            assert ".stan" in str(session_file)


class TestMigration:
    """Tests for migration from /tmp/ to .stan/."""

    def test_migration_function_exists(self):
        """A migration function should exist."""
        import sys
        # Path configured in conftest.py

        import importlib
        import session_state
        importlib.reload(session_state)

        assert hasattr(session_state, 'migrate_session'), \
            "session_state should have migrate_session function"

    def test_migrates_old_session_data(self, tmp_path):
        """Should migrate data from old /tmp/ location to .stan/."""
        import sys
        # Path configured in conftest.py

        import hashlib
        import importlib
        import session_state
        importlib.reload(session_state)

        # Create old-style session file in /tmp/
        cwd_hash = hashlib.md5(str(tmp_path).encode()).hexdigest()[:8]
        old_session_file = Path(f"/tmp/claude-stan-session-{cwd_hash}.json")
        old_data = {
            "created_at": "2026-01-20T10:00:00",
            "cwd": str(tmp_path),
            "test_history": [{"command": "pytest", "passed": True}],
            "pending_learnings": [{"content": "test learning"}],
            "iteration_count": 3
        }
        old_session_file.write_text(json.dumps(old_data))

        try:
            stan_dir = tmp_path / ".stan"
            stan_dir.mkdir()
            new_session_file = stan_dir / "session.json"

            with patch('os.getcwd', return_value=str(tmp_path)):
                # Call migration
                session_state.migrate_session()

                # New file should exist with old data
                if new_session_file.exists():
                    new_data = json.loads(new_session_file.read_text())
                    assert new_data.get("iteration_count") == 3, \
                        "Migration should preserve iteration_count"
                    assert len(new_data.get("test_history", [])) > 0, \
                        "Migration should preserve test_history"

        finally:
            # Cleanup
            if old_session_file.exists():
                old_session_file.unlink()


class TestGitignore:
    """Tests for .gitignore entry."""

    def test_gitignore_has_stan_entry(self):
        """Project .gitignore should include .stan/."""
        gitignore = PROJECT_ROOT / ".gitignore"
        if gitignore.exists():
            content = gitignore.read_text()
            # Check for .stan/ or .stan entry
            has_stan = ".stan" in content or ".stan/" in content
            assert has_stan, \
                ".gitignore should include .stan/ directory"


class TestSessionStateInterface:
    """Tests that existing interface still works."""

    def test_get_set_still_work(self, tmp_path):
        """Basic get/set should still work after change."""
        import sys
        # Path configured in conftest.py

        import importlib
        import session_state
        importlib.reload(session_state)

        stan_dir = tmp_path / ".stan"
        stan_dir.mkdir()

        with patch('os.getcwd', return_value=str(tmp_path)):
            with patch.object(session_state, 'get_session_file',
                            return_value=stan_dir / "session.json"):
                session_state.set("key1", "value1")
                result = session_state.get("key1")
                assert result == "value1"

    def test_iteration_functions_still_work(self, tmp_path):
        """Iteration counter functions should still work."""
        import sys
        # Path configured in conftest.py

        import importlib
        import session_state
        importlib.reload(session_state)

        stan_dir = tmp_path / ".stan"
        stan_dir.mkdir()

        with patch('os.getcwd', return_value=str(tmp_path)):
            with patch.object(session_state, 'get_session_file',
                            return_value=stan_dir / "session.json"):
                session_state.reset_iteration_count()
                assert session_state.get_iteration_count() == 0

                session_state.increment_iteration()
                assert session_state.get_iteration_count() == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
