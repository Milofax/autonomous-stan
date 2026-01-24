#!/usr/bin/env python3
"""
STAN Context Hook (UserPromptSubmit)

Injiziert STAN-Kontext in jede Nachricht:
- Phase und aktueller Task aus stan.md
- Lokale Learnings (hot + recent)
- User Config (Sprache, Skill-Level, Name)
"""

import json
import os
import sys
import re
from pathlib import Path

# Importiere Module
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from learnings import load_learnings, get_stats, rotate_learnings, LEARNINGS_DIR
from config import load_config, config_exists
from datetime import datetime


ROTATION_INTERVAL_HOURS = 24
LAST_ROTATION_FILE = LEARNINGS_DIR / ".last_rotation"


def should_rotate() -> bool:
    """Prüfe ob Rotation nötig (max einmal pro Tag)."""
    if not LAST_ROTATION_FILE.exists():
        return True

    try:
        last = datetime.fromisoformat(LAST_ROTATION_FILE.read_text().strip())
        hours_since = (datetime.now() - last).total_seconds() / 3600
        return hours_since >= ROTATION_INTERVAL_HOURS
    except (ValueError, IOError):
        return True


def mark_rotation_done():
    """Markiere Rotation als durchgeführt."""
    LEARNINGS_DIR.mkdir(parents=True, exist_ok=True)
    LAST_ROTATION_FILE.write_text(datetime.now().isoformat())


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

    # Periodische Rotation (max einmal pro Tag)
    rotation_msg = None
    if should_rotate():
        try:
            result = rotate_learnings()
            mark_rotation_done()
            total_moved = result["hot_demoted"] + result["hot_archived"] + result["recent_archived"]
            if total_moved > 0:
                rotation_msg = f"[Rotation: {total_moved} Learnings verschoben]"
        except Exception:
            pass  # Rotation-Fehler nicht kritisch

    # Lade Manifest
    manifest = read_manifest()

    # Lade lokale Learnings
    learnings = load_learnings()
    stats = get_stats()

    # Lade Config
    config = load_config()

    # Baue System-Message
    parts = ["[STAN]"]

    # Config-Info (Sprache, Skill, Name)
    if config:
        config_parts = []
        config_parts.append(f"Lang: {config.language.communication}")
        config_parts.append(f"Docs: {config.language.documents}")
        config_parts.append(f"Skill: {config.user.skill_level}")
        if config.user.name:
            config_parts.append(f"User: {config.user.name}")
        parts.append(" | ".join(config_parts))
    else:
        parts.append("No config (run /stan init for personalization)")

    if manifest:
        parts.append(f"Project: {manifest['name']}")
        parts.append(f"Phase: {manifest['phase']}")
        if manifest['current_task'] != "-":
            parts.append(f"Task: {manifest['current_task']}")
    else:
        parts.append("No stan.md found (not initialized)")

    parts.append(f"Learnings: {stats['hot_count']} hot, {stats['recent_count']} recent")

    # Wenn Learnings vorhanden, zeige relevante
    if learnings:
        parts.append("\nRelevante Learnings:")
        parts.append(format_learnings_summary(learnings))

    system_message = " | ".join(parts[:4])  # Kompakte erste Zeile
    if len(parts) > 4:
        system_message += "\n" + "\n".join(parts[4:])

    # Füge Rotation-Info hinzu wenn vorhanden
    if rotation_msg:
        system_message += f"\n{rotation_msg}"

    # Output
    result = {
        "continue": True,
        "systemMessage": system_message
    }

    print(json.dumps(result))


if __name__ == "__main__":
    main()
