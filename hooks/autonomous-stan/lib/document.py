#!/usr/bin/env python3
"""
STAN Document Lifecycle Management

Handles document status validation and transitions.

Status Lifecycle:
    draft → approved → in-progress → done → completed

Transitions:
    - draft → approved: Manual (User approval after criteria check)
    - approved → in-progress: Auto (when CREATE phase starts)
    - in-progress → done: Auto (when all tasks completed)
    - done → completed: Manual (User runs /stan complete)
"""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

try:
    import yaml
except ImportError:
    yaml = None


# Valid statuses in lifecycle order
VALID_STATUSES = ["draft", "approved", "in-progress", "done", "completed"]

# Allowed transitions: from_status -> [allowed_to_statuses]
ALLOWED_TRANSITIONS = {
    "draft": ["approved"],
    "approved": ["in-progress", "draft"],  # Can go back to draft if changes needed
    "in-progress": ["done", "approved"],   # Can go back if blockers found
    "done": ["completed", "in-progress"],  # Can reopen if issues found
    "completed": ["draft"],                # Can uncomplete to start fresh
}

# Auto-transitions (triggered by system, not user)
AUTO_TRANSITIONS = {
    ("approved", "in-progress"): "CREATE Phase started",
    ("in-progress", "done"): "All tasks completed",
}

# Manual transitions (require user confirmation)
MANUAL_TRANSITIONS = {
    ("draft", "approved"): "User approved after criteria check",
    ("done", "completed"): "User completed feature via /stan complete",
    ("completed", "draft"): "User uncompleted document",
}


def _simple_yaml_parse(content: str) -> dict:
    """Simple YAML frontmatter parser as fallback."""
    result = {}
    for line in content.split('\n'):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        if ':' in stripped:
            key, value = stripped.split(':', 1)
            key = key.strip()
            value = value.strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            elif value == '':
                value = None
            result[key] = value
    return result


def read_frontmatter(file_path: Path) -> Optional[dict]:
    """
    Read YAML frontmatter from a markdown file.

    Args:
        file_path: Path to the markdown file

    Returns:
        Dict with frontmatter data or None if no frontmatter
    """
    if not file_path.exists():
        return None

    content = file_path.read_text(encoding='utf-8')

    if not content.startswith('---'):
        return None

    # Find end of frontmatter
    end_match = re.search(r'\n---\s*\n', content[3:])
    if not end_match:
        return None

    frontmatter_text = content[3:end_match.start() + 3]

    if yaml:
        return yaml.safe_load(frontmatter_text)
    else:
        return _simple_yaml_parse(frontmatter_text)


def write_frontmatter(file_path: Path, frontmatter: dict) -> bool:
    """
    Write/update YAML frontmatter in a markdown file.

    Args:
        file_path: Path to the markdown file
        frontmatter: Dict with frontmatter data

    Returns:
        True if successful
    """
    if not file_path.exists():
        return False

    content = file_path.read_text(encoding='utf-8')

    # Find existing frontmatter
    if content.startswith('---'):
        end_match = re.search(r'\n---\s*\n', content[3:])
        if end_match:
            body = content[end_match.end() + 3:]
        else:
            body = content
    else:
        body = content

    # Build new frontmatter
    if yaml:
        new_frontmatter = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
    else:
        # Simple serialization
        lines = []
        for key, value in frontmatter.items():
            if isinstance(value, list):
                lines.append(f"{key}:")
                for item in value:
                    lines.append(f"  - {item}")
            elif value is None:
                lines.append(f"{key}:")
            else:
                lines.append(f"{key}: {value}")
        new_frontmatter = '\n'.join(lines)

    new_content = f"---\n{new_frontmatter}---\n{body}"
    file_path.write_text(new_content, encoding='utf-8')
    return True


def get_document_status(file_path: Path) -> Optional[str]:
    """
    Get the current status of a document.

    Args:
        file_path: Path to the markdown file

    Returns:
        Status string or None
    """
    frontmatter = read_frontmatter(file_path)
    if frontmatter:
        return frontmatter.get("status")
    return None


def validate_status(status: str) -> Tuple[bool, str]:
    """
    Validate if a status is valid.

    Args:
        status: Status to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if status in VALID_STATUSES:
        return True, ""
    return False, f"Invalid status '{status}'. Valid: {', '.join(VALID_STATUSES)}"


def can_transition(from_status: str, to_status: str) -> Tuple[bool, str]:
    """
    Check if a status transition is allowed.

    Args:
        from_status: Current status
        to_status: Target status

    Returns:
        Tuple of (is_allowed, reason)
    """
    # Validate both statuses
    valid, err = validate_status(from_status)
    if not valid:
        return False, f"Current {err}"

    valid, err = validate_status(to_status)
    if not valid:
        return False, f"Target {err}"

    # Same status is always allowed (no-op)
    if from_status == to_status:
        return True, "No change"

    # Check allowed transitions
    allowed = ALLOWED_TRANSITIONS.get(from_status, [])
    if to_status in allowed:
        return True, ""

    return False, f"Cannot transition from '{from_status}' to '{to_status}'. Allowed: {', '.join(allowed)}"


def is_auto_transition(from_status: str, to_status: str) -> bool:
    """Check if this is an automatic transition."""
    return (from_status, to_status) in AUTO_TRANSITIONS


def is_manual_transition(from_status: str, to_status: str) -> bool:
    """Check if this is a manual transition requiring user confirmation."""
    return (from_status, to_status) in MANUAL_TRANSITIONS


def update_document_status(
    file_path: Path,
    new_status: str,
    force: bool = False
) -> Tuple[bool, str]:
    """
    Update the status of a document.

    Args:
        file_path: Path to the markdown file
        new_status: New status to set
        force: Skip transition validation

    Returns:
        Tuple of (success, message)
    """
    frontmatter = read_frontmatter(file_path)
    if frontmatter is None:
        return False, f"Could not read frontmatter from {file_path}"

    current_status = frontmatter.get("status", "draft")

    # Validate transition
    if not force:
        allowed, reason = can_transition(current_status, new_status)
        if not allowed:
            return False, reason

    # Update frontmatter
    frontmatter["status"] = new_status
    frontmatter["updated"] = datetime.now().strftime("%Y-%m-%d")

    # Write back
    success = write_frontmatter(file_path, frontmatter)
    if success:
        return True, f"Status changed: {current_status} → {new_status}"
    return False, "Failed to write frontmatter"


def get_status_info(status: str) -> dict:
    """
    Get information about a status.

    Args:
        status: Status to get info for

    Returns:
        Dict with status information
    """
    info = {
        "status": status,
        "valid": status in VALID_STATUSES,
        "index": VALID_STATUSES.index(status) if status in VALID_STATUSES else -1,
        "allowed_transitions": ALLOWED_TRANSITIONS.get(status, []),
        "is_terminal": status == "completed",
        "is_initial": status == "draft",
    }
    return info


def get_lifecycle_position(status: str) -> int:
    """
    Get the position in the lifecycle (0-4).

    Args:
        status: Status to check

    Returns:
        Position index or -1 if invalid
    """
    if status in VALID_STATUSES:
        return VALID_STATUSES.index(status)
    return -1


def scan_documents(directory: Path) -> list[dict]:
    """
    Scan a directory for markdown documents with frontmatter.

    Args:
        directory: Directory to scan

    Returns:
        List of dicts with file info
    """
    results = []
    for md_file in directory.glob("**/*.md"):
        frontmatter = read_frontmatter(md_file)
        if frontmatter:
            results.append({
                "path": md_file,
                "type": frontmatter.get("type", "unknown"),
                "status": frontmatter.get("status", "unknown"),
                "created": frontmatter.get("created"),
                "updated": frontmatter.get("updated"),
            })
    return results


# CLI for direct invocation
if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: document.py [status <file>|set <file> <status>|validate <status>|scan <dir>]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "status" and len(sys.argv) >= 3:
        file_path = Path(sys.argv[2])
        status = get_document_status(file_path)
        if status:
            info = get_status_info(status)
            print(json.dumps(info, indent=2))
        else:
            print("No status found")
            sys.exit(1)

    elif cmd == "set" and len(sys.argv) >= 4:
        file_path = Path(sys.argv[2])
        new_status = sys.argv[3]
        force = "--force" in sys.argv
        success, msg = update_document_status(file_path, new_status, force)
        print(msg)
        sys.exit(0 if success else 1)

    elif cmd == "validate" and len(sys.argv) >= 3:
        status = sys.argv[2]
        valid, err = validate_status(status)
        if valid:
            print(f"'{status}' is valid")
        else:
            print(err)
            sys.exit(1)

    elif cmd == "can-transition" and len(sys.argv) >= 4:
        from_status = sys.argv[2]
        to_status = sys.argv[3]
        allowed, reason = can_transition(from_status, to_status)
        print(f"{'Allowed' if allowed else 'Not allowed'}: {reason}")
        sys.exit(0 if allowed else 1)

    elif cmd == "scan" and len(sys.argv) >= 3:
        directory = Path(sys.argv[2])
        docs = scan_documents(directory)
        for doc in docs:
            print(f"{doc['type']:10} | {doc['status']:12} | {doc['path']}")

    else:
        print("Unknown command")
        sys.exit(1)
