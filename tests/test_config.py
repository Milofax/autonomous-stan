#!/usr/bin/env python3
"""Tests für STAN Config Library."""

import pytest
import tempfile
import os
import sys
from pathlib import Path

# Add lib to path
PROJECT_ROOT = Path(__file__).parent.parent
HOOKS_LIB = PROJECT_ROOT / "hooks" / "autonomous-stan" / "lib"
sys.path.insert(0, str(HOOKS_LIB))

import config


class TestConfigDataClasses:
    """Tests für Config Dataclasses."""

    def test_user_config_defaults(self):
        """UserConfig hat sinnvolle Defaults."""
        uc = config.UserConfig()
        assert uc.name == ""
        assert uc.skill_level == "intermediate"

    def test_user_config_with_values(self):
        """UserConfig akzeptiert Werte."""
        uc = config.UserConfig(name="Mathias", skill_level="expert")
        assert uc.name == "Mathias"
        assert uc.skill_level == "expert"

    def test_user_config_invalid_skill_level(self):
        """Ungültiges skill_level wird auf intermediate gesetzt."""
        uc = config.UserConfig(skill_level="invalid")
        assert uc.skill_level == "intermediate"

    def test_language_config_defaults(self):
        """LanguageConfig hat sinnvolle Defaults."""
        lc = config.LanguageConfig()
        assert lc.communication == "en"
        assert lc.documents == "en"

    def test_language_config_with_values(self):
        """LanguageConfig akzeptiert Werte."""
        lc = config.LanguageConfig(communication="de", documents="en")
        assert lc.communication == "de"
        assert lc.documents == "en"

    def test_project_config_defaults(self):
        """ProjectConfig hat sinnvolle Defaults."""
        pc = config.ProjectConfig()
        assert pc.name == ""
        assert pc.output_folder == ".stan"

    def test_stan_config_defaults(self):
        """StanConfig hat sinnvolle Defaults."""
        sc = config.StanConfig()
        assert sc.user.name == ""
        assert sc.user.skill_level == "intermediate"
        assert sc.language.communication == "en"
        assert sc.language.documents == "en"
        assert sc.project.name == ""
        assert sc.project.output_folder == ".stan"


class TestConfigLoadSave:
    """Tests für Config Load/Save."""

    def test_load_nonexistent_returns_none(self, tmp_path, monkeypatch):
        """load_config gibt None zurück wenn Datei nicht existiert."""
        monkeypatch.chdir(tmp_path)
        result = config.load_config()
        assert result is None

    def test_config_exists_false(self, tmp_path, monkeypatch):
        """config_exists gibt False zurück wenn keine Config."""
        monkeypatch.chdir(tmp_path)
        assert config.config_exists() is False

    def test_save_creates_directory(self, tmp_path, monkeypatch):
        """save_config erstellt .stan/ Verzeichnis."""
        monkeypatch.chdir(tmp_path)

        cfg = config.StanConfig(
            user=config.UserConfig(name="Test", skill_level="beginner"),
            language=config.LanguageConfig(communication="de", documents="en"),
            project=config.ProjectConfig(name="TestProject")
        )

        result = config.save_config(cfg)
        assert result is True
        assert (tmp_path / ".stan").is_dir()
        assert (tmp_path / ".stan" / "config.yaml").exists()

    def test_save_and_load_roundtrip(self, tmp_path, monkeypatch):
        """Config kann gespeichert und wieder geladen werden."""
        monkeypatch.chdir(tmp_path)

        original = config.StanConfig(
            user=config.UserConfig(name="Mathias", skill_level="expert"),
            language=config.LanguageConfig(communication="de", documents="en"),
            project=config.ProjectConfig(name="MyProject", output_folder=".stan")
        )

        config.save_config(original)
        loaded = config.load_config()

        assert loaded is not None
        assert loaded.user.name == "Mathias"
        assert loaded.user.skill_level == "expert"
        assert loaded.language.communication == "de"
        assert loaded.language.documents == "en"
        assert loaded.project.name == "MyProject"

    def test_config_exists_true_after_save(self, tmp_path, monkeypatch):
        """config_exists gibt True zurück nach save."""
        monkeypatch.chdir(tmp_path)

        cfg = config.StanConfig()
        config.save_config(cfg)

        assert config.config_exists() is True


class TestEnsureConfig:
    """Tests für ensure_config."""

    def test_ensure_returns_defaults_when_no_file(self, tmp_path, monkeypatch):
        """ensure_config gibt Defaults zurück wenn keine Datei."""
        monkeypatch.chdir(tmp_path)

        cfg = config.ensure_config()

        assert cfg is not None
        assert cfg.user.skill_level == "intermediate"
        assert cfg.language.communication == "en"

    def test_ensure_returns_saved_config(self, tmp_path, monkeypatch):
        """ensure_config gibt gespeicherte Config zurück."""
        monkeypatch.chdir(tmp_path)

        saved = config.StanConfig(
            user=config.UserConfig(name="Test", skill_level="beginner")
        )
        config.save_config(saved)

        loaded = config.ensure_config()

        assert loaded.user.name == "Test"
        assert loaded.user.skill_level == "beginner"


class TestConvenienceGetters:
    """Tests für Convenience Getter Functions."""

    def test_get_user_name_empty_when_no_config(self, tmp_path, monkeypatch):
        """get_user_name gibt '' zurück wenn keine Config."""
        monkeypatch.chdir(tmp_path)
        assert config.get_user_name() == ""

    def test_get_user_name_returns_value(self, tmp_path, monkeypatch):
        """get_user_name gibt gespeicherten Namen zurück."""
        monkeypatch.chdir(tmp_path)

        cfg = config.StanConfig(user=config.UserConfig(name="Mathias"))
        config.save_config(cfg)

        assert config.get_user_name() == "Mathias"

    def test_get_skill_level_default(self, tmp_path, monkeypatch):
        """get_skill_level gibt 'intermediate' als Default."""
        monkeypatch.chdir(tmp_path)
        assert config.get_skill_level() == "intermediate"

    def test_get_skill_level_returns_value(self, tmp_path, monkeypatch):
        """get_skill_level gibt gespeicherten Wert zurück."""
        monkeypatch.chdir(tmp_path)

        cfg = config.StanConfig(user=config.UserConfig(skill_level="expert"))
        config.save_config(cfg)

        assert config.get_skill_level() == "expert"

    def test_get_communication_language_default(self, tmp_path, monkeypatch):
        """get_communication_language gibt 'en' als Default."""
        monkeypatch.chdir(tmp_path)
        assert config.get_communication_language() == "en"

    def test_get_communication_language_returns_value(self, tmp_path, monkeypatch):
        """get_communication_language gibt gespeicherten Wert zurück."""
        monkeypatch.chdir(tmp_path)

        cfg = config.StanConfig(language=config.LanguageConfig(communication="de"))
        config.save_config(cfg)

        assert config.get_communication_language() == "de"

    def test_get_document_language_default(self, tmp_path, monkeypatch):
        """get_document_language gibt 'en' als Default."""
        monkeypatch.chdir(tmp_path)
        assert config.get_document_language() == "en"

    def test_get_document_language_returns_value(self, tmp_path, monkeypatch):
        """get_document_language gibt gespeicherten Wert zurück."""
        monkeypatch.chdir(tmp_path)

        cfg = config.StanConfig(language=config.LanguageConfig(documents="de"))
        config.save_config(cfg)

        assert config.get_document_language() == "de"


class TestSkillBehavior:
    """Tests für Skill Level Behavior."""

    def test_skill_behavior_beginner(self):
        """Beginner hat erklärende Flags."""
        behavior = config.SKILL_LEVEL_BEHAVIOR["beginner"]
        assert behavior["explain_new_concepts"] is True
        assert behavior["ask_if_explanation_needed"] is True
        assert behavior["use_analogies"] is True
        assert behavior["verbose_guidance"] is True

    def test_skill_behavior_intermediate(self):
        """Intermediate hat keine erklärenden Flags."""
        behavior = config.SKILL_LEVEL_BEHAVIOR["intermediate"]
        assert behavior["explain_new_concepts"] is False
        assert behavior["ask_if_explanation_needed"] is False

    def test_skill_behavior_expert(self):
        """Expert ist direkt und technisch."""
        behavior = config.SKILL_LEVEL_BEHAVIOR["expert"]
        assert behavior["direct_and_technical"] is True
        assert behavior["skip_basics"] is True

    def test_get_skill_behavior_returns_correct(self, tmp_path, monkeypatch):
        """get_skill_behavior gibt korrektes Verhalten zurück."""
        monkeypatch.chdir(tmp_path)

        cfg = config.StanConfig(user=config.UserConfig(skill_level="beginner"))
        config.save_config(cfg)

        behavior = config.get_skill_behavior()
        assert behavior["explain_new_concepts"] is True


class TestConfigFileFormat:
    """Tests für Config File Format."""

    def test_config_file_is_yaml(self, tmp_path, monkeypatch):
        """Config-Datei ist gültiges YAML mit Kommentaren."""
        monkeypatch.chdir(tmp_path)

        cfg = config.StanConfig(
            user=config.UserConfig(name="Test"),
            language=config.LanguageConfig(communication="de")
        )
        config.save_config(cfg)

        content = (tmp_path / ".stan" / "config.yaml").read_text()

        # Hat Kommentare
        assert "# STAN Framework Configuration" in content
        assert "# How STAN addresses you" in content

        # Hat alle Sektionen
        assert "user:" in content
        assert "language:" in content
        assert "project:" in content

    def test_config_preserves_special_characters(self, tmp_path, monkeypatch):
        """Config-Datei behält Sonderzeichen bei."""
        monkeypatch.chdir(tmp_path)

        cfg = config.StanConfig(
            user=config.UserConfig(name="Müller"),
            project=config.ProjectConfig(name="Über-Projekt")
        )
        config.save_config(cfg)

        loaded = config.load_config()
        assert loaded.user.name == "Müller"
        assert loaded.project.name == "Über-Projekt"


class TestYAMLFallback:
    """Tests für Bug #3 Verification: Graceful YAML Fallback."""

    def test_load_returns_none_when_yaml_unavailable(self, tmp_path, monkeypatch):
        """load_config gibt None zurück wenn YAML nicht verfügbar."""
        import importlib
        monkeypatch.chdir(tmp_path)

        # Create a config file (would normally need yaml to read)
        config_dir = tmp_path / ".stan"
        config_dir.mkdir()
        (config_dir / "config.yaml").write_text("user:\n  name: Test\n")

        # Mock YAML_AVAILABLE = False
        monkeypatch.setattr(config, 'YAML_AVAILABLE', False)

        # Should return None, not crash
        result = config.load_config()
        assert result is None

    def test_save_returns_false_when_yaml_unavailable(self, tmp_path, monkeypatch):
        """save_config gibt False zurück wenn YAML nicht verfügbar."""
        monkeypatch.chdir(tmp_path)

        # Mock YAML_AVAILABLE = False
        monkeypatch.setattr(config, 'YAML_AVAILABLE', False)

        cfg = config.StanConfig(user=config.UserConfig(name="Test"))

        # Should return False, not crash
        result = config.save_config(cfg)
        assert result is False


class TestPathConstants:
    """Tests for Path Constants."""

    def test_stan_dir_constant(self):
        """STAN_DIR constant is correct."""
        assert config.STAN_DIR == ".stan"

    def test_tasks_file_constant(self):
        """TASKS_FILE constant is correct."""
        assert config.TASKS_FILE == ".stan/tasks.jsonl"

    def test_session_file_constant(self):
        """SESSION_FILE constant is correct."""
        assert config.SESSION_FILE == ".stan/session.json"

    def test_completed_dir_constant(self):
        """COMPLETED_DIR constant is correct."""
        assert config.COMPLETED_DIR == ".stan/completed"

    def test_config_file_constant(self):
        """CONFIG_FILE constant is correct."""
        assert config.CONFIG_FILE == ".stan/config.yaml"


class TestPathFunctions:
    """Tests for Path Functions."""

    def test_get_stan_dir(self, tmp_path, monkeypatch):
        """get_stan_dir returns correct path."""
        monkeypatch.chdir(tmp_path)
        result = config.get_stan_dir()
        assert result == tmp_path / ".stan"

    def test_get_tasks_file(self, tmp_path, monkeypatch):
        """get_tasks_file returns correct path."""
        monkeypatch.chdir(tmp_path)
        result = config.get_tasks_file()
        assert result == tmp_path / ".stan" / "tasks.jsonl"

    def test_get_session_file(self, tmp_path, monkeypatch):
        """get_session_file returns correct path."""
        monkeypatch.chdir(tmp_path)
        result = config.get_session_file()
        assert result == tmp_path / ".stan" / "session.json"

    def test_get_completed_dir(self, tmp_path, monkeypatch):
        """get_completed_dir returns correct path."""
        monkeypatch.chdir(tmp_path)
        result = config.get_completed_dir()
        assert result == tmp_path / ".stan" / "completed"

    def test_get_config_dir_alias(self, tmp_path, monkeypatch):
        """get_config_dir is an alias for get_stan_dir."""
        monkeypatch.chdir(tmp_path)
        assert config.get_config_dir() == config.get_stan_dir()


class TestEnsureFunctions:
    """Tests for Ensure Functions."""

    def test_ensure_stan_dir_creates_directory(self, tmp_path, monkeypatch):
        """ensure_stan_dir creates .stan/ directory."""
        monkeypatch.chdir(tmp_path)
        assert not (tmp_path / ".stan").exists()

        result = config.ensure_stan_dir()

        assert result == tmp_path / ".stan"
        assert (tmp_path / ".stan").is_dir()

    def test_ensure_stan_dir_idempotent(self, tmp_path, monkeypatch):
        """ensure_stan_dir is idempotent (can be called multiple times)."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".stan").mkdir()

        result = config.ensure_stan_dir()

        assert result == tmp_path / ".stan"
        assert (tmp_path / ".stan").is_dir()

    def test_ensure_completed_dir_creates_directory(self, tmp_path, monkeypatch):
        """ensure_completed_dir creates .stan/completed/ directory."""
        monkeypatch.chdir(tmp_path)
        assert not (tmp_path / ".stan" / "completed").exists()

        result = config.ensure_completed_dir()

        assert result == tmp_path / ".stan" / "completed"
        assert (tmp_path / ".stan" / "completed").is_dir()

    def test_ensure_completed_dir_creates_parents(self, tmp_path, monkeypatch):
        """ensure_completed_dir creates parent .stan/ directory."""
        monkeypatch.chdir(tmp_path)
        assert not (tmp_path / ".stan").exists()

        config.ensure_completed_dir()

        assert (tmp_path / ".stan").is_dir()
        assert (tmp_path / ".stan" / "completed").is_dir()


class TestIsStanInitialized:
    """Tests for is_stan_initialized function."""

    def test_not_initialized_when_nothing_exists(self, tmp_path, monkeypatch):
        """is_stan_initialized returns False when nothing exists."""
        monkeypatch.chdir(tmp_path)
        assert config.is_stan_initialized() is False

    def test_not_initialized_when_only_directory_exists(self, tmp_path, monkeypatch):
        """is_stan_initialized returns False when only directory exists."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".stan").mkdir()
        assert config.is_stan_initialized() is False

    def test_initialized_when_directory_and_tasks_exist(self, tmp_path, monkeypatch):
        """is_stan_initialized returns True when directory and tasks.jsonl exist."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".stan").mkdir()
        (tmp_path / ".stan" / "tasks.jsonl").touch()
        assert config.is_stan_initialized() is True


class TestInitializeStanStructure:
    """Tests for initialize_stan_structure function."""

    def test_creates_all_structures(self, tmp_path, monkeypatch):
        """initialize_stan_structure creates all necessary structures."""
        monkeypatch.chdir(tmp_path)

        result = config.initialize_stan_structure()

        assert result["stan_dir"] == tmp_path / ".stan"
        assert result["tasks_file"] == tmp_path / ".stan" / "tasks.jsonl"
        assert result["completed_dir"] == tmp_path / ".stan" / "completed"
        assert result["already_initialized"] is False

        assert (tmp_path / ".stan").is_dir()
        assert (tmp_path / ".stan" / "tasks.jsonl").exists()
        assert (tmp_path / ".stan" / "completed").is_dir()

    def test_returns_already_initialized_when_exists(self, tmp_path, monkeypatch):
        """initialize_stan_structure returns already_initialized=True when exists."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".stan").mkdir()
        (tmp_path / ".stan" / "tasks.jsonl").touch()

        result = config.initialize_stan_structure()

        assert result["already_initialized"] is True
        assert result["stan_dir"] == tmp_path / ".stan"

    def test_idempotent_structure_creation(self, tmp_path, monkeypatch):
        """initialize_stan_structure is idempotent."""
        monkeypatch.chdir(tmp_path)

        # First call
        config.initialize_stan_structure()

        # Second call
        result = config.initialize_stan_structure()

        assert result["already_initialized"] is True
        assert (tmp_path / ".stan").is_dir()
        assert (tmp_path / ".stan" / "tasks.jsonl").exists()

    def test_tasks_file_is_empty(self, tmp_path, monkeypatch):
        """initialize_stan_structure creates empty tasks.jsonl."""
        monkeypatch.chdir(tmp_path)

        config.initialize_stan_structure()

        tasks_file = tmp_path / ".stan" / "tasks.jsonl"
        assert tasks_file.read_text() == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
