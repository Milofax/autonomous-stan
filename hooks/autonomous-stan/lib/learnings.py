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
MAX_HOT = 20
PROMOTE_THRESHOLD = 3  # Nach 3x Nutzung -> hot
DECAY_DAYS = 14  # Nach 14 Tagen ohne Nutzung -> demote/archive


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


def calculate_heat_score(learning: dict) -> float:
    """
    Berechne Heat-Score für ein Learning.

    Score basiert auf:
    - use_count (wichtiger)
    - Recency (Tage seit letzter Nutzung)

    Returns:
        Heat-Score (höher = heißer)
    """
    use_count = learning.get("use_count", 0)
    last_used = learning.get("last_used")

    if not last_used:
        # Nie genutzt -> nur created_at
        last_used = learning.get("created_at")

    if last_used:
        try:
            last_dt = datetime.fromisoformat(last_used)
            days_ago = (datetime.now() - last_dt).days
            recency_factor = max(0, 1 - (days_ago / DECAY_DAYS))
        except (ValueError, TypeError):
            recency_factor = 0.5
    else:
        recency_factor = 0.5

    # Score: use_count gewichtet + recency bonus
    return (use_count * 2) + (recency_factor * 3)


def is_stale(learning: dict) -> bool:
    """
    Prüfe ob ein Learning "stale" ist (zu lange nicht genutzt).

    Returns:
        True wenn länger als DECAY_DAYS nicht genutzt
    """
    last_used = learning.get("last_used") or learning.get("created_at")

    if not last_used:
        return True

    try:
        last_dt = datetime.fromisoformat(last_used)
        days_ago = (datetime.now() - last_dt).days
        return days_ago > DECAY_DAYS
    except (ValueError, TypeError):
        return True


def demote_from_hot(learning_id: str) -> bool:
    """
    Demote ein Learning von hot zurück nach recent.

    Returns:
        True wenn erfolgreich
    """
    hot = load_file(HOT_FILE)
    for i, learning in enumerate(hot):
        if learning["id"] == learning_id:
            recent = load_file(RECENT_FILE)
            recent.insert(0, learning)

            # Check recent overflow
            if len(recent) > MAX_RECENT:
                overflow = recent[MAX_RECENT:]
                recent = recent[:MAX_RECENT]
                archive = load_file(ARCHIVE_FILE)
                archive.extend(overflow)
                save_file(ARCHIVE_FILE, archive)

            save_file(RECENT_FILE, recent)
            hot.pop(i)
            save_file(HOT_FILE, hot)
            return True
    return False


def rotate_learnings() -> dict:
    """
    Führe periodische Rotation durch:
    1. Stale hot Learnings -> demote oder archive
    2. Hot overflow -> demote niedrigste Scores
    3. Recent overflow -> archive

    Returns:
        Dict mit Rotation-Statistiken
    """
    stats = {
        "hot_demoted": 0,
        "hot_archived": 0,
        "recent_archived": 0
    }

    # 1. Check stale hot learnings
    hot = load_file(HOT_FILE)
    to_demote = []
    to_archive_from_hot = []

    for learning in hot:
        if is_stale(learning):
            # Wenn use_count hoch -> nur demote, sonst archive
            if learning.get("use_count", 0) >= PROMOTE_THRESHOLD:
                to_demote.append(learning["id"])
            else:
                to_archive_from_hot.append(learning["id"])

    for lid in to_demote:
        if demote_from_hot(lid):
            stats["hot_demoted"] += 1

    for lid in to_archive_from_hot:
        if archive_learning(lid):
            stats["hot_archived"] += 1

    # 2. Check hot overflow (nach Demote/Archive reload)
    hot = load_file(HOT_FILE)
    if len(hot) > MAX_HOT:
        # Sortiere nach heat score, behalte top MAX_HOT
        hot_with_scores = [(l, calculate_heat_score(l)) for l in hot]
        hot_with_scores.sort(key=lambda x: x[1], reverse=True)

        keep = [l for l, _ in hot_with_scores[:MAX_HOT]]
        demote_list = [l for l, _ in hot_with_scores[MAX_HOT:]]

        save_file(HOT_FILE, keep)

        # Demote niedrigste nach recent
        recent = load_file(RECENT_FILE)
        recent = demote_list + recent
        save_file(RECENT_FILE, recent)
        stats["hot_demoted"] += len(demote_list)

    # 3. Check recent overflow (nach Demote reload)
    recent = load_file(RECENT_FILE)
    if len(recent) > MAX_RECENT:
        overflow = recent[MAX_RECENT:]
        recent = recent[:MAX_RECENT]
        archive = load_file(ARCHIVE_FILE)
        archive.extend(overflow)
        save_file(ARCHIVE_FILE, archive)
        save_file(RECENT_FILE, recent)
        stats["recent_archived"] += len(overflow)

    return stats


def get_learning_with_score(learning_id: str) -> Optional[dict]:
    """
    Hole Learning mit berechneten Heat-Score.

    Returns:
        Learning dict mit 'heat_score' Feld oder None
    """
    all_learnings = load_learnings(include_archive=True)
    for learning in all_learnings:
        if learning["id"] == learning_id:
            learning["heat_score"] = calculate_heat_score(learning)
            learning["is_stale"] = is_stale(learning)
            return learning
    return None


def get_hot_ranked() -> list:
    """
    Hole hot Learnings sortiert nach Heat-Score.

    Returns:
        Liste von Learnings mit heat_score, absteigend sortiert
    """
    hot = load_file(HOT_FILE)
    for learning in hot:
        learning["heat_score"] = calculate_heat_score(learning)
        learning["is_stale"] = is_stale(learning)

    hot.sort(key=lambda x: x["heat_score"], reverse=True)
    return hot


def get_stats() -> dict:
    """Statistiken über Learnings."""
    hot = load_file(HOT_FILE)
    recent = load_file(RECENT_FILE)

    # Zähle stale Learnings
    stale_hot = sum(1 for l in hot if is_stale(l))
    stale_recent = sum(1 for l in recent if is_stale(l))

    return {
        "recent_count": len(recent),
        "hot_count": len(hot),
        "archive_count": len(load_file(ARCHIVE_FILE)),
        "stale_hot": stale_hot,
        "stale_recent": stale_recent,
        "max_recent": MAX_RECENT,
        "max_hot": MAX_HOT,
        "promote_threshold": PROMOTE_THRESHOLD,
        "decay_days": DECAY_DAYS
    }


# CLI für direkten Aufruf
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: learnings.py [stats|list|hot|save|rotate|demote|promote]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "stats":
        stats = get_stats()
        print(json.dumps(stats, indent=2))

    elif cmd == "list":
        learnings = load_learnings()
        for l in learnings[:10]:
            score = calculate_heat_score(l)
            stale = "⚠" if is_stale(l) else "✓"
            print(f"[{l['id']}] {stale} score={score:.1f} {l['content'][:50]}...")

    elif cmd == "hot":
        hot = get_hot_ranked()
        if not hot:
            print("Keine hot Learnings")
        else:
            for l in hot:
                stale = "⚠ STALE" if l.get("is_stale") else ""
                print(f"[{l['id']}] score={l['heat_score']:.1f} uses={l.get('use_count', 0)} {stale}")
                print(f"  {l['content'][:70]}...")

    elif cmd == "save" and len(sys.argv) >= 4:
        content = sys.argv[2]
        context = sys.argv[3]
        tags = sys.argv[4:] if len(sys.argv) > 4 else []
        learning = save_learning(content, context, tags)
        print(f"Saved: {learning['id']}")

    elif cmd == "rotate":
        result = rotate_learnings()
        print(f"Rotation complete:")
        print(f"  Hot demoted: {result['hot_demoted']}")
        print(f"  Hot archived: {result['hot_archived']}")
        print(f"  Recent archived: {result['recent_archived']}")

    elif cmd == "demote" and len(sys.argv) >= 3:
        learning_id = sys.argv[2]
        if demote_from_hot(learning_id):
            print(f"Demoted: {learning_id}")
        else:
            print(f"Not found in hot: {learning_id}")
            sys.exit(1)

    elif cmd == "promote" and len(sys.argv) >= 3:
        learning_id = sys.argv[2]
        if promote_to_hot(learning_id):
            print(f"Promoted: {learning_id}")
        else:
            print(f"Not found in recent: {learning_id}")
            sys.exit(1)

    elif cmd == "use" and len(sys.argv) >= 3:
        learning_id = sys.argv[2]
        record_usage(learning_id)
        learning = get_learning_with_score(learning_id)
        if learning:
            print(f"Usage recorded: {learning_id} (score={learning['heat_score']:.1f}, uses={learning.get('use_count', 0)})")
        else:
            print(f"Not found: {learning_id}")

    else:
        print("Unknown command")
        print("Commands: stats, list, hot, save, rotate, demote, promote, use")
        sys.exit(1)
