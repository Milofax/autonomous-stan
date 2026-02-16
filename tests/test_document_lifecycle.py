#!/usr/bin/env python3
"""
Tests für STAN Document Lifecycle Management.

Testet:
- Status-Validierung
- Transition-Regeln
- Frontmatter-Handling
- Auto-Transitions
"""

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Path configured in conftest.py

from document import (
    VALID_STATUSES,
    ALLOWED_TRANSITIONS,
    AUTO_TRANSITIONS,
    MANUAL_TRANSITIONS,
    read_frontmatter,
    write_frontmatter,
    get_document_status,
    validate_status,
    can_transition,
    is_auto_transition,
    is_manual_transition,
    update_document_status,
    get_status_info,
    get_lifecycle_position,
    scan_documents,
)


# =============================================================================
# Status Validation Tests
# =============================================================================

class TestStatusValidation:
    """Tests für Status-Validierung."""

    def test_valid_statuses_exist(self):
        """5 gültige Status müssen existieren."""
        assert len(VALID_STATUSES) == 5
        assert "draft" in VALID_STATUSES
        assert "approved" in VALID_STATUSES
        assert "in-progress" in VALID_STATUSES
        assert "done" in VALID_STATUSES
        assert "completed" in VALID_STATUSES

    def test_validate_valid_status(self):
        """Gültige Status werden akzeptiert."""
        for status in VALID_STATUSES:
            valid, err = validate_status(status)
            assert valid, f"Status '{status}' should be valid"
            assert err == ""

    def test_validate_invalid_status(self):
        """Ungültige Status werden abgelehnt."""
        invalid = ["pending", "active", "closed", "wip", ""]
        for status in invalid:
            valid, err = validate_status(status)
            assert not valid, f"Status '{status}' should be invalid"
            assert "Invalid status" in err

    def test_lifecycle_order(self):
        """Status sind in Lifecycle-Reihenfolge."""
        assert VALID_STATUSES[0] == "draft"
        assert VALID_STATUSES[1] == "approved"
        assert VALID_STATUSES[2] == "in-progress"
        assert VALID_STATUSES[3] == "done"
        assert VALID_STATUSES[4] == "completed"


# =============================================================================
# Transition Tests
# =============================================================================

class TestTransitions:
    """Tests für Status-Übergänge."""

    def test_allowed_transitions_defined(self):
        """Alle Status haben definierte Übergänge."""
        for status in VALID_STATUSES:
            assert status in ALLOWED_TRANSITIONS

    def test_draft_transitions(self):
        """draft → approved ist erlaubt."""
        allowed, _ = can_transition("draft", "approved")
        assert allowed

        # Nicht erlaubt
        not_allowed = ["in-progress", "done", "archived"]
        for target in not_allowed:
            allowed, _ = can_transition("draft", target)
            assert not allowed, f"draft → {target} should not be allowed"

    def test_approved_transitions(self):
        """approved → in-progress und → draft sind erlaubt."""
        allowed, _ = can_transition("approved", "in-progress")
        assert allowed

        allowed, _ = can_transition("approved", "draft")
        assert allowed  # Rückgang erlaubt

        # Nicht erlaubt
        allowed, _ = can_transition("approved", "done")
        assert not allowed

    def test_in_progress_transitions(self):
        """in-progress → done und → approved sind erlaubt."""
        allowed, _ = can_transition("in-progress", "done")
        assert allowed

        allowed, _ = can_transition("in-progress", "approved")
        assert allowed  # Rückgang erlaubt

    def test_done_transitions(self):
        """done → completed und → in-progress sind erlaubt."""
        allowed, _ = can_transition("done", "completed")
        assert allowed

        allowed, _ = can_transition("done", "in-progress")
        assert allowed  # Reopen erlaubt

    def test_completed_transitions(self):
        """completed → draft ist erlaubt (Uncomplete)."""
        allowed, _ = can_transition("completed", "draft")
        assert allowed

    def test_same_status_transition(self):
        """Gleicher Status ist immer erlaubt (no-op)."""
        for status in VALID_STATUSES:
            allowed, reason = can_transition(status, status)
            assert allowed
            assert "No change" in reason

    def test_invalid_from_status(self):
        """Ungültiger Ausgangsstatus wird abgelehnt."""
        allowed, err = can_transition("invalid", "approved")
        assert not allowed
        assert "Invalid status" in err

    def test_invalid_to_status(self):
        """Ungültiger Zielstatus wird abgelehnt."""
        allowed, err = can_transition("draft", "invalid")
        assert not allowed
        assert "Invalid status" in err


# =============================================================================
# Auto/Manual Transition Tests
# =============================================================================

class TestAutoManualTransitions:
    """Tests für Auto- und Manual-Transitions."""

    def test_auto_transitions_defined(self):
        """Auto-Transitions sind definiert."""
        assert ("approved", "in-progress") in AUTO_TRANSITIONS
        assert ("in-progress", "done") in AUTO_TRANSITIONS

    def test_manual_transitions_defined(self):
        """Manual-Transitions sind definiert."""
        assert ("draft", "approved") in MANUAL_TRANSITIONS
        assert ("done", "completed") in MANUAL_TRANSITIONS
        assert ("completed", "draft") in MANUAL_TRANSITIONS

    def test_is_auto_transition(self):
        """is_auto_transition erkennt Auto-Transitions."""
        assert is_auto_transition("approved", "in-progress")
        assert is_auto_transition("in-progress", "done")
        assert not is_auto_transition("draft", "approved")

    def test_is_manual_transition(self):
        """is_manual_transition erkennt Manual-Transitions."""
        assert is_manual_transition("draft", "approved")
        assert is_manual_transition("done", "completed")
        assert not is_manual_transition("approved", "in-progress")


# =============================================================================
# Frontmatter Tests
# =============================================================================

class TestFrontmatter:
    """Tests für Frontmatter-Handling."""

    def test_read_frontmatter_valid(self):
        """Gültiges Frontmatter wird gelesen."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""---
type: prd
status: draft
created: "2026-01-22"
---

# Content
""")
            f.flush()

            try:
                fm = read_frontmatter(Path(f.name))
                assert fm is not None
                assert fm["type"] == "prd"
                assert fm["status"] == "draft"
                assert fm["created"] == "2026-01-22"
            finally:
                os.unlink(f.name)

    def test_read_frontmatter_no_frontmatter(self):
        """Datei ohne Frontmatter gibt None zurück."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Just content\n\nNo frontmatter here.")
            f.flush()

            try:
                fm = read_frontmatter(Path(f.name))
                assert fm is None
            finally:
                os.unlink(f.name)

    def test_read_frontmatter_nonexistent_file(self):
        """Nicht existierende Datei gibt None zurück."""
        fm = read_frontmatter(Path("/nonexistent/file.md"))
        assert fm is None

    def test_write_frontmatter(self):
        """Frontmatter wird korrekt geschrieben."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""---
type: prd
status: draft
---

# Content here
""")
            f.flush()

            try:
                path = Path(f.name)
                success = write_frontmatter(path, {
                    "type": "prd",
                    "status": "approved",
                    "updated": "2026-01-22"
                })
                assert success

                # Verify
                fm = read_frontmatter(path)
                assert fm["status"] == "approved"
                assert fm["updated"] == "2026-01-22"

                # Content erhalten
                content = path.read_text()
                assert "# Content here" in content
            finally:
                os.unlink(f.name)


# =============================================================================
# Document Status Tests
# =============================================================================

class TestDocumentStatus:
    """Tests für Dokument-Status-Operationen."""

    def test_get_document_status(self):
        """Status wird aus Dokument gelesen."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""---
status: in-progress
---

# Content
""")
            f.flush()

            try:
                status = get_document_status(Path(f.name))
                assert status == "in-progress"
            finally:
                os.unlink(f.name)

    def test_get_document_status_missing(self):
        """Fehlender Status gibt None zurück."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""---
type: prd
---

# Content
""")
            f.flush()

            try:
                status = get_document_status(Path(f.name))
                assert status is None
            finally:
                os.unlink(f.name)

    def test_update_document_status_allowed(self):
        """Erlaubter Status-Wechsel funktioniert."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""---
type: prd
status: draft
---

# Content
""")
            f.flush()

            try:
                path = Path(f.name)
                success, msg = update_document_status(path, "approved")
                assert success
                assert "draft → approved" in msg

                # Verify
                status = get_document_status(path)
                assert status == "approved"
            finally:
                os.unlink(f.name)

    def test_update_document_status_not_allowed(self):
        """Nicht erlaubter Status-Wechsel wird abgelehnt."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""---
type: prd
status: draft
---

# Content
""")
            f.flush()

            try:
                path = Path(f.name)
                success, msg = update_document_status(path, "done")
                assert not success
                assert "Cannot transition" in msg

                # Status unverändert
                status = get_document_status(path)
                assert status == "draft"
            finally:
                os.unlink(f.name)

    def test_update_document_status_force(self):
        """Mit force können ungültige Übergänge erzwungen werden."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""---
type: prd
status: draft
---

# Content
""")
            f.flush()

            try:
                path = Path(f.name)
                success, msg = update_document_status(path, "done", force=True)
                assert success

                status = get_document_status(path)
                assert status == "done"
            finally:
                os.unlink(f.name)


# =============================================================================
# Status Info Tests
# =============================================================================

class TestStatusInfo:
    """Tests für Status-Info-Funktionen."""

    def test_get_status_info(self):
        """Status-Info enthält alle Felder."""
        info = get_status_info("draft")
        assert info["status"] == "draft"
        assert info["valid"] is True
        assert info["index"] == 0
        assert info["is_initial"] is True
        assert info["is_terminal"] is False
        assert "approved" in info["allowed_transitions"]

    def test_get_status_info_completed(self):
        """completed ist Terminal-Status."""
        info = get_status_info("completed")
        assert info["is_terminal"] is True
        assert info["is_initial"] is False

    def test_get_lifecycle_position(self):
        """Lifecycle-Position wird korrekt zurückgegeben."""
        assert get_lifecycle_position("draft") == 0
        assert get_lifecycle_position("approved") == 1
        assert get_lifecycle_position("in-progress") == 2
        assert get_lifecycle_position("done") == 3
        assert get_lifecycle_position("completed") == 4
        assert get_lifecycle_position("invalid") == -1


# =============================================================================
# Scan Documents Tests
# =============================================================================

class TestScanDocuments:
    """Tests für Document-Scanning."""

    def test_scan_documents(self):
        """Dokumente werden gescannt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            doc1 = Path(tmpdir) / "prd.md"
            doc1.write_text("""---
type: prd
status: draft
---

# PRD
""")

            doc2 = Path(tmpdir) / "plan.md"
            doc2.write_text("""---
type: plan
status: approved
---

# Plan
""")

            # File without frontmatter
            doc3 = Path(tmpdir) / "notes.md"
            doc3.write_text("# Notes\n\nNo frontmatter.")

            results = scan_documents(Path(tmpdir))

            assert len(results) == 2  # notes.md hat kein Frontmatter
            types = [r["type"] for r in results]
            assert "prd" in types
            assert "plan" in types

    def test_scan_documents_empty(self):
        """Leeres Verzeichnis gibt leere Liste."""
        with tempfile.TemporaryDirectory() as tmpdir:
            results = scan_documents(Path(tmpdir))
            assert results == []


# =============================================================================
# Integration Tests
# =============================================================================

class TestLifecycleIntegration:
    """Integration-Tests für den kompletten Lifecycle."""

    def test_full_lifecycle(self):
        """Kompletter Lifecycle: draft → approved → in-progress → done → completed."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""---
type: prd
status: draft
created: 2026-01-22
---

# Content
""")
            f.flush()

            try:
                path = Path(f.name)

                # draft → approved
                success, _ = update_document_status(path, "approved")
                assert success
                assert get_document_status(path) == "approved"

                # approved → in-progress
                success, _ = update_document_status(path, "in-progress")
                assert success
                assert get_document_status(path) == "in-progress"

                # in-progress → done
                success, _ = update_document_status(path, "done")
                assert success
                assert get_document_status(path) == "done"

                # done → completed
                success, _ = update_document_status(path, "completed")
                assert success
                assert get_document_status(path) == "completed"
            finally:
                os.unlink(f.name)

    def test_backward_transitions(self):
        """Rückwärts-Übergänge für Korrektur."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""---
status: in-progress
---

# Content
""")
            f.flush()

            try:
                path = Path(f.name)

                # in-progress → approved (Blocker gefunden)
                success, _ = update_document_status(path, "approved")
                assert success

                # approved → draft (Änderungen nötig)
                success, _ = update_document_status(path, "draft")
                assert success
            finally:
                os.unlink(f.name)

    def test_reopen_done(self):
        """done kann zu in-progress zurückgesetzt werden."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""---
status: done
---

# Content
""")
            f.flush()

            try:
                path = Path(f.name)

                # done → in-progress (Issue gefunden)
                success, _ = update_document_status(path, "in-progress")
                assert success
                assert get_document_status(path) == "in-progress"
            finally:
                os.unlink(f.name)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
