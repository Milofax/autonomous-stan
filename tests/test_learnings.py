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

    def test_stats_includes_stale_counts(self, temp_learnings_dir):
        """Stats zeigt stale Learnings."""
        from datetime import datetime, timedelta

        old_date = (datetime.now() - timedelta(days=30)).isoformat()
        new_date = datetime.now().isoformat()

        learnings.save_file(learnings.HOT_FILE, [
            {"id": "1", "last_used": old_date},  # stale
            {"id": "2", "last_used": new_date},  # fresh
        ])

        stats = learnings.get_stats()

        assert stats["stale_hot"] == 1


class TestHeatScore:
    """Tests für Heat-Score Berechnung."""

    def test_heat_score_increases_with_use_count(self, temp_learnings_dir):
        """Höhere use_count = höherer Score."""
        from datetime import datetime

        low = {"use_count": 1, "last_used": datetime.now().isoformat()}
        high = {"use_count": 10, "last_used": datetime.now().isoformat()}

        score_low = learnings.calculate_heat_score(low)
        score_high = learnings.calculate_heat_score(high)

        assert score_high > score_low

    def test_heat_score_decays_with_time(self, temp_learnings_dir):
        """Ältere last_used = niedrigerer Score."""
        from datetime import datetime, timedelta

        recent = {"use_count": 3, "last_used": datetime.now().isoformat()}
        old = {"use_count": 3, "last_used": (datetime.now() - timedelta(days=10)).isoformat()}

        score_recent = learnings.calculate_heat_score(recent)
        score_old = learnings.calculate_heat_score(old)

        assert score_recent > score_old

    def test_heat_score_handles_missing_fields(self, temp_learnings_dir):
        """Score funktioniert auch ohne optionale Felder."""
        minimal = {"content": "Test"}

        score = learnings.calculate_heat_score(minimal)

        assert score >= 0  # Sollte nicht crashen


class TestStaleDetection:
    """Tests für is_stale()."""

    def test_stale_after_decay_days(self, temp_learnings_dir):
        """Learning ist stale nach DECAY_DAYS."""
        from datetime import datetime, timedelta

        old = {"last_used": (datetime.now() - timedelta(days=20)).isoformat()}

        with patch.object(learnings, 'DECAY_DAYS', 14):
            assert learnings.is_stale(old) is True

    def test_not_stale_within_decay_days(self, temp_learnings_dir):
        """Learning ist nicht stale innerhalb DECAY_DAYS."""
        from datetime import datetime, timedelta

        recent = {"last_used": (datetime.now() - timedelta(days=5)).isoformat()}

        with patch.object(learnings, 'DECAY_DAYS', 14):
            assert learnings.is_stale(recent) is False

    def test_stale_uses_created_at_if_no_last_used(self, temp_learnings_dir):
        """Falls kein last_used, wird created_at verwendet."""
        from datetime import datetime, timedelta

        old_created = {"created_at": (datetime.now() - timedelta(days=20)).isoformat()}

        with patch.object(learnings, 'DECAY_DAYS', 14):
            assert learnings.is_stale(old_created) is True

    def test_stale_handles_missing_dates(self, temp_learnings_dir):
        """Ohne Datum ist Learning stale."""
        no_dates = {"content": "Test"}

        assert learnings.is_stale(no_dates) is True


class TestDemoteFromHot:
    """Tests für demote_from_hot()."""

    def test_demote_moves_to_recent(self, temp_learnings_dir):
        """Demote verschiebt von hot nach recent."""
        learnings.save_file(learnings.HOT_FILE, [
            {"id": "hot1", "content": "Hot Learning"}
        ])

        result = learnings.demote_from_hot("hot1")

        assert result is True
        assert len(learnings.load_file(learnings.HOT_FILE)) == 0
        recent = learnings.load_file(learnings.RECENT_FILE)
        assert len(recent) == 1
        assert recent[0]["id"] == "hot1"

    def test_demote_nonexistent_returns_false(self, temp_learnings_dir):
        """Demote nicht existierendes Learning gibt False."""
        result = learnings.demote_from_hot("nonexistent")

        assert result is False

    def test_demote_handles_recent_overflow(self, temp_learnings_dir):
        """Demote respektiert MAX_RECENT."""
        with patch.object(learnings, 'MAX_RECENT', 2):
            # Recent voll
            learnings.save_file(learnings.RECENT_FILE, [
                {"id": "r1"}, {"id": "r2"}
            ])
            learnings.save_file(learnings.HOT_FILE, [
                {"id": "hot1", "content": "Hot"}
            ])

            learnings.demote_from_hot("hot1")

            recent = learnings.load_file(learnings.RECENT_FILE)
            archive = learnings.load_file(learnings.ARCHIVE_FILE)

            assert len(recent) == 2  # MAX_RECENT respektiert
            assert len(archive) == 1  # Overflow nach archive


class TestRotateLearnings:
    """Tests für rotate_learnings()."""

    def test_rotate_demotes_stale_hot(self, temp_learnings_dir):
        """Stale hot Learnings werden demoted."""
        from datetime import datetime, timedelta

        old_date = (datetime.now() - timedelta(days=20)).isoformat()

        learnings.save_file(learnings.HOT_FILE, [
            {"id": "hot1", "last_used": old_date, "use_count": 5}  # stale, high use
        ])

        with patch.object(learnings, 'DECAY_DAYS', 14):
            result = learnings.rotate_learnings()

        assert result["hot_demoted"] >= 1

    def test_rotate_archives_low_use_stale(self, temp_learnings_dir):
        """Stale hot Learnings mit niedrigem use_count werden archiviert."""
        from datetime import datetime, timedelta

        old_date = (datetime.now() - timedelta(days=20)).isoformat()

        learnings.save_file(learnings.HOT_FILE, [
            {"id": "hot1", "last_used": old_date, "use_count": 1}  # stale, low use
        ])

        with patch.object(learnings, 'DECAY_DAYS', 14):
            with patch.object(learnings, 'PROMOTE_THRESHOLD', 3):
                result = learnings.rotate_learnings()

        assert result["hot_archived"] >= 1

    def test_rotate_handles_hot_overflow(self, temp_learnings_dir):
        """Hot overflow wird nach recent demoted."""
        from datetime import datetime

        now = datetime.now().isoformat()

        # Mehr als MAX_HOT Learnings
        hot_learnings = [
            {"id": f"hot{i}", "last_used": now, "use_count": i}
            for i in range(25)
        ]
        learnings.save_file(learnings.HOT_FILE, hot_learnings)

        with patch.object(learnings, 'MAX_HOT', 20):
            result = learnings.rotate_learnings()

        hot = learnings.load_file(learnings.HOT_FILE)
        assert len(hot) <= 20
        assert result["hot_demoted"] >= 5

    def test_rotate_handles_recent_overflow(self, temp_learnings_dir):
        """Recent overflow wird archiviert."""
        recent_learnings = [{"id": f"r{i}"} for i in range(60)]
        learnings.save_file(learnings.RECENT_FILE, recent_learnings)

        with patch.object(learnings, 'MAX_RECENT', 50):
            result = learnings.rotate_learnings()

        recent = learnings.load_file(learnings.RECENT_FILE)
        archive = learnings.load_file(learnings.ARCHIVE_FILE)

        assert len(recent) <= 50
        assert result["recent_archived"] >= 10


class TestGetHotRanked:
    """Tests für get_hot_ranked()."""

    def test_hot_ranked_sorts_by_score(self, temp_learnings_dir):
        """Hot Learnings werden nach Score sortiert."""
        from datetime import datetime

        now = datetime.now().isoformat()

        learnings.save_file(learnings.HOT_FILE, [
            {"id": "low", "use_count": 1, "last_used": now},
            {"id": "high", "use_count": 10, "last_used": now},
            {"id": "mid", "use_count": 5, "last_used": now},
        ])

        ranked = learnings.get_hot_ranked()

        assert ranked[0]["id"] == "high"
        assert ranked[2]["id"] == "low"

    def test_hot_ranked_includes_score(self, temp_learnings_dir):
        """Jedes Learning hat heat_score Feld."""
        from datetime import datetime

        learnings.save_file(learnings.HOT_FILE, [
            {"id": "hot1", "use_count": 5, "last_used": datetime.now().isoformat()}
        ])

        ranked = learnings.get_hot_ranked()

        assert "heat_score" in ranked[0]
        assert "is_stale" in ranked[0]


class TestGetLearningWithScore:
    """Tests für get_learning_with_score()."""

    def test_returns_learning_with_score(self, temp_learnings_dir):
        """Learning wird mit Score zurückgegeben."""
        learning = learnings.save_learning("Test", "Context")

        result = learnings.get_learning_with_score(learning["id"])

        assert result is not None
        assert "heat_score" in result
        assert "is_stale" in result

    def test_returns_none_for_nonexistent(self, temp_learnings_dir):
        """Nicht existierendes Learning gibt None."""
        result = learnings.get_learning_with_score("nonexistent")

        assert result is None


class TestPendingLearningsPersistence:
    """Tests für Bug #1: Pending Learnings müssen in Local Storage persistiert werden."""

    def test_save_pending_learnings_persists_to_local_storage(self, temp_learnings_dir, tmp_path):
        """Pending Learnings werden in ~/.stan/learnings/recent.json gespeichert."""
        import session_state

        # Mock session file
        session_file = tmp_path / "session.json"
        with patch.object(session_state, 'get_session_file', return_value=session_file):
            # Add pending learning via session_state
            session_state.add_pending_learning(
                content="Test ROT->GRÜN: pytest fixed",
                context="Command: pytest tests/"
            )

            # Verify pending learning exists in session
            pending = session_state.get_pending_learnings()
            assert len(pending) == 1
            assert "ROT->GRÜN" in pending[0]["content"]

            # Now save pending learnings to local storage
            saved = session_state.save_pending_learnings()

            # Verify learning is now in local storage
            recent = learnings.load_file(learnings.RECENT_FILE)
            assert len(recent) == 1
            assert "ROT->GRÜN" in recent[0]["content"]

            # Verify pending learnings are cleared
            pending_after = session_state.get_pending_learnings()
            assert len(pending_after) == 0

            # Verify return value
            assert saved == 1

    def test_save_pending_learnings_with_no_pending_returns_zero(self, temp_learnings_dir, tmp_path):
        """Keine pending Learnings = 0 gespeichert."""
        import session_state

        session_file = tmp_path / "session.json"
        with patch.object(session_state, 'get_session_file', return_value=session_file):
            saved = session_state.save_pending_learnings()
            assert saved == 0

    def test_save_pending_learnings_preserves_all_fields(self, temp_learnings_dir, tmp_path):
        """Alle Felder des pending Learnings werden übernommen."""
        import session_state

        session_file = tmp_path / "session.json"
        with patch.object(session_state, 'get_session_file', return_value=session_file):
            session_state.add_pending_learning(
                content="GraphQL error: missing return type",
                context="File: schema.graphql, Line: 42"
            )

            session_state.save_pending_learnings()

            recent = learnings.load_file(learnings.RECENT_FILE)
            assert recent[0]["content"] == "GraphQL error: missing return type"
            assert recent[0]["context"] == "File: schema.graphql, Line: 42"
            assert recent[0]["source"] == "auto"  # Default from pending
            assert "created_at" in recent[0]
