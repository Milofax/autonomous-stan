#!/usr/bin/env python3
"""Tests for Acceptance Criteria completion checking."""

import pytest
from pathlib import Path
import tempfile
import os

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src" / "stan" / "lib"))

from acceptance import (
    parse_checkboxes,
    get_unchecked_criteria,
    all_criteria_checked,
    count_checkboxes,
)


class TestParseCheckboxes:
    """Tests for parsing checkboxes from markdown."""

    def test_finds_unchecked_checkboxes(self, tmp_path):
        """Findet unchecked checkboxes."""
        doc = tmp_path / "plan.md"
        doc.write_text("""---
type: plan
---
# Plan

**Acceptance Criteria:**
- [ ] First criterion
- [ ] Second criterion
""")
        checked, unchecked = parse_checkboxes(doc)
        assert len(unchecked) == 2
        assert len(checked) == 0

    def test_finds_checked_checkboxes(self, tmp_path):
        """Findet checked checkboxes."""
        doc = tmp_path / "plan.md"
        doc.write_text("""---
type: plan
---
# Plan

**Acceptance Criteria:**
- [x] First criterion
- [x] Second criterion
""")
        checked, unchecked = parse_checkboxes(doc)
        assert len(checked) == 2
        assert len(unchecked) == 0

    def test_finds_mixed_checkboxes(self, tmp_path):
        """Findet gemischte checkboxes."""
        doc = tmp_path / "plan.md"
        doc.write_text("""---
type: plan
---
# Plan

**Acceptance Criteria:**
- [x] Done criterion
- [ ] Pending criterion
- [x] Another done
""")
        checked, unchecked = parse_checkboxes(doc)
        assert len(checked) == 2
        assert len(unchecked) == 1
        assert "Pending criterion" in unchecked[0]

    def test_handles_uppercase_x(self, tmp_path):
        """Akzeptiert auch großes X."""
        doc = tmp_path / "plan.md"
        doc.write_text("""---
type: plan
---
- [X] Done with uppercase
- [x] Done with lowercase
""")
        checked, unchecked = parse_checkboxes(doc)
        assert len(checked) == 2

    def test_handles_empty_document(self, tmp_path):
        """Leeres Dokument gibt leere Listen."""
        doc = tmp_path / "plan.md"
        doc.write_text("")
        checked, unchecked = parse_checkboxes(doc)
        assert len(checked) == 0
        assert len(unchecked) == 0

    def test_ignores_non_checkbox_lines(self, tmp_path):
        """Ignoriert Zeilen ohne Checkboxen."""
        doc = tmp_path / "plan.md"
        doc.write_text("""---
type: plan
---
# Plan

Some text here.

- Regular list item
- Another item

**Acceptance Criteria:**
- [ ] Real criterion
""")
        checked, unchecked = parse_checkboxes(doc)
        assert len(unchecked) == 1


class TestGetUncheckedCriteria:
    """Tests for getting unchecked criteria."""

    def test_returns_unchecked_text(self, tmp_path):
        """Gibt Text der unchecked Criteria zurück."""
        doc = tmp_path / "plan.md"
        doc.write_text("""---
type: plan
---
**Acceptance Criteria:**
- [ ] Typecheck passes
- [x] Tests pass
- [ ] Verify in browser
""")
        unchecked = get_unchecked_criteria(doc)
        assert len(unchecked) == 2
        assert "Typecheck passes" in unchecked
        assert "Verify in browser" in unchecked

    def test_empty_when_all_checked(self, tmp_path):
        """Leer wenn alle abgehakt."""
        doc = tmp_path / "plan.md"
        doc.write_text("""---
type: plan
---
- [x] Done 1
- [x] Done 2
""")
        unchecked = get_unchecked_criteria(doc)
        assert len(unchecked) == 0


class TestAllCriteriaChecked:
    """Tests for checking if all criteria are complete."""

    def test_true_when_all_checked(self, tmp_path):
        """True wenn alle abgehakt."""
        doc = tmp_path / "plan.md"
        doc.write_text("""---
type: plan
---
- [x] Done 1
- [x] Done 2
- [x] Done 3
""")
        assert all_criteria_checked(doc) is True

    def test_false_when_some_unchecked(self, tmp_path):
        """False wenn welche offen."""
        doc = tmp_path / "plan.md"
        doc.write_text("""---
type: plan
---
- [x] Done 1
- [ ] Not done
- [x] Done 3
""")
        assert all_criteria_checked(doc) is False

    def test_true_when_no_checkboxes(self, tmp_path):
        """True wenn keine Checkboxen (nichts zu prüfen)."""
        doc = tmp_path / "plan.md"
        doc.write_text("""---
type: plan
---
# No checkboxes here
""")
        assert all_criteria_checked(doc) is True

    def test_handles_nonexistent_file(self):
        """Wirft Exception bei nicht existierendem File."""
        with pytest.raises(FileNotFoundError):
            all_criteria_checked("/nonexistent/file.md")


class TestCountCheckboxes:
    """Tests for counting checkboxes."""

    def test_counts_correctly(self, tmp_path):
        """Zählt korrekt."""
        doc = tmp_path / "plan.md"
        doc.write_text("""---
type: plan
---
- [x] Done 1
- [ ] Open 1
- [x] Done 2
- [ ] Open 2
- [ ] Open 3
""")
        total, checked, unchecked = count_checkboxes(doc)
        assert total == 5
        assert checked == 2
        assert unchecked == 3


class TestMultipleTaskSections:
    """Tests for documents with multiple tasks."""

    def test_finds_checkboxes_in_all_tasks(self, tmp_path):
        """Findet Checkboxen in allen Tasks."""
        doc = tmp_path / "plan.md"
        doc.write_text("""---
type: plan
---
### T-001: First Task

**Acceptance Criteria:**
- [ ] T1 criterion 1
- [x] T1 criterion 2

---

### T-002: Second Task

**Acceptance Criteria:**
- [ ] T2 criterion 1
- [ ] T2 criterion 2
""")
        checked, unchecked = parse_checkboxes(doc)
        assert len(checked) == 1
        assert len(unchecked) == 3

    def test_all_checked_requires_all_tasks(self, tmp_path):
        """all_criteria_checked braucht alle Tasks."""
        doc = tmp_path / "plan.md"
        doc.write_text("""---
type: plan
---
### T-001: Done Task
- [x] Done

### T-002: Open Task
- [ ] Not done
""")
        assert all_criteria_checked(doc) is False


class TestRealWorldPlan:
    """Tests with realistic plan content."""

    def test_realistic_plan_unchecked(self, tmp_path):
        """Realistischer Plan mit offenen Criteria."""
        doc = tmp_path / "plan.md"
        doc.write_text("""---
type: plan
status: in-progress
criteria:
  - task-is-actionable
  - task-fits-iteration
---

# Implementation Plan: Feature X

## Tasks

### T-001: Add database migration

**Description:** Add status column to tasks table.

**Acceptance Criteria:**
- [ ] Migration file created
- [ ] Column has correct type
- [ ] Typecheck passes

---

### T-002: Update UI component

**Description:** Show status badge.

**Acceptance Criteria:**
- [ ] Badge displays correctly
- [ ] Colors match spec
- [ ] Typecheck passes
- [ ] Verify in browser
""")
        assert all_criteria_checked(doc) is False
        unchecked = get_unchecked_criteria(doc)
        assert len(unchecked) == 7

    def test_realistic_plan_all_done(self, tmp_path):
        """Realistischer Plan mit allen abgehakten Criteria."""
        doc = tmp_path / "plan.md"
        doc.write_text("""---
type: plan
status: done
---

# Implementation Plan: Feature X

### T-001: Add database migration

**Acceptance Criteria:**
- [x] Migration file created
- [x] Column has correct type
- [x] Typecheck passes

### T-002: Update UI component

**Acceptance Criteria:**
- [x] Badge displays correctly
- [x] Colors match spec
- [x] Typecheck passes
- [x] Verify in browser
""")
        assert all_criteria_checked(doc) is True
