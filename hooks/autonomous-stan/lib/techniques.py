#!/usr/bin/env python3
"""
STAN Techniques Library - Denktechniken-Loader

Lädt Techniken und Zwecke aus YAML-Dateien und ermöglicht:
- Abrufen aller Zwecke
- Abrufen von Techniken für einen Zweck
- Abrufen einer einzelnen Technik mit Details
"""

import os
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    # Fallback: Vereinfachtes YAML-Parsing
    yaml = None


def _simple_yaml_load(content: str) -> dict:
    """Einfacher YAML-Parser als Fallback."""
    result = {}
    current_key = None
    current_list = None

    for line in content.split('\n'):
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue

        # Key-Value auf Top-Level
        if ':' in stripped and not stripped.startswith('-'):
            parts = stripped.split(':', 1)
            key = parts[0].strip()
            value = parts[1].strip() if len(parts) > 1 else ''

            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            elif value == '':
                value = None

            result[key] = value
            current_key = key
            if value is None:
                current_list = []
                result[key] = current_list

        # List Item
        elif stripped.startswith('- ') and current_list is not None:
            item = stripped[2:].strip()
            if item.startswith('"') and item.endswith('"'):
                item = item[1:-1]
            elif item.startswith("'") and item.endswith("'"):
                item = item[1:-1]
            current_list.append(item)

    return result


def _load_yaml(path: Path) -> dict:
    """Lade YAML-Datei."""
    if not path.exists():
        return {}

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    if yaml:
        return yaml.safe_load(content) or {}
    else:
        return _simple_yaml_load(content)


# Pfade relativ zum Projekt-Root
def _get_project_root() -> Path:
    """Finde das Projekt-Root (wo techniques/ liegt)."""
    # Versuche von diesem Skript aus
    current = Path(__file__).resolve()

    # Gehe hoch bis wir techniques/ finden
    for _ in range(10):
        if (current / "techniques").exists():
            return current
        current = current.parent

    # Fallback: CWD
    cwd = Path.cwd()
    if (cwd / "techniques").exists():
        return cwd

    raise FileNotFoundError("techniques/ Verzeichnis nicht gefunden")


def get_techniques_dir() -> Path:
    """Pfad zum techniques/ Verzeichnis."""
    return _get_project_root() / "techniques"


def get_purposes_dir() -> Path:
    """Pfad zum techniques/purposes/ Verzeichnis."""
    return get_techniques_dir() / "purposes"


def list_purposes() -> list[dict]:
    """
    Liste aller verfügbaren Zwecke.

    Returns:
        Liste von Dicts mit id, name, question
    """
    purposes_dir = get_purposes_dir()
    if not purposes_dir.exists():
        return []

    purposes = []
    for yaml_file in purposes_dir.glob("*.yaml"):
        data = _load_yaml(yaml_file)
        if data:
            purposes.append({
                "id": data.get("id", yaml_file.stem),
                "name": data.get("name", yaml_file.stem),
                "question": data.get("question", ""),
                "description": data.get("description", "")
            })

    return sorted(purposes, key=lambda x: x["name"])


def get_purpose(purpose_id: str) -> Optional[dict]:
    """
    Lade einen Zweck mit allen Details.

    Args:
        purpose_id: ID des Zwecks (z.B. "ursachenanalyse")

    Returns:
        Dict mit allen Zweck-Details oder None
    """
    purpose_file = get_purposes_dir() / f"{purpose_id}.yaml"
    if not purpose_file.exists():
        return None

    return _load_yaml(purpose_file)


def get_techniques_for_purpose(purpose_id: str) -> list[dict]:
    """
    Lade alle Techniken für einen Zweck.

    Args:
        purpose_id: ID des Zwecks

    Returns:
        Liste von Technik-Dicts mit id, name, description
    """
    purpose = get_purpose(purpose_id)
    if not purpose:
        return []

    technique_ids = purpose.get("techniques", [])
    techniques = []

    for tech_id in technique_ids:
        tech = get_technique(tech_id)
        if tech:
            techniques.append({
                "id": tech.get("id", tech_id),
                "name": tech.get("name", tech_id),
                "description": tech.get("description", "")
            })

    return techniques


def list_techniques() -> list[dict]:
    """
    Liste aller verfügbaren Techniken.

    Returns:
        Liste von Dicts mit id, name, description
    """
    techniques_dir = get_techniques_dir()
    if not techniques_dir.exists():
        return []

    techniques = []
    for yaml_file in techniques_dir.glob("*.yaml"):
        # Überspringe schema.yaml
        if yaml_file.name == "schema.yaml":
            continue

        data = _load_yaml(yaml_file)
        if data and "id" in data:
            techniques.append({
                "id": data.get("id"),
                "name": data.get("name", yaml_file.stem),
                "description": data.get("description", ""),
                "purposes": data.get("purposes", [])
            })

    return sorted(techniques, key=lambda x: x["name"])


def get_technique(technique_id: str) -> Optional[dict]:
    """
    Lade eine Technik mit allen Details.

    Args:
        technique_id: ID der Technik (z.B. "five-whys")

    Returns:
        Dict mit allen Technik-Details oder None
    """
    technique_file = get_techniques_dir() / f"{technique_id}.yaml"
    if not technique_file.exists():
        return None

    return _load_yaml(technique_file)


def format_technique_for_display(technique: dict) -> str:
    """
    Formatiere eine Technik für die Anzeige.

    Args:
        technique: Technik-Dict

    Returns:
        Formatierter String
    """
    lines = []

    # Header
    lines.append(f"# {technique.get('name', 'Unbekannt')}")
    if technique.get('aliases'):
        lines.append(f"*Auch bekannt als: {', '.join(technique['aliases'])}*")
    lines.append("")

    # Description
    lines.append(technique.get('description', ''))
    lines.append("")

    # Meta
    meta = []
    if technique.get('source'):
        meta.append(f"**Quelle:** {technique['source']}")
    if technique.get('duration'):
        meta.append(f"**Dauer:** {technique['duration']}")
    if technique.get('participants'):
        meta.append(f"**Teilnehmer:** {technique['participants']}")
    if meta:
        lines.extend(meta)
        lines.append("")

    # Steps
    if technique.get('steps'):
        lines.append("## Schritte")
        for i, step in enumerate(technique['steps'], 1):
            lines.append(f"{i}. {step}")
        lines.append("")

    # When to use
    if technique.get('when_to_use'):
        lines.append("## Wann nutzen")
        for item in technique['when_to_use']:
            lines.append(f"- {item}")
        lines.append("")

    # When NOT to use
    if technique.get('when_not'):
        lines.append("## Wann NICHT nutzen")
        for item in technique['when_not']:
            lines.append(f"- {item}")
        lines.append("")

    # Tips
    if technique.get('tips'):
        lines.append("## Tipps")
        for tip in technique['tips']:
            lines.append(f"- {tip}")
        lines.append("")

    # Examples
    if technique.get('examples'):
        lines.append("## Beispiele")
        for example in technique['examples']:
            if isinstance(example, dict):
                lines.append(f"**{example.get('situation', 'Situation')}:**")
                lines.append(example.get('application', ''))
            else:
                lines.append(f"- {example}")
        lines.append("")

    return '\n'.join(lines)


def format_purpose_for_display(purpose: dict) -> str:
    """
    Formatiere einen Zweck für die Anzeige.

    Args:
        purpose: Zweck-Dict

    Returns:
        Formatierter String
    """
    lines = []

    lines.append(f"# {purpose.get('name', 'Unbekannt')}")
    lines.append(f"**Kernfrage:** {purpose.get('question', '')}")
    lines.append("")
    lines.append(purpose.get('description', ''))
    lines.append("")

    # Triggers
    if purpose.get('triggers'):
        lines.append("## Wann ist dieser Zweck relevant?")
        for trigger in purpose['triggers']:
            lines.append(f"- {trigger}")
        lines.append("")

    # Techniques
    if purpose.get('techniques'):
        lines.append("## Verfügbare Techniken")
        for tech_id in purpose['techniques']:
            tech = get_technique(tech_id)
            if tech:
                lines.append(f"- **{tech.get('name', tech_id)}**: {tech.get('description', '')[:80]}...")
            else:
                lines.append(f"- {tech_id}")
        lines.append("")

    # Recommendation
    if purpose.get('recommended_start'):
        rec_tech = get_technique(purpose['recommended_start'])
        rec_name = rec_tech.get('name', purpose['recommended_start']) if rec_tech else purpose['recommended_start']
        lines.append(f"## Empfehlung: {rec_name}")
        if purpose.get('recommended_start_reason'):
            lines.append(purpose['recommended_start_reason'])
        lines.append("")

    # Escalation
    if purpose.get('escalation'):
        lines.append("## Eskalation")
        lines.append(purpose['escalation'])

    return '\n'.join(lines)


# CLI für direkten Aufruf
if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 2:
        print("Usage: techniques.py [purposes|techniques|purpose <id>|technique <id>]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "purposes":
        purposes = list_purposes()
        for p in purposes:
            print(f"- {p['id']}: {p['name']}")
            print(f"  {p['question']}")

    elif cmd == "techniques":
        techniques = list_techniques()
        for t in techniques:
            print(f"- {t['id']}: {t['name']}")

    elif cmd == "purpose" and len(sys.argv) >= 3:
        purpose_id = sys.argv[2]
        purpose = get_purpose(purpose_id)
        if purpose:
            print(format_purpose_for_display(purpose))
        else:
            print(f"Zweck '{purpose_id}' nicht gefunden")
            sys.exit(1)

    elif cmd == "technique" and len(sys.argv) >= 3:
        tech_id = sys.argv[2]
        tech = get_technique(tech_id)
        if tech:
            print(format_technique_for_display(tech))
        else:
            print(f"Technik '{tech_id}' nicht gefunden")
            sys.exit(1)

    elif cmd == "for-purpose" and len(sys.argv) >= 3:
        purpose_id = sys.argv[2]
        techniques = get_techniques_for_purpose(purpose_id)
        for t in techniques:
            print(f"- {t['id']}: {t['name']}")

    else:
        print("Unknown command")
        sys.exit(1)
