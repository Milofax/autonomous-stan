#!/usr/bin/env python3
"""Tests für Session State in src/stan/lib/."""

import pytest
import json
from pathlib import Path
from unittest.mock import patch

# Add src to path for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from stan.lib.session_state import (
    get_session_file,
    get,
    set,
    record_test_result,
    get_last_test_result,
    add_pending_learning,
    get_pending_learnings,
    mark_learning_saved,
    clear_pending_learnings,
    increment_error,
    get_error_count,
    reset_error_count,
    reset_all_errors,
)


class TestSessionState:
    """Tests für Session State Management."""

    @pytest.fixture
    def temp_session(self, tmp_path):
        """Create temporary session file."""
        session_file = tmp_path / "test-session.json"
        with patch("stan.lib.session_state.get_session_file", return_value=session_file):
            yield session_file

    def test_get_set_basic(self, temp_session):
        """get/set funktioniert für einfache Werte."""
        with patch("stan.lib.session_state.get_session_file", return_value=temp_session):
            set("test_key", "test_value")
            assert get("test_key") == "test_value"

    def test_get_default(self, temp_session):
        """get gibt default zurück wenn key fehlt."""
        with patch("stan.lib.session_state.get_session_file", return_value=temp_session):
            assert get("nonexistent", "default") == "default"

    def test_record_test_result_pass(self, temp_session):
        """Test-Ergebnis wird korrekt gespeichert (passed)."""
        with patch("stan.lib.session_state.get_session_file", return_value=temp_session):
            result = record_test_result("npm test", 0)
            assert result["passed"] is True
            assert result["red_to_green"] is False

    def test_record_test_result_fail(self, temp_session):
        """Test-Ergebnis wird korrekt gespeichert (failed)."""
        with patch("stan.lib.session_state.get_session_file", return_value=temp_session):
            result = record_test_result("npm test", 1)
            assert result["passed"] is False
            assert result["red_to_green"] is False

    def test_red_to_green_detection(self, temp_session):
        """ROT→GRÜN wird erkannt."""
        with patch("stan.lib.session_state.get_session_file", return_value=temp_session):
            # Erst ROT
            record_test_result("npm test", 1)
            # Dann GRÜN
            result = record_test_result("npm test", 0)
            assert result["passed"] is True
            assert result["red_to_green"] is True

    def test_green_to_green_no_detection(self, temp_session):
        """GRÜN→GRÜN ist kein Learning."""
        with patch("stan.lib.session_state.get_session_file", return_value=temp_session):
            # Erst GRÜN
            record_test_result("npm test", 0)
            # Dann wieder GRÜN
            result = record_test_result("npm test", 0)
            assert result["passed"] is True
            assert result["red_to_green"] is False

    def test_get_last_test_result(self, temp_session):
        """Letztes Test-Ergebnis wird korrekt abgerufen."""
        with patch("stan.lib.session_state.get_session_file", return_value=temp_session):
            record_test_result("npm test", 0)
            record_test_result("pytest", 1)

            # Ohne Filter: letzter Test
            last = get_last_test_result()
            assert last["command"] == "pytest"
            assert last["passed"] is False

            # Mit Filter: spezifischer Command
            npm_last = get_last_test_result("npm test")
            assert npm_last["command"] == "npm test"
            assert npm_last["passed"] is True

    def test_add_pending_learning(self, temp_session):
        """Pending Learning wird hinzugefügt."""
        with patch("stan.lib.session_state.get_session_file", return_value=temp_session):
            add_pending_learning("Test Learning", "Context")
            pending = get_pending_learnings()
            assert len(pending) == 1
            assert pending[0]["content"] == "Test Learning"
            assert pending[0]["context"] == "Context"
            assert pending[0]["saved"] is False

    def test_mark_learning_saved(self, temp_session):
        """Learning kann als saved markiert werden."""
        with patch("stan.lib.session_state.get_session_file", return_value=temp_session):
            add_pending_learning("Test Learning", "")
            mark_learning_saved(0)
            pending = get_pending_learnings()
            assert len(pending) == 0  # Saved ones are filtered out

    def test_clear_pending_learnings(self, temp_session):
        """Pending Learnings können gelöscht werden."""
        with patch("stan.lib.session_state.get_session_file", return_value=temp_session):
            add_pending_learning("Learning 1", "")
            add_pending_learning("Learning 2", "")
            clear_pending_learnings()
            pending = get_pending_learnings()
            assert len(pending) == 0

    def test_increment_error(self, temp_session):
        """Error Counter wird inkrementiert."""
        with patch("stan.lib.session_state.get_session_file", return_value=temp_session):
            count = increment_error("test_error")
            assert count == 1
            count = increment_error("test_error")
            assert count == 2
            count = increment_error("test_error")
            assert count == 3

    def test_get_error_count(self, temp_session):
        """Error Count wird korrekt abgerufen."""
        with patch("stan.lib.session_state.get_session_file", return_value=temp_session):
            assert get_error_count("unknown") == 0
            increment_error("known")
            assert get_error_count("known") == 1

    def test_reset_error_count(self, temp_session):
        """Error Count kann zurückgesetzt werden."""
        with patch("stan.lib.session_state.get_session_file", return_value=temp_session):
            increment_error("test_error")
            increment_error("test_error")
            reset_error_count("test_error")
            assert get_error_count("test_error") == 0

    def test_reset_all_errors(self, temp_session):
        """Alle Error Counts können zurückgesetzt werden."""
        with patch("stan.lib.session_state.get_session_file", return_value=temp_session):
            increment_error("error_1")
            increment_error("error_2")
            reset_all_errors()
            assert get_error_count("error_1") == 0
            assert get_error_count("error_2") == 0
