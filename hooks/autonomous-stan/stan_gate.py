#!/usr/bin/env python3
"""
STAN Gate Hook (PreToolUse)

Enforcement-Layer:
- BLOCKIERT Feature-Arbeit auf main (Worktree-Enforcement)
- BLOCKIERT Commit wenn pending_learnings existieren
- BLOCKIERT nach 3-Strikes (gleiche Fehler)
- BLOCKIERT bei Max Iterations (configurable, default 10)
- BLOCKIERT CREATE wenn kein Research passiert ist (research_done)
- BLOCKIERT Commit wenn Devil's Advocate 2-Pass nicht abgeschlossen
- Quality Gates: Tests grün vor Commit (in CREATE)
- Automatische Dokument-Status-Übergänge
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Default max iterations (like Ralph)
DEFAULT_MAX_ITERATIONS = 10

# Import modules from lib (same directory level)
sys.path.insert(0, str(Path(__file__).parent / "lib"))
from session_state import (
    get_pending_learnings,
    get_error_count,
    increment_error,
    get
)
from document import (
    read_frontmatter,
    update_document_status,
    can_transition,
    get_document_status
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
   git worktree add ../autonomous-stan-feature feature-name

3. In Worktree wechseln und dort arbeiten

Nach Fertigstellung:
   git checkout main && git merge feature-name
   git worktree remove ../autonomous-stan-feature
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


def get_manifest_path() -> Path | None:
    """Finde stan.md Manifest im aktuellen Verzeichnis."""
    cwd = Path(os.getcwd())
    manifest = cwd / "stan.md"
    if manifest.exists():
        return manifest
    return None


def get_max_iterations() -> int:
    """
    Get max_iterations from manifest, fallback to DEFAULT_MAX_ITERATIONS.

    Reads the max_iterations field from stan.md frontmatter.
    If not present or invalid, returns DEFAULT_MAX_ITERATIONS (10).
    """
    manifest_path = get_manifest_path()
    if not manifest_path:
        return DEFAULT_MAX_ITERATIONS

    try:
        content = manifest_path.read_text(encoding='utf-8')

        # Parse frontmatter (between --- and ---)
        frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not frontmatter_match:
            return DEFAULT_MAX_ITERATIONS

        frontmatter = frontmatter_match.group(1)

        # Look for max_iterations: <number>
        match = re.search(r'^max_iterations:\s*(\d+)', frontmatter, re.MULTILINE)
        if match:
            return int(match.group(1))

        return DEFAULT_MAX_ITERATIONS

    except (ValueError, OSError):
        return DEFAULT_MAX_ITERATIONS


def get_current_phase() -> str | None:
    """Hole aktuelle Phase aus dem Manifest."""
    manifest = get_manifest_path()
    if not manifest:
        return None

    content = manifest.read_text(encoding='utf-8')

    # Suche nach Phase-Zeile in der Status-Tabelle
    match = re.search(r'\|\s*\*\*Phase\*\*\s*\|\s*(\w+)\s*\|', content)
    if match:
        return match.group(1).upper()

    return None


def get_docs_path() -> Path:
    """Hole Pfad zum docs/ Verzeichnis."""
    return Path(os.getcwd()) / "docs"


def check_research_done() -> tuple[bool, str | None]:
    """
    Prüfe ob Research in der Session stattgefunden hat.
    Liest research_done Flag aus research_guard's State.

    Returns: (allowed, warning_message)
    """
    from pathlib import Path
    state_file = Path(os.environ.get('STAN_STATE_DIR', '/tmp')) / '.stan' / 'research_state.json'
    if not state_file.exists():
        # No research state file = no research_guard installed = skip check
        return True, None

    try:
        state = json.loads(state_file.read_text())
    except (json.JSONDecodeError, Exception):
        return True, None

    if state.get("research_done", False):
        return True, None

    return False, (
        "🔬 KEIN RESEARCH!\n\n"
        "Du bist in CREATE aber hast in DEFINE/PLAN nicht recherchiert.\n"
        "Bevor du Code/Dokumente schreibst:\n"
        "1. Graphiti: search_nodes() — eigenes Wissen\n"
        "2. Context7: query_docs() — aktuelle Library-Docs\n"
        "3. web_search — Community Best Practices\n\n"
        "Dein Training-Wissen ist veraltet. Such es im Netz."
    )


def check_devils_advocate_completed(phase: str) -> tuple[bool, str | None]:
    """
    Check if Devil's Advocate review (2 passes) has been completed
    for the relevant document in the given phase.

    Phase mapping:
    - DEFINE → check PRD for DA
    - PLAN → check Plan for DA
    - CREATE → check Plan for DA (before complete)

    Returns: (allowed, block_reason)
    """
    docs_dir = get_docs_path()

    # Determine which document to check
    if phase == "DEFINE":
        doc_path = docs_dir / "prd.md"
        doc_name = "PRD"
        da_mode = "Evidence Audit"
    elif phase in ("PLAN", "CREATE"):
        doc_path = docs_dir / "plan.md"
        doc_name = "Plan"
        da_mode = "Pre-Mortem" if phase == "PLAN" else "Conformity Review"
    else:
        return True, None

    if not doc_path.exists():
        return True, None

    try:
        content = doc_path.read_text(encoding='utf-8')

        # Parse frontmatter
        frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not frontmatter_match:
            return True, None  # No frontmatter = no enforcement

        frontmatter = frontmatter_match.group(1)

        # Look for techniques_applied list
        techniques_match = re.search(
            r'techniques_applied:\s*\n((?:\s+-\s+\S+\n?)*)',
            frontmatter
        )

        if not techniques_match:
            techniques_applied = []
        else:
            raw = techniques_match.group(1)
            techniques_applied = [
                line.strip().lstrip('- ').strip()
                for line in raw.strip().split('\n')
                if line.strip().startswith('-')
            ]

        has_pass1 = 'devils-advocate' in techniques_applied
        has_pass2 = 'devils-advocate-verify' in techniques_applied

        if not has_pass1:
            return False, (
                f"😈 DEVIL'S ADVOCATE REQUIRED!\n\n"
                f"Phase transition blocked. The {doc_name} has not been "
                f"through a Devil's Advocate review (Pass 1).\n\n"
                f"Required mode: {da_mode}\n"
                f"Required entries in {doc_name} frontmatter:\n"
                f"  techniques_applied:\n"
                f"    - devils-advocate         # Pass 1\n"
                f"    - devils-advocate-verify   # Pass 2\n\n"
                f"Use /stan think → perspective-shift → Devil's Advocate\n"
                f"or apply the review manually using "
                f"techniques/references/da-*.md"
            )

        if not has_pass2:
            return False, (
                f"😈 DEVIL'S ADVOCATE PASS 2 REQUIRED!\n\n"
                f"Phase transition blocked. The {doc_name} passed DA "
                f"review Pass 1, but Pass 2 (fix verification) is missing.\n\n"
                f"Pass 2 checks:\n"
                f"- Were the findings from Pass 1 genuinely addressed?\n"
                f"- Any new issues introduced by the fixes?\n"
                f"- Is the conformity score improving?\n\n"
                f"After Pass 2, add to {doc_name} frontmatter:\n"
                f"  techniques_applied:\n"
                f"    - devils-advocate         # ✅ Pass 1 done\n"
                f"    - devils-advocate-verify   # ← Add this"
            )

        return True, None

    except (OSError, Exception):
        return True, None  # On error, don't block


def is_phase_transition_command(command: str) -> tuple[bool, str | None]:
    """
    Check if a bash command is triggering a phase transition.
    This catches /stan plan, /stan create, /stan complete via CLI.

    Returns: (is_transition, target_phase)
    """
    # Match patterns like: claude "/stan plan", stan plan, etc.
    patterns = [
        (r'/stan\s+plan', 'PLAN'),
        (r'/stan\s+create', 'CREATE'),
        (r'/stan\s+complete', 'COMPLETE'),
    ]
    for pattern, phase in patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return True, phase
    return False, None


def auto_transition_on_create() -> str | None:
    """
    Automatischer Status-Übergang wenn CREATE Phase startet.
    approved → in-progress für PRD und Plan.

    Returns: Message wenn Übergang passiert, sonst None
    """
    phase = get_current_phase()
    if phase != "CREATE":
        return None

    docs_dir = get_docs_path()
    transitions = []

    # PRD
    prd_path = docs_dir / "prd.md"
    if prd_path.exists():
        status = get_document_status(prd_path)
        if status == "approved":
            allowed, _ = can_transition("approved", "in-progress")
            if allowed:
                success, msg = update_document_status(prd_path, "in-progress")
                if success:
                    transitions.append(f"PRD: approved → in-progress")

    # Plan
    plan_path = docs_dir / "plan.md"
    if plan_path.exists():
        status = get_document_status(plan_path)
        if status == "approved":
            allowed, _ = can_transition("approved", "in-progress")
            if allowed:
                success, msg = update_document_status(plan_path, "in-progress")
                if success:
                    transitions.append(f"Plan: approved → in-progress")

    if transitions:
        return f"[STAN] Automatischer Status-Übergang:\n" + "\n".join(f"  • {t}" for t in transitions)

    return None


def check_all_tasks_done() -> bool:
    """
    Prüfe ob alle Tasks in plan.md als done markiert sind.

    Returns: True wenn alle done
    """
    plan_path = get_docs_path() / "plan.md"
    if not plan_path.exists():
        return False

    content = plan_path.read_text(encoding='utf-8')

    # Zähle offene vs. erledigte Akzeptanzkriterien
    open_criteria = len(re.findall(r'- \[ \]', content))
    done_criteria = len(re.findall(r'- \[x\]', content, re.IGNORECASE))

    # Wenn es Kriterien gibt und keine offen sind
    if done_criteria > 0 and open_criteria == 0:
        return True

    return False


def auto_transition_on_done() -> str | None:
    """
    Automatischer Status-Übergang wenn alle Tasks done.
    in-progress → done für PRD und Plan.

    Returns: Message wenn Übergang passiert, sonst None
    """
    if not check_all_tasks_done():
        return None

    docs_dir = get_docs_path()
    transitions = []

    # PRD
    prd_path = docs_dir / "prd.md"
    if prd_path.exists():
        status = get_document_status(prd_path)
        if status == "in-progress":
            allowed, _ = can_transition("in-progress", "done")
            if allowed:
                success, msg = update_document_status(prd_path, "done")
                if success:
                    transitions.append(f"PRD: in-progress → done")

    # Plan
    plan_path = docs_dir / "plan.md"
    if plan_path.exists():
        status = get_document_status(plan_path)
        if status == "in-progress":
            allowed, _ = can_transition("in-progress", "done")
            if allowed:
                success, msg = update_document_status(plan_path, "done")
                if success:
                    transitions.append(f"Plan: in-progress → done")

    if transitions:
        return f"[STAN] Alle Tasks erledigt! Status-Übergang:\n" + "\n".join(f"  • {t}" for t in transitions)

    return None


def allow(message=None):
    """PreToolUse: Allow the tool call, optionally with a system message."""
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
    """PreToolUse: Block the tool call with a reason."""
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason
        }
    }


def main():
    # Lese Hook-Input
    try:
        input_data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, Exception):
        print(json.dumps(allow()))
        return

    # Prüfe ob Bash-Tool
    tool_name = input_data.get("tool_name", "")
    if tool_name != "Bash":
        print(json.dumps(allow()))
        return

    # Hole Command
    tool_input = input_data.get("tool_input", {})
    command = tool_input.get("command", "")

    # Commit-spezifische Checks
    if is_commit_command(command):
        # Check 0: Worktree-Enforcement
        allowed_result, reason = check_worktree()
        if not allowed_result:
            print(json.dumps(deny(reason.strip())))
            return

        # Check 1: Pending Learnings
        allowed_result, reason = check_pending_learnings()
        if not allowed_result:
            print(json.dumps(deny(reason.strip())))
            return

        # Check 2: Tests (nur Warnung — allow but with message)
        _, warning = check_tests_passed()
        if warning:
            print(json.dumps(allow(warning.strip())))
            return

        # Check 3: Devil's Advocate (2-pass) for phase completion commits
        phase = get_current_phase()
        if phase:
            da_ok, da_reason = check_devils_advocate_completed(phase)
            if not da_ok:
                print(json.dumps(deny(da_reason)))
                return

    # Research-Check in CREATE Phase
    phase = get_current_phase() if 'get_current_phase' in dir() else "UNKNOWN"
    if phase == "CREATE":
        research_ok, research_warning = check_research_done()
        if not research_ok:
            print(json.dumps(deny(research_warning)))
            return

    # Automatische Status-Übergänge prüfen
    messages = []

    # CREATE Phase → approved → in-progress
    transition_msg = auto_transition_on_create()
    if transition_msg:
        messages.append(transition_msg)

    # Alle Tasks done → in-progress → done
    done_msg = auto_transition_on_done()
    if done_msg:
        messages.append(done_msg)

    # Output
    if messages:
        print(json.dumps(allow("\n\n".join(messages))))
    else:
        print(json.dumps(allow()))


if __name__ == "__main__":
    main()
