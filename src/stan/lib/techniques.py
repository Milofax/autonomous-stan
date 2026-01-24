#!/usr/bin/env python3
"""Techniques and Purposes loading for STAN."""

import yaml
from pathlib import Path
from typing import Optional

# Default paths - can be overridden for testing
_PROJECT_ROOT: Optional[Path] = None


def set_project_root(path: Path) -> None:
    """Set the project root for finding techniques."""
    global _PROJECT_ROOT
    _PROJECT_ROOT = path


def get_project_root() -> Path:
    """Get the project root directory."""
    if _PROJECT_ROOT:
        return _PROJECT_ROOT
    return Path(__file__).parent.parent.parent.parent


def get_techniques_dir() -> Path:
    """Get the techniques directory."""
    return get_project_root() / "techniques"


def get_purposes_dir() -> Path:
    """Get the purposes directory."""
    return get_techniques_dir() / "purposes"


def load_yaml(path: Path) -> dict:
    """Load a YAML file."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def list_techniques() -> list[str]:
    """List all available technique IDs."""
    techniques_dir = get_techniques_dir()
    return [
        f.stem for f in techniques_dir.glob("*.yaml")
        if f.name != "schema.yaml"
    ]


def list_purposes() -> list[str]:
    """List all available purpose IDs."""
    purposes_dir = get_purposes_dir()
    return [f.stem for f in purposes_dir.glob("*.yaml")]


def get_technique(technique_id: str) -> Optional[dict]:
    """
    Load a technique by ID.

    Args:
        technique_id: The technique ID (filename without extension)

    Returns:
        Technique data or None if not found
    """
    technique_path = get_techniques_dir() / f"{technique_id}.yaml"
    if not technique_path.exists():
        return None
    return load_yaml(technique_path)


def get_purpose(purpose_id: str) -> Optional[dict]:
    """
    Load a purpose by ID.

    Args:
        purpose_id: The purpose ID (filename without extension)

    Returns:
        Purpose data or None if not found
    """
    purpose_path = get_purposes_dir() / f"{purpose_id}.yaml"
    if not purpose_path.exists():
        return None
    return load_yaml(purpose_path)


def get_techniques_for_purpose(purpose_id: str) -> list[dict]:
    """
    Get all techniques for a purpose.

    Args:
        purpose_id: The purpose ID

    Returns:
        List of technique data dicts
    """
    purpose = get_purpose(purpose_id)
    if not purpose:
        return []

    techniques = []
    for tech_id in purpose.get("techniques", []):
        tech = get_technique(tech_id)
        if tech:
            techniques.append(tech)
    return techniques


def get_purposes_for_technique(technique_id: str) -> list[str]:
    """
    Get all purposes that include a technique.

    Args:
        technique_id: The technique ID

    Returns:
        List of purpose IDs
    """
    tech = get_technique(technique_id)
    if not tech:
        return []
    return tech.get("purposes", [])


def get_recommended_technique(purpose_id: str) -> Optional[dict]:
    """
    Get the recommended starting technique for a purpose.

    Args:
        purpose_id: The purpose ID

    Returns:
        Technique data or None
    """
    purpose = get_purpose(purpose_id)
    if not purpose:
        return None

    recommended_id = purpose.get("recommended_start")
    if not recommended_id:
        return None

    return get_technique(recommended_id)
