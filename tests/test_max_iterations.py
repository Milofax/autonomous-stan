#!/usr/bin/env python3
"""Tests for Max Iterations configuration (T-036).

TDD: Tests written before implementation.
"""

import pytest
from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).parent.parent


class TestStanTemplateMaxIterations:
    """Tests for max_iterations in stan.md.template."""

    def test_template_exists(self):
        """Template must exist."""
        template = PROJECT_ROOT / "templates" / "stan.md.template"
        assert template.exists(), f"Template not found: {template}"

    def test_template_documents_max_iterations(self):
        """Template should mention max_iterations as optional field."""
        template = PROJECT_ROOT / "templates" / "stan.md.template"
        content = template.read_text()
        # Should document max_iterations somewhere
        assert "max_iterations" in content.lower(), \
            "Template should document max_iterations field"


class TestStanGateMaxIterations:
    """Tests for max_iterations in stan_gate.py."""

    def test_gate_exists(self):
        """Gate hook must exist."""
        gate = PROJECT_ROOT / ".claude" / "hooks" / "stan" / "pre-tool-use" / "stan_gate.py"
        assert gate.exists(), f"Gate hook not found: {gate}"

    def test_gate_has_default_constant(self):
        """Gate should have DEFAULT_MAX_ITERATIONS constant."""
        gate = PROJECT_ROOT / ".claude" / "hooks" / "stan" / "pre-tool-use" / "stan_gate.py"
        content = gate.read_text()
        assert "DEFAULT_MAX_ITERATIONS" in content, \
            "Gate should have DEFAULT_MAX_ITERATIONS constant"

    def test_gate_default_is_10(self):
        """Default max_iterations should be 10 (like Ralph)."""
        gate = PROJECT_ROOT / ".claude" / "hooks" / "stan" / "pre-tool-use" / "stan_gate.py"
        content = gate.read_text()
        # Should have DEFAULT_MAX_ITERATIONS = 10
        match = re.search(r'DEFAULT_MAX_ITERATIONS\s*=\s*(\d+)', content)
        assert match, "DEFAULT_MAX_ITERATIONS constant not found"
        assert match.group(1) == "10", \
            f"DEFAULT_MAX_ITERATIONS should be 10, got {match.group(1)}"

    def test_gate_has_get_max_iterations_function(self):
        """Gate should have function to get max_iterations from manifest."""
        gate = PROJECT_ROOT / ".claude" / "hooks" / "stan" / "pre-tool-use" / "stan_gate.py"
        content = gate.read_text()
        assert "def get_max_iterations" in content, \
            "Gate should have get_max_iterations function"


class TestMaxIterationsLogic:
    """Tests for max_iterations logic."""

    def test_get_max_iterations_returns_default_without_manifest(self):
        """Without manifest, should return default 10."""
        import sys
        sys.path.insert(0, str(PROJECT_ROOT / ".claude" / "hooks" / "stan" / "pre-tool-use"))

        # Mock: no manifest
        from unittest.mock import patch
        import stan_gate

        with patch.object(stan_gate, 'get_manifest_path', return_value=None):
            result = stan_gate.get_max_iterations()
            assert result == 10, f"Expected 10 without manifest, got {result}"

    def test_get_max_iterations_returns_default_without_field(self, tmp_path):
        """With manifest but no max_iterations field, should return default 10."""
        import sys
        sys.path.insert(0, str(PROJECT_ROOT / ".claude" / "hooks" / "stan" / "pre-tool-use"))

        from unittest.mock import patch
        import stan_gate

        # Create manifest without max_iterations
        manifest = tmp_path / "stan.md"
        manifest.write_text("""---
type: manifest
status: draft
---
# Test Project
""")

        with patch.object(stan_gate, 'get_manifest_path', return_value=manifest):
            result = stan_gate.get_max_iterations()
            assert result == 10, f"Expected 10 without field, got {result}"

    def test_get_max_iterations_reads_from_manifest(self, tmp_path):
        """With max_iterations in manifest, should return that value."""
        import sys
        sys.path.insert(0, str(PROJECT_ROOT / ".claude" / "hooks" / "stan" / "pre-tool-use"))

        from unittest.mock import patch
        import stan_gate

        # Reload to get fresh module
        import importlib
        importlib.reload(stan_gate)

        # Create manifest with max_iterations
        manifest = tmp_path / "stan.md"
        manifest.write_text("""---
type: manifest
status: draft
max_iterations: 15
---
# Test Project
""")

        with patch.object(stan_gate, 'get_manifest_path', return_value=manifest):
            result = stan_gate.get_max_iterations()
            assert result == 15, f"Expected 15 from manifest, got {result}"

    def test_get_max_iterations_handles_invalid_value(self, tmp_path):
        """With invalid max_iterations, should fall back to default."""
        import sys
        sys.path.insert(0, str(PROJECT_ROOT / ".claude" / "hooks" / "stan" / "pre-tool-use"))

        from unittest.mock import patch
        import stan_gate

        # Reload to get fresh module
        import importlib
        importlib.reload(stan_gate)

        # Create manifest with invalid value
        manifest = tmp_path / "stan.md"
        manifest.write_text("""---
type: manifest
max_iterations: not_a_number
---
# Test Project
""")

        with patch.object(stan_gate, 'get_manifest_path', return_value=manifest):
            result = stan_gate.get_max_iterations()
            assert result == 10, f"Expected 10 for invalid value, got {result}"


class TestPlanDocumentation:
    """Tests for documentation in plan.md."""

    def test_plan_exists(self):
        """Plan must exist."""
        plan = PROJECT_ROOT / "docs" / "plan.md"
        assert plan.exists(), f"Plan not found: {plan}"

    def test_plan_documents_max_iterations_decision(self):
        """Plan should document the max_iterations decision."""
        plan = PROJECT_ROOT / "docs" / "plan.md"
        content = plan.read_text()
        # Should mention max_iterations in Entscheidungs-Log or elsewhere
        assert "max_iterations" in content.lower() or "iterations" in content.lower(), \
            "Plan should document max_iterations setting"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
