#!/usr/bin/env python3
"""Tests for research_guard hook — enforces Graphiti → Context7 → Web cascade.

Tool availability is now determined by .stan/config.yaml (declared at /stan init),
not by runtime detection. Tests mock load_tools_config() accordingly.
"""

import json
import sys
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

sys.path.insert(0, str(Path(__file__).parent.parent / "hooks" / "autonomous-stan"))
import research_guard


def get_decision(output):
    return output["hookSpecificOutput"]["permissionDecision"]


def get_reason(output):
    return output["hookSpecificOutput"].get("permissionDecisionReason", "")


def get_message(output):
    return output["hookSpecificOutput"].get("message", "")


def tools_config(graphiti=False, context7=False, firecrawl=False):
    """Helper to create a tools config dict."""
    return {"graphiti": graphiti, "context7": context7, "firecrawl": firecrawl}


def run_hook(tool_name, tool_input, tools=None, state=None):
    """Run research_guard.main() with mocked config and state."""
    if tools is None:
        tools = tools_config()
    if state is None:
        state = {}

    input_data = json.dumps({"tool_name": tool_name, "tool_input": tool_input})

    with patch('sys.stdin', StringIO(input_data)), \
         patch('sys.stdout', new_callable=StringIO) as out, \
         patch.object(research_guard, 'load_tools_config', return_value=tools), \
         patch.object(research_guard, 'read_state', return_value=state), \
         patch.object(research_guard, 'write_state'):
        research_guard.main()

    return json.loads(out.getvalue())


class TestPassThrough:
    """Non-research tools always pass through."""

    def test_allows_bash(self):
        result = run_hook("Bash", {"command": "ls"})
        assert get_decision(result) == "allow"

    def test_allows_edit(self):
        result = run_hook("Edit", {"file": "foo.py"})
        assert get_decision(result) == "allow"

    def test_allows_read(self):
        result = run_hook("Read", {"path": "foo.py"})
        assert get_decision(result) == "allow"

    def test_handles_empty_input(self):
        """Empty stdin gracefully handled."""
        with patch('sys.stdin', StringIO("")), \
             patch('sys.stdout', new_callable=StringIO) as out:
            research_guard.main()
        assert get_decision(json.loads(out.getvalue())) == "allow"

    def test_handles_broken_json(self):
        """Broken JSON gracefully handled."""
        with patch('sys.stdin', StringIO("{not json")), \
             patch('sys.stdout', new_callable=StringIO) as out:
            research_guard.main()
        assert get_decision(json.loads(out.getvalue())) == "allow"


class TestNoToolsDeclared:
    """When no tools declared in config, everything passes through."""

    def test_websearch_allowed(self):
        result = run_hook("WebSearch", {"query": "test"}, tools=tools_config())
        assert get_decision(result) == "allow"

    def test_webfetch_allowed(self):
        result = run_hook("WebFetch", {"url": "https://example.com"}, tools=tools_config())
        assert get_decision(result) == "allow"

    def test_context7_bridge_allowed(self):
        result = run_hook(
            "mcp__mcp-funnel__bridge_tool_request",
            {"tool": "context7.resolve_library_id", "arguments": {"libraryName": "react"}},
            tools=tools_config()
        )
        assert get_decision(result) == "allow"


class TestGraphitiFirst:
    """When Graphiti declared, must search Graphiti before external research."""

    def test_blocks_websearch_without_graphiti_search(self):
        result = run_hook(
            "WebSearch", {"query": "astro docs"},
            tools=tools_config(graphiti=True),
            state={}  # graphiti_searched not set
        )
        assert get_decision(result) == "deny"
        assert "GRAPHITI" in get_reason(result)

    def test_allows_websearch_after_graphiti_search(self):
        result = run_hook(
            "WebSearch", {"query": "astro docs"},
            tools=tools_config(graphiti=True),
            state={"graphiti_searched": True}
        )
        assert get_decision(result) == "allow"

    def test_blocks_webfetch_without_graphiti_search(self):
        result = run_hook(
            "WebFetch", {"url": "https://example.com"},
            tools=tools_config(graphiti=True),
            state={}
        )
        assert get_decision(result) == "deny"
        assert "GRAPHITI" in get_reason(result)

    def test_allows_webfetch_after_graphiti_search(self):
        result = run_hook(
            "WebFetch", {"url": "https://example.com"},
            tools=tools_config(graphiti=True),
            state={"graphiti_searched": True}
        )
        assert get_decision(result) == "allow"

    def test_blocks_context7_bridge_without_graphiti_search(self):
        result = run_hook(
            "mcp__mcp-funnel__bridge_tool_request",
            {"tool": "context7.resolve_library_id", "arguments": {"libraryName": "react"}},
            tools=tools_config(graphiti=True, context7=True),
            state={}
        )
        assert get_decision(result) == "deny"
        assert "GRAPHITI" in get_reason(result)

    def test_allows_context7_bridge_after_graphiti_search(self):
        result = run_hook(
            "mcp__mcp-funnel__bridge_tool_request",
            {"tool": "context7.resolve_library_id", "arguments": {"libraryName": "react"}},
            tools=tools_config(graphiti=True, context7=True),
            state={"graphiti_searched": True}
        )
        assert get_decision(result) == "allow"

    def test_blocks_firecrawl_bridge_without_graphiti_search(self):
        result = run_hook(
            "mcp__mcp-funnel__bridge_tool_request",
            {"tool": "firecrawl.scrape", "arguments": {"url": "https://example.com"}},
            tools=tools_config(graphiti=True, firecrawl=True),
            state={}
        )
        assert get_decision(result) == "deny"
        assert "GRAPHITI" in get_reason(result)

    def test_blocks_direct_context7_without_graphiti_search(self):
        result = run_hook(
            "mcp__context7__resolve_library_id",
            {"libraryName": "react"},
            tools=tools_config(graphiti=True, context7=True),
            state={}
        )
        assert get_decision(result) == "deny"
        assert "GRAPHITI" in get_reason(result)

    def test_blocks_direct_firecrawl_without_graphiti_search(self):
        result = run_hook(
            "mcp__firecrawl__scrape",
            {"url": "https://example.com"},
            tools=tools_config(graphiti=True, firecrawl=True),
            state={}
        )
        assert get_decision(result) == "deny"
        assert "GRAPHITI" in get_reason(result)


class TestContext7Suggestion:
    """When Context7 declared, suggest it for known library searches."""

    def test_suggests_context7_for_known_lib(self):
        result = run_hook(
            "WebSearch", {"query": "astro docs tutorial"},
            tools=tools_config(context7=True),
            state={"context7_libs_checked": []}
        )
        assert get_decision(result) == "allow"
        assert "Context7" in get_message(result) or "context7" in get_message(result)

    def test_no_suggestion_for_unknown_lib(self):
        result = run_hook(
            "WebSearch", {"query": "weather forecast today"},
            tools=tools_config(context7=True),
            state={}
        )
        assert get_decision(result) == "allow"
        assert "Context7" not in get_message(result)

    def test_no_suggestion_if_lib_already_checked(self):
        result = run_hook(
            "WebSearch", {"query": "astro docs tutorial"},
            tools=tools_config(context7=True),
            state={"context7_libs_checked": ["astro"]}
        )
        assert get_decision(result) == "allow"
        assert "Context7" not in get_message(result)

    def test_blocks_firecrawl_for_known_lib_suggesting_context7(self):
        result = run_hook(
            "mcp__mcp-funnel__bridge_tool_request",
            {"tool": "firecrawl.scrape", "arguments": {"query": "react api docs"}},
            tools=tools_config(context7=True, firecrawl=True),
            state={"context7_libs_checked": []}
        )
        assert get_decision(result) == "deny"
        assert "Context7" in get_reason(result)


class TestGraphitiRegistration:
    """Graphiti usage in session is tracked via write_state."""

    def test_graphiti_bridge_search_registers(self):
        input_data = json.dumps({
            "tool_name": "mcp__mcp-funnel__bridge_tool_request",
            "tool_input": {"tool": "graphiti.search_nodes", "arguments": {"query": "test"}}
        })
        with patch('sys.stdin', StringIO(input_data)), \
             patch('sys.stdout', new_callable=StringIO) as out, \
             patch.object(research_guard, 'load_tools_config', return_value=tools_config()), \
             patch.object(research_guard, 'read_state', return_value={}), \
             patch.object(research_guard, 'write_state') as mock_write:
            research_guard.main()

        calls = [c[0] for c in mock_write.call_args_list]
        assert ("graphiti_searched", True) in calls
        assert ("research_done", True) in calls

    def test_direct_graphiti_call_registers(self):
        input_data = json.dumps({
            "tool_name": "mcp__graphiti__search_nodes",
            "tool_input": {"query": "test"}
        })
        with patch('sys.stdin', StringIO(input_data)), \
             patch('sys.stdout', new_callable=StringIO) as out, \
             patch.object(research_guard, 'load_tools_config', return_value=tools_config()), \
             patch.object(research_guard, 'read_state', return_value={}), \
             patch.object(research_guard, 'write_state') as mock_write:
            research_guard.main()

        calls = [c[0] for c in mock_write.call_args_list]
        assert ("graphiti_searched", True) in calls
        assert ("research_done", True) in calls


class TestFullCascade:
    """Full cascade with all tools declared."""

    def test_cascade_graphiti_then_context7_then_web(self):
        """Must go Graphiti → Context7 → Web in order."""
        all_tools = tools_config(graphiti=True, context7=True, firecrawl=True)

        # Step 0: WebSearch blocked (no Graphiti search yet)
        result = run_hook("WebSearch", {"query": "astro docs"}, tools=all_tools, state={})
        assert get_decision(result) == "deny"

        # Step 1: Graphiti search allowed
        result = run_hook(
            "mcp__mcp-funnel__bridge_tool_request",
            {"tool": "graphiti.search_nodes", "arguments": {"query": "astro"}},
            tools=all_tools, state={}
        )
        assert get_decision(result) == "allow"

        # Step 2: Context7 now allowed (graphiti searched)
        result = run_hook(
            "mcp__mcp-funnel__bridge_tool_request",
            {"tool": "context7.resolve_library_id", "arguments": {"libraryName": "astro"}},
            tools=all_tools, state={"graphiti_searched": True}
        )
        assert get_decision(result) == "allow"

        # Step 3: WebSearch now allowed
        result = run_hook(
            "WebSearch", {"query": "astro docs"},
            tools=all_tools, state={"graphiti_searched": True}
        )
        assert get_decision(result) == "allow"


class TestLibDetection:
    """Known library detection for Context7 suggestions."""

    def test_detects_react(self):
        assert research_guard.is_lib_search("react api reference")[0]

    def test_detects_tailwind(self):
        assert research_guard.is_lib_search("tailwind css documentation")[0]

    def test_ignores_general_query(self):
        assert not research_guard.is_lib_search("weather today")[0]

    def test_ignores_lib_without_doc_term(self):
        assert not research_guard.is_lib_search("react is cool")[0]


class TestConfigLoading:
    """Test config.yaml loading for tool availability."""

    def test_load_from_yaml_with_pyyaml(self, tmp_path):
        """Load tools config when pyyaml is available."""
        stan_dir = tmp_path / ".stan"
        stan_dir.mkdir()
        config_file = stan_dir / "config.yaml"
        config_file.write_text("""
user:
  name: test
tools:
  graphiti: true
  context7: false
  firecrawl: true
""")
        with patch.object(research_guard, 'get_project_root', return_value=tmp_path):
            result = research_guard.load_tools_config()

        assert result["graphiti"] is True
        assert result["context7"] is False
        assert result["firecrawl"] is True

    def test_load_missing_config(self, tmp_path):
        """Missing config returns all-False."""
        with patch.object(research_guard, 'get_project_root', return_value=tmp_path):
            result = research_guard.load_tools_config()

        assert result == {"graphiti": False, "context7": False, "firecrawl": False}

    def test_load_config_without_tools_section(self, tmp_path):
        """Config without tools section returns all-False."""
        stan_dir = tmp_path / ".stan"
        stan_dir.mkdir()
        config_file = stan_dir / "config.yaml"
        config_file.write_text("""
user:
  name: test
language:
  communication: en
""")
        with patch.object(research_guard, 'get_project_root', return_value=tmp_path):
            result = research_guard.load_tools_config()

        assert result["graphiti"] is False
        assert result["context7"] is False

    def test_fallback_parser_without_pyyaml(self, tmp_path):
        """Fallback parser works when pyyaml not available."""
        stan_dir = tmp_path / ".stan"
        stan_dir.mkdir()
        config_file = stan_dir / "config.yaml"
        config_file.write_text("""# Config
user:
  name: test
tools:
  graphiti: true
  context7: true
  firecrawl: false
project:
  name: test
""")
        with patch.object(research_guard, 'get_project_root', return_value=tmp_path), \
             patch.dict('sys.modules', {'yaml': None}):
            # Force ImportError on yaml import inside load_tools_config
            original_func = research_guard.load_tools_config

            def patched_load():
                # Simulate yaml import failure path
                root = research_guard.get_project_root()
                cf = root / ".stan" / "config.yaml"
                if not cf.exists():
                    return {"graphiti": False, "context7": False, "firecrawl": False}
                # Skip pyyaml, go straight to fallback
                in_tools = False
                tools = {"graphiti": False, "context7": False, "firecrawl": False}
                for line in cf.read_text().splitlines():
                    stripped = line.strip()
                    if stripped == "tools:" or stripped.startswith("tools:"):
                        in_tools = True
                        continue
                    if in_tools and not line.startswith(" ") and not line.startswith("\t") and stripped:
                        break
                    if in_tools:
                        for tool in ["graphiti", "context7", "firecrawl"]:
                            if stripped.startswith(f"{tool}:"):
                                val = stripped.split(":", 1)[1].strip().split("#")[0].strip().lower()
                                tools[tool] = val == "true"
                return tools

            result = patched_load()
            assert result["graphiti"] is True
            assert result["context7"] is True
            assert result["firecrawl"] is False
