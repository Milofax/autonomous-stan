#!/usr/bin/env python3
"""Tests für Criteria YAML Validierung und Template Frontmatter."""

import yaml
import pytest
from pathlib import Path

CRITERIA_DIR = Path(__file__).parent.parent / "criteria"
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def load_yaml(path: Path) -> dict:
    """Lade YAML-Datei."""
    with open(path, "r") as f:
        return yaml.safe_load(f)


def load_template_frontmatter(path: Path) -> dict:
    """Extrahiere Frontmatter aus Template."""
    content = path.read_text()
    if not content.startswith("---"):
        return {}

    # Find end of frontmatter
    end = content.find("---", 3)
    if end == -1:
        return {}

    frontmatter = content[3:end].strip()
    return yaml.safe_load(frontmatter)


class TestCriteriaStructure:
    """Tests für Criteria Verzeichnis-Struktur."""

    def test_criteria_directory_exists(self):
        """criteria/ Verzeichnis existiert."""
        assert CRITERIA_DIR.exists()
        assert CRITERIA_DIR.is_dir()

    def test_has_subdirectories(self):
        """criteria/ hat Unterverzeichnisse (code, text, strategy)."""
        subdirs = [d.name for d in CRITERIA_DIR.iterdir() if d.is_dir()]
        assert "code" in subdirs
        assert "text" in subdirs
        assert "strategy" in subdirs

    def test_all_files_are_yaml(self):
        """Alle Dateien in criteria/ sind YAML."""
        for yaml_file in CRITERIA_DIR.rglob("*.yaml"):
            assert yaml_file.suffix == ".yaml"
            # Verify it's valid YAML
            try:
                load_yaml(yaml_file)
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in {yaml_file}: {e}")


class TestCriteriaSchema:
    """Tests für Criteria YAML Schema."""

    @pytest.fixture
    def all_criteria_files(self):
        """Alle Criteria YAML-Dateien."""
        return list(CRITERIA_DIR.rglob("*.yaml"))

    def test_all_criteria_have_name(self, all_criteria_files):
        """Alle Criteria haben ein 'name' Feld."""
        for yaml_file in all_criteria_files:
            data = load_yaml(yaml_file)
            assert "name" in data, f"{yaml_file} missing 'name'"
            assert isinstance(data["name"], str)
            assert len(data["name"]) > 0

    def test_all_criteria_have_description(self, all_criteria_files):
        """Alle Criteria haben ein 'description' Feld."""
        for yaml_file in all_criteria_files:
            data = load_yaml(yaml_file)
            assert "description" in data, f"{yaml_file} missing 'description'"
            assert isinstance(data["description"], str)

    def test_all_criteria_have_checks(self, all_criteria_files):
        """Alle Criteria haben ein 'checks' Array."""
        for yaml_file in all_criteria_files:
            data = load_yaml(yaml_file)
            assert "checks" in data, f"{yaml_file} missing 'checks'"
            assert isinstance(data["checks"], list)
            assert len(data["checks"]) > 0, f"{yaml_file} has empty checks"

    def test_checks_have_required_fields(self, all_criteria_files):
        """Alle Checks haben id, question, required."""
        for yaml_file in all_criteria_files:
            data = load_yaml(yaml_file)
            for i, check in enumerate(data["checks"]):
                assert "id" in check, f"{yaml_file} check {i} missing 'id'"
                assert "question" in check, f"{yaml_file} check {i} missing 'question'"
                assert "required" in check, f"{yaml_file} check {i} missing 'required'"

    def test_check_ids_are_unique_within_file(self, all_criteria_files):
        """Check IDs sind innerhalb einer Datei eindeutig."""
        for yaml_file in all_criteria_files:
            data = load_yaml(yaml_file)
            ids = [check["id"] for check in data["checks"]]
            assert len(ids) == len(set(ids)), f"{yaml_file} has duplicate check IDs"

    def test_auto_checks_have_commands(self, all_criteria_files):
        """Auto-Checks haben 'commands' oder 'command' Feld."""
        for yaml_file in all_criteria_files:
            data = load_yaml(yaml_file)
            for check in data["checks"]:
                if check.get("auto"):
                    has_command = "command" in check or "commands" in check
                    assert has_command, f"{yaml_file} check '{check['id']}' is auto but has no command"


class TestSpecificCriteria:
    """Tests für spezifische Criteria-Dateien."""

    def test_tests_criteria_has_test_commands(self):
        """code/tests.yaml hat Test-Commands."""
        tests_yaml = CRITERIA_DIR / "code" / "tests.yaml"
        data = load_yaml(tests_yaml)

        # Find auto check
        auto_checks = [c for c in data["checks"] if c.get("auto")]
        assert len(auto_checks) > 0, "tests.yaml should have auto checks"

        # Verify commands exist
        for check in auto_checks:
            commands = check.get("commands", [])
            assert len(commands) > 0, f"Check {check['id']} has no commands"

    def test_goal_quality_checks_smart_criteria(self):
        """strategy/goal-quality.yaml prüft SMART Kriterien."""
        goal_yaml = CRITERIA_DIR / "strategy" / "goal-quality.yaml"
        data = load_yaml(goal_yaml)

        check_ids = [c["id"] for c in data["checks"]]

        # SMART: Specific, Measurable, Achievable, Relevant, Time-bound
        assert "concrete" in check_ids or "specific" in check_ids
        assert "measurable" in check_ids


class TestTemplatesStructure:
    """Tests für Template Verzeichnis-Struktur."""

    def test_templates_directory_exists(self):
        """templates/ Verzeichnis existiert."""
        assert TEMPLATES_DIR.exists()
        assert TEMPLATES_DIR.is_dir()

    def test_has_required_templates(self):
        """Alle erforderlichen Templates existieren."""
        required = ["stan.md.template", "prd.md.template", "plan.md.template"]
        existing = [f.name for f in TEMPLATES_DIR.iterdir()]

        for template in required:
            assert template in existing, f"Missing required template: {template}"


class TestTemplateFrontmatter:
    """Tests für Template Frontmatter."""

    @pytest.fixture
    def all_template_files(self):
        """Alle Template-Dateien."""
        return list(TEMPLATES_DIR.glob("*.template"))

    def test_all_templates_have_frontmatter(self, all_template_files):
        """Alle Templates haben Frontmatter."""
        for template in all_template_files:
            content = template.read_text()
            assert content.startswith("---"), f"{template} missing frontmatter"

    def test_all_templates_have_type(self, all_template_files):
        """Alle Templates haben 'type' im Frontmatter."""
        for template in all_template_files:
            fm = load_template_frontmatter(template)
            assert "type" in fm, f"{template} missing 'type' in frontmatter"

    def test_all_templates_have_criteria_list(self, all_template_files):
        """Alle Templates haben 'criteria' Liste im Frontmatter."""
        for template in all_template_files:
            fm = load_template_frontmatter(template)
            assert "criteria" in fm, f"{template} missing 'criteria' in frontmatter"
            assert isinstance(fm["criteria"], list)


class TestTemplateCriteriaLinks:
    """Tests für Verknüpfung zwischen Templates und Criteria."""

    def test_template_criteria_exist(self):
        """Alle in Templates referenzierten Criteria existieren."""
        # Collect all existing criteria names
        existing_criteria = set()
        for yaml_file in CRITERIA_DIR.rglob("*.yaml"):
            # Use filename without extension as criteria name
            existing_criteria.add(yaml_file.stem)

        # Check each template
        for template in TEMPLATES_DIR.glob("*.template"):
            fm = load_template_frontmatter(template)
            criteria_list = fm.get("criteria", [])

            for criteria_name in criteria_list:
                assert criteria_name in existing_criteria, \
                    f"{template} references non-existent criteria: {criteria_name}"

    def test_no_orphan_criteria(self):
        """Warnung wenn Criteria von keinem Template referenziert wird."""
        # Collect all referenced criteria
        referenced = set()
        for template in TEMPLATES_DIR.glob("*.template"):
            fm = load_template_frontmatter(template)
            referenced.update(fm.get("criteria", []))

        # Collect all existing criteria
        existing = set()
        for yaml_file in CRITERIA_DIR.rglob("*.yaml"):
            existing.add(yaml_file.stem)

        orphans = existing - referenced
        # This is a warning, not a failure (some criteria might be standalone)
        if orphans:
            print(f"Note: Orphan criteria (not linked to any template): {orphans}")


class TestCriteriaContent:
    """Tests für inhaltliche Qualität der Criteria."""

    def test_questions_end_with_question_mark(self):
        """Fragen enden mit Fragezeichen."""
        for yaml_file in CRITERIA_DIR.rglob("*.yaml"):
            data = load_yaml(yaml_file)
            for check in data["checks"]:
                question = check["question"]
                assert question.endswith("?"), \
                    f"{yaml_file} check '{check['id']}' question doesn't end with '?'"

    def test_questions_are_yes_no_answerable(self):
        """Fragen sollten mit Ja/Nein beantwortbar sein."""
        # This is a heuristic check - questions should typically start with
        # "Ist", "Sind", "Hat", "Haben", "Gibt", "Wurde" etc.
        german_question_starters = [
            "ist", "sind", "hat", "haben", "gibt", "wurde", "wurden",
            "kann", "können", "wird", "werden", "existier", "läuft", "laufen"
        ]
        english_question_starters = [
            "is", "are", "has", "have", "does", "do", "can", "will", "was", "were"
        ]
        valid_starters = german_question_starters + english_question_starters

        for yaml_file in CRITERIA_DIR.rglob("*.yaml"):
            data = load_yaml(yaml_file)
            for check in data["checks"]:
                question = check["question"].lower()
                # Remove leading quote if present
                if question.startswith('"'):
                    question = question[1:]

                starts_valid = any(question.startswith(s) for s in valid_starters)
                if not starts_valid:
                    print(f"Warning: {yaml_file} check '{check['id']}' may not be yes/no: {check['question']}")
