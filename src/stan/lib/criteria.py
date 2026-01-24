#!/usr/bin/env python3
"""Criteria loading and validation for STAN."""

import yaml
from pathlib import Path
from typing import Optional

# Default paths - can be overridden for testing
_PROJECT_ROOT: Optional[Path] = None


def set_project_root(path: Path) -> None:
    """Set the project root for finding criteria/templates."""
    global _PROJECT_ROOT
    _PROJECT_ROOT = path


def get_project_root() -> Path:
    """Get the project root directory."""
    if _PROJECT_ROOT:
        return _PROJECT_ROOT
    # Default: assume we're somewhere in the project
    return Path(__file__).parent.parent.parent.parent


def get_criteria_dir() -> Path:
    """Get the criteria directory."""
    return get_project_root() / "criteria"


def get_templates_dir() -> Path:
    """Get the templates directory."""
    return get_project_root() / "templates"


def load_yaml(path: Path) -> dict:
    """Load a YAML file."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_criteria(criteria_name: str) -> Optional[dict]:
    """
    Load a criteria YAML file by name.

    Args:
        criteria_name: Name of the criteria (without .yaml extension)

    Returns:
        Criteria data or None if not found
    """
    criteria_path = get_criteria_dir() / f"{criteria_name}.yaml"
    if not criteria_path.exists():
        return None
    return load_yaml(criteria_path)


def get_template_criteria(template_name: str) -> list[str]:
    """
    Get the criteria list from a template.

    Args:
        template_name: Name of template (e.g., "prd.md.template")

    Returns:
        List of criteria names from template frontmatter
    """
    from .frontmatter import parse_frontmatter

    template_path = get_templates_dir() / template_name
    if not template_path.exists():
        return []

    fm = parse_frontmatter(template_path)
    return fm.get("criteria", [])


def get_template_for_type(doc_type: str) -> Optional[str]:
    """
    Find the template filename for a document type.

    Args:
        doc_type: Document type (e.g., "prd", "plan")

    Returns:
        Template filename or None if not found
    """
    templates_dir = get_templates_dir()
    for template in templates_dir.glob("*.template"):
        from .frontmatter import parse_frontmatter
        fm = parse_frontmatter(template)
        if fm.get("type") == doc_type:
            return template.name
    return None


def list_all_criteria() -> list[str]:
    """List all available criteria names."""
    criteria_dir = get_criteria_dir()
    return [f.stem for f in criteria_dir.glob("*.yaml")]


def get_required_checks(criteria_name: str) -> list[dict]:
    """
    Get all required checks from a criteria.

    Args:
        criteria_name: Name of the criteria

    Returns:
        List of required check dicts
    """
    criteria = load_criteria(criteria_name)
    if not criteria:
        return []

    return [
        check for check in criteria.get("checks", [])
        if check.get("required", False)
    ]


def check_criteria_not_removed(
    doc_criteria: list[str],
    template_criteria: list[str]
) -> tuple[bool, list[str]]:
    """
    Check if any template criteria were removed from document.

    Args:
        doc_criteria: Criteria list from document
        template_criteria: Criteria list from template (minimum)

    Returns:
        Tuple of (is_valid, list of missing criteria)
    """
    doc_set = set(doc_criteria)
    template_set = set(template_criteria)

    missing = template_set - doc_set
    return (len(missing) == 0, list(missing))
