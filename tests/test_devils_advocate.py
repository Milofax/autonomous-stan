#!/usr/bin/env python3
"""Tests for Devil's Advocate technique and enforcement."""

import json
import os
import re
import tempfile
import textwrap
from pathlib import Path

import pytest
import sys

# Add hooks directory to path for testing stan_gate functions
HOOKS_DIR = Path(__file__).parent.parent / "hooks" / "autonomous-stan"
sys.path.insert(0, str(HOOKS_DIR))
sys.path.insert(0, str(HOOKS_DIR / "lib"))


# ============================================================
# Test Technique YAML Structure
# ============================================================

class TestDevilsAdvocateTechniqueStructure:
    """Test that the technique YAML has all required fields."""

    @pytest.fixture
    def technique_path(self):
        return Path(__file__).parent.parent / "techniques" / "devils-advocate.yaml"

    @pytest.fixture
    def technique_content(self, technique_path):
        return technique_path.read_text(encoding="utf-8")

    def test_technique_file_exists(self, technique_path):
        assert technique_path.exists(), "devils-advocate.yaml must exist"

    def test_has_required_fields(self, technique_content):
        required = ["id:", "name:", "description:", "purposes:", "roles:",
                     "steps:", "constraints:", "two_pass_rule:"]
        for field in required:
            assert field in technique_content, f"Missing field: {field}"

    def test_has_six_roles(self, technique_content):
        role_count = technique_content.count("- id:")
        assert role_count == 6, f"Expected 6 roles, got {role_count}"

    def test_role_ids(self, technique_content):
        assert "analyst" in technique_content
        assert "product-manager" in technique_content
        assert "architect" in technique_content
        assert "security" in technique_content
        assert "  dev" in technique_content or "id: dev" in technique_content
        assert "  qa" in technique_content or "id: qa" in technique_content

    def test_role_phases(self, technique_content):
        assert "phase: define" in technique_content
        assert "phase: plan" in technique_content
        assert "phase: create" in technique_content

    def test_role_passes(self, technique_content):
        assert "pass: 1" in technique_content
        assert "pass: 2" in technique_content

    def test_purposes_listed(self, technique_content):
        assert "code-review" in technique_content
        assert "self-reflection" in technique_content
        assert "perspective-shift" in technique_content

    def test_constraints_present(self, technique_content):
        assert "must_do:" in technique_content
        assert "must_not:" in technique_content

    def test_no_role_combining_constraint(self, technique_content):
        assert "Combine roles" in technique_content, \
            "Must explicitly forbid combining roles"


# ============================================================
# Test Reference Files
# ============================================================

class TestDevilsAdvocateReferences:
    """Test that all 6 role reference files exist and have required content."""

    REFS_DIR = Path(__file__).parent.parent / "techniques" / "references"

    @pytest.mark.parametrize("filename", [
        "da-role-analyst.md",
        "da-role-pm.md",
        "da-role-architect.md",
        "da-role-security.md",
        "da-role-dev.md",
        "da-role-qa.md",
    ])
    def test_reference_exists(self, filename):
        path = self.REFS_DIR / filename
        assert path.exists(), f"Reference file missing: {filename}"

    @pytest.mark.parametrize("filename", [
        "da-role-analyst.md",
        "da-role-pm.md",
        "da-role-architect.md",
        "da-role-security.md",
        "da-role-dev.md",
        "da-role-qa.md",
    ])
    def test_reference_has_output_template(self, filename):
        content = (self.REFS_DIR / filename).read_text(encoding="utf-8")
        assert "## Output Template" in content, \
            f"{filename} must have an output template section"

    @pytest.mark.parametrize("filename", [
        "da-role-analyst.md",
        "da-role-pm.md",
        "da-role-architect.md",
        "da-role-security.md",
        "da-role-dev.md",
        "da-role-qa.md",
    ])
    def test_reference_has_you_are_not(self, filename):
        content = (self.REFS_DIR / filename).read_text(encoding="utf-8")
        assert "You Are NOT" in content, \
            f"{filename} must have 'You Are NOT' boundary section"

    @pytest.mark.parametrize("filename,expected_role", [
        ("da-role-analyst.md", "Analyst"),
        ("da-role-pm.md", "Product Manager"),
        ("da-role-architect.md", "Architect"),
        ("da-role-security.md", "Security"),
        ("da-role-dev.md", "Developer"),
        ("da-role-qa.md", "QA"),
    ])
    def test_reference_has_role_identity(self, filename, expected_role):
        content = (self.REFS_DIR / filename).read_text(encoding="utf-8")
        assert expected_role in content, \
            f"{filename} must mention {expected_role} role"

    def test_analyst_has_evidence_grading(self):
        content = (self.REFS_DIR / "da-role-analyst.md").read_text()
        assert "Grade" in content, "Analyst must have evidence grading scale"
        assert "Falsification" in content or "falsification" in content, \
            "Analyst must cover falsification"

    def test_pm_has_story_size_rule(self):
        content = (self.REFS_DIR / "da-role-pm.md").read_text()
        assert "Story Size" in content or "story" in content.lower(), \
            "PM must check story atomicity"
        assert "MoSCoW" in content, "PM must audit MoSCoW"

    def test_architect_has_failure_narratives(self):
        content = (self.REFS_DIR / "da-role-architect.md").read_text()
        assert "Failure Narrative" in content, "Architect must use failure narratives"
        assert "Inversion" in content, "Architect must use inversion technique"

    def test_security_has_owasp(self):
        content = (self.REFS_DIR / "da-role-security.md").read_text()
        assert "OWASP" in content, "Security must reference OWASP"
        assert "injection" in content.lower(), "Security must check for injection"

    def test_dev_has_shortcut_detection(self):
        content = (self.REFS_DIR / "da-role-dev.md").read_text()
        assert "Shortcut" in content, "Dev must detect shortcuts"
        assert "Research Integrity" in content, "Dev must verify research"

    def test_qa_has_named_failure_modes(self):
        content = (self.REFS_DIR / "da-role-qa.md").read_text()
        assert "SCOPE_CREEP" in content, "QA must check for SCOPE_CREEP"
        assert "QUALITY_GATE_SKIP" in content, "QA must check for QUALITY_GATE_SKIP"
        assert "RESEARCH_BYPASS" in content, "QA must check for RESEARCH_BYPASS"

    def test_pass2_roles_verify_pass1(self):
        """Pass 2 roles (PM, Security, QA) must verify Pass 1 findings."""
        for filename in ["da-role-pm.md", "da-role-security.md", "da-role-qa.md"]:
            content = (self.REFS_DIR / filename).read_text()
            assert "Pass 1" in content, \
                f"{filename} (Pass 2 role) must verify Pass 1 findings"


# ============================================================
# Test Gate Enforcement (stan_gate.py)
# ============================================================

class TestDevilsAdvocateGateEnforcement:
    """Test the DA check in stan_gate.py."""

    def _create_doc_with_techniques(self, tmpdir, filename, techniques=None):
        """Helper to create a doc file with techniques_applied in frontmatter."""
        doc_path = tmpdir / "docs" / filename
        doc_path.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            "---",
            "type: prd",
            "status: approved",
        ]
        if techniques:
            lines.append("techniques_applied:")
            for t in techniques:
                lines.append(f"  - {t}")
        lines.extend([
            "---",
            "# Test Document",
            "Content here.",
        ])
        content = "\n".join(lines) + "\n"
        doc_path.write_text(content, encoding="utf-8")
        return doc_path

    def test_no_da_blocks_define_phase(self, tmp_path):
        """Commit should be blocked in DEFINE if PRD has no DA entries."""
        self._create_doc_with_techniques(tmp_path, "prd.md", techniques=[])

        # Import and call the check function
        from stan_gate import check_devils_advocate_completed

        # Monkey-patch get_docs_path
        import stan_gate
        original = stan_gate.get_docs_path
        stan_gate.get_docs_path = lambda: tmp_path / "docs"

        try:
            allowed, reason = check_devils_advocate_completed("DEFINE")
            assert not allowed, "Should block when no DA in DEFINE"
            assert "DEVIL'S ADVOCATE REQUIRED" in reason
            assert "Evidence Audit" in reason
        finally:
            stan_gate.get_docs_path = original

    def test_pass1_only_blocks(self, tmp_path):
        """Only Pass 1 done should still block (Pass 2 missing)."""
        self._create_doc_with_techniques(
            tmp_path, "prd.md",
            techniques=["devils-advocate"]
        )

        from stan_gate import check_devils_advocate_completed
        import stan_gate
        original = stan_gate.get_docs_path
        stan_gate.get_docs_path = lambda: tmp_path / "docs"

        try:
            allowed, reason = check_devils_advocate_completed("DEFINE")
            assert not allowed, "Should block when only Pass 1 done"
            assert "PASS 2 REQUIRED" in reason
        finally:
            stan_gate.get_docs_path = original

    def test_both_passes_allows(self, tmp_path):
        """Both DA passes should allow transition."""
        self._create_doc_with_techniques(
            tmp_path, "prd.md",
            techniques=["devils-advocate", "devils-advocate-verify"]
        )

        from stan_gate import check_devils_advocate_completed
        import stan_gate
        original = stan_gate.get_docs_path
        stan_gate.get_docs_path = lambda: tmp_path / "docs"

        try:
            allowed, reason = check_devils_advocate_completed("DEFINE")
            assert allowed, f"Should allow with both passes. Reason: {reason}"
            assert reason is None
        finally:
            stan_gate.get_docs_path = original

    def test_plan_phase_checks_plan_doc(self, tmp_path):
        """PLAN phase should check plan.md, not prd.md."""
        self._create_doc_with_techniques(
            tmp_path, "plan.md",
            techniques=["devils-advocate", "devils-advocate-verify"]
        )

        from stan_gate import check_devils_advocate_completed
        import stan_gate
        original = stan_gate.get_docs_path
        stan_gate.get_docs_path = lambda: tmp_path / "docs"

        try:
            allowed, reason = check_devils_advocate_completed("PLAN")
            assert allowed, "PLAN should check plan.md"
        finally:
            stan_gate.get_docs_path = original

    def test_no_docs_dir_allows(self, tmp_path):
        """If docs dir doesn't exist, should not block."""
        from stan_gate import check_devils_advocate_completed
        import stan_gate
        original = stan_gate.get_docs_path
        stan_gate.get_docs_path = lambda: tmp_path / "nonexistent"

        try:
            allowed, reason = check_devils_advocate_completed("DEFINE")
            assert allowed, "Missing docs dir should not block"
        finally:
            stan_gate.get_docs_path = original

    def test_no_frontmatter_allows(self, tmp_path):
        """Doc without frontmatter should not block."""
        doc_path = tmp_path / "docs" / "prd.md"
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        doc_path.write_text("# Just a doc\nNo frontmatter here.", encoding="utf-8")

        from stan_gate import check_devils_advocate_completed
        import stan_gate
        original = stan_gate.get_docs_path
        stan_gate.get_docs_path = lambda: tmp_path / "docs"

        try:
            allowed, reason = check_devils_advocate_completed("DEFINE")
            assert allowed, "No frontmatter = no enforcement"
        finally:
            stan_gate.get_docs_path = original

    def test_unknown_phase_allows(self, tmp_path):
        """Unknown phase should not block."""
        from stan_gate import check_devils_advocate_completed
        allowed, reason = check_devils_advocate_completed("UNKNOWN")
        assert allowed

    def test_additional_techniques_dont_interfere(self, tmp_path):
        """Other techniques in the list should not affect DA check."""
        self._create_doc_with_techniques(
            tmp_path, "prd.md",
            techniques=[
                "mind-mapping",
                "devils-advocate",
                "five-whys",
                "devils-advocate-verify",
                "six-thinking-hats"
            ]
        )

        from stan_gate import check_devils_advocate_completed
        import stan_gate
        original = stan_gate.get_docs_path
        stan_gate.get_docs_path = lambda: tmp_path / "docs"

        try:
            allowed, reason = check_devils_advocate_completed("DEFINE")
            assert allowed, "Additional techniques should not interfere"
        finally:
            stan_gate.get_docs_path = original


# ============================================================
# Test hooks.json Structure
# ============================================================

class TestHooksJsonStructure:
    """Test that hooks.json is valid and includes DA hook."""

    @pytest.fixture
    def hooks_data(self):
        hooks_path = Path(__file__).parent.parent / "hooks" / "hooks.json"
        with open(hooks_path) as f:
            return json.load(f)

    def test_hooks_json_valid(self, hooks_data):
        assert "hooks" in hooks_data

    def test_stop_has_two_prompt_hooks(self, hooks_data):
        stop_hooks = hooks_data["hooks"]["Stop"]
        prompt_hooks = [
            h for entry in stop_hooks
            for h in entry.get("hooks", [])
            if h.get("type") == "prompt"
        ]
        assert len(prompt_hooks) >= 2, \
            f"Stop should have >=2 prompt hooks (Gate + DA), got {len(prompt_hooks)}"

    def test_da_hook_prompt_present(self, hooks_data):
        stop_hooks = hooks_data["hooks"]["Stop"]
        prompts = [
            h.get("prompt", "")
            for entry in stop_hooks
            for h in entry.get("hooks", [])
            if h.get("type") == "prompt"
        ]
        da_found = any("DEVIL'S ADVOCATE" in p for p in prompts)
        assert da_found, "DA prompt hook must be in Stop hooks"

    def test_da_hook_has_timeout(self, hooks_data):
        stop_hooks = hooks_data["hooks"]["Stop"]
        for entry in stop_hooks:
            for h in entry.get("hooks", []):
                if h.get("type") == "prompt" and "DEVIL'S ADVOCATE" in h.get("prompt", ""):
                    assert h.get("timeout", 0) >= 30, \
                        "DA hook needs sufficient timeout (>=30s)"


# ============================================================
# Test Purpose Mapping
# ============================================================

class TestPurposeMapping:
    """Test that devils-advocate is listed in the correct purposes."""

    PURPOSES_DIR = Path(__file__).parent.parent / "techniques" / "purposes"

    @pytest.mark.parametrize("purpose_file", [
        "code-review.yaml",
        "self-reflection.yaml",
        "perspective-shift.yaml",
    ])
    def test_da_listed_in_purpose(self, purpose_file):
        content = (self.PURPOSES_DIR / purpose_file).read_text(encoding="utf-8")
        assert "devils-advocate" in content, \
            f"devils-advocate must be listed in {purpose_file}"
