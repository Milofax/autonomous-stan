#!/usr/bin/env python3
"""Tests for Model Auto-Selection (T-044).

TDD: Tests for automatic model selection based on task complexity.
"""

import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent
# Path configured in conftest.py


class TestModelSelectionModule:
    """Tests for model_selection.py module."""

    def test_module_exists(self):
        """model_selection.py should exist."""
        module_path = PROJECT_ROOT / "hooks" / "autonomous-stan" / "lib" / "model_selection.py"
        assert module_path.exists(), f"Module not found: {module_path}"

    def test_module_importable(self):
        """model_selection module should be importable."""
        try:
            import importlib
            import model_selection
            importlib.reload(model_selection)
        except ImportError as e:
            pytest.fail(f"Could not import model_selection: {e}")


class TestModelConstants:
    """Tests for model constants."""

    def test_available_models_defined(self):
        """AVAILABLE_MODELS should be defined."""
        import importlib
        import model_selection
        importlib.reload(model_selection)

        assert hasattr(model_selection, "AVAILABLE_MODELS")
        assert "haiku" in model_selection.AVAILABLE_MODELS
        assert "sonnet" in model_selection.AVAILABLE_MODELS
        assert "opus" in model_selection.AVAILABLE_MODELS

    def test_default_model_defined(self):
        """DEFAULT_MODEL should be defined."""
        import importlib
        import model_selection
        importlib.reload(model_selection)

        assert hasattr(model_selection, "DEFAULT_MODEL")
        assert model_selection.DEFAULT_MODEL in model_selection.AVAILABLE_MODELS

    def test_escalation_order_defined(self):
        """ESCALATION_ORDER should be defined."""
        import importlib
        import model_selection
        importlib.reload(model_selection)

        assert hasattr(model_selection, "ESCALATION_ORDER")
        assert model_selection.ESCALATION_ORDER == ["haiku", "sonnet", "opus"]


class TestSelectModelFunction:
    """Tests for select_model_for_task function."""

    def test_select_model_exists(self):
        """select_model_for_task function should exist."""
        import importlib
        import model_selection
        importlib.reload(model_selection)

        assert hasattr(model_selection, "select_model_for_task")

    def test_low_complexity_returns_sonnet(self):
        """Complexity < 3 should return sonnet."""
        import importlib
        import model_selection
        importlib.reload(model_selection)

        result = model_selection.select_model_for_task(complexity=1)
        assert result == "sonnet"

        result = model_selection.select_model_for_task(complexity=2)
        assert result == "sonnet"

    def test_high_complexity_returns_opus(self):
        """Complexity >= 3 should return opus."""
        import importlib
        import model_selection
        importlib.reload(model_selection)

        result = model_selection.select_model_for_task(complexity=3)
        assert result == "opus"

        result = model_selection.select_model_for_task(complexity=4)
        assert result == "opus"

    def test_explicit_model_overrides_auto(self):
        """Explicit model parameter should override auto-selection."""
        import importlib
        import model_selection
        importlib.reload(model_selection)

        result = model_selection.select_model_for_task(complexity=4, model="haiku")
        assert result == "haiku"

    def test_auto_model_uses_complexity(self):
        """model='auto' should use complexity-based selection."""
        import importlib
        import model_selection
        importlib.reload(model_selection)

        result = model_selection.select_model_for_task(complexity=1, model="auto")
        assert result == "sonnet"

        result = model_selection.select_model_for_task(complexity=4, model="auto")
        assert result == "opus"


class TestModelEscalation:
    """Tests for model escalation logic."""

    def test_escalate_model_exists(self):
        """escalate_model function should exist."""
        import importlib
        import model_selection
        importlib.reload(model_selection)

        assert hasattr(model_selection, "escalate_model")

    def test_escalate_from_haiku(self):
        """Escalation from haiku should go to sonnet."""
        import importlib
        import model_selection
        importlib.reload(model_selection)

        result = model_selection.escalate_model("haiku")
        assert result == "sonnet"

    def test_escalate_from_sonnet(self):
        """Escalation from sonnet should go to opus."""
        import importlib
        import model_selection
        importlib.reload(model_selection)

        result = model_selection.escalate_model("sonnet")
        assert result == "opus"

    def test_escalate_from_opus_returns_none(self):
        """Escalation from opus should return None (max reached)."""
        import importlib
        import model_selection
        importlib.reload(model_selection)

        result = model_selection.escalate_model("opus")
        assert result is None

    def test_can_escalate_function(self):
        """can_escalate function should exist and work."""
        import importlib
        import model_selection
        importlib.reload(model_selection)

        assert hasattr(model_selection, "can_escalate")
        assert model_selection.can_escalate("haiku") is True
        assert model_selection.can_escalate("sonnet") is True
        assert model_selection.can_escalate("opus") is False


class TestGetModelInfo:
    """Tests for get_model_info function."""

    def test_get_model_info_exists(self):
        """get_model_info function should exist."""
        import importlib
        import model_selection
        importlib.reload(model_selection)

        assert hasattr(model_selection, "get_model_info")

    def test_model_info_contains_description(self):
        """Model info should contain description."""
        import importlib
        import model_selection
        importlib.reload(model_selection)

        info = model_selection.get_model_info("sonnet")
        assert "description" in info

    def test_model_info_contains_use_case(self):
        """Model info should contain use_case."""
        import importlib
        import model_selection
        importlib.reload(model_selection)

        info = model_selection.get_model_info("opus")
        assert "use_case" in info


class TestCreateCommandIntegration:
    """Tests for integration with /stan create command."""

    def test_create_command_mentions_model_selection(self):
        """Create command should mention model selection."""
        create_cmd = PROJECT_ROOT / "commands" / "autonomous-stan" / "create.md"
        content = create_cmd.read_text()

        # Should mention model or auto-selection
        has_model = "model" in content.lower()
        has_auto = "auto" in content.lower() or "automatic" in content.lower()
        assert has_model or has_auto, "Create command should mention model selection"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
