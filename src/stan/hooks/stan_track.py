#!/usr/bin/env python3
"""
STAN Track Hook (PostToolUse - Bash)

Trackt Test-Ergebnisse und erkennt automatisch Learnings:
- Erkennt Test-Commands (npm test, pytest, etc.)
- Speichert Exit-Code in Session State
- Erkennt ROT→GRÜN Wechsel
- Erstellt pending_learning bei Wechsel

Dieses Script ist ein Claude Code Hook.
Es liest JSON von stdin und gibt JSON auf stdout aus.

Output Format:
{
    "continue": true,
    "systemMessage": "Optionale Nachricht"
}
"""

import json
import re
import sys
from pathlib import Path

# Add library to path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from session_state import (
    record_test_result,
    add_pending_learning,
    get_pending_learnings,
    increment_error,
    reset_error_count,
)


# Test-Command Patterns
TEST_PATTERNS = [
    r'^npm\s+(?:run\s+)?test',
    r'^yarn\s+(?:run\s+)?test',
    r'^pnpm\s+(?:run\s+)?test',
    r'^pytest',
    r'^python3?\s+-m\s+pytest',
    r'^cargo\s+test',
    r'^go\s+test',
    r'^jest',
    r'^vitest',
    r'^mocha',
    r'^make\s+test',
]


def is_test_command(command: str) -> bool:
    """Prüfe ob Command ein Test-Command ist."""
    command_lower = command.strip().lower()
    for pattern in TEST_PATTERNS:
        if re.match(pattern, command_lower, re.IGNORECASE):
            return True
    return False


def extract_exit_code(tool_result: dict) -> int:
    """Extrahiere Exit-Code aus Tool-Result."""
    # Claude Code gibt exit_code im Result zurück
    if "exit_code" in tool_result:
        return tool_result["exit_code"]

    # Fallback: Prüfe Output auf Fehlermuster
    output = tool_result.get("output", "")
    if "FAILED" in output or "Error" in output or "error:" in output.lower():
        return 1

    return 0


def main():
    # Lese Hook-Input
    try:
        input_data = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        print(json.dumps({"continue": True}))
        return

    # Prüfe ob Bash-Tool
    tool_name = input_data.get("tool_name", "")
    if tool_name != "Bash":
        print(json.dumps({"continue": True}))
        return

    # Hole Command und Result
    tool_input = input_data.get("tool_input", {})
    tool_result = input_data.get("tool_result", {})
    command = tool_input.get("command", "")

    # Prüfe ob Test-Command
    if not is_test_command(command):
        print(json.dumps({"continue": True}))
        return

    # Tracke Test-Ergebnis
    exit_code = extract_exit_code(tool_result)
    result = record_test_result(command, exit_code)

    # 3-Strikes Error Tracking
    if exit_code != 0:
        # Test fehlgeschlagen → Error Counter hochzählen
        increment_error("test_failure")
    else:
        # Test erfolgreich → Error Counter zurücksetzen
        reset_error_count("test_failure")

    # ROT→GRÜN erkannt?
    message = None
    if result.get("red_to_green"):
        # Erstelle pending Learning
        add_pending_learning(
            content=f"Test '{command}' ging von ROT zu GRÜN",
            context=f"Command: {command}"
        )

        pending_count = len(get_pending_learnings())
        message = f"""
[STAN] Learning erkannt! ROT→GRÜN bei: {command}

Du hast {pending_count} pending Learning(s).
WICHTIG: Vor dem Commit speichern!
"""

    # Output
    output = {"continue": True}
    if message:
        output["systemMessage"] = message.strip()

    print(json.dumps(output))


if __name__ == "__main__":
    main()
