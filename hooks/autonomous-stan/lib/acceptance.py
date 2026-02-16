#!/usr/bin/env python3
"""
Acceptance Criteria completion checking.

Parses markdown checkboxes and checks if all are completed.
Used by stan-gate hook for Ralph-style autonomous loop.
"""

import re
from pathlib import Path


# Regex for markdown checkboxes
# Matches: - [ ] text, - [x] text, - [X] text
CHECKBOX_PATTERN = re.compile(r'^[\s]*-\s*\[([ xX])\]\s*(.+)$', re.MULTILINE)


def parse_checkboxes(doc_path: str | Path) -> tuple[list[str], list[str]]:
    """
    Parse all checkboxes from a markdown document.

    Args:
        doc_path: Path to the markdown document

    Returns:
        Tuple of (checked_items, unchecked_items)
        Each item is the text content of the checkbox line.
    """
    path = Path(doc_path)
    if not path.exists():
        raise FileNotFoundError(f"Document not found: {doc_path}")

    content = path.read_text()

    checked = []
    unchecked = []

    for match in CHECKBOX_PATTERN.finditer(content):
        checkbox_state = match.group(1)
        text = match.group(2).strip()

        if checkbox_state.lower() == 'x':
            checked.append(text)
        else:
            unchecked.append(text)

    return checked, unchecked


def get_unchecked_criteria(doc_path: str | Path) -> list[str]:
    """
    Get list of unchecked criteria from a document.

    Args:
        doc_path: Path to the markdown document

    Returns:
        List of unchecked criterion texts
    """
    _, unchecked = parse_checkboxes(doc_path)
    return unchecked


def all_criteria_checked(doc_path: str | Path) -> bool:
    """
    Check if all checkboxes in a document are checked.

    Args:
        doc_path: Path to the markdown document

    Returns:
        True if all checkboxes are checked (or no checkboxes exist)
    """
    _, unchecked = parse_checkboxes(doc_path)
    return len(unchecked) == 0


def count_checkboxes(doc_path: str | Path) -> tuple[int, int, int]:
    """
    Count checkboxes in a document.

    Args:
        doc_path: Path to the markdown document

    Returns:
        Tuple of (total, checked, unchecked)
    """
    checked, unchecked = parse_checkboxes(doc_path)
    total = len(checked) + len(unchecked)
    return total, len(checked), len(unchecked)


def format_unchecked_for_message(unchecked: list[str], max_items: int = 5) -> str:
    """
    Format unchecked items for a hook message.

    Args:
        unchecked: List of unchecked criterion texts
        max_items: Maximum items to show before truncating

    Returns:
        Formatted string for display
    """
    if not unchecked:
        return ""

    lines = []
    for i, item in enumerate(unchecked[:max_items]):
        # Truncate long items
        if len(item) > 60:
            item = item[:57] + "..."
        lines.append(f"  - [ ] {item}")

    if len(unchecked) > max_items:
        remaining = len(unchecked) - max_items
        lines.append(f"  ... und {remaining} weitere")

    return "\n".join(lines)
