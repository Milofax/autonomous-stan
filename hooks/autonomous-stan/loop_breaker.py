#!/usr/bin/env python3
"""
Loop Breaker (PostToolUse Hook)

Tracks Edit→Test pairs. If the same file is edited 3+ times and
the test still fails after each edit, this is a thinking loop —
not a tool error.

Escalation: Injects "STOP. Question your approach." into the
system message, inspired by Superpowers' Systematic Debugging.

Unlike taming-stan's retry-guard (which counts tool crashes),
this detects COGNITIVE loops where the agent keeps trying the
same approach with minor variations.
"""
import json
import sys
import os
import time
import hashlib

STATE_FILE = os.path.join(os.getcwd(), ".stan", "loop_state.json")
EDIT_THRESHOLD = 3
TIME_WINDOW = 600  # 10 minutes


def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"edits": {}, "test_failures": 0, "last_test_pass": True}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


def is_test_command(command):
    """Detect test commands."""
    test_indicators = [
        "pytest", "python -m pytest", "npm test", "npx jest",
        "cargo test", "go test", "mvn test", "gradle test",
        "rspec", "bundle exec", "make test", "yarn test",
        "vitest", "npx vitest", "bun test"
    ]
    cmd_lower = command.lower()
    return any(t in cmd_lower for t in test_indicators)


def is_edit_related(tool_name):
    """Was this a file edit?"""
    return tool_name in ("Edit", "Write", "MultiEdit")


def main():
    try:
        hook_input = json.load(sys.stdin)
    except Exception:
        print(json.dumps({"continue": True}))
        return

    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})
    tool_error = hook_input.get("tool_error")

    state = load_state()
    now = time.time()

    # Track file edits
    if is_edit_related(tool_name):
        filepath = tool_input.get("file_path", tool_input.get("path", "unknown"))
        edits = state.get("edits", {})

        if filepath not in edits:
            edits[filepath] = {"count": 0, "first_edit": now, "last_edit": now}

        entry = edits[filepath]
        # Reset if outside time window
        if now - entry["first_edit"] > TIME_WINDOW:
            entry = {"count": 0, "first_edit": now, "last_edit": now}

        entry["count"] += 1
        entry["last_edit"] = now
        edits[filepath] = entry
        state["edits"] = edits
        save_state(state)
        print(json.dumps({"continue": True}))
        return

    # Track test results (Bash commands)
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        if not is_test_command(command):
            print(json.dumps({"continue": True}))
            return

        exit_code = hook_input.get("tool_result", {}).get("exit_code")
        if exit_code is None:
            # Try to detect from output
            output = hook_input.get("tool_result", {}).get("output", "")
            exit_code = 1 if ("FAILED" in output or "Error" in output) else 0

        if exit_code == 0:
            # Test passed — reset all edit counters
            state["edits"] = {}
            state["test_failures"] = 0
            state["last_test_pass"] = True
            save_state(state)
            print(json.dumps({"continue": True}))
            return

        # Test failed — check if we're in a loop
        state["test_failures"] = state.get("test_failures", 0) + 1
        state["last_test_pass"] = False

        # Find files edited multiple times
        loop_files = []
        for filepath, entry in state.get("edits", {}).items():
            if entry["count"] >= EDIT_THRESHOLD and now - entry["first_edit"] <= TIME_WINDOW:
                loop_files.append((filepath, entry["count"]))

        save_state(state)

        if loop_files:
            files_str = ", ".join(f"{f} ({c}x)" for f, c in loop_files[:3])
            print(json.dumps({
                "continue": True,
                "systemMessage": (
                    f"⚠️ LOOP DETECTED: Files edited {EDIT_THRESHOLD}+ times with test still failing: {files_str}\n\n"
                    "STOP. You are in a thinking loop. The same approach with minor variations won't work.\n\n"
                    "Apply Systematic Debugging (Phase 1 — Root Cause Investigation):\n"
                    "1. Read the FULL error message carefully\n"
                    "2. What EXACTLY is different from working code?\n"
                    "3. Is your APPROACH fundamentally wrong? (not just the details)\n"
                    "4. If 3+ fixes failed: Question the ARCHITECTURE, not the implementation\n\n"
                    "Do NOT attempt another fix without completing Phase 1."
                )
            }))
            return

        print(json.dumps({"continue": True}))
        return

    print(json.dumps({"continue": True}))


if __name__ == "__main__":
    main()
