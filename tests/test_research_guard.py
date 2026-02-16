#!/usr/bin/env python3
"""Tests for research_guard hook — enforces Graphiti → Context7 → Web cascade."""

import json
import sys
import pytest
from pathlib import Path
from unittest.mock import patch
from io import StringIO

sys.path.insert(0, str(Path(__file__).parent.parent / "hooks" / "autonomous-stan"))
import research_guard


def get_decision(output):
    return output["hookSpecificOutput"]["permissionDecision"]


def get_reason(output):
    return output["hookSpecificOutput"].get("permissionDecisionReason", "")


class TestResearchCascade:
    """Tests for the Graphiti → Context7 → Web research cascade."""

    def test_allows_normal_tools(self):
        """Non-research tools pass through."""
        input_data = json.dumps({"tool_name": "Bash", "tool_input": {"command": "ls"}})
        with patch('sys.stdin', StringIO(input_data)):
            with patch('sys.stdout', new_callable=StringIO) as out:
                research_guard.main()
        assert get_decision(json.loads(out.getvalue())) == "allow"

    def test_blocks_websearch_when_graphiti_available(self):
        """WebSearch blocked if Graphiti available but not searched yet."""
        input_data = json.dumps({"tool_name": "WebSearch", "tool_input": {"query": "astro docs"}})
        with patch('sys.stdin', StringIO(input_data)):
            with patch('sys.stdout', new_callable=StringIO) as out:
                with patch.object(research_guard, 'is_graphiti_available', return_value=True):
                    with patch.object(research_guard, 'graphiti_was_searched', return_value=False):
                        research_guard.main()
        result = json.loads(out.getvalue())
        assert get_decision(result) == "deny"
        assert "GRAPHITI" in get_reason(result)

    def test_allows_websearch_after_graphiti(self):
        """WebSearch allowed after Graphiti was searched."""
        input_data = json.dumps({"tool_name": "WebSearch", "tool_input": {"query": "astro docs"}})
        with patch('sys.stdin', StringIO(input_data)):
            with patch('sys.stdout', new_callable=StringIO) as out:
                with patch.object(research_guard, 'is_graphiti_available', return_value=True):
                    with patch.object(research_guard, 'graphiti_was_searched', return_value=True):
                        with patch.object(research_guard, 'is_context7_available', return_value=False):
                            research_guard.main()
        assert get_decision(json.loads(out.getvalue())) == "allow"

    def test_allows_websearch_when_no_graphiti(self):
        """WebSearch allowed if Graphiti not available at all."""
        input_data = json.dumps({"tool_name": "WebSearch", "tool_input": {"query": "general question"}})
        with patch('sys.stdin', StringIO(input_data)):
            with patch('sys.stdout', new_callable=StringIO) as out:
                with patch.object(research_guard, 'is_graphiti_available', return_value=False):
                    research_guard.main()
        assert get_decision(json.loads(out.getvalue())) == "allow"

    def test_suggests_context7_for_known_lib(self):
        """WebSearch for a known lib suggests Context7 when available."""
        input_data = json.dumps({"tool_name": "WebSearch", "tool_input": {"query": "astro docs tutorial"}})
        with patch('sys.stdin', StringIO(input_data)):
            with patch('sys.stdout', new_callable=StringIO) as out:
                with patch.object(research_guard, 'is_graphiti_available', return_value=True):
                    with patch.object(research_guard, 'graphiti_was_searched', return_value=True):
                        with patch.object(research_guard, 'is_context7_available', return_value=True):
                            with patch.object(research_guard, 'read_state', return_value={"graphiti_searched": True, "context7_libs_checked": []}):
                                research_guard.main()
        result = json.loads(out.getvalue())
        assert get_decision(result) == "allow"
        # Should have a tip about Context7
        msg = result["hookSpecificOutput"].get("message", "")
        assert "Context7" in msg or "context7" in msg

    def test_blocks_webfetch_without_graphiti_search(self):
        """WebFetch blocked if Graphiti available but not searched."""
        input_data = json.dumps({"tool_name": "WebFetch", "tool_input": {"url": "https://example.com"}})
        with patch('sys.stdin', StringIO(input_data)):
            with patch('sys.stdout', new_callable=StringIO) as out:
                with patch.object(research_guard, 'is_graphiti_available', return_value=True):
                    with patch.object(research_guard, 'graphiti_was_searched', return_value=False):
                        research_guard.main()
        assert get_decision(json.loads(out.getvalue())) == "deny"

    def test_handles_empty_input(self):
        """Empty stdin gracefully handled."""
        with patch('sys.stdin', StringIO("")):
            with patch('sys.stdout', new_callable=StringIO) as out:
                research_guard.main()
        assert get_decision(json.loads(out.getvalue())) == "allow"

    def test_is_lib_search_detection(self):
        """Known library + doc term = library search."""
        assert research_guard.is_lib_search("astro docs tutorial")[0]
        assert research_guard.is_lib_search("tailwind css documentation")[0]
        assert research_guard.is_lib_search("react api reference")[0]
        assert not research_guard.is_lib_search("weather today")[0]
        assert not research_guard.is_lib_search("best restaurants")[0]

    def test_graphiti_search_registers(self):
        """MCP bridge call to graphiti.search registers graphiti as available+searched."""
        input_data = json.dumps({
            "tool_name": "mcp__mcp-funnel__bridge_tool_request",
            "tool_input": {"tool": "graphiti.search_nodes", "arguments": {"query": "test"}}
        })
        with patch('sys.stdin', StringIO(input_data)):
            with patch('sys.stdout', new_callable=StringIO) as out:
                with patch.object(research_guard, 'write_state') as mock_write:
                    research_guard.main()
        # Should have called write_state for graphiti_available and graphiti_searched
        calls = [c[0] for c in mock_write.call_args_list]
        assert ("graphiti_available", True) in calls
        assert ("graphiti_searched", True) in calls
