#!/usr/bin/env python3
"""Tests for Project Complexity Levels (T-034).

TDD: Tests written before implementation.
"""

import pytest
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


class TestConfigHasComplexitySupport:
    """Tests for complexity level in config."""

    def test_config_module_exists(self):
        """Config module should exist."""
        config_file = PROJECT_ROOT / "hooks" / "autonomous-stan" / "lib" / "config.py"
        assert config_file.exists(), f"Config module not found: {config_file}"

    def test_config_has_complexity_levels(self):
        """Config should define complexity levels."""
        import sys
        # Path configured in conftest.py

        import importlib
        import config
        importlib.reload(config)

        # Should have COMPLEXITY_LEVELS constant
        assert hasattr(config, 'COMPLEXITY_LEVELS'), \
            "config should have COMPLEXITY_LEVELS"

    def test_complexity_levels_are_0_to_4(self):
        """Complexity levels should be 0-4."""
        import sys
        # Path configured in conftest.py

        import importlib
        import config
        importlib.reload(config)

        levels = config.COMPLEXITY_LEVELS
        assert 0 in levels, "Level 0 (trivial) should exist"
        assert 1 in levels, "Level 1 (minimal) should exist"
        assert 2 in levels, "Level 2 (standard) should exist"
        assert 3 in levels, "Level 3 (detailed) should exist"
        assert 4 in levels, "Level 4 (comprehensive) should exist"

    def test_complexity_levels_have_names(self):
        """Each complexity level should have a name."""
        import sys
        # Path configured in conftest.py

        import importlib
        import config
        importlib.reload(config)

        levels = config.COMPLEXITY_LEVELS
        for level_num, level_data in levels.items():
            assert "name" in level_data, f"Level {level_num} should have name"


class TestComplexityLevelFunctions:
    """Tests for complexity level functions."""

    def test_get_complexity_exists(self):
        """get_project_complexity function should exist."""
        import sys
        # Path configured in conftest.py

        import importlib
        import config
        importlib.reload(config)

        assert hasattr(config, 'get_project_complexity'), \
            "config should have get_project_complexity function"

    def test_set_complexity_exists(self):
        """set_project_complexity function should exist."""
        import sys
        # Path configured in conftest.py

        import importlib
        import config
        importlib.reload(config)

        assert hasattr(config, 'set_project_complexity'), \
            "config should have set_project_complexity function"

    def test_default_complexity_is_2(self, tmp_path):
        """Default complexity should be 2 (standard)."""
        import sys
        # Path configured in conftest.py

        import importlib
        import config
        importlib.reload(config)

        from unittest.mock import patch

        # No config file = default level
        with patch.object(config, 'get_config_file', return_value=tmp_path / "config.yaml"):
            complexity = config.get_project_complexity()
            assert complexity == 2, f"Default complexity should be 2, got {complexity}"


class TestInitCommandComplexity:
    """Tests for /stan init complexity selection."""

    def test_init_command_exists(self):
        """Init command should exist."""
        init_file = PROJECT_ROOT / "commands" / "autonomous-stan" / "init.md"
        assert init_file.exists(), f"Init command not found: {init_file}"

    def test_init_command_mentions_complexity(self):
        """Init command should mention complexity."""
        init_file = PROJECT_ROOT / "commands" / "autonomous-stan" / "init.md"
        content = init_file.read_text()

        assert "complexity" in content.lower(), \
            "Init command should mention complexity"


class TestComplexityLevelDescriptions:
    """Tests for complexity level descriptions."""

    def test_level_0_is_trivial(self):
        """Level 0 should be trivial (no planning)."""
        import sys
        # Path configured in conftest.py

        import importlib
        import config
        importlib.reload(config)

        level = config.COMPLEXITY_LEVELS[0]
        assert "trivial" in level.get("name", "").lower() or \
               "trivial" in level.get("description", "").lower(), \
            "Level 0 should be described as trivial"

    def test_level_1_is_minimal(self):
        """Level 1 should be minimal (bug fix)."""
        import sys
        # Path configured in conftest.py

        import importlib
        import config
        importlib.reload(config)

        level = config.COMPLEXITY_LEVELS[1]
        assert "minimal" in level.get("name", "").lower() or \
               "bug" in level.get("description", "").lower(), \
            "Level 1 should be described as minimal/bug fix"

    def test_level_2_is_standard(self):
        """Level 2 should be standard (feature)."""
        import sys
        # Path configured in conftest.py

        import importlib
        import config
        importlib.reload(config)

        level = config.COMPLEXITY_LEVELS[2]
        assert "standard" in level.get("name", "").lower() or \
               "feature" in level.get("description", "").lower(), \
            "Level 2 should be described as standard/feature"

    def test_level_3_is_detailed(self):
        """Level 3 should be detailed (complex feature)."""
        import sys
        # Path configured in conftest.py

        import importlib
        import config
        importlib.reload(config)

        level = config.COMPLEXITY_LEVELS[3]
        assert "detailed" in level.get("name", "").lower() or \
               "complex" in level.get("description", "").lower(), \
            "Level 3 should be described as detailed/complex"

    def test_level_4_is_comprehensive(self):
        """Level 4 should be comprehensive (enterprise)."""
        import sys
        # Path configured in conftest.py

        import importlib
        import config
        importlib.reload(config)

        level = config.COMPLEXITY_LEVELS[4]
        assert "comprehensive" in level.get("name", "").lower() or \
               "enterprise" in level.get("description", "").lower(), \
            "Level 4 should be described as comprehensive/enterprise"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
