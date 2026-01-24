#!/usr/bin/env python3
"""Tests für STAN Enforcement Library in src/stan/lib/."""

import pytest
import tempfile
from pathlib import Path

# Add src to path for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from stan.lib.frontmatter import (
    parse_frontmatter,
    get_document_type,
    get_document_criteria,
    get_document_status,
    get_techniques_applied,
    is_archived,
)
from stan.lib.criteria import (
    load_criteria,
    get_template_criteria,
    get_template_for_type,
    list_all_criteria,
    check_criteria_not_removed,
    set_project_root,
)
from stan.lib.enforcement import (
    EnforcementResult,
    allow,
    deny,
    check_document_criteria,
    check_techniques_for_phase,
    get_purposes_for_techniques,
    check_phase_transition,
    PHASE_PURPOSES,
)
from stan.lib.techniques import (
    list_techniques,
    list_purposes,
    get_technique,
    get_purpose,
    get_techniques_for_purpose,
    get_purposes_for_technique,
    set_project_root as set_techniques_root,
)


# Set project root for all tests
PROJECT_ROOT = Path(__file__).parent.parent
set_project_root(PROJECT_ROOT)
set_techniques_root(PROJECT_ROOT)


class TestFrontmatterParsing:
    """Tests für Frontmatter-Parsing."""

    def test_parse_valid_frontmatter(self, tmp_path):
        """Gültiges Frontmatter wird korrekt geparsed."""
        doc = tmp_path / "test.md"
        doc.write_text("""---
type: prd
status: draft
criteria:
  - goal-is-smart
  - text-quality
---

# Content here
""")
        fm = parse_frontmatter(doc)
        assert fm["type"] == "prd"
        assert fm["status"] == "draft"
        assert "goal-is-smart" in fm["criteria"]

    def test_parse_no_frontmatter(self, tmp_path):
        """Ohne Frontmatter wird leeres Dict zurückgegeben."""
        doc = tmp_path / "test.md"
        doc.write_text("# Just content\n\nNo frontmatter here.")
        fm = parse_frontmatter(doc)
        assert fm == {}

    def test_parse_nonexistent_file(self, tmp_path):
        """Nicht-existierende Datei gibt leeres Dict."""
        fm = parse_frontmatter(tmp_path / "nonexistent.md")
        assert fm == {}

    def test_parse_frontmatter_with_placeholders(self, tmp_path):
        """Frontmatter mit {{placeholders}} wird geparsed."""
        doc = tmp_path / "test.md"
        # Note: YAML needs proper quoting for values with special chars
        doc.write_text("---\ntype: prd\ncreated: \"{{date}}\"\ntitle: \"{{title}}\"\n---\n\n# Content\n")
        fm = parse_frontmatter(doc)
        assert fm["type"] == "prd"
        # Placeholders should be replaced with dummy values
        assert "created" in fm

    def test_get_document_type(self, tmp_path):
        """get_document_type extrahiert type korrekt."""
        doc = tmp_path / "test.md"
        doc.write_text("""---
type: plan
---
""")
        assert get_document_type(doc) == "plan"

    def test_get_document_criteria(self, tmp_path):
        """get_document_criteria extrahiert criteria Liste."""
        doc = tmp_path / "test.md"
        doc.write_text("""---
criteria:
  - criterion-a
  - criterion-b
---
""")
        criteria = get_document_criteria(doc)
        assert "criterion-a" in criteria
        assert "criterion-b" in criteria

    def test_get_techniques_applied(self, tmp_path):
        """get_techniques_applied extrahiert techniques_applied Liste."""
        doc = tmp_path / "test.md"
        doc.write_text("""---
type: prd
techniques_applied:
  - five-whys
  - mind-mapping
---
""")
        techniques = get_techniques_applied(doc)
        assert "five-whys" in techniques
        assert "mind-mapping" in techniques

    def test_is_archived(self, tmp_path):
        """is_archived erkennt archivierte Dokumente."""
        archived_doc = tmp_path / "archived.md"
        archived_doc.write_text("""---
status: archived
---
""")
        active_doc = tmp_path / "active.md"
        active_doc.write_text("""---
status: draft
---
""")

        assert is_archived(archived_doc) is True
        assert is_archived(active_doc) is False


class TestCriteriaLoading:
    """Tests für Criteria-Loading."""

    def test_load_existing_criteria(self):
        """Existierende Criteria werden geladen."""
        criteria = load_criteria("goal-is-smart")
        assert criteria is not None
        assert "name" in criteria
        assert "checks" in criteria

    def test_load_nonexistent_criteria(self):
        """Nicht-existierende Criteria geben None."""
        criteria = load_criteria("nonexistent-criteria")
        assert criteria is None

    def test_list_all_criteria(self):
        """Alle Criteria werden aufgelistet."""
        criteria = list_all_criteria()
        assert len(criteria) > 0
        assert "goal-is-smart" in criteria
        assert "text-quality" in criteria

    def test_get_template_criteria(self):
        """Template-Criteria werden korrekt geladen."""
        criteria = get_template_criteria("prd.md.template")
        assert len(criteria) > 0
        assert "goal-is-smart" in criteria

    def test_get_template_for_type(self):
        """Template für Typ wird gefunden."""
        template = get_template_for_type("prd")
        assert template == "prd.md.template"

    def test_get_template_for_unknown_type(self):
        """Unbekannter Typ gibt None."""
        template = get_template_for_type("unknown-type")
        assert template is None


class TestCriteriaNotRemoved:
    """Tests für check_criteria_not_removed."""

    def test_all_criteria_present(self):
        """Wenn alle Criteria vorhanden → valid."""
        doc_criteria = ["a", "b", "c", "d"]
        template_criteria = ["a", "b"]
        is_valid, missing = check_criteria_not_removed(doc_criteria, template_criteria)
        assert is_valid is True
        assert len(missing) == 0

    def test_criteria_removed(self):
        """Wenn Criteria entfernt → invalid mit missing Liste."""
        doc_criteria = ["a", "c"]
        template_criteria = ["a", "b", "c"]
        is_valid, missing = check_criteria_not_removed(doc_criteria, template_criteria)
        assert is_valid is False
        assert "b" in missing

    def test_extra_criteria_allowed(self):
        """Zusätzliche Criteria sind erlaubt."""
        doc_criteria = ["a", "b", "c", "d", "e"]
        template_criteria = ["a", "b"]
        is_valid, missing = check_criteria_not_removed(doc_criteria, template_criteria)
        assert is_valid is True

    def test_empty_document_criteria(self):
        """Leere Doc-Criteria bei nicht-leerem Template → invalid."""
        doc_criteria = []
        template_criteria = ["a", "b"]
        is_valid, missing = check_criteria_not_removed(doc_criteria, template_criteria)
        assert is_valid is False
        assert "a" in missing
        assert "b" in missing


class TestEnforcementResults:
    """Tests für EnforcementResult Helpers."""

    def test_allow_result(self):
        """allow() erstellt positives Result."""
        result = allow("All good")
        assert result.allowed is True
        assert "All good" in result.message

    def test_deny_result(self):
        """deny() erstellt negatives Result."""
        result = deny("Something wrong", {"detail": "info"})
        assert result.allowed is False
        assert "Something wrong" in result.message
        assert result.details["detail"] == "info"


class TestDocumentCriteriaCheck:
    """Tests für check_document_criteria."""

    def test_archived_document_skipped(self, tmp_path):
        """Archivierte Dokumente werden übersprungen."""
        doc = tmp_path / "archived.md"
        doc.write_text("""---
type: prd
status: archived
criteria: []
---
""")
        result = check_document_criteria(doc)
        assert result.allowed is True
        assert "Archived" in result.message

    def test_document_without_type(self, tmp_path):
        """Dokument ohne type → denied."""
        doc = tmp_path / "notype.md"
        doc.write_text("""---
status: draft
criteria:
  - text-quality
---
""")
        result = check_document_criteria(doc)
        assert result.allowed is False
        assert "type" in result.message.lower()

    def test_document_with_valid_criteria(self, tmp_path):
        """Dokument mit allen Template-Criteria → allowed."""
        # Get PRD template criteria first
        template_criteria = get_template_criteria("prd.md.template")

        doc = tmp_path / "valid-prd.md"
        criteria_yaml = "\n  - ".join([""] + template_criteria)
        doc.write_text(f"""---
type: prd
status: draft
criteria:{criteria_yaml}
---

# Valid PRD
""")
        result = check_document_criteria(doc)
        assert result.allowed is True

    def test_document_missing_criteria(self, tmp_path):
        """Dokument mit fehlenden Criteria → denied."""
        doc = tmp_path / "incomplete-prd.md"
        doc.write_text("""---
type: prd
status: draft
criteria:
  - goal-is-smart
---

# Incomplete PRD
""")
        result = check_document_criteria(doc)
        assert result.allowed is False
        assert "removed" in result.message.lower()

    def test_nonexistent_document(self, tmp_path):
        """Nicht-existierendes Dokument → denied."""
        result = check_document_criteria(tmp_path / "nonexistent.md")
        assert result.allowed is False
        assert "not found" in result.message.lower()


class TestTechniquesLoading:
    """Tests für Techniques-Loading."""

    def test_list_techniques(self):
        """Alle Techniques werden aufgelistet."""
        techniques = list_techniques()
        assert len(techniques) > 0
        assert "five-whys" in techniques
        assert "mind-mapping" in techniques

    def test_list_purposes(self):
        """Alle Purposes werden aufgelistet."""
        purposes = list_purposes()
        assert len(purposes) > 0
        # Check some expected purposes based on PHASE_PURPOSES
        expected_purposes = ["root-cause-analysis", "ideation", "code-review"]
        for p in expected_purposes:
            assert p in purposes, f"Purpose {p} should exist"

    def test_get_technique(self):
        """Technique wird korrekt geladen."""
        tech = get_technique("five-whys")
        assert tech is not None
        assert tech.get("name") == "Five Whys"
        assert "purposes" in tech
        assert "root-cause-analysis" in tech["purposes"]

    def test_get_nonexistent_technique(self):
        """Nicht-existierende Technique gibt None."""
        tech = get_technique("nonexistent-technique")
        assert tech is None

    def test_get_purposes_for_technique(self):
        """Purposes für Technique werden korrekt zurückgegeben."""
        purposes = get_purposes_for_technique("five-whys")
        assert "root-cause-analysis" in purposes


class TestTechniquesForPhase:
    """Tests für check_techniques_for_phase."""

    def test_archived_document_skipped(self, tmp_path):
        """Archivierte Dokumente werden übersprungen."""
        doc = tmp_path / "archived.md"
        doc.write_text("""---
status: archived
---
""")
        result = check_techniques_for_phase(doc, "define")
        assert result.allowed is True
        assert "Archived" in result.message

    def test_no_techniques_applied(self, tmp_path):
        """Keine techniques_applied → denied."""
        doc = tmp_path / "no-techniques.md"
        doc.write_text("""---
type: prd
status: draft
---
""")
        result = check_techniques_for_phase(doc, "define")
        assert result.allowed is False
        assert "techniques_applied" in result.message.lower()

    def test_define_phase_with_valid_technique(self, tmp_path):
        """DEFINE Phase mit big-picture/ideation Technique → allowed."""
        # mind-mapping has "ideation" in its purposes
        doc = tmp_path / "with-technique.md"
        doc.write_text("""---
type: prd
status: draft
techniques_applied:
  - mind-mapping
---
""")
        result = check_techniques_for_phase(doc, "define")
        assert result.allowed is True

    def test_create_phase_with_valid_technique(self, tmp_path):
        """CREATE Phase mit code-review Technique → allowed."""
        # five-whys has "code-review" in its purposes
        doc = tmp_path / "with-technique.md"
        doc.write_text("""---
type: plan
status: draft
techniques_applied:
  - five-whys
---
""")
        result = check_techniques_for_phase(doc, "create")
        assert result.allowed is True

    def test_phase_without_required_purpose(self, tmp_path):
        """Phase ohne erforderliche Purpose → denied."""
        # Create a technique that doesn't cover required purposes
        doc = tmp_path / "wrong-technique.md"
        doc.write_text("""---
type: plan
status: draft
techniques_applied:
  - dot-voting
---
""")
        # dot-voting is for "decision-making" which is PLAN phase, not CREATE
        result = check_techniques_for_phase(doc, "create")
        # This should fail unless dot-voting covers code-review
        # Let's check what purposes dot-voting has
        tech = get_technique("dot-voting")
        if tech and "code-review" not in tech.get("purposes", []):
            assert result.allowed is False


class TestPurposesForTechniques:
    """Tests für get_purposes_for_techniques."""

    def test_single_technique(self):
        """Purposes für einzelne Technique."""
        purposes = get_purposes_for_techniques(["five-whys"])
        assert "root-cause-analysis" in purposes

    def test_multiple_techniques(self):
        """Purposes für mehrere Techniques werden vereinigt."""
        purposes = get_purposes_for_techniques(["five-whys", "mind-mapping"])
        # Should contain purposes from both
        assert "root-cause-analysis" in purposes  # from five-whys
        assert "ideation" in purposes  # from mind-mapping

    def test_nonexistent_technique_ignored(self):
        """Nicht-existierende Techniques werden ignoriert."""
        purposes = get_purposes_for_techniques(["five-whys", "nonexistent"])
        assert "root-cause-analysis" in purposes
        # Should not crash

    def test_empty_list(self):
        """Leere Liste gibt leeres Set."""
        purposes = get_purposes_for_techniques([])
        assert len(purposes) == 0


class TestPhaseTransitions:
    """Tests für check_phase_transition."""

    def test_define_to_plan_allowed(self):
        """DEFINE → PLAN ist erlaubt."""
        result = check_phase_transition("define", "plan")
        assert result.allowed is True

    def test_plan_to_create_allowed(self):
        """PLAN → CREATE ist erlaubt."""
        result = check_phase_transition("plan", "create")
        assert result.allowed is True

    def test_create_to_define_allowed(self):
        """CREATE → DEFINE ist erlaubt (Reconciliation)."""
        result = check_phase_transition("create", "define")
        assert result.allowed is True

    def test_define_to_create_denied(self):
        """DEFINE → CREATE ist NICHT erlaubt (muss durch PLAN)."""
        result = check_phase_transition("define", "create")
        assert result.allowed is False

    def test_plan_to_define_allowed(self):
        """PLAN → DEFINE ist erlaubt (zurück für Reconciliation)."""
        result = check_phase_transition("plan", "define")
        assert result.allowed is True

    def test_create_to_plan_denied(self):
        """CREATE → PLAN ist NICHT erlaubt."""
        result = check_phase_transition("create", "plan")
        assert result.allowed is False


class TestPhasePurposes:
    """Tests für PHASE_PURPOSES Konfiguration."""

    def test_define_requires_big_picture_or_ideation(self):
        """DEFINE Phase erfordert big-picture oder ideation."""
        required = PHASE_PURPOSES.get("define", [])
        assert "big-picture" in required or "ideation" in required

    def test_plan_requires_problem_solving_or_decision(self):
        """PLAN Phase erfordert structured-problem-solving oder decision-making."""
        required = PHASE_PURPOSES.get("plan", [])
        assert "structured-problem-solving" in required or "decision-making" in required

    def test_create_requires_code_review(self):
        """CREATE Phase erfordert code-review."""
        required = PHASE_PURPOSES.get("create", [])
        assert "code-review" in required


class TestIntegration:
    """Integrationstests für vollständige Workflows."""

    def test_full_prd_workflow(self, tmp_path):
        """Vollständiger PRD Workflow mit Criteria und Techniques."""
        # Create a valid PRD document
        template_criteria = get_template_criteria("prd.md.template")
        criteria_yaml = "\n  - ".join([""] + template_criteria)

        doc = tmp_path / "my-prd.md"
        doc.write_text(f"""---
type: prd
status: draft
criteria:{criteria_yaml}
techniques_applied:
  - mind-mapping
  - brainstorming
---

# My PRD

This is a valid PRD with all required criteria and DEFINE phase techniques.
""")

        # Check criteria
        criteria_result = check_document_criteria(doc)
        assert criteria_result.allowed is True, f"Criteria check failed: {criteria_result.message}"

        # Check techniques for DEFINE phase
        techniques_result = check_techniques_for_phase(doc, "define")
        assert techniques_result.allowed is True, f"Techniques check failed: {techniques_result.message}"

    def test_full_plan_workflow(self, tmp_path):
        """Vollständiger Plan Workflow."""
        template_criteria = get_template_criteria("plan.md.template")
        criteria_yaml = "\n  - ".join([""] + template_criteria)

        doc = tmp_path / "my-plan.md"
        doc.write_text(f"""---
type: plan
status: draft
criteria:{criteria_yaml}
techniques_applied:
  - decision-matrix
---

# My Plan

This plan uses decision-making techniques.
""")

        # Check criteria
        criteria_result = check_document_criteria(doc)
        assert criteria_result.allowed is True, f"Criteria check failed: {criteria_result.message}"

        # Check techniques for PLAN phase
        techniques_result = check_techniques_for_phase(doc, "plan")
        assert techniques_result.allowed is True, f"Techniques check failed: {techniques_result.message}"
