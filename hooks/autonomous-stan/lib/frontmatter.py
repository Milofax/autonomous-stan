#!/usr/bin/env python3
"""Frontmatter parsing utilities for STAN."""

import re
import yaml
from pathlib import Path
from typing import Optional


def parse_frontmatter(file_path: str | Path) -> dict:
    """
    Parse YAML frontmatter from a Markdown file.

    Args:
        file_path: Path to the Markdown file

    Returns:
        Dictionary with frontmatter data, or empty dict if no frontmatter
    """
    path = Path(file_path)
    if not path.exists():
        return {}

    content = path.read_text(encoding="utf-8")

    if not content.startswith("---"):
        return {}

    # Find end of frontmatter
    end = content.find("---", 3)
    if end == -1:
        return {}

    frontmatter_str = content[3:end].strip()

    # Replace template placeholders with dummy values for YAML parsing
    # First handle quoted placeholders: "{{...}}" → "placeholder"
    frontmatter_str = re.sub(r'"\{\{[^}]+\}\}"', '"placeholder"', frontmatter_str)
    # Then handle unquoted placeholders: {{...}} → "placeholder"
    frontmatter_str = re.sub(r'\{\{[^}]+\}\}', '"placeholder"', frontmatter_str)

    try:
        return yaml.safe_load(frontmatter_str) or {}
    except yaml.YAMLError:
        return {}


def get_document_type(file_path: str | Path) -> Optional[str]:
    """Get the 'type' field from document frontmatter."""
    fm = parse_frontmatter(file_path)
    return fm.get("type")


def get_document_criteria(file_path: str | Path) -> list[str]:
    """Get the 'criteria' list from document frontmatter."""
    fm = parse_frontmatter(file_path)
    return fm.get("criteria", [])


def get_document_status(file_path: str | Path) -> Optional[str]:
    """Get the 'status' field from document frontmatter."""
    fm = parse_frontmatter(file_path)
    return fm.get("status")


def get_techniques_applied(file_path: str | Path) -> list[str]:
    """Get the 'techniques_applied' list from document frontmatter."""
    fm = parse_frontmatter(file_path)
    return fm.get("techniques_applied", [])


def is_archived(file_path: str | Path) -> bool:
    """Check if document has status: archived."""
    return get_document_status(file_path) == "archived"
