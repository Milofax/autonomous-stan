#!/usr/bin/env python3
"""
STAN Context Hook (UserPromptSubmit)

Injiziert STAN-Kontext in jede Nachricht:
- Phase und aktueller Task aus stan.md
- Lokale Learnings (hot + recent)
"""

import json
import os
import sys
import re
from pathlib import Path

# Importiere Learnings-Modul
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from learnings import load_learnings, get_stats


def read_manifest() -> dict | None:
    """Lese stan.md Manifest aus aktuellem Verzeichnis."""
    cwd = os.getcwd()
    stan_path = Path(cwd) / "stan.md"

    if not stan_path.exists():
        return None

    try:
        content = stan_path.read_text()

        # Parse Phase aus Tabelle
        phase_match = re.search(r'\*\*Phase\*\*\s*\|\s*(\w+)', content)
        phase = phase_match.group(1) if phase_match else "UNKNOWN"

        # Parse Current Task aus Tabelle
        task_match = re.search(r'\*\*Current Task\*\*\s*\|\s*([^\|]+)', content)
        task = task_match.group(1).strip() if task_match else "-"

        # Parse Projekt-Name aus Heading
        name_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        name = name_match.group(1) if name_match else "Unknown Project"

        return {
            "name": name,
            "phase": phase,
            "current_task": task,
            "path": str(stan_path)
        }
    except Exception:
        return None


def format_learnings_summary(learnings: list, max_show: int = 5) -> str:
    """Formatiere Learnings für Kontext-Injection."""
    if not learnings:
        return "Keine lokalen Learnings."

    lines = []
    for l in learnings[:max_show]:
        content = l["content"][:80]
        if len(l["content"]) > 80:
            content += "..."
        lines.append(f"  - {content}")

    total = len(learnings)
    if total > max_show:
        lines.append(f"  ... und {total - max_show} weitere")

    return "\n".join(lines)


def main():
    # Lese Hook-Input
    input_data = json.loads(sys.stdin.read())

    # Lade Manifest
    manifest = read_manifest()

    # Lade lokale Learnings
    learnings = load_learnings()
    stats = get_stats()

    # Baue System-Message
    parts = ["[STAN]"]

    if manifest:
        parts.append(f"Projekt: {manifest['name']}")
        parts.append(f"Phase: {manifest['phase']}")
        if manifest['current_task'] != "-":
            parts.append(f"Task: {manifest['current_task']}")
    else:
        parts.append("Kein stan.md gefunden (nicht initialisiert)")

    parts.append(f"Learnings: {stats['hot_count']} hot, {stats['recent_count']} recent")

    # Wenn Learnings vorhanden, zeige relevante
    if learnings:
        parts.append("\nRelevante Learnings:")
        parts.append(format_learnings_summary(learnings))

    system_message = " | ".join(parts[:4])  # Kompakte erste Zeile
    if len(parts) > 4:
        system_message += "\n" + "\n".join(parts[4:])

    # Output
    result = {
        "continue": True,
        "systemMessage": system_message
    }

    print(json.dumps(result))


if __name__ == "__main__":
    main()
