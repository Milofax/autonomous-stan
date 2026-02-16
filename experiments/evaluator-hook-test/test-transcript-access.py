#!/usr/bin/env python3
"""
Test: Can a command hook read the transcript?
This is a minimal test to verify transcript access from command hooks.
"""

import json
import sys

def main():
    # 1. Read hook input from stdin
    try:
        hook_input = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        output = {
            "continue": True,
            "systemMessage": f"[TEST] Failed to parse stdin JSON: {e}"
        }
        print(json.dumps(output))
        return

    # 2. Get transcript_path
    transcript_path = hook_input.get("transcript_path", "NOT FOUND")

    # 3. Try to read the transcript file
    transcript_content = "COULD NOT READ"
    last_lines = []

    try:
        with open(transcript_path, 'r') as f:
            lines = f.readlines()
            # Get last 5 lines (or fewer if file is smaller)
            last_lines = lines[-5:] if len(lines) >= 5 else lines
            transcript_content = f"READ SUCCESS - {len(lines)} total lines"
    except FileNotFoundError:
        transcript_content = f"FILE NOT FOUND: {transcript_path}"
    except PermissionError:
        transcript_content = f"PERMISSION DENIED: {transcript_path}"
    except Exception as e:
        transcript_content = f"ERROR: {type(e).__name__}: {e}"

    # 4. Build output
    output = {
        "continue": True,
        "systemMessage": f"""[TRANSCRIPT ACCESS TEST]
Path: {transcript_path}
Status: {transcript_content}
Last lines preview: {len(last_lines)} lines captured
Hook input keys: {list(hook_input.keys())}"""
    }

    print(json.dumps(output))

if __name__ == "__main__":
    main()
