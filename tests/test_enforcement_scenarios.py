#!/usr/bin/env python3
"""
Fachliche Szenarien-Tests für STAN Enforcement.

Diese Tests prüfen die Enforcement-Logik mit realen Dokumenten
und echten Szenarien - nicht nur technische Unit Tests.

Test-Philosophie:
- Jeder Test = Ein konkretes Nutzungsszenario
- Echte Dateien statt nur Mocks
- Verständliche Namen die das Szenario beschreiben
- AAA Pattern: Arrange, Act, Assert
"""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from stan.lib.frontmatter import (
    parse_frontmatter,
    get_document_type,
    get_document_criteria,
    get_techniques_applied,
    is_archived,
)
from stan.lib.criteria import (
    get_template_criteria,
    check_criteria_not_removed,
    set_project_root,
)
from stan.lib.enforcement import (
    check_document_criteria,
    check_techniques_for_phase,
    check_phase_transition,
    PHASE_PURPOSES,
)
from stan.lib.techniques import (
    get_technique,
    get_purposes_for_technique,
    set_project_root as set_techniques_root,
)

# Set project root for real file access
PROJECT_ROOT = Path(__file__).parent.parent
set_project_root(PROJECT_ROOT)
set_techniques_root(PROJECT_ROOT)


class TestScenario_PRD_Erstellung:
    """
    Szenario: User erstellt ein PRD im DEFINE Phase.

    Erwartung:
    - PRD muss alle Template-Criteria haben
    - PRD muss Technique für DEFINE Phase haben (big-picture oder ideation)
    - Ohne Techniques → BLOCKED
    - Mit falschen Techniques → BLOCKED
    """

    def test_prd_ohne_criteria_wird_abgelehnt(self, tmp_path):
        """Ein PRD ohne Criteria wird abgelehnt."""
        # Arrange: PRD ohne criteria Liste
        prd = tmp_path / "prd.md"
        prd.write_text("""---
type: prd
status: draft
---

# Mein Feature
""")

        # Act
        result = check_document_criteria(prd)

        # Assert
        assert result.allowed is False
        assert "removed" in result.message.lower() or "missing" in result.message.lower()

    def test_prd_mit_allen_criteria_wird_akzeptiert(self, tmp_path):
        """Ein PRD mit allen Template-Criteria wird akzeptiert."""
        # Arrange: Hole echte Template-Criteria
        template_criteria = get_template_criteria("prd.md.template")
        criteria_yaml = "\n  - ".join([""] + template_criteria)

        prd = tmp_path / "prd.md"
        prd.write_text(f"""---
type: prd
status: draft
criteria:{criteria_yaml}
---

# Mein Feature
""")

        # Act
        result = check_document_criteria(prd)

        # Assert
        assert result.allowed is True, f"Sollte erlaubt sein: {result.message}"

    def test_prd_mit_zusaetzlichen_criteria_wird_akzeptiert(self, tmp_path):
        """Ein PRD kann MEHR Criteria haben als das Template."""
        # Arrange
        template_criteria = get_template_criteria("prd.md.template")
        extra_criteria = template_criteria + ["custom-criteria", "another-custom"]
        criteria_yaml = "\n  - ".join([""] + extra_criteria)

        prd = tmp_path / "prd.md"
        prd.write_text(f"""---
type: prd
status: draft
criteria:{criteria_yaml}
---

# Mein Feature
""")

        # Act
        result = check_document_criteria(prd)

        # Assert
        assert result.allowed is True, "Zusätzliche Criteria sollten erlaubt sein"

    def test_prd_mit_entfernten_criteria_wird_abgelehnt(self, tmp_path):
        """Ein PRD mit entfernten Template-Criteria wird BLOCKIERT."""
        # Arrange: Nur ein Criterion, aber Template hat mehr
        prd = tmp_path / "prd.md"
        prd.write_text("""---
type: prd
status: draft
criteria:
  - goal-is-smart
---

# Mein Feature
""")

        # Act
        result = check_document_criteria(prd)

        # Assert
        assert result.allowed is False
        assert result.details is not None
        assert "missing" in result.details or len(result.details.get("missing", [])) > 0


class TestScenario_Techniques_In_Phasen:
    """
    Szenario: User arbeitet in verschiedenen Phasen.

    Erwartung:
    - DEFINE Phase braucht big-picture ODER ideation Techniques
    - PLAN Phase braucht structured-problem-solving ODER decision-making
    - CREATE Phase braucht code-review
    """

    def test_define_phase_ohne_techniques_wird_abgelehnt(self, tmp_path):
        """DEFINE Phase ohne techniques_applied wird abgelehnt."""
        # Arrange
        doc = tmp_path / "doc.md"
        doc.write_text("""---
type: prd
status: draft
---

# Ohne Techniques
""")

        # Act
        result = check_techniques_for_phase(doc, "define")

        # Assert
        assert result.allowed is False
        assert "techniques_applied" in result.message.lower()

    def test_define_phase_mit_mind_mapping_wird_akzeptiert(self, tmp_path):
        """DEFINE Phase mit mind-mapping (hat ideation) wird akzeptiert."""
        # Arrange: Verifiziere dass mind-mapping 'ideation' hat
        tech = get_technique("mind-mapping")
        assert tech is not None, "mind-mapping Technique muss existieren"
        assert "ideation" in tech.get("purposes", []), "mind-mapping muss ideation Purpose haben"

        doc = tmp_path / "doc.md"
        doc.write_text("""---
type: prd
status: draft
techniques_applied:
  - mind-mapping
---

# Mit Mind-Mapping
""")

        # Act
        result = check_techniques_for_phase(doc, "define")

        # Assert
        assert result.allowed is True, f"Sollte erlaubt sein: {result.message}"

    def test_plan_phase_mit_decision_matrix_wird_akzeptiert(self, tmp_path):
        """PLAN Phase mit decision-matrix (hat decision-making) wird akzeptiert."""
        # Arrange: Verifiziere dass decision-matrix 'decision-making' hat
        tech = get_technique("decision-matrix")
        assert tech is not None, "decision-matrix Technique muss existieren"
        assert "decision-making" in tech.get("purposes", []), "decision-matrix muss decision-making Purpose haben"

        doc = tmp_path / "doc.md"
        doc.write_text("""---
type: plan
status: draft
techniques_applied:
  - decision-matrix
---

# Mit Decision Matrix
""")

        # Act
        result = check_techniques_for_phase(doc, "plan")

        # Assert
        assert result.allowed is True, f"Sollte erlaubt sein: {result.message}"

    def test_create_phase_mit_five_whys_wird_akzeptiert(self, tmp_path):
        """CREATE Phase mit five-whys (hat code-review) wird akzeptiert."""
        # Arrange: Verifiziere dass five-whys 'code-review' hat
        tech = get_technique("five-whys")
        assert tech is not None, "five-whys Technique muss existieren"
        assert "code-review" in tech.get("purposes", []), "five-whys muss code-review Purpose haben"

        doc = tmp_path / "doc.md"
        doc.write_text("""---
type: plan
status: draft
techniques_applied:
  - five-whys
---

# Mit Five Whys
""")

        # Act
        result = check_techniques_for_phase(doc, "create")

        # Assert
        assert result.allowed is True, f"Sollte erlaubt sein: {result.message}"

    def test_falsche_technique_fuer_phase_wird_abgelehnt(self, tmp_path):
        """Eine Technique die nicht zur Phase passt wird abgelehnt."""
        # Arrange: dot-voting hat decision-making, nicht code-review
        tech = get_technique("dot-voting")
        if tech and "code-review" not in tech.get("purposes", []):
            doc = tmp_path / "doc.md"
            doc.write_text("""---
type: plan
status: draft
techniques_applied:
  - dot-voting
---

# Mit Dot Voting
""")

            # Act
            result = check_techniques_for_phase(doc, "create")

            # Assert: CREATE braucht code-review, dot-voting hat das nicht
            assert result.allowed is False, "dot-voting sollte für CREATE nicht reichen"


class TestScenario_Archivierte_Dokumente:
    """
    Szenario: Archivierte Dokumente werden ignoriert.

    Erwartung:
    - status: archived → keine Enforcement
    - Egal welche Criteria fehlen
    - Egal welche Techniques fehlen
    """

    def test_archiviertes_dokument_wird_uebersprungen(self, tmp_path):
        """Ein archiviertes Dokument wird bei Criteria-Check übersprungen."""
        # Arrange: Dokument mit status: archived aber ohne Criteria
        doc = tmp_path / "old.md"
        doc.write_text("""---
type: prd
status: archived
---

# Altes Dokument ohne Criteria
""")

        # Act
        result = check_document_criteria(doc)

        # Assert
        assert result.allowed is True
        assert "archived" in result.message.lower()

    def test_archiviertes_dokument_braucht_keine_techniques(self, tmp_path):
        """Ein archiviertes Dokument braucht keine techniques_applied."""
        # Arrange
        doc = tmp_path / "old.md"
        doc.write_text("""---
type: prd
status: archived
---

# Altes Dokument
""")

        # Act
        result = check_techniques_for_phase(doc, "define")

        # Assert
        assert result.allowed is True
        assert "archived" in result.message.lower()


class TestScenario_Phasen_Uebergaenge:
    """
    Szenario: User wechselt zwischen Phasen.

    Erwartung:
    - DEFINE → PLAN: erlaubt
    - PLAN → CREATE: erlaubt
    - CREATE → DEFINE: erlaubt (Reconciliation)
    - DEFINE → CREATE: VERBOTEN (muss durch PLAN)
    """

    def test_define_zu_plan_ist_erlaubt(self):
        """Übergang DEFINE → PLAN ist erlaubt."""
        result = check_phase_transition("define", "plan")
        assert result.allowed is True

    def test_plan_zu_create_ist_erlaubt(self):
        """Übergang PLAN → CREATE ist erlaubt."""
        result = check_phase_transition("plan", "create")
        assert result.allowed is True

    def test_create_zu_define_ist_erlaubt_reconciliation(self):
        """Übergang CREATE → DEFINE ist erlaubt (Reconciliation)."""
        result = check_phase_transition("create", "define")
        assert result.allowed is True

    def test_define_direkt_zu_create_ist_verboten(self):
        """Übergang DEFINE → CREATE ist VERBOTEN."""
        result = check_phase_transition("define", "create")
        assert result.allowed is False
        assert "invalid" in result.message.lower()

    def test_create_zu_plan_ist_verboten(self):
        """Übergang CREATE → PLAN ist VERBOTEN."""
        result = check_phase_transition("create", "plan")
        assert result.allowed is False


class TestScenario_Edge_Cases:
    """
    Edge Cases und Grenzfälle.
    """

    def test_dokument_ohne_type_wird_abgelehnt(self, tmp_path):
        """Ein Dokument ohne type im Frontmatter wird abgelehnt."""
        doc = tmp_path / "notype.md"
        doc.write_text("""---
status: draft
criteria:
  - text-quality
---

# Kein Type
""")

        result = check_document_criteria(doc)
        assert result.allowed is False
        assert "type" in result.message.lower()

    def test_nicht_existierendes_dokument(self, tmp_path):
        """Ein nicht-existierendes Dokument gibt Fehler."""
        result = check_document_criteria(tmp_path / "gibts-nicht.md")
        assert result.allowed is False
        assert "not found" in result.message.lower()

    def test_leeres_frontmatter(self, tmp_path):
        """Ein Dokument mit leerem Frontmatter wird abgelehnt."""
        doc = tmp_path / "empty.md"
        doc.write_text("""---
---

# Leeres Frontmatter
""")

        result = check_document_criteria(doc)
        assert result.allowed is False

    def test_dokument_ohne_frontmatter(self, tmp_path):
        """Ein Dokument ohne Frontmatter wird abgelehnt."""
        doc = tmp_path / "nofm.md"
        doc.write_text("""# Kein Frontmatter

Nur Text.
""")

        result = check_document_criteria(doc)
        assert result.allowed is False

    def test_unbekannter_document_type(self, tmp_path):
        """Ein Dokument mit unbekanntem Type wird abgelehnt."""
        doc = tmp_path / "unknown.md"
        doc.write_text("""---
type: unbekannter-typ
status: draft
criteria:
  - text-quality
---

# Unbekannter Typ
""")

        result = check_document_criteria(doc)
        assert result.allowed is False
        assert "template" in result.message.lower()


class TestScenario_Echte_Templates:
    """
    Tests mit den echten Templates aus dem Projekt.

    Diese Tests validieren, dass die echten Templates
    korrekt konfiguriert sind.
    """

    def test_prd_template_hat_criteria(self):
        """Das PRD Template hat Criteria definiert."""
        criteria = get_template_criteria("prd.md.template")
        assert len(criteria) > 0, "PRD Template sollte Criteria haben"
        assert "goal-is-smart" in criteria, "PRD sollte goal-is-smart haben"

    def test_plan_template_hat_criteria(self):
        """Das Plan Template hat Criteria definiert."""
        criteria = get_template_criteria("plan.md.template")
        assert len(criteria) > 0, "Plan Template sollte Criteria haben"

    def test_alle_template_criteria_existieren(self):
        """Alle im Template referenzierten Criteria existieren als YAML."""
        from stan.lib.criteria import load_criteria

        for template_name in ["prd.md.template", "plan.md.template"]:
            criteria = get_template_criteria(template_name)
            for criterion in criteria:
                loaded = load_criteria(criterion)
                assert loaded is not None, f"Criterion '{criterion}' aus {template_name} existiert nicht"


class TestScenario_Echte_Techniques:
    """
    Tests mit den echten Techniques aus dem Projekt.
    """

    def test_phase_purposes_haben_passende_techniques(self):
        """Für jeden Phase-Purpose gibt es mindestens eine Technique."""
        from stan.lib.techniques import list_techniques

        all_techniques = list_techniques()

        for phase, required_purposes in PHASE_PURPOSES.items():
            for purpose in required_purposes:
                # Finde Techniques die diesen Purpose erfüllen
                matching = []
                for tech_id in all_techniques:
                    tech = get_technique(tech_id)
                    if tech and purpose in tech.get("purposes", []):
                        matching.append(tech_id)

                assert len(matching) > 0, \
                    f"Phase '{phase}' braucht Purpose '{purpose}', aber keine Technique hat diesen Purpose"

    def test_five_whys_hat_erwartete_purposes(self):
        """five-whys hat die dokumentierten Purposes."""
        tech = get_technique("five-whys")
        assert tech is not None
        purposes = tech.get("purposes", [])

        # Laut techniques/five-whys.yaml
        assert "root-cause-analysis" in purposes
        assert "code-review" in purposes

    def test_mind_mapping_hat_ideation(self):
        """mind-mapping hat ideation Purpose (wichtig für DEFINE)."""
        tech = get_technique("mind-mapping")
        assert tech is not None
        assert "ideation" in tech.get("purposes", [])
