#!/usr/bin/env python3
"""
STAN Evaluator Prototype - Command Hook with LLM API Call

This hook:
1. Reads criteria from stan.md or task files
2. Reads recent transcript for context
3. Calls LLM API (Haiku for speed/cost)
4. Evaluates edit against actual criteria
5. Returns feedback as systemMessage
"""

import json
import sys
import os
from pathlib import Path

# Optional: Use Anthropic SDK if available
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


def read_stdin():
    """Read hook input from stdin."""
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError as e:
        return {"error": f"Failed to parse stdin: {e}"}


def find_criteria_file(cwd: str) -> str | None:
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
            return str(path)
    return None


def read_file_safely(path: str, max_lines: int = 100) -> str:
    """Read file with line limit."""
    try:
        with open(path, 'r') as f:
            lines = f.readlines()[:max_lines]
            return ''.join(lines)
    except Exception as e:
        return f"[Could not read: {e}]"


def read_transcript_tail(path: str, max_lines: int = 50) -> str:
    """Read last N lines of transcript for context."""
    try:
        with open(path, 'r') as f:
            lines = f.readlines()
            tail = lines[-max_lines:] if len(lines) > max_lines else lines
            return ''.join(tail)
    except Exception as e:
        return f"[Could not read transcript: {e}]"


def call_llm_evaluator(prompt: str, api_key: str = None, base_url: str = None) -> str:
    """Call LLM API to evaluate."""
    if not HAS_ANTHROPIC:
        return "[Anthropic SDK not installed - evaluation skipped]"

    # Get API key from environment if not provided
    if not api_key:
        api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        return "[No API key - evaluation skipped]"

    try:
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url

        client = anthropic.Anthropic(**client_kwargs)

        response = client.messages.create(
            model="claude-3-5-haiku-20241022",  # Fast & cheap
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        return response.content[0].text
    except Exception as e:
        return f"[LLM call failed: {e}]"


def build_evaluation_prompt(
    file_path: str,
    old_string: str,
    new_string: str,
    criteria_content: str,
    transcript_tail: str
) -> str:
    """Build the evaluation prompt."""
    return f"""You are the STAN EVALUATOR - independent quality checker.

## Current Criteria (from stan.md)
{criteria_content[:2000]}

## Recent Context (transcript tail)
{transcript_tail[:1000]}

## Edit Being Evaluated
File: {file_path}
Change: "{old_string[:200]}" → "{new_string[:200]}"

## Your Task
Evaluate this edit against the criteria above:

1. If a checkbox was marked complete: Is the criterion ACTUALLY met based on the criteria?
2. If code was written: Does it meet the acceptance criteria?
3. Is this a legitimate completion or superficial checkbox-ticking?

Be skeptical. The main agent has self-serving bias.

Respond in 1-2 sentences. If issues found, be specific. If legitimate, confirm briefly."""


def main():
    # 1. Read hook input
    hook_input = read_stdin()

    if "error" in hook_input:
        output = {
            "continue": True,
            "systemMessage": f"[STAN Evaluator] {hook_input['error']}"
        }
        print(json.dumps(output))
        return

    # 2. Extract relevant fields
    cwd = hook_input.get("cwd", ".")
    transcript_path = hook_input.get("transcript_path", "")
    tool_input = hook_input.get("tool_input", {})

    file_path = tool_input.get("file_path", "unknown")
    old_string = tool_input.get("old_string", "")
    new_string = tool_input.get("new_string", "")

    # 3. Find and read criteria
    criteria_file = find_criteria_file(cwd)
    if criteria_file:
        criteria_content = read_file_safely(criteria_file)
    else:
        criteria_content = "[No stan.md found - using generic evaluation]"

    # 4. Read transcript tail for context
    transcript_tail = ""
    if transcript_path:
        transcript_tail = read_transcript_tail(transcript_path)

    # 5. Build evaluation prompt
    eval_prompt = build_evaluation_prompt(
        file_path=file_path,
        old_string=old_string,
        new_string=new_string,
        criteria_content=criteria_content,
        transcript_tail=transcript_tail
    )

    # 6. Call LLM for evaluation
    # Check for custom API endpoint (e.g., CLIProxyAPI)
    base_url = os.environ.get("ANTHROPIC_BASE_URL")
    evaluation = call_llm_evaluator(eval_prompt, base_url=base_url)

    # 7. Build output
    output = {
        "continue": True,  # Don't block, just provide feedback
        "systemMessage": f"[STAN Evaluator] {evaluation}"
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()
