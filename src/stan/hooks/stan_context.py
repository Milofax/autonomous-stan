#!/usr/bin/env python3
"""
STAN Context Hook (UserPromptSubmit)

Injiziert STAN-Kontext in jede Nachricht:
- Phase und aktueller Task aus stan.md
- Enforcement Status (welche Criteria gelten)
- Applied Techniques

Dieses Script ist ein Claude Code Hook.
Es liest JSON von stdin und gibt JSON auf stdout aus.

Output Format:
{
    "continue": true,
    "systemMessage": "Optionaler Kontext für Claude"
}
"""

import json
import os
import re
import sys
from pathlib import Path

# Add library to path
sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from frontmatter import parse_frontmatter
from criteria import get_template_criteria, get_template_for_type


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


def get_active_documents() -> list[dict]:
    """Finde aktive STAN-Dokumente im Projekt."""
    docs = []
    docs_dir = Path(os.getcwd()) / "docs"

    if not docs_dir.exists():
        return docs

    for md_file in docs_dir.glob("*.md"):
        fm = parse_frontmatter(md_file)
        if fm.get("status") == "archived":
            continue

        doc_type = fm.get("type")
        if doc_type:
            docs.append({
                "path": str(md_file.relative_to(os.getcwd())),
                "type": doc_type,
                "status": fm.get("status", "unknown"),
                "criteria": fm.get("criteria", []),
                "techniques_applied": fm.get("techniques_applied", []),
            })

    return docs


def format_context(manifest: dict | None, docs: list[dict]) -> str:
    """Formatiere Kontext für System Message."""
    parts = ["[STAN]"]

    if manifest:
        parts.append(f"Project: {manifest['name']}")
        parts.append(f"Phase: {manifest['phase']}")
        if manifest['current_task'] != "-":
            parts.append(f"Task: {manifest['current_task']}")
    else:
        parts.append("Not initialized (no stan.md)")

    # Active documents summary
    if docs:
        doc_summary = ", ".join(f"{d['type']}({d['status']})" for d in docs)
        parts.append(f"Docs: {doc_summary}")

        # Show techniques if any applied
        all_techniques = set()
        for d in docs:
            all_techniques.update(d.get("techniques_applied", []))
        if all_techniques:
            parts.append(f"Techniques: {', '.join(sorted(all_techniques))}")

    return " | ".join(parts)


def main():
    # Lese Hook-Input
    try:
        input_data = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        input_data = {}

    # Lade Manifest
    manifest = read_manifest()

    # Lade aktive Dokumente
    docs = get_active_documents()

    # Baue System-Message
    system_message = format_context(manifest, docs)

    # Output - Hook soll immer weiterlaufen
    result = {
        "continue": True,
        "systemMessage": system_message
    }

    print(json.dumps(result))


if __name__ == "__main__":
    main()
