#!/usr/bin/env python3
"""Tests for STAN Skill (T-033).

TDD: Tests for hybrid skill with automatic phase detection.
"""

import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
PLUGIN_DIR = PROJECT_ROOT


class TestSkillDirectory:
    """Tests for skill directory structure."""

    def test_skills_directory_exists(self):
        """skills directory should exist in plugin."""
        assert (PLUGIN_DIR / "skills").exists()

    def test_stan_skill_directory_exists(self):
        """skills/stan/ directory should exist."""
        assert (PLUGIN_DIR / "skills" / "stan").exists()

    def test_skill_md_exists(self):
        """SKILL.md should exist."""
        assert (PLUGIN_DIR / "skills" / "stan" / "SKILL.md").exists()


class TestSkillContent:
    """Tests for SKILL.md content."""

    @pytest.fixture
    def skill_content(self):
        """Load SKILL.md content."""
        skill_path = PLUGIN_DIR / "skills" / "stan" / "SKILL.md"
        if not skill_path.exists():
            pytest.skip("SKILL.md not yet created")
        return skill_path.read_text()

    def test_has_trigger_section(self, skill_content):
        """SKILL.md should have trigger section."""
        assert "trigger" in skill_content.lower() or "aktivier" in skill_content.lower()

    def test_has_phase_detection(self, skill_content):
        """SKILL.md should describe phase detection."""
        has_phase = "phase" in skill_content.lower()
        has_define = "define" in skill_content.lower()
        has_plan = "plan" in skill_content.lower()
        has_create = "create" in skill_content.lower()
        assert has_phase and has_define and has_plan and has_create

    def test_has_german_triggers(self, skill_content):
        """SKILL.md should have German trigger words."""
        german_triggers = ["feature", "idee", "projekt", "bauen", "implementier"]
        has_german = any(t in skill_content.lower() for t in german_triggers)
        assert has_german, "Should have German trigger words"

    def test_has_english_triggers(self, skill_content):
        """SKILL.md should have English trigger words."""
        english_triggers = ["build", "implement", "create", "develop", "feature"]
        has_english = any(t in skill_content.lower() for t in english_triggers)
        assert has_english, "Should have English trigger words"

    def test_has_think_triggers(self, skill_content):
        """SKILL.md should have think/technique triggers."""
        think_triggers = ["stuck", "stecke", "warum", "why", "problem"]
        has_think = any(t in skill_content.lower() for t in think_triggers)
        assert has_think, "Should have think/technique triggers"

    def test_references_commands(self, skill_content):
        """SKILL.md should reference /stan commands."""
        assert "/stan" in skill_content


class TestSkillReferences:
    """Tests for skill reference files."""

    def test_references_directory_exists(self):
        """references directory should exist."""
        refs_dir = PLUGIN_DIR / "skills" / "stan" / "references"
        # References are optional, but if present should be structured
        if refs_dir.exists():
            assert refs_dir.is_dir()


class TestPhaseDetectionLogic:
    """Tests for phase detection logic described in skill."""

    @pytest.fixture
    def skill_content(self):
        """Load SKILL.md content."""
        skill_path = PLUGIN_DIR / "skills" / "stan" / "SKILL.md"
        if not skill_path.exists():
            pytest.skip("SKILL.md not yet created")
        return skill_path.read_text()

    def test_describes_no_stan_md_detection(self, skill_content):
        """Should describe behavior when no stan.md exists."""
        # When no stan.md: Should suggest /stan init
        assert "stan.md" in skill_content.lower() or "init" in skill_content.lower()

    def test_describes_prd_approved_detection(self, skill_content):
        """Should describe detection when PRD is approved."""
        # When PRD approved: Should suggest PLAN phase
        assert "approved" in skill_content.lower() or "plan" in skill_content.lower()

    def test_describes_tasks_ready_detection(self, skill_content):
        """Should describe detection when tasks are ready."""
        # When tasks ready: Should suggest CREATE phase
        assert "ready" in skill_content.lower() or "create" in skill_content.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
