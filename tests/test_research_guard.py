#!/usr/bin/env python3
"""Tests for research_guard hook."""

import json
import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch
from io import StringIO

# Add hooks path
sys.path.insert(0, str(Path(__file__).parent.parent / "hooks" / "autonomous-stan"))
import research_guard


class TestResearchGuard:
    """Tests for the research guard hook."""

    def test_allows_normal_edit(self):
        """Regular markdown edit should pass through."""
        input_data = json.dumps({
            "tool_name": "Edit",
            "tool_input": {"file_path": "README.md", "new_string": "# Hello"}
        })
        with patch('sys.stdin', StringIO(input_data)):
            with patch('sys.stdout', new_callable=StringIO) as out:
                research_guard.main()
        result = json.loads(out.getvalue())
        assert result["hookSpecificOutput"]["permissionDecision"] == "allow"

    def test_blocks_config_without_research(self):
        """Writing a config file without research should be blocked."""
        input_data = json.dumps({
            "tool_name": "Write",
            "tool_input": {
                "file_path": "astro.config.mjs",
                "content": "export default defineConfig({})"
            }
        })
        with patch('sys.stdin', StringIO(input_data)):
            with patch('sys.stdout', new_callable=StringIO) as out:
                with patch.object(research_guard, 'check_session_for_research', return_value=False):
                    research_guard.main()
        result = json.loads(out.getvalue())
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
        assert "RESEARCH REQUIRED" in result["hookSpecificOutput"]["permissionDecisionReason"]

    def test_allows_config_with_research(self):
        """Writing a config file AFTER research should be allowed."""
        input_data = json.dumps({
            "tool_name": "Write",
            "tool_input": {
                "file_path": "astro.config.mjs",
                "content": "export default defineConfig({})"
            }
        })
        with patch('sys.stdin', StringIO(input_data)):
            with patch('sys.stdout', new_callable=StringIO) as out:
                with patch.object(research_guard, 'check_session_for_research', return_value=True):
                    research_guard.main()
        result = json.loads(out.getvalue())
        assert result["hookSpecificOutput"]["permissionDecision"] == "allow"

    def test_blocks_clamp_without_research(self):
        """CSS clamp() values without research = blocked."""
        input_data = json.dumps({
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "styles.css",
                "new_string": "font-size: clamp(1.2rem, 2vw, 2.4rem);"
            }
        })
        with patch('sys.stdin', StringIO(input_data)):
            with patch('sys.stdout', new_callable=StringIO) as out:
                with patch.object(research_guard, 'check_session_for_research', return_value=False):
                    research_guard.main()
        result = json.loads(out.getvalue())
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"

    def test_blocks_package_json_without_research(self):
        """Adding dependencies without research = blocked."""
        input_data = json.dumps({
            "tool_name": "Edit",
            "tool_input": {
                "file_path": "package.json",
                "new_string": '"dependencies": { "react": "^19" }'
            }
        })
        with patch('sys.stdin', StringIO(input_data)):
            with patch('sys.stdout', new_callable=StringIO) as out:
                with patch.object(research_guard, 'check_session_for_research', return_value=False):
                    research_guard.main()
        result = json.loads(out.getvalue())
        assert result["hookSpecificOutput"]["permissionDecision"] == "deny"

    def test_allows_non_edit_tools(self):
        """Bash, Read etc. should always pass."""
        input_data = json.dumps({
            "tool_name": "Bash",
            "tool_input": {"command": "npm install"}
        })
        with patch('sys.stdin', StringIO(input_data)):
            with patch('sys.stdout', new_callable=StringIO) as out:
                research_guard.main()
        result = json.loads(out.getvalue())
        assert result["hookSpecificOutput"]["permissionDecision"] == "allow"

    def test_handles_empty_input(self):
        """Empty stdin should not crash."""
        with patch('sys.stdin', StringIO("")):
            with patch('sys.stdout', new_callable=StringIO) as out:
                research_guard.main()
        result = json.loads(out.getvalue())
        assert result["hookSpecificOutput"]["permissionDecision"] == "allow"

    def test_detects_decision_files(self):
        """Known config files should be detected."""
        assert research_guard.is_decision_file("package.json")
        assert research_guard.is_decision_file("src/astro.config.mjs")
        assert research_guard.is_decision_file("Dockerfile")
        assert not research_guard.is_decision_file("README.md")
        assert not research_guard.is_decision_file("src/app.ts")

    def test_detects_decision_patterns(self):
        """Technology choice patterns should be detected."""
        assert research_guard.contains_decision_pattern('font-size: clamp(1.5rem, 2vw, 3rem);')
        assert research_guard.contains_decision_pattern('import React from "react"')
        assert research_guard.contains_decision_pattern('"dependencies": {}')
        assert not research_guard.contains_decision_pattern('console.log("hello")')
        assert not research_guard.contains_decision_pattern('# Just a comment')
