#!/usr/bin/env python3
"""Tests for STAN Plugin structure (T-032).

TDD: Tests for plugin that can be installed with cc --plugin-dir.
"""

import json
import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
PLUGIN_DIR = PROJECT_ROOT  # Plugin root IS repo root


class TestPluginDirectoryStructure:
    """Tests for plugin directory structure."""

    def test_plugin_directory_exists(self):
        """Plugin directory should exist."""
        assert PLUGIN_DIR.exists(), f"Plugin directory not found: {PLUGIN_DIR}"

    def test_claude_plugin_directory_exists(self):
        """.claude-plugin directory should exist."""
        assert (PLUGIN_DIR / ".claude-plugin").exists()

    def test_plugin_manifest_exists(self):
        """plugin.json manifest should exist."""
        assert (PLUGIN_DIR / ".claude-plugin" / "plugin.json").exists()

    def test_commands_directory_exists(self):
        """commands directory should exist."""
        assert (PLUGIN_DIR / "commands").exists()

    def test_hooks_directory_exists(self):
        """hooks directory should exist."""
        assert (PLUGIN_DIR / "hooks").exists()

    def test_hooks_json_exists(self):
        """hooks.json should exist."""
        assert (PLUGIN_DIR / "hooks" / "hooks.json").exists()


class TestPluginManifest:
    """Tests for plugin.json manifest."""

    @pytest.fixture
    def manifest(self):
        """Load plugin manifest."""
        manifest_path = PLUGIN_DIR / ".claude-plugin" / "plugin.json"
        if not manifest_path.exists():
            pytest.skip("Manifest not yet created")
        return json.loads(manifest_path.read_text())

    def test_manifest_has_name(self, manifest):
        """Manifest should have name."""
        assert "name" in manifest
        assert manifest["name"] == "autonomous-stan"

    def test_manifest_has_version(self, manifest):
        """Manifest should have version."""
        assert "version" in manifest
        assert manifest["version"]  # Non-empty

    def test_manifest_has_description(self, manifest):
        """Manifest should have description."""
        assert "description" in manifest

    def test_manifest_has_commands_path(self, manifest):
        """Manifest should specify commands path."""
        assert "commands" in manifest

    def test_manifest_has_hooks_path(self, manifest):
        """Manifest should specify hooks path."""
        assert "hooks" in manifest


class TestPluginCommands:
    """Tests for plugin commands."""

    def test_stan_commands_directory_exists(self):
        """commands/stan/ directory should exist."""
        assert (PLUGIN_DIR / "commands" / "stan").exists()

    def test_init_command_exists(self):
        """/stan init command should exist."""
        assert (PLUGIN_DIR / "commands" / "stan" / "init.md").exists()

    def test_define_command_exists(self):
        """/stan define command should exist."""
        assert (PLUGIN_DIR / "commands" / "stan" / "define.md").exists()

    def test_plan_command_exists(self):
        """/stan plan command should exist."""
        assert (PLUGIN_DIR / "commands" / "stan" / "plan.md").exists()

    def test_create_command_exists(self):
        """/stan create command should exist."""
        assert (PLUGIN_DIR / "commands" / "stan" / "create.md").exists()

    def test_complete_command_exists(self):
        """/stan complete command should exist."""
        assert (PLUGIN_DIR / "commands" / "stan" / "complete.md").exists()

    def test_think_command_exists(self):
        """/stan think command should exist."""
        assert (PLUGIN_DIR / "commands" / "stan" / "think.md").exists()

    def test_all_commands_count(self):
        """Should have all 10 STAN commands."""
        commands_dir = PLUGIN_DIR / "commands" / "stan"
        if not commands_dir.exists():
            pytest.skip("Commands directory not yet created")
        commands = list(commands_dir.glob("*.md"))
        assert len(commands) >= 10, f"Expected 10 commands, found {len(commands)}"


class TestPluginHooksConfig:
    """Tests for hooks.json configuration."""

    @pytest.fixture
    def hooks_config(self):
        """Load hooks configuration."""
        hooks_path = PLUGIN_DIR / "hooks" / "hooks.json"
        if not hooks_path.exists():
            pytest.skip("hooks.json not yet created")
        data = json.loads(hooks_path.read_text())
        # Support both flat format and nested {hooks: {...}} format
        return data.get("hooks", data)

    def test_has_pre_tool_use_hooks(self, hooks_config):
        """Should have PreToolUse hooks configured."""
        assert "PreToolUse" in hooks_config

    def test_has_post_tool_use_hooks(self, hooks_config):
        """Should have PostToolUse hooks configured."""
        assert "PostToolUse" in hooks_config

    def test_has_user_prompt_submit_hooks(self, hooks_config):
        """Should have UserPromptSubmit hooks configured."""
        assert "UserPromptSubmit" in hooks_config

    def test_pre_tool_use_has_stan_gate(self, hooks_config):
        """PreToolUse should include stan-gate logic."""
        pre_tool_use = hooks_config.get("PreToolUse", [])
        assert len(pre_tool_use) > 0, "PreToolUse should have at least one hook"

    def test_hooks_use_plugin_root_variable(self, hooks_config):
        """Hooks should use ${CLAUDE_PLUGIN_ROOT} for paths."""
        config_str = json.dumps(hooks_config)
        # Either uses CLAUDE_PLUGIN_ROOT or inline prompts
        has_plugin_root = "${CLAUDE_PLUGIN_ROOT}" in config_str
        has_prompts = '"type": "prompt"' in config_str
        assert has_plugin_root or has_prompts, "Hooks should use CLAUDE_PLUGIN_ROOT or inline prompts"


class TestPluginAssets:
    """Tests for plugin assets (templates, criteria, techniques)."""

    def test_assets_directory_exists(self):
        """Assets (templates, criteria, techniques) should exist at root level."""
        # In v2, assets are at root level (not in assets/ subdir)
        assert (PLUGIN_DIR / "criteria").exists() or (PLUGIN_DIR / "assets").exists()

    def test_templates_exist(self):
        """Should have template files."""
        templates_dir = PLUGIN_DIR / "templates"
        if not templates_dir.exists():
            templates_dir = PLUGIN_DIR / "assets" / "templates"
        if not templates_dir.exists():
            pytest.skip("Templates directory not yet created")
        templates = list(templates_dir.glob("*.template"))
        assert len(templates) >= 3, "Should have at least 3 templates"

    def test_criteria_exist(self):
        """Should have criteria files."""
        criteria_dir = PLUGIN_DIR / "criteria"
        if not criteria_dir.exists():
            criteria_dir = PLUGIN_DIR / "assets" / "criteria"
        if not criteria_dir.exists():
            pytest.skip("Criteria directory not yet created")
        criteria = list(criteria_dir.glob("*.yaml"))
        assert len(criteria) >= 10, "Should have at least 10 criteria"


class TestPluginRules:
    """Tests for plugin rules."""

    def test_rules_directory_exists(self):
        """rules directory should exist."""
        assert (PLUGIN_DIR / "rules").exists()

    def test_skill_level_rule_exists(self):
        """skill-level.md rule should exist."""
        assert (PLUGIN_DIR / "rules" / "stan" / "skill-level.md").exists()

    def test_task_priority_rule_exists(self):
        """task-priority.md rule should exist."""
        assert (PLUGIN_DIR / "rules" / "stan" / "task-priority.md").exists()


class TestPluginInstallability:
    """Tests that plugin can be installed."""

    def test_plugin_has_no_absolute_paths(self):
        """Plugin should not have hardcoded absolute paths."""
        skip_dirs = {"vendor", "submodules", "experiments", ".git", ".claude", "node_modules", ".stan"}
        plugin_files = [
            f for f in PLUGIN_DIR.rglob("*")
            if not any(part in skip_dirs for part in f.parts)
        ]

        problematic_files = []
        for f in plugin_files:
            if f.is_file() and f.suffix in [".json", ".md", ".sh", ".py"]:
                try:
                    content = f.read_text()
                    # Check for absolute paths (but allow ${CLAUDE_PLUGIN_ROOT})
                    if "/Volumes/" in content or "/Users/" in content:
                        if "${CLAUDE_PLUGIN_ROOT}" not in content:
                            problematic_files.append(str(f))
                except Exception:
                    pass

        assert len(problematic_files) == 0, f"Files with absolute paths: {problematic_files}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
