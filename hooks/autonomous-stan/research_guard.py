#!/usr/bin/env python3
"""
Research Guard — Forces research before architecture/technology decisions.

PreToolUse Hook for Edit/Write/MultiEdit.
Detects when the agent is making technology choices, architecture decisions,
or writing configuration without having researched first.

The guard checks session state for evidence of research (web_search, web_fetch,
context7 queries) before allowing edits that contain technology-specific content.
"""

import json
import sys
import os
import re
from pathlib import Path

# Patterns that indicate technology/architecture decisions
DECISION_PATTERNS = [
    # CSS values that should come from tools like Utopia.fyi
    r'clamp\(\s*[\d.]+rem',
    r'font-size:\s*[\d.]+(?:px|rem|em)',
    # Framework config files
    r'astro\.config',
    r'next\.config',
    r'vite\.config',
    r'tailwind\.config',
    r'tsconfig',
    # Package choices
    r'"dependencies"',
    r'"devDependencies"',
    # Architecture patterns
    r'(?:import|from)\s+[\'"](?:react|vue|svelte|angular)',
    # API endpoints / versions
    r'api/v\d+',
    r'https?://api\.',
]

# File types that typically contain architecture decisions
DECISION_FILES = [
    'package.json', 'Cargo.toml', 'pyproject.toml', 'go.mod',
    'Dockerfile', 'docker-compose', '.env',
    'astro.config', 'next.config', 'vite.config', 'tailwind.config',
    'tsconfig.json', 'webpack.config',
]

# Evidence that research was done (tool names from session)
RESEARCH_EVIDENCE_TOOLS = [
    'web_search', 'web_fetch', 'context7', 'firecrawl',
    'WebSearch', 'WebFetch',
]


def check_session_for_research():
    """Check if research tools were used in the current session."""
    state_dir = Path(os.environ.get('STAN_STATE_DIR', '/tmp'))
    state_file = state_dir / '.stan' / 'session_state.json'

    if not state_file.exists():
        return False

    try:
        data = json.loads(state_file.read_text())
        research_count = data.get('research_count', 0)
        return research_count > 0
    except (json.JSONDecodeError, Exception):
        return False


def increment_research_count():
    """Track that research was performed."""
    state_dir = Path(os.environ.get('STAN_STATE_DIR', '/tmp'))
    state_file = state_dir / '.stan' / 'session_state.json'
    state_file.parent.mkdir(parents=True, exist_ok=True)

    data = {}
    if state_file.exists():
        try:
            data = json.loads(state_file.read_text())
        except (json.JSONDecodeError, Exception):
            pass

    data['research_count'] = data.get('research_count', 0) + 1
    state_file.write_text(json.dumps(data))


def is_decision_file(file_path):
    """Check if the file typically contains architecture decisions."""
    if not file_path:
        return False
    name = Path(file_path).name.lower()
    return any(df.lower() in name for df in DECISION_FILES)


def contains_decision_pattern(content):
    """Check if content contains technology/architecture decision patterns."""
    if not content:
        return False
    for pattern in DECISION_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            return True
    return False


def allow(message=None):
    result = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow"
        }
    }
    if message:
        result["hookSpecificOutput"]["message"] = message
    return result


def deny(reason):
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason
        }
    }


def main():
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, Exception):
        print(json.dumps(allow()))
        return

    tool_name = input_data.get("tool_name", "")

    # Track research tool usage (PostToolUse context)
    if tool_name in RESEARCH_EVIDENCE_TOOLS:
        increment_research_count()
        print(json.dumps(allow()))
        return

    # Only check Edit/Write/MultiEdit
    if tool_name not in ("Edit", "Write", "MultiEdit"):
        print(json.dumps(allow()))
        return

    tool_input = input_data.get("tool_input", {})
    file_path = tool_input.get("file_path", tool_input.get("path", ""))
    new_content = tool_input.get("new_string", tool_input.get("content", ""))

    # Check: Is this a decision file or does it contain decision patterns?
    is_decision = is_decision_file(file_path) or contains_decision_pattern(new_content)

    if not is_decision:
        print(json.dumps(allow()))
        return

    # Check: Was research done in this session?
    if check_session_for_research():
        print(json.dumps(allow(
            "✅ Research-Nachweis vorhanden. Architektur-Entscheidung erlaubt."
        )))
        return

    # BLOCK: Architecture decision without research
    print(json.dumps(deny(
        "🔬 RESEARCH REQUIRED!\n\n"
        "Du triffst eine Architektur-/Technologie-Entscheidung ohne vorher recherchiert zu haben.\n\n"
        f"Datei: {file_path}\n\n"
        "BEVOR du diese Änderung machen kannst:\n"
        "1. Recherchiere aktuelle Best Practices (web_search, Context7, Docs)\n"
        "2. Vergleiche mindestens 2 Ansätze\n"
        "3. Dann erst editieren\n\n"
        "Tools: web_search, context7 (query-docs), web_fetch\n"
        "Dein Training-Wissen ist veraltet. Such es im Netz."
    )))


if __name__ == "__main__":
    main()
