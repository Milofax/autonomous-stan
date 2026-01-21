#!/usr/bin/env python3
"""Tests für das Learnings-System (Tiered Storage)."""

import json
import os
import sys
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch

# Add hooks lib to path
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude/hooks/stan/lib"))

import learnings


@pytest.fixture
def temp_learnings_dir(tmp_path):
    """Temporäres Learnings-Verzeichnis für Tests."""
    learnings_dir = tmp_path / "learnings"
    learnings_dir.mkdir()

    with patch.object(learnings, 'LEARNINGS_DIR', learnings_dir):
        with patch.object(learnings, 'RECENT_FILE', learnings_dir / "recent.json"):
            with patch.object(learnings, 'HOT_FILE', learnings_dir / "hot.json"):
                with patch.object(learnings, 'ARCHIVE_FILE', learnings_dir / "archive.json"):
                    yield learnings_dir


class TestSaveLearning:
    """Tests für save_learning()."""

    def test_save_creates_learning_with_all_fields(self, temp_learnings_dir):
        """Learning wird mit allen Feldern erstellt."""
        result = learnings.save_learning(
            content="Test content",
            context="Test context",
            tags=["test", "unit"],
            source="manual"
        )

        assert "id" in result
        assert result["content"] == "Test content"
        assert result["context"] == "Test context"
        assert result["tags"] == ["test", "unit"]
        assert result["source"] == "manual"
        assert result["use_count"] == 0
        assert result["last_used"] is None
        assert "created_at" in result

    def test_save_adds_to_recent(self, temp_learnings_dir):
        """Learning wird in recent.json gespeichert."""
        learnings.save_learning("Content 1", "Context 1")
        learnings.save_learning("Content 2", "Context 2")

        recent = learnings.load_file(learnings.RECENT_FILE)
        assert len(recent) == 2
        # Neuestes zuerst
        assert recent[0]["content"] == "Content 2"
        assert recent[1]["content"] == "Content 1"

    def test_fifo_overflow_to_archive(self, temp_learnings_dir):
        """Bei Overflow werden alte Learnings nach archive verschoben."""
        with patch.object(learnings, 'MAX_RECENT', 3):
            # 5 Learnings speichern, MAX ist 3
            for i in range(5):
                learnings.save_learning(f"Content {i}", f"Context {i}")

            recent = learnings.load_file(learnings.RECENT_FILE)
            archive = learnings.load_file(learnings.ARCHIVE_FILE)

            assert len(recent) == 3  # Max 3 in recent
            assert len(archive) == 2  # 2 overflow nach archive

            # Neueste in recent
            assert recent[0]["content"] == "Content 4"
            # Älteste in archive
            assert archive[0]["content"] == "Content 0"


class TestLoadLearnings:
    """Tests für load_learnings()."""

    def test_load_returns_hot_plus_recent(self, temp_learnings_dir):
        """load_learnings() gibt hot + recent zurück."""
        # Manuell hot und recent füllen
        learnings.save_file(learnings.HOT_FILE, [
            {"id": "hot1", "content": "Hot 1"}
        ])
        learnings.save_file(learnings.RECENT_FILE, [
            {"id": "recent1", "content": "Recent 1"}
        ])

        result = learnings.load_learnings()

        assert len(result) == 2
        assert result[0]["content"] == "Hot 1"  # Hot zuerst
        assert result[1]["content"] == "Recent 1"

    def test_load_with_archive(self, temp_learnings_dir):
        """include_archive=True lädt auch archive."""
        learnings.save_file(learnings.HOT_FILE, [{"id": "h1", "content": "Hot"}])
        learnings.save_file(learnings.RECENT_FILE, [{"id": "r1", "content": "Recent"}])
        learnings.save_file(learnings.ARCHIVE_FILE, [{"id": "a1", "content": "Archive"}])

        result = learnings.load_learnings(include_archive=True)

        assert len(result) == 3

    def test_load_empty_returns_empty_list(self, temp_learnings_dir):
        """Leere Dateien geben leere Liste zurück."""
        result = learnings.load_learnings()
        assert result == []


class TestRecordUsage:
    """Tests für record_usage() und Promotion."""

    def test_usage_increments_count(self, temp_learnings_dir):
        """use_count wird erhöht."""
        learning = learnings.save_learning("Test", "Context")
        learning_id = learning["id"]

        learnings.record_usage(learning_id)

        recent = learnings.load_file(learnings.RECENT_FILE)
        assert recent[0]["use_count"] == 1
        assert recent[0]["last_used"] is not None

    def test_promotion_to_hot_at_threshold(self, temp_learnings_dir):
        """Learning wird nach PROMOTE_THRESHOLD zu hot promotet."""
        with patch.object(learnings, 'PROMOTE_THRESHOLD', 2):
            learning = learnings.save_learning("Test", "Context")
            learning_id = learning["id"]

            learnings.record_usage(learning_id)  # count = 1
            learnings.record_usage(learning_id)  # count = 2 -> promote!

            recent = learnings.load_file(learnings.RECENT_FILE)
            hot = learnings.load_file(learnings.HOT_FILE)

            assert len(recent) == 0  # Aus recent entfernt
            assert len(hot) == 1     # In hot hinzugefügt
            assert hot[0]["use_count"] == 2

    def test_usage_in_hot_stays_in_hot(self, temp_learnings_dir):
        """Learnings in hot bleiben dort bei weiterer Nutzung."""
        learnings.save_file(learnings.HOT_FILE, [
            {"id": "hot1", "content": "Hot", "use_count": 5}
        ])

        learnings.record_usage("hot1")

        hot = learnings.load_file(learnings.HOT_FILE)
        assert hot[0]["use_count"] == 6


class TestPromoteAndArchive:
    """Tests für manuelle Promotion und Archivierung."""

    def test_promote_to_hot_manual(self, temp_learnings_dir):
        """Manuelles Promoten funktioniert."""
        learning = learnings.save_learning("Test", "Context")

        result = learnings.promote_to_hot(learning["id"])

        assert result is True
        assert len(learnings.load_file(learnings.RECENT_FILE)) == 0
        assert len(learnings.load_file(learnings.HOT_FILE)) == 1

    def test_archive_from_recent(self, temp_learnings_dir):
        """Archivieren aus recent funktioniert."""
        learning = learnings.save_learning("Test", "Context")

        result = learnings.archive_learning(learning["id"])

        assert result is True
        assert len(learnings.load_file(learnings.RECENT_FILE)) == 0
        assert len(learnings.load_file(learnings.ARCHIVE_FILE)) == 1

    def test_archive_from_hot(self, temp_learnings_dir):
        """Archivieren aus hot funktioniert."""
        learnings.save_file(learnings.HOT_FILE, [
            {"id": "hot1", "content": "Hot"}
        ])

        result = learnings.archive_learning("hot1")

        assert result is True
        assert len(learnings.load_file(learnings.HOT_FILE)) == 0
        assert len(learnings.load_file(learnings.ARCHIVE_FILE)) == 1


class TestSearchLearnings:
    """Tests für search_learnings()."""

    def test_search_by_content(self, temp_learnings_dir):
        """Suche in content funktioniert."""
        learnings.save_learning("Python async await", "Context")
        learnings.save_learning("JavaScript promises", "Context")

        results = learnings.search_learnings("python")

        assert len(results) == 1
        assert "Python" in results[0]["content"]

    def test_search_by_context(self, temp_learnings_dir):
        """Suche in context funktioniert."""
        learnings.save_learning("Content", "Project Alpha")
        learnings.save_learning("Content", "Project Beta")

        results = learnings.search_learnings("alpha")

        assert len(results) == 1

    def test_search_by_tag(self, temp_learnings_dir):
        """Suche in tags funktioniert."""
        learnings.save_learning("Content", "Context", tags=["python", "async"])
        learnings.save_learning("Content", "Context", tags=["javascript"])

        results = learnings.search_learnings("async")

        assert len(results) == 1

    def test_search_case_insensitive(self, temp_learnings_dir):
        """Suche ist case-insensitive."""
        learnings.save_learning("UPPERCASE content", "Context")

        results = learnings.search_learnings("uppercase")

        assert len(results) == 1


class TestGetStats:
    """Tests für get_stats()."""

    def test_stats_returns_counts(self, temp_learnings_dir):
        """Stats gibt korrekte Zahlen zurück."""
        learnings.save_file(learnings.RECENT_FILE, [{"id": "1"}, {"id": "2"}])
        learnings.save_file(learnings.HOT_FILE, [{"id": "3"}])
        learnings.save_file(learnings.ARCHIVE_FILE, [{"id": "4"}, {"id": "5"}, {"id": "6"}])

        stats = learnings.get_stats()

        assert stats["recent_count"] == 2
        assert stats["hot_count"] == 1
        assert stats["archive_count"] == 3
