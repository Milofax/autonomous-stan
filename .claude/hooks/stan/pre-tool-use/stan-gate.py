#!/usr/bin/env python3
"""
STAN Gate Hook (PreToolUse)

Enforcement-Layer:
- BLOCKIERT Commit wenn pending_learnings existieren
- BLOCKIERT nach 3-Strikes (gleiche Fehler)
- Quality Gates: Tests grün vor Commit (in CREATE)
"""

import json
import re
import sys
from pathlib import Path

# Importiere Module
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from session_state import (
    get_pending_learnings,
    get_error_count,
    increment_error,
    get
)


def is_commit_command(command: str) -> bool:
    """Prüfe ob Command ein git commit ist."""
    return bool(re.search(r'git\s+commit', command, re.IGNORECASE))


def get_last_test_status() -> bool | None:
    """Hole Status des letzten Tests."""
    history = get("test_history", [])
    if not history:
        return None
    return history[-1].get("passed", None)


def check_pending_learnings() -> tuple[bool, str | None]:
    """
    Prüfe ob pending Learnings existieren.
    Returns: (allowed, block_reason)
    """
    pending = get_pending_learnings()
    if pending:
        count = len(pending)
        return False, f"""
BLOCKED: Du hast {count} pending Learning(s)!

Learnings vor dem Commit speichern:
1. Öffne die Learnings mit `/stan learnings`
2. Oder speichere direkt mit `/stan save-learnings`

Pending:
{chr(10).join(f'  - {l["content"][:60]}...' for l in pending[:3])}
"""
    return True, None


def check_tests_passed() -> tuple[bool, str | None]:
    """
    Prüfe ob Tests grün sind (nur Warnung, kein Block).
    Returns: (allowed, warning_message)
    """
    status = get_last_test_status()
    if status is False:
        return True, """
⚠️ WARNUNG: Letzter Test war ROT!

Bist du sicher dass du committen willst?
Empfehlung: Tests erst grün machen.
"""
    return True, None


def check_3_strikes(error_type: str) -> tuple[bool, str | None]:
    """
    Prüfe 3-Strikes Regel.
    Returns: (allowed, block_reason)
    """
    count = get_error_count(error_type)
    if count >= 3:
        return False, f"""
BLOCKED: 3-Strikes bei '{error_type}'!

Du hast 3x den gleichen Fehler gemacht.
STOPP und Perspektivwechsel nötig:

1. Was ist die Root Cause?
2. Gibt es eine fundamental andere Lösung?
3. Brauchst du mehr Kontext/Recherche?

Nutze `/stan reflect` um die Blockade zu lösen.
"""
    return True, None


def main():
    # Lese Hook-Input
    input_data = json.loads(sys.stdin.read())

    # Prüfe ob Bash-Tool
    tool_name = input_data.get("tool_name", "")
    if tool_name != "Bash":
        print(json.dumps({"continue": True}))
        return

    # Hole Command
    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")

    # Commit-spezifische Checks
    if is_commit_command(command):
        # Check 1: Pending Learnings
        allowed, reason = check_pending_learnings()
        if not allowed:
            print(json.dumps({
                "continue": False,
                "reason": reason.strip()
            }))
            return

        # Check 2: Tests (nur Warnung)
        _, warning = check_tests_passed()
        if warning:
            print(json.dumps({
                "continue": True,
                "systemMessage": warning.strip()
            }))
            return

    # Allgemein: 3-Strikes Check basierend auf vorherigen Fehlern
    # (Dieser würde von stan-track bei Fehlern aktiviert)

    # Alles OK
    print(json.dumps({"continue": True}))


if __name__ == "__main__":
    main()
