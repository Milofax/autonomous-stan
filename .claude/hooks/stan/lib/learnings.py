#!/usr/bin/env python3
"""
STAN Learnings - Tiered Local Storage

Struktur:
- ~/.stan/learnings/recent.json  - Rolling ~50, FIFO
- ~/.stan/learnings/hot.json     - Oft genutzte (promoted)
- ~/.stan/learnings/archive.json - Permanent (manuell archiviert)
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

STAN_DIR = Path.home() / ".stan"
LEARNINGS_DIR = STAN_DIR / "learnings"

RECENT_FILE = LEARNINGS_DIR / "recent.json"
HOT_FILE = LEARNINGS_DIR / "hot.json"
ARCHIVE_FILE = LEARNINGS_DIR / "archive.json"

MAX_RECENT = 50
PROMOTE_THRESHOLD = 3  # Nach 3x Nutzung -> hot


def ensure_dirs():
    """Erstelle Verzeichnisse falls nicht vorhanden."""
    LEARNINGS_DIR.mkdir(parents=True, exist_ok=True)


def load_file(path: Path) -> list:
    """Lade JSON-Datei oder leere Liste."""
    if path.exists():
        try:
            with open(path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_file(path: Path, data: list):
    """Speichere JSON-Datei."""
    ensure_dirs()
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_learning(
    content: str,
    context: str,
    tags: Optional[list] = None,
    source: str = "auto"
) -> dict:
    """
    Speichere ein neues Learning in recent.

    Args:
        content: Das Learning selbst
        context: Kontext (Projekt, Datei, etc.)
        tags: Optionale Tags für Kategorisierung
        source: Quelle (auto, manual, review)

    Returns:
        Das erstellte Learning-Objekt
    """
    ensure_dirs()

    learning = {
        "id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "content": content,
        "context": context,
        "tags": tags or [],
        "source": source,
        "created_at": datetime.now().isoformat(),
        "use_count": 0,
        "last_used": None
    }

    recent = load_file(RECENT_FILE)
    recent.insert(0, learning)

    # FIFO: Entferne älteste wenn über Limit
    if len(recent) > MAX_RECENT:
        overflow = recent[MAX_RECENT:]
        recent = recent[:MAX_RECENT]

        # Overflow nach Archive verschieben
        archive = load_file(ARCHIVE_FILE)
        archive.extend(overflow)
        save_file(ARCHIVE_FILE, archive)

    save_file(RECENT_FILE, recent)
    return learning


def load_learnings(include_archive: bool = False) -> list:
    """
    Lade alle aktiven Learnings (hot + recent).

    Args:
        include_archive: Auch archivierte Learnings laden

    Returns:
        Liste von Learnings, hot zuerst
    """
    hot = load_file(HOT_FILE)
    recent = load_file(RECENT_FILE)

    result = hot + recent

    if include_archive:
        archive = load_file(ARCHIVE_FILE)
        result.extend(archive)

    return result


def record_usage(learning_id: str):
    """
    Markiere ein Learning als genutzt.
    Promoted nach hot wenn Schwelle erreicht.
    """
    # Suche in recent
    recent = load_file(RECENT_FILE)
    for i, learning in enumerate(recent):
        if learning["id"] == learning_id:
            learning["use_count"] = learning.get("use_count", 0) + 1
            learning["last_used"] = datetime.now().isoformat()

            # Promote zu hot?
            if learning["use_count"] >= PROMOTE_THRESHOLD:
                hot = load_file(HOT_FILE)
                hot.insert(0, learning)
                save_file(HOT_FILE, hot)
                recent.pop(i)

            save_file(RECENT_FILE, recent)
            return

    # Suche in hot (nur use_count erhöhen)
    hot = load_file(HOT_FILE)
    for learning in hot:
        if learning["id"] == learning_id:
            learning["use_count"] = learning.get("use_count", 0) + 1
            learning["last_used"] = datetime.now().isoformat()
            save_file(HOT_FILE, hot)
            return


def promote_to_hot(learning_id: str):
    """Manuell ein Learning nach hot verschieben."""
    recent = load_file(RECENT_FILE)
    for i, learning in enumerate(recent):
        if learning["id"] == learning_id:
            hot = load_file(HOT_FILE)
            hot.insert(0, learning)
            save_file(HOT_FILE, hot)
            recent.pop(i)
            save_file(RECENT_FILE, recent)
            return True
    return False


def archive_learning(learning_id: str):
    """Learning nach archive verschieben."""
    # Suche in recent
    recent = load_file(RECENT_FILE)
    for i, learning in enumerate(recent):
        if learning["id"] == learning_id:
            archive = load_file(ARCHIVE_FILE)
            archive.insert(0, learning)
            save_file(ARCHIVE_FILE, archive)
            recent.pop(i)
            save_file(RECENT_FILE, recent)
            return True

    # Suche in hot
    hot = load_file(HOT_FILE)
    for i, learning in enumerate(hot):
        if learning["id"] == learning_id:
            archive = load_file(ARCHIVE_FILE)
            archive.insert(0, learning)
            save_file(ARCHIVE_FILE, archive)
            hot.pop(i)
            save_file(HOT_FILE, hot)
            return True

    return False


def search_learnings(query: str) -> list:
    """Suche in allen Learnings nach Query."""
    all_learnings = load_learnings(include_archive=True)
    query_lower = query.lower()

    results = []
    for learning in all_learnings:
        if (query_lower in learning["content"].lower() or
            query_lower in learning["context"].lower() or
            any(query_lower in tag.lower() for tag in learning.get("tags", []))):
            results.append(learning)

    return results


def get_stats() -> dict:
    """Statistiken über Learnings."""
    return {
        "recent_count": len(load_file(RECENT_FILE)),
        "hot_count": len(load_file(HOT_FILE)),
        "archive_count": len(load_file(ARCHIVE_FILE)),
        "max_recent": MAX_RECENT,
        "promote_threshold": PROMOTE_THRESHOLD
    }


# CLI für direkten Aufruf
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: learnings.py [stats|list|save <content> <context>]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "stats":
        stats = get_stats()
        print(json.dumps(stats, indent=2))

    elif cmd == "list":
        learnings = load_learnings()
        for l in learnings[:10]:
            print(f"[{l['id']}] {l['content'][:60]}...")

    elif cmd == "save" and len(sys.argv) >= 4:
        content = sys.argv[2]
        context = sys.argv[3]
        tags = sys.argv[4:] if len(sys.argv) > 4 else []
        learning = save_learning(content, context, tags)
        print(f"Saved: {learning['id']}")

    else:
        print("Unknown command")
        sys.exit(1)
