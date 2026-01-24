#!/usr/bin/env python3
"""
STAN Gate Hook (PreToolUse)

Enforcement-Layer:
- BLOCKIERT Feature-Arbeit auf main (Worktree-Enforcement)
- BLOCKIERT Commit wenn pending_learnings existieren
- BLOCKIERT nach 3-Strikes (gleiche Fehler)
- Quality Gates: Tests grün vor Commit (Warnung)

Dieses Script ist ein Claude Code Hook.
Es liest JSON von stdin und gibt JSON auf stdout aus.

Output Format bei Block:
{
    "continue": false,
    "reason": "Grund für den Block"
}

Output Format bei Continue:
{
    "continue": true,
    "systemMessage": "Optionale Warnung/Info"
}
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Add library to path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from session_state import (
    get_pending_learnings,
    get_error_count,
    get,
    get_iteration_count,
    increment_iteration,
    set_current_task,
    get_current_task,
)
from acceptance import (
    all_criteria_checked,
    get_unchecked_criteria,
    format_unchecked_for_message,
)


def is_commit_command(command: str) -> bool:
    """Prüfe ob Command ein git commit ist."""
    return bool(re.search(r'git\s+commit', command, re.IGNORECASE))


def is_git_repo() -> bool:
    """Prüfe ob aktuelles Verzeichnis ein Git-Repo ist."""
    try:
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True,
            check=True,
            cwd=os.getcwd()
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def is_main_worktree() -> bool:
    """
    Prüfe ob wir im Haupt-Worktree sind (nicht in einem Feature-Worktree).

    Haupt-Repo: .git ist ein Verzeichnis
    Worktree: .git ist eine Datei (zeigt auf Haupt-Repo)
    """
    git_path = Path(os.getcwd()) / ".git"
    return git_path.is_dir()  # True = Haupt-Repo, False = Worktree


def get_current_branch() -> str | None:
    """Hole aktuellen Branch-Namen."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            cwd=os.getcwd()
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def is_feature_work() -> bool:
    """
    Heuristik: Ist das eine Feature-Arbeit oder triviale Änderung?

    Trivial: wenige Dateien, keine src/, keine neuen Features
    Feature: viele Dateien, src/ betroffen, oder hooks/templates/criteria
    """
    try:
        # Staged files
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
            cwd=os.getcwd()
        )
        staged = result.stdout.strip().split("\n") if result.stdout.strip() else []

        # Feature-Indikatoren
        feature_patterns = [
            "src/",
            ".claude/hooks/",
            "templates/",
            "criteria/",
            ".claude/commands/",
        ]

        # Wenn mehr als 5 Dateien oder Feature-Pattern betroffen
        if len(staged) > 5:
            return True

        for file in staged:
            for pattern in feature_patterns:
                if pattern in file:
                    return True

        return False
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_worktree() -> tuple[bool, str | None]:
    """
    Prüfe Worktree-Regel: Feature-Arbeit nur in Worktree, nicht auf main.
    Returns: (allowed, block_reason)
    """
    # Nur bei Git-Projekten
    if not is_git_repo():
        return True, None

    # Nur wenn auf main/master
    branch = get_current_branch()
    if branch not in ("main", "master"):
        return True, None

    # Nur wenn im Haupt-Worktree
    if not is_main_worktree():
        return True, None

    # Nur wenn Feature-Arbeit
    if not is_feature_work():
        return True, None

    # Feature-Arbeit auf main im Haupt-Repo → BLOCK
    return False, """
BLOCKED: Feature-Arbeit auf main erkannt!

Nutze einen Worktree für Feature-Entwicklung:

1. Branch erstellen:
   git branch feature-name

2. Worktree erstellen:
   git worktree add ../project-feature feature-name

3. In Worktree wechseln und dort arbeiten

Nach Fertigstellung:
   git checkout main && git merge feature-name
   git worktree remove ../project-feature
   git branch -d feature-name
"""


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
        learning_list = "\n".join(f"  - {l['content'][:60]}..." for l in pending[:3])
        return False, f"""
BLOCKED: Du hast {count} pending Learning(s)!

Learnings vor dem Commit speichern:
{learning_list}
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
WARNUNG: Letzter Test war ROT!

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
"""
    return True, None


def find_plan_file() -> Path | None:
    """Finde docs/plan.md im aktuellen Projekt."""
    cwd = Path(os.getcwd())
    plan_path = cwd / "docs" / "plan.md"
    if plan_path.exists():
        return plan_path
    return None


def get_max_iterations() -> int:
    """Hole max_iterations aus stan.md oder Default (10)."""
    # Default wie Ralph
    return 10


def check_acceptance_criteria() -> tuple[bool, str | None]:
    """
    Prüfe ob alle Acceptance Criteria abgehakt sind (Ralph-Style Loop).
    Returns: (allowed, block_reason)
    """
    plan_path = find_plan_file()
    if not plan_path:
        # Kein Plan → kein Check
        return True, None

    # Alle Checkboxen abgehakt?
    if all_criteria_checked(plan_path):
        return True, None

    # Unchecked Criteria → Block
    unchecked = get_unchecked_criteria(plan_path)
    iteration = increment_iteration()
    max_iter = get_max_iterations()

    # Max-Iterations Check
    if iteration >= max_iter:
        return False, f"""
BLOCKED: Max {max_iter} Iterationen erreicht!

Eskalation nötig:
1. Recherchiere in Graphiti nach ähnlichen Problemen
2. Überprüfe die Acceptance Criteria - sind sie realistisch?
3. Brauchst du externe Hilfe?

Offene Criteria ({len(unchecked)}):
{format_unchecked_for_message(unchecked)}
"""

    # Noch unter Max → Block mit Info
    return False, f"""
BLOCKED: {len(unchecked)} Acceptance Criteria nicht abgehakt!

{format_unchecked_for_message(unchecked)}

Iteration {iteration}/{max_iter} - Weiter arbeiten bis alle abgehakt.
"""


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

    # Hole Command
    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")

    # Commit-spezifische Checks
    if is_commit_command(command):
        # Check 0: Worktree-Enforcement
        allowed, reason = check_worktree()
        if not allowed:
            print(json.dumps({
                "continue": False,
                "reason": reason.strip()
            }))
            return

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

        # Check 3: Acceptance Criteria (Ralph-Style Loop)
        allowed, reason = check_acceptance_criteria()
        if not allowed:
            print(json.dumps({
                "continue": False,
                "reason": reason.strip()
            }))
            return

    # Default: Allow
    print(json.dumps({"continue": True}))


if __name__ == "__main__":
    main()
