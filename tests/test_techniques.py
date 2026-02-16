#!/usr/bin/env python3
"""Tests für Techniques und Purposes YAML Validierung."""

import yaml
import pytest
from pathlib import Path
import sys

# Add lib to path for techniques module
LIB_DIR = Path(__file__).parent.parent / "hooks" / "autonomous-stan" / "lib"
sys.path.insert(0, str(LIB_DIR))

from techniques import (
    list_purposes,
    list_techniques,
    get_purpose,
    get_technique,
    get_techniques_for_purpose,
    get_techniques_dir,
    get_purposes_dir,
)

TECHNIQUES_DIR = Path(__file__).parent.parent / "techniques"
PURPOSES_DIR = TECHNIQUES_DIR / "purposes"


def load_yaml(path: Path) -> dict:
    """Lade YAML-Datei."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class TestTechniquesDirectory:
    """Tests für Techniques Verzeichnis-Struktur."""

    def test_techniques_directory_exists(self):
        """techniques/ Verzeichnis existiert."""
        assert TECHNIQUES_DIR.exists()
        assert TECHNIQUES_DIR.is_dir()

    def test_purposes_directory_exists(self):
        """techniques/purposes/ Verzeichnis existiert."""
        assert PURPOSES_DIR.exists()
        assert PURPOSES_DIR.is_dir()

    def test_schema_exists(self):
        """techniques/schema.yaml existiert."""
        schema = TECHNIQUES_DIR / "schema.yaml"
        assert schema.exists()

    def test_has_minimum_techniques(self):
        """Mindestens 20 Techniken existieren."""
        technique_files = [
            f for f in TECHNIQUES_DIR.glob("*.yaml")
            if f.name != "schema.yaml"
        ]
        assert len(technique_files) >= 20, \
            f"Nur {len(technique_files)} Techniken gefunden, mindestens 20 erwartet"

    def test_has_all_purposes(self):
        """All 9 purposes exist."""
        expected_purposes = [
            "root-cause-analysis",
            "ideation",
            "perspective-shift",
            "structured-problem-solving",
            "code-review",
            "big-picture",
            "self-reflection",
            "teamwork",
            "decision-making",
        ]

        existing = [f.stem for f in PURPOSES_DIR.glob("*.yaml")]

        for purpose in expected_purposes:
            assert purpose in existing, f"Purpose '{purpose}' missing"


class TestTechniqueSchema:
    """Tests für Technique YAML Schema."""

    @pytest.fixture
    def all_technique_files(self):
        """Alle Technique YAML-Dateien."""
        return [
            f for f in TECHNIQUES_DIR.glob("*.yaml")
            if f.name != "schema.yaml"
        ]

    def test_all_techniques_have_id(self, all_technique_files):
        """Alle Techniken haben ein 'id' Feld."""
        for yaml_file in all_technique_files:
            data = load_yaml(yaml_file)
            assert "id" in data, f"{yaml_file} missing 'id'"
            assert data["id"] == yaml_file.stem, \
                f"{yaml_file} id '{data['id']}' doesn't match filename"

    def test_all_techniques_have_name(self, all_technique_files):
        """Alle Techniken haben ein 'name' Feld."""
        for yaml_file in all_technique_files:
            data = load_yaml(yaml_file)
            assert "name" in data, f"{yaml_file} missing 'name'"
            assert isinstance(data["name"], str)
            assert len(data["name"]) > 0

    def test_all_techniques_have_description(self, all_technique_files):
        """Alle Techniken haben ein 'description' Feld."""
        for yaml_file in all_technique_files:
            data = load_yaml(yaml_file)
            assert "description" in data, f"{yaml_file} missing 'description'"
            assert isinstance(data["description"], str)

    def test_all_techniques_have_steps(self, all_technique_files):
        """Alle Techniken haben ein 'steps' Array."""
        for yaml_file in all_technique_files:
            data = load_yaml(yaml_file)
            assert "steps" in data, f"{yaml_file} missing 'steps'"
            assert isinstance(data["steps"], list)
            assert len(data["steps"]) >= 2, \
                f"{yaml_file} should have at least 2 steps"

    def test_all_techniques_have_purposes(self, all_technique_files):
        """Alle Techniken haben ein 'purposes' Array mit gültigen Referenzen."""
        valid_purposes = [f.stem for f in PURPOSES_DIR.glob("*.yaml")]

        for yaml_file in all_technique_files:
            data = load_yaml(yaml_file)
            assert "purposes" in data, f"{yaml_file} missing 'purposes'"
            assert isinstance(data["purposes"], list)
            assert len(data["purposes"]) >= 1, \
                f"{yaml_file} should have at least 1 purpose"

            for purpose in data["purposes"]:
                assert purpose in valid_purposes, \
                    f"{yaml_file} references invalid purpose: {purpose}"


class TestPurposeSchema:
    """Tests für Purpose YAML Schema."""

    @pytest.fixture
    def all_purpose_files(self):
        """Alle Purpose YAML-Dateien."""
        return list(PURPOSES_DIR.glob("*.yaml"))

    def test_all_purposes_have_id(self, all_purpose_files):
        """Alle Zwecke haben ein 'id' Feld."""
        for yaml_file in all_purpose_files:
            data = load_yaml(yaml_file)
            assert "id" in data, f"{yaml_file} missing 'id'"
            assert data["id"] == yaml_file.stem, \
                f"{yaml_file} id '{data['id']}' doesn't match filename"

    def test_all_purposes_have_name(self, all_purpose_files):
        """Alle Zwecke haben ein 'name' Feld."""
        for yaml_file in all_purpose_files:
            data = load_yaml(yaml_file)
            assert "name" in data, f"{yaml_file} missing 'name'"
            assert isinstance(data["name"], str)

    def test_all_purposes_have_question(self, all_purpose_files):
        """Alle Zwecke haben ein 'question' Feld."""
        for yaml_file in all_purpose_files:
            data = load_yaml(yaml_file)
            assert "question" in data, f"{yaml_file} missing 'question'"
            assert data["question"].endswith("?"), \
                f"{yaml_file} question should end with '?'"

    def test_all_purposes_have_techniques(self, all_purpose_files):
        """Alle Zwecke haben ein 'techniques' Array."""
        existing_techniques = [
            f.stem for f in TECHNIQUES_DIR.glob("*.yaml")
            if f.name != "schema.yaml"
        ]

        for yaml_file in all_purpose_files:
            data = load_yaml(yaml_file)
            assert "techniques" in data, f"{yaml_file} missing 'techniques'"
            assert isinstance(data["techniques"], list)
            assert len(data["techniques"]) >= 2, \
                f"{yaml_file} should have at least 2 techniques"

            for tech in data["techniques"]:
                assert tech in existing_techniques, \
                    f"{yaml_file} references non-existent technique: {tech}"

    def test_all_purposes_have_recommendation(self, all_purpose_files):
        """Alle Zwecke haben eine Empfehlung."""
        for yaml_file in all_purpose_files:
            data = load_yaml(yaml_file)
            assert "recommended_start" in data, \
                f"{yaml_file} missing 'recommended_start'"
            assert "recommended_start_reason" in data, \
                f"{yaml_file} missing 'recommended_start_reason'"


class TestTechniquesLoader:
    """Tests für die techniques.py Loader-Library."""

    def test_list_purposes_returns_all(self):
        """list_purposes() gibt alle 9 Zwecke zurück."""
        purposes = list_purposes()
        assert len(purposes) == 9

    def test_list_techniques_returns_minimum(self):
        """list_techniques() gibt mindestens 20 Techniken zurück."""
        techniques = list_techniques()
        assert len(techniques) >= 20

    def test_get_purpose_returns_data(self):
        """get_purpose() returns purpose data."""
        purpose = get_purpose("root-cause-analysis")
        assert purpose is not None
        assert purpose["id"] == "root-cause-analysis"
        assert "techniques" in purpose

    def test_get_purpose_invalid_returns_none(self):
        """get_purpose() gibt None für ungültigen Zweck."""
        purpose = get_purpose("nicht-existent")
        assert purpose is None

    def test_get_technique_returns_data(self):
        """get_technique() gibt Technik-Daten zurück."""
        tech = get_technique("five-whys")
        assert tech is not None
        assert tech["id"] == "five-whys"
        assert "steps" in tech

    def test_get_technique_invalid_returns_none(self):
        """get_technique() gibt None für ungültige Technik."""
        tech = get_technique("nicht-existent")
        assert tech is None

    def test_get_techniques_for_purpose(self):
        """get_techniques_for_purpose() returns techniques for purpose."""
        techniques = get_techniques_for_purpose("root-cause-analysis")
        assert len(techniques) >= 2

        # Check structure
        for tech in techniques:
            assert "id" in tech
            assert "name" in tech
            assert "description" in tech


class TestNtoMRelationship:
    """Tests für n:m Beziehung zwischen Techniken und Zwecken."""

    def test_technique_in_multiple_purposes(self):
        """A technique can be in multiple purposes."""
        # Five Whys should be in root-cause-analysis AND self-reflection
        tech = get_technique("five-whys")
        assert tech is not None
        assert "root-cause-analysis" in tech["purposes"]
        assert "self-reflection" in tech["purposes"]

    def test_purpose_has_multiple_techniques(self):
        """A purpose has multiple techniques."""
        purpose = get_purpose("decision-making")
        assert purpose is not None
        assert len(purpose["techniques"]) >= 3

    def test_bidirectional_consistency(self):
        """Bidirektionale Konsistenz: Technik→Purpose und Purpose→Technik."""
        # Für jeden Purpose: Prüfe dass alle Techniken diesen Purpose referenzieren
        for purpose_file in PURPOSES_DIR.glob("*.yaml"):
            purpose_data = load_yaml(purpose_file)
            purpose_id = purpose_data["id"]

            for tech_id in purpose_data["techniques"]:
                tech = get_technique(tech_id)
                assert tech is not None, f"Technique {tech_id} not found"
                assert purpose_id in tech["purposes"], \
                    f"Technique {tech_id} doesn't reference purpose {purpose_id}"


class TestAllPurposesCovered:
    """Tests dass alle Zwecke durch Techniken abgedeckt sind."""

    def test_every_purpose_has_techniques(self):
        """Jeder Zweck hat mindestens 2 Techniken."""
        for purpose_file in PURPOSES_DIR.glob("*.yaml"):
            purpose = load_yaml(purpose_file)
            techniques = get_techniques_for_purpose(purpose["id"])
            assert len(techniques) >= 2, \
                f"Purpose '{purpose['id']}' has fewer than 2 techniques"

    def test_no_orphan_techniques(self):
        """Warnung wenn Technik keinem Zweck zugeordnet ist."""
        # Collect all techniques referenced by purposes
        referenced = set()
        for purpose_file in PURPOSES_DIR.glob("*.yaml"):
            purpose = load_yaml(purpose_file)
            referenced.update(purpose.get("techniques", []))

        # Check each technique
        for tech_file in TECHNIQUES_DIR.glob("*.yaml"):
            if tech_file.name == "schema.yaml":
                continue
            tech = load_yaml(tech_file)
            if tech["id"] not in referenced:
                print(f"Warning: Technique '{tech['id']}' not referenced by any purpose")


class TestSpecificTechniques:
    """Tests für spezifische Techniken."""

    def test_five_whys_has_required_fields(self):
        """Five Whys hat alle wichtigen Felder."""
        tech = get_technique("five-whys")
        assert tech is not None
        assert "source" in tech  # Toyota
        assert "examples" in tech
        assert "when_to_use" in tech
        assert "when_not" in tech
        assert "tips" in tech

    def test_six_thinking_hats_has_all_hats(self):
        """Six Thinking Hats beschreibt alle 6 Hüte."""
        tech = get_technique("six-thinking-hats")
        assert tech is not None

        steps_text = " ".join(tech["steps"]).lower()
        # Check that all hats are mentioned
        assert "weiß" in steps_text or "white" in steps_text
        assert "rot" in steps_text or "red" in steps_text
        assert "schwarz" in steps_text or "black" in steps_text
        assert "gelb" in steps_text or "yellow" in steps_text
        assert "grün" in steps_text or "green" in steps_text
        assert "blau" in steps_text or "blue" in steps_text
