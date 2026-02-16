#!/usr/bin/env python3
"""
Credential Guard (PreToolUse Hook)

Blocks git add/commit when staged files contain secrets.
Uses 905 regex patterns from secrets-patterns-db.

Source: taming-stan credential protection, adapted for autonomous-stan.
"""
import json
import sys
import os
import subprocess
import re

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
from secret_patterns import detect_secret, has_keyword_with_value

STRIKE_FILE = os.path.join(os.getcwd(), ".stan", "credential_strikes.json")
MAX_STRIKES = 3


def allow():
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "allow"
        }
    }


def deny(msg):
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": msg
        }
    }


def get_strikes():
    try:
        with open(STRIKE_FILE) as f:
            return json.load(f).get("count", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0


def add_strike():
    count = get_strikes() + 1
    os.makedirs(os.path.dirname(STRIKE_FILE), exist_ok=True)
    with open(STRIKE_FILE, "w") as f:
        json.dump({"count": count}, f)
    return count


def get_staged_content():
    """Get content of staged files via git diff --cached."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--diff-filter=ACMR", "-U0"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout if result.returncode == 0 else ""
    except Exception:
        return ""


def get_file_content(filepath):
    """Read file content for checking before git add."""
    try:
        with open(filepath) as f:
            return f.read()
    except Exception:
        return ""


def scan_for_secrets(content):
    """Scan content for secrets. Returns list of (pattern_name, match) tuples."""
    findings = []
    for line in content.split("\n"):
        # Skip removed lines in diffs
        if line.startswith("-") and not line.startswith("---"):
            continue
        # Check added lines
        check_line = line
        if line.startswith("+"):
            check_line = line[1:]

        result = detect_secret(check_line)
        if result:
            pattern_name, match = result
            findings.append((pattern_name, match[:40] + "..." if len(match) > 40 else match))

        if has_keyword_with_value(check_line):
            findings.append(("keyword_with_value", check_line.strip()[:60]))

    return findings


def parse_git_command(command):
    """Extract git subcommand and args."""
    parts = command.strip().split()
    if not parts or parts[0] != "git":
        return None, []
    if len(parts) < 2:
        return None, []
    return parts[1], parts[2:]


def main():
    try:
        hook_input = json.load(sys.stdin)
    except Exception:
        print(json.dumps(allow()))
        return

    tool_name = hook_input.get("tool_name", "")
    if tool_name != "Bash":
        print(json.dumps(allow()))
        return

    command = hook_input.get("tool_input", {}).get("command", "")
    subcmd, args = parse_git_command(command)

    if not subcmd:
        print(json.dumps(allow()))
        return

    # Check git commit — scan staged content
    if subcmd == "commit":
        staged = get_staged_content()
        if not staged:
            print(json.dumps(allow()))
            return

        findings = scan_for_secrets(staged)
        if findings:
            strikes = add_strike()
            patterns = ", ".join(set(f[0] for f in findings[:5]))
            msg = (
                f"🔐 CREDENTIAL GUARD: {len(findings)} potential secret(s) in staged files!\n"
                f"Patterns: {patterns}\n"
                f"Strike {strikes}/{MAX_STRIKES}."
            )
            if strikes >= MAX_STRIKES:
                msg += "\n\n🛑 3 STRIKES: Session blocked for credential violations."
                msg += "\nReview ALL staged files. Use `git diff --cached` to inspect."
                msg += "\nRemove secrets, use environment variables or .env files instead."
            else:
                msg += "\n\nRemove secrets before committing."
                msg += "\nUse: git reset HEAD <file> to unstage."
            print(json.dumps(deny(msg)))
            return

    # Check git add — scan file content before staging
    if subcmd == "add":
        files = [a for a in args if not a.startswith("-") and a != "."]
        # For `git add .` or `git add -A`, we can't pre-scan efficiently
        # Let the commit hook catch it
        if not files or "." in args or "-A" in args:
            print(json.dumps(allow()))
            return

        all_findings = []
        for filepath in files:
            content = get_file_content(filepath)
            findings = scan_for_secrets(content)
            if findings:
                all_findings.extend([(filepath, f) for f in findings])

        if all_findings:
            strikes = add_strike()
            file_names = ", ".join(set(f[0] for f in all_findings[:3]))
            msg = (
                f"🔐 CREDENTIAL GUARD: Secrets detected in: {file_names}\n"
                f"Strike {strikes}/{MAX_STRIKES}. Remove secrets before staging."
            )
            print(json.dumps(deny(msg)))
            return

    # Check git push — one more chance to catch
    if subcmd == "push":
        staged = get_staged_content()
        findings = scan_for_secrets(staged) if staged else []
        if findings:
            print(json.dumps(deny(
                f"🔐 CREDENTIAL GUARD: {len(findings)} secret(s) still staged! "
                f"Clean up before pushing."
            )))
            return

    print(json.dumps(allow()))


if __name__ == "__main__":
    main()
