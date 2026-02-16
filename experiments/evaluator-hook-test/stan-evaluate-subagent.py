#!/usr/bin/env python3
"""
STAN Evaluate Hook (PostToolUse - Edit)

Triggers Subagent-based evaluation:
1. Detects Edit tool usage
2. Reads criteria from stan.md
3. Returns systemMessage prompting main agent to spawn evaluator subagent

The main agent then uses Task tool to spawn an independent evaluator.
No API token needed - uses Claude Code subscription.
"""

import json
import sys
import os
from pathlib import Path


def find_criteria_file(cwd: str) -> Path | None:
    """Find stan.md or similar criteria file."""
    candidates = [
        "stan.md",
        "STAN.md",
        ".stan/manifest.md",
        "docs/criteria.md"
    ]
    for candidate in candidates:
        path = Path(cwd) / candidate
        if path.exists():
            return path
    return None


def read_criteria(path: Path) -> str:
    """Read criteria content from file."""
    try:
        content = path.read_text()
        # Extract acceptance criteria section if present
        if "## Acceptance Criteria" in content or "### Acceptance Criteria" in content:
            # Find the section
            lines = content.split('\n')
            in_criteria = False
            criteria_lines = []
            for line in lines:
                if 'Acceptance Criteria' in line:
                    in_criteria = True
                    criteria_lines.append(line)
                elif in_criteria:
                    if line.startswith('## ') or line.startswith('### '):
                        break  # Next section
                    criteria_lines.append(line)
            return '\n'.join(criteria_lines)
        return content[:1500]  # Fallback: first 1500 chars
    except Exception as e:
        return f"[Could not read criteria: {e}]"


def main():
    # Read hook input
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"continue": True}))
        return

    # Only trigger on Edit tool
    tool_name = hook_input.get("tool_name", "")
    if tool_name != "Edit":
        print(json.dumps({"continue": True}))
        return

    # Get edit details
    tool_input = hook_input.get("tool_input", {})
    file_path = tool_input.get("file_path", "unknown")
    old_string = tool_input.get("old_string", "")[:100]
    new_string = tool_input.get("new_string", "")[:100]

    # Find and read criteria
    cwd = hook_input.get("cwd", os.getcwd())
    criteria_file = find_criteria_file(cwd)

    if not criteria_file:
        # No criteria file, skip evaluation
        print(json.dumps({"continue": True}))
        return

    criteria = read_criteria(criteria_file)

    # Build the evaluation prompt for the subagent
    eval_prompt = f'''Evaluate this edit against the acceptance criteria.

## Criteria (from {criteria_file.name})
{criteria}

## Edit Being Evaluated
File: {file_path}
Changed: "{old_string}" → "{new_string}"

## Your Task
1. If a checkbox was marked complete: Is it ACTUALLY met?
2. If code was written: Does it meet the criteria?
3. Be skeptical - the main agent has self-serving bias.

Respond with:
- PASS: If criteria genuinely met
- FAIL: If criteria NOT met (explain why)
- WARN: If questionable (explain concern)'''

    # Build systemMessage that prompts main agent to spawn evaluator
    system_message = f"""[STAN] Edit detected - independent evaluation required.

Spawn evaluator subagent NOW:

```
Task(
    subagent_type="Explore",
    model="haiku",
    description="Evaluate edit against criteria",
    prompt=\"\"\"{eval_prompt}\"\"\"
)
```

Wait for subagent result before proceeding."""

    output = {
        "continue": True,
        "systemMessage": system_message
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()
