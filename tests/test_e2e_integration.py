#!/usr/bin/env python3
"""
E2E Integration Tests für STAN Framework.

Testet das Zusammenspiel aller Komponenten:
- Hooks (stan-context, stan-track, stan-gate)
- Skills (/stan init, define, plan, create, etc.)
- Templates und Criteria
- Learnings System
- Document Lifecycle
"""

import json
import os
import sys
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

# Add paths
PROJECT_ROOT = Path(__file__).parent.parent
HOOKS_LIB = PROJECT_ROOT / "hooks" / "autonomous-stan" / "lib"
sys.path.insert(0, str(HOOKS_LIB))


class TestHooksExist:
    """Verifiziere dass alle Hooks existieren und ausführbar sind."""

    def test_stan_context_hook_exists(self):
        """stan_context.py existiert."""
        hook = PROJECT_ROOT / "hooks/autonomous-stan/stan_context.py"
        assert hook.exists(), f"Hook nicht gefunden: {hook}"

    def test_stan_track_hook_exists(self):
        """stan_track.py existiert."""
        hook = PROJECT_ROOT / "hooks/autonomous-stan/stan_track.py"
        assert hook.exists(), f"Hook nicht gefunden: {hook}"

    def test_stan_gate_hook_exists(self):
        """stan_gate.py existiert."""
        hook = PROJECT_ROOT / "hooks/autonomous-stan/stan_gate.py"
        assert hook.exists(), f"Hook nicht gefunden: {hook}"


class TestSkillsExist:
    """Verifiziere dass alle Skills existieren."""

    REQUIRED_SKILLS = [
        "init.md",
        "define.md",
        "plan.md",
        "create.md",
        "statusupdate.md",
        "healthcheck.md",
        "build-template.md",
        "build-criteria.md",
        "think.md",
    ]

    def test_all_skills_exist(self):
        """Alle erforderlichen Skills existieren."""
        skills_dir = PROJECT_ROOT / "commands/autonomous-stan"
        for skill in self.REQUIRED_SKILLS:
            skill_path = skills_dir / skill
            assert skill_path.exists(), f"Skill nicht gefunden: {skill}"


class TestTemplatesExist:
    """Verifiziere dass alle Templates existieren."""

    REQUIRED_TEMPLATES = [
        "stan.md.template",
        "prd.md.template",
        "plan.md.template",
    ]

    def test_all_templates_exist(self):
        """Alle erforderlichen Templates existieren."""
        templates_dir = PROJECT_ROOT / "templates"
        for template in self.REQUIRED_TEMPLATES:
            template_path = templates_dir / template
            assert template_path.exists(), f"Template nicht gefunden: {template}"

    def test_templates_have_status_field(self):
        """Alle Templates haben status Feld im Frontmatter."""
        templates_dir = PROJECT_ROOT / "templates"
        for template in self.REQUIRED_TEMPLATES:
            content = (templates_dir / template).read_text()
            assert "status:" in content, f"Template {template} hat kein status Feld"


class TestCriteriaPrefixes:
    """Verifiziere dass Criteria mit Prefixen existieren (flache Struktur laut Plan)."""

    # Flache Struktur mit Prefixen statt Unterverzeichnissen
    REQUIRED_PREFIXES = ["code-", "text-", "ui-", "meta-"]

    def test_criteria_with_prefixes_exist(self):
        """Für jeden Prefix existiert mindestens ein Criteria."""
        criteria_dir = PROJECT_ROOT / "criteria"
        for prefix in self.REQUIRED_PREFIXES:
            yaml_files = list(criteria_dir.glob(f"{prefix}*.yaml"))
            assert len(yaml_files) > 0, f"Kein Criteria mit Prefix '{prefix}' gefunden"

    def test_minimum_criteria_count(self):
        """Mindestens 15 Criteria existieren insgesamt."""
        criteria_dir = PROJECT_ROOT / "criteria"
        yaml_files = list(criteria_dir.glob("*.yaml"))
        assert len(yaml_files) >= 15, f"Nur {len(yaml_files)} Criteria gefunden"


class TestTechniquesExist:
    """Verifiziere dass Techniken-System funktioniert."""

    def test_techniques_directory_exists(self):
        """techniques/ Verzeichnis existiert."""
        techniques_dir = PROJECT_ROOT / "techniques"
        assert techniques_dir.is_dir()

    def test_purposes_directory_exists(self):
        """techniques/purposes/ existiert."""
        purposes_dir = PROJECT_ROOT / "techniques/purposes"
        assert purposes_dir.is_dir()

    def test_minimum_techniques(self):
        """Mindestens 15 Techniken existieren."""
        techniques_dir = PROJECT_ROOT / "techniques"
        yaml_files = [f for f in techniques_dir.glob("*.yaml") if f.name != "schema.yaml"]
        assert len(yaml_files) >= 15, f"Nur {len(yaml_files)} Techniken gefunden"

    def test_all_purposes_exist(self):
        """Alle 9 Purposes existieren."""
        purposes_dir = PROJECT_ROOT / "techniques/purposes"
        yaml_files = list(purposes_dir.glob("*.yaml"))
        assert len(yaml_files) == 9, f"Erwartet 9 Purposes, gefunden {len(yaml_files)}"


class TestLibModules:
    """Verifiziere dass alle Lib-Module importierbar sind."""

    def test_learnings_module_importable(self):
        """learnings.py ist importierbar."""
        import learnings
        assert hasattr(learnings, 'save_learning')
        assert hasattr(learnings, 'load_learnings')
        assert hasattr(learnings, 'rotate_learnings')

    def test_session_state_module_importable(self):
        """session_state.py ist importierbar."""
        import session_state
        assert hasattr(session_state, 'get')
        assert hasattr(session_state, 'set')

    def test_document_module_importable(self):
        """document.py ist importierbar."""
        import document
        assert hasattr(document, 'get_document_status')
        assert hasattr(document, 'update_document_status')
        assert hasattr(document, 'can_transition')

    def test_techniques_module_importable(self):
        """techniques.py ist importierbar."""
        import techniques
        assert hasattr(techniques, 'list_purposes')
        assert hasattr(techniques, 'get_techniques_for_purpose')


class TestHookBehavior:
    """Teste Hook-Verhalten mit simuliertem Input."""

    def test_stan_context_outputs_valid_json(self):
        """stan_context gibt valides JSON zurück."""
        hook_path = PROJECT_ROOT / "hooks/autonomous-stan/stan_context.py"

        # Simuliere Hook-Input
        input_data = json.dumps({"userMessage": "test"})

        result = subprocess.run(
            ["python3", str(hook_path)],
            input=input_data,
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT)
        )

        # Sollte valides JSON ausgeben
        output = json.loads(result.stdout)
        assert "continue" in output
        assert output["continue"] is True

    def test_stan_gate_allows_non_commit(self):
        """stan_gate erlaubt Nicht-Commit Befehle."""
        hook_path = PROJECT_ROOT / "hooks/autonomous-stan/stan_gate.py"

        # Simuliere Nicht-Commit Befehl
        input_data = json.dumps({
            "tool_name": "Bash",
            "tool_input": {"command": "ls -la"}
        })

        result = subprocess.run(
            ["python3", str(hook_path)],
            input=input_data,
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT)
        )

        output = json.loads(result.stdout)
        assert output["continue"] is True

    def test_stan_track_outputs_valid_json(self):
        """stan_track gibt valides JSON zurück."""
        hook_path = PROJECT_ROOT / "hooks/autonomous-stan/stan_track.py"

        # Simuliere Tool-Output
        input_data = json.dumps({
            "tool_name": "Bash",
            "tool_input": {"command": "echo test"},
            "tool_result": {"stdout": "test", "exit_code": 0}
        })

        result = subprocess.run(
            ["python3", str(hook_path)],
            input=input_data,
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT)
        )

        output = json.loads(result.stdout)
        assert "continue" in output


class TestDocumentLifecycleIntegration:
    """Teste Document Lifecycle Integration."""

    def test_valid_statuses_defined(self):
        """5 gültige Status sind definiert."""
        import document
        assert len(document.VALID_STATUSES) == 5
        assert "draft" in document.VALID_STATUSES
        assert "completed" in document.VALID_STATUSES

    def test_transition_rules_defined(self):
        """Transition-Regeln sind definiert."""
        import document
        assert len(document.ALLOWED_TRANSITIONS) == 5
        assert "draft" in document.ALLOWED_TRANSITIONS


class TestLearningsIntegration:
    """Teste Learnings System Integration."""

    def test_tiered_storage_configured(self):
        """Tiered Storage ist konfiguriert."""
        import learnings
        assert learnings.MAX_RECENT == 50
        assert learnings.MAX_HOT == 20
        assert learnings.PROMOTE_THRESHOLD == 3
        assert learnings.DECAY_DAYS == 14

    def test_learnings_dir_path(self):
        """Learnings Directory Path ist korrekt."""
        import learnings
        assert str(learnings.LEARNINGS_DIR).endswith(".stan/learnings")


class TestOverallStats:
    """Gesamtstatistiken für das Framework."""

    def test_total_criteria_count(self):
        """Framework hat ausreichend Criteria."""
        criteria_dir = PROJECT_ROOT / "criteria"
        yaml_files = list(criteria_dir.rglob("*.yaml"))
        assert len(yaml_files) >= 20, f"Nur {len(yaml_files)} Criteria gefunden"

    def test_total_techniques_count(self):
        """Framework hat ausreichend Techniken."""
        techniques_dir = PROJECT_ROOT / "techniques"
        yaml_files = [f for f in techniques_dir.glob("*.yaml") if f.name != "schema.yaml"]
        assert len(yaml_files) >= 15, f"Nur {len(yaml_files)} Techniken gefunden"

    def test_total_skills_count(self):
        """Framework hat ausreichend Skills."""
        skills_dir = PROJECT_ROOT / "commands/autonomous-stan"
        skill_files = list(skills_dir.glob("*.md"))
        assert len(skill_files) >= 9, f"Nur {len(skill_files)} Skills gefunden"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
