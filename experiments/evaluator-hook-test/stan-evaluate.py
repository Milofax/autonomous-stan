#!/usr/bin/env python3
"""
STAN Evaluate Hook (PostToolUse - Edit)

Triggers subagent-based evaluation with model selection based on criteria type.

Workflow:
1. Detects Edit tool usage
2. Reads current task from .stan/tasks.jsonl
3. Parses acceptance_criteria for {criteria-name} references
4. For Acceptance Criteria ({...}): Load YAML, get model from YAML
5. For Success Criteria (no {...}): Always use sonnet
6. Returns systemMessage prompting main agent to spawn evaluator subagent
"""

import json
import re
import sys
import os
from pathlib import Path

# Script directory for relative imports
SCRIPT_DIR = Path(__file__).parent
PROMPTS_DIR = SCRIPT_DIR / "prompts"
CRITERIA_DIR = SCRIPT_DIR.parent / "criteria"


def load_current_task(cwd: str) -> dict | None:
    """Load current in_progress task from .stan/tasks.jsonl."""
    tasks_file = Path(cwd) / ".stan" / "tasks.jsonl"
    if not tasks_file.exists():
        return None

    try:
        with open(tasks_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                task = json.loads(line)
                if task.get("status") == "in_progress":
                    return task
    except (json.JSONDecodeError, IOError):
        pass

    return None


def parse_criteria_reference(criterion: str) -> tuple[str | None, str]:
    """Parse a criterion string for {criteria-name} reference.

    Returns: (criteria_name or None, display_text)

    Examples:
        "Best practices followed {code-quality}" -> ("code-quality", "Best practices followed")
        "User finds UI beautiful" -> (None, "User finds UI beautiful")
    """
    match = re.search(r"\{([a-z0-9-]+)\}", criterion)
    if match:
        criteria_name = match.group(1)
        display_text = re.sub(r"\s*\{[a-z0-9-]+\}\s*", "", criterion).strip()
        return criteria_name, display_text
    return None, criterion


def load_criteria_yaml(criteria_name: str, cwd: str) -> tuple[str, str]:
    """Load criteria YAML and extract evaluator_model.

    Returns: (criteria_content, evaluator_model)
    """
    # Try project-local criteria first, then plugin criteria
    search_paths = [
        Path(cwd) / "criteria" / f"{criteria_name}.yaml",
        CRITERIA_DIR / f"{criteria_name}.yaml",
    ]

    for criteria_path in search_paths:
        if criteria_path.exists():
            try:
                content = criteria_path.read_text()

                # Extract evaluator_model (default: sonnet)
                evaluator_model = "sonnet"
                for line in content.split("\n"):
                    if "evaluator_model:" in line:
                        model = line.split(":")[-1].strip().lower()
                        # Remove comment if present
                        model = model.split("#")[0].strip()
                        if model in ["haiku", "sonnet", "opus"]:
                            evaluator_model = model
                        break

                return content, evaluator_model
            except IOError:
                continue

    return f"[Criteria '{criteria_name}' not found]", "sonnet"


def categorize_criteria(acceptance_criteria: list[str], cwd: str) -> dict:
    """Categorize criteria into Acceptance (with YAML) and Success (free text).

    Returns dict with:
        - acceptance: [(display_text, criteria_content, model), ...]
        - success: [display_text, ...]
        - primary_model: The model to use (haiku if all are code, else sonnet)
    """
    result = {
        "acceptance": [],
        "success": [],
        "primary_model": "sonnet",
    }

    models_used = set()

    for criterion in acceptance_criteria:
        criteria_name, display_text = parse_criteria_reference(criterion)

        if criteria_name:
            # Acceptance Criteria with YAML reference
            content, model = load_criteria_yaml(criteria_name, cwd)
            result["acceptance"].append((display_text, content, model))
            models_used.add(model)
        else:
            # Success Criteria (free text, semantic evaluation)
            result["success"].append(display_text)

    # Determine primary model
    if result["success"]:
        # Has free-text criteria -> needs semantic understanding
        result["primary_model"] = "sonnet"
    elif models_used == {"haiku"}:
        # All acceptance criteria use haiku
        result["primary_model"] = "haiku"
    else:
        # Mixed or includes sonnet/opus
        result["primary_model"] = "sonnet"

    return result


def load_prompt_template() -> str:
    """Load the evaluator prompt template."""
    prompt_path = PROMPTS_DIR / "criteria-eval.md"
    try:
        return prompt_path.read_text()
    except FileNotFoundError:
        # Fallback prompt
        return """You are the STAN Evaluator. Evaluate this edit against criteria.

## Edit
{edit_info}

## Criteria
{criteria}

Respond with PASS, FAIL, or WARN with explanation."""


def build_criteria_text(categorized: dict) -> str:
    """Build formatted criteria text for the evaluator prompt."""
    lines = []

    if categorized["acceptance"]:
        lines.append("### Acceptance Criteria (from YAML)")
        for display_text, content, model in categorized["acceptance"]:
            lines.append(f"\n**{display_text}** (evaluator: {model})")
            # Extract just the checks from YAML
            in_checks = False
            for line in content.split("\n"):
                if "checks:" in line:
                    in_checks = True
                elif in_checks and line.strip().startswith("- id:"):
                    lines.append(line)
                elif in_checks and line.strip().startswith("question:"):
                    lines.append(f"  {line.strip()}")

    if categorized["success"]:
        lines.append("\n### Success Criteria (free evaluation)")
        for criterion in categorized["success"]:
            lines.append(f"- [ ] {criterion}")

    return "\n".join(lines) if lines else "[No criteria defined]"


def main():
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
    old_string = tool_input.get("old_string", "")[:200]
    new_string = tool_input.get("new_string", "")[:200]

    cwd = hook_input.get("cwd", os.getcwd())

    # Load current task from JSONL
    current_task = load_current_task(cwd)

    if not current_task:
        # No active task, skip evaluation
        print(json.dumps({"continue": True}))
        return

    acceptance_criteria = current_task.get("acceptance_criteria", [])
    if not acceptance_criteria:
        # No criteria defined, skip evaluation
        print(json.dumps({"continue": True}))
        return

    # Categorize criteria
    categorized = categorize_criteria(acceptance_criteria, cwd)

    # Build edit info
    edit_info = f"""**File:** {file_path}
**Task:** {current_task.get('subject', 'Unknown')}
**Changed:**
```
{old_string}
```
**To:**
```
{new_string}
```"""

    # Build criteria text
    criteria_text = build_criteria_text(categorized)

    # Load prompt template
    prompt_template = load_prompt_template()

    # Fill prompt template
    eval_prompt = prompt_template.replace("{edit_info}", edit_info).replace("{criteria}", criteria_text)

    # Use the primary model determined from criteria
    evaluator_model = categorized["primary_model"]

    # Build systemMessage that prompts main agent to spawn evaluator
    system_message = f"""[STAN] Edit detected on task '{current_task.get('subject', 'Unknown')}' - evaluation required.

**Criteria Types:**
- Acceptance Criteria: {len(categorized['acceptance'])} (from YAML)
- Success Criteria: {len(categorized['success'])} (free text, semantic)

Spawn evaluator subagent NOW with model '{evaluator_model}':

```
Task(
    subagent_type="Explore",
    model="{evaluator_model}",
    description="Evaluate edit against criteria",
    prompt=\"\"\"{eval_prompt}\"\"\"
)
```

Wait for subagent result before proceeding. If FAIL, fix the issue."""

    output = {
        "continue": True,
        "systemMessage": system_message
    }

    print(json.dumps(output))


if __name__ == "__main__":
    main()
