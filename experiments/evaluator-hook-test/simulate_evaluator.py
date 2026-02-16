#!/usr/bin/env python3
"""
Simulate Evaluator Hook Behavior

This script simulates what an evaluator prompt hook would do:
1. Read a document with checkboxes
2. Analyze if criteria are REALLY met (not just checked)
3. Return evaluation result

This helps us understand the hook flow before implementing it.
"""

import json
import re
from pathlib import Path


def parse_checkboxes(content: str) -> dict:
    """Parse checkboxes from markdown content."""
    checked = []
    unchecked = []

    for match in re.finditer(r'- \[([ xX])\] (.+)', content):
        is_checked = match.group(1).lower() == 'x'
        text = match.group(2).strip()
        if is_checked:
            checked.append(text)
        else:
            unchecked.append(text)

    return {
        "checked": checked,
        "unchecked": unchecked,
        "all_checked": len(unchecked) == 0
    }


def evaluate_criteria(doc_path: str, code_content: str = None) -> dict:
    """
    Simulate what an LLM evaluator would do.

    In reality, this would be a prompt hook that uses an LLM.
    Here we simulate the logic.
    """
    content = Path(doc_path).read_text()
    checkboxes = parse_checkboxes(content)

    evaluation = {
        "pass": True,
        "issues": [],
        "feedback": ""
    }

    # Check 1: Are all checkboxes checked?
    if not checkboxes["all_checked"]:
        evaluation["pass"] = False
        evaluation["issues"].append({
            "type": "unchecked_criteria",
            "items": checkboxes["unchecked"]
        })

    # Check 2: If "No hardcoded values" is checked, verify it's true
    if "No hardcoded values" in checkboxes["checked"]:
        # Look for hardcoded strings in code blocks
        code_blocks = re.findall(r'```python\n(.+?)```', content, re.DOTALL)
        for block in code_blocks:
            if '"Hello World"' in block or "'Hello World'" in block:
                evaluation["pass"] = False
                evaluation["issues"].append({
                    "type": "criterion_not_actually_met",
                    "criterion": "No hardcoded values",
                    "evidence": "Found hardcoded string 'Hello World' in code"
                })

    # Check 3: If "Documentation is updated" is checked but no docs found
    if "Documentation is updated" in checkboxes["checked"]:
        if "# TODO" in content or "TODO:" in content:
            evaluation["pass"] = False
            evaluation["issues"].append({
                "type": "incomplete_documentation",
                "criterion": "Documentation is updated",
                "evidence": "TODO comments still present"
            })

    # Generate feedback
    if evaluation["pass"]:
        evaluation["feedback"] = "All criteria properly met."
    else:
        issue_summaries = [f"- {i['type']}: {i.get('evidence', i.get('items', ''))}"
                          for i in evaluation["issues"]]
        evaluation["feedback"] = "Issues found:\n" + "\n".join(issue_summaries)

    return evaluation


def simulate_stop_hook_decision(evaluation: dict) -> dict:
    """
    Simulate Stop Hook decision based on evaluation.

    This is what the Stop hook would return.
    """
    if evaluation["pass"]:
        return {
            "decision": "approve",
            "reason": "All criteria verified and met.",
            "systemMessage": None
        }
    else:
        return {
            "decision": "block",
            "reason": evaluation["feedback"],
            "systemMessage": f"EVALUATOR FEEDBACK: The following issues were found:\n{evaluation['feedback']}\n\nPlease fix these issues before completing the task."
        }


def main():
    print("=" * 60)
    print("EVALUATOR HOOK SIMULATION")
    print("=" * 60)

    doc_path = Path(__file__).parent / "test-criteria.md"

    print(f"\n1. Reading document: {doc_path}")
    content = doc_path.read_text()

    print("\n2. Parsing checkboxes...")
    checkboxes = parse_checkboxes(content)
    print(f"   Checked: {checkboxes['checked']}")
    print(f"   Unchecked: {checkboxes['unchecked']}")

    print("\n3. Evaluating criteria (simulating LLM evaluation)...")
    evaluation = evaluate_criteria(str(doc_path))
    print(f"   Pass: {evaluation['pass']}")
    print(f"   Issues: {json.dumps(evaluation['issues'], indent=4)}")

    print("\n4. Simulating Stop Hook decision...")
    decision = simulate_stop_hook_decision(evaluation)
    print(f"   Decision: {decision['decision']}")
    print(f"   Reason: {decision['reason']}")

    if decision['systemMessage']:
        print(f"\n5. systemMessage that would be sent to main agent:")
        print("-" * 40)
        print(decision['systemMessage'])
        print("-" * 40)

    print("\n" + "=" * 60)
    print("CONCLUSION")
    print("=" * 60)
    print("""
Key Findings:
1. PostToolUse with prompt hook CAN evaluate edits
2. Stop hook CAN access transcript and block completion
3. systemMessage CAN provide feedback to main agent
4. The flow would be:
   - Claude edits file, checks checkboxes
   - PostToolUse prompt hook evaluates (optional)
   - When Claude tries to stop, Stop hook evaluates
   - If issues found: block + systemMessage with feedback
   - Main agent receives feedback, must iterate

IMPORTANT: This is a SIMULATION. Real test needs:
- Actual Claude Code session with hooks enabled
- Real LLM prompt evaluation (not rule-based)
- Test in separate project to avoid affecting main code
""")


if __name__ == "__main__":
    main()
