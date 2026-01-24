# STAN Tasks

> **AUTO-GENERATED** from `.stan/tasks.jsonl` - DO NOT EDIT DIRECTLY
>
> Last generated: 2026-01-24 20:15:00

## Status Legend

| Symbol | Status | Meaning |
|--------|--------|---------|
| `·` | pending | Waiting to start |
| `►` | in_progress | Currently being worked on |
| `✓` | done | Completed |
| `⏸` | blocked | Blocked by dependencies |

---

## Phase: CREATE (9/9)

### ✓ t-doc1: README: Tagline + Einleitung

**Status:** done

Starker Tagline der 'autonomous' betont. Kurze Einleitung die den Wert erklärt ohne Vergleiche.

**Acceptance Criteria:**
- [x] Tagline enthält 'autonomous'
- [x] Kein Vergleich mit anderen Frameworks
- [x] Value klar in 2-3 Sätzen

---

### ✓ t-doc2: README: Kernkonzept Sektion

**Status:** done

Erklärt was autonomous-stan ist und warum. Fokus auf Modularität und Autonomie.

**Acceptance Criteria:**
- [x] Modularität erklärt
- [x] Autonomie erklärt
- [x] Kein Namedropping

**Dependencies:** t-doc1

---

### ✓ t-doc3: README: Features mit Value

**Status:** done

Jedes Feature mit WARUM. Templates, Criteria, Techniques, Phasen, Learnings.

**Acceptance Criteria:**
- [x] Jedes Feature hat Value-Erklärung
- [x] Standalone-Nutzung erwähnt
- [x] Modularität sichtbar

**Dependencies:** t-doc2

---

### ✓ t-doc4: README: Standalone-Usage Sektion

**Status:** done

Explizite Sektion die zeigt welche Komponenten einzeln nutzbar sind.

**Acceptance Criteria:**
- [x] Tabelle mit Komponenten
- [x] Beispiele für Einzelnutzung
- [x] /stan think als Beispiel

**Dependencies:** t-doc3

---

### ✓ t-doc5: README: Meta-Tricks Sektion

**Status:** done

Pro Tips: Techniques nutzen, Purpose als Einstieg, Criteria-Check als Denkwerkzeug.

**Acceptance Criteria:**
- [x] Techniques-Trick erklärt
- [x] Purpose-Trick erklärt
- [x] Criteria-Check erklärt

**Dependencies:** t-doc4

---

### ✓ t-doc6: README: Getting Started

**Status:** done

Konkreter Einstieg für neue User. Installation + erster Schritt.

**Acceptance Criteria:**
- [x] Installation klar
- [x] Erster konkreter Schritt
- [x] Erwartung gesetzt

**Dependencies:** t-doc5

---

### ✓ t-doc7: README: Workflow-Diagramm

**Status:** done

Erweitertes ASCII-Diagramm das den Flow zeigt und wo man einsteigen kann.

**Acceptance Criteria:**
- [x] Phasen sichtbar
- [x] Einstiegspunkte markiert
- [x] Modularität sichtbar

**Dependencies:** t-doc6

---

### ✓ t-doc8: Plugin CLAUDE.md Template erstellen

**Status:** done

CLAUDE.md für autonomous-stan Plugin im PITH-Format. Vollständige Anleitung für Claude.

**Acceptance Criteria:**
- [x] PITH-Format
- [x] Meta-Tricks enthalten
- [x] Phase-Workflow erklärt
- [x] Skills-Referenz

**Dependencies:** t-doc7

---

### ✓ t-doc9: Development CLAUDE.md Review

**Status:** done

Prüfen ob aktuelle CLAUDE.md für Entwicklung ausreicht. Minimal halten.

**Acceptance Criteria:**
- [x] Nicht einschränkend für Entwicklung
- [x] Verweise auf Plan korrekt
- [x] Version-Tracking aktuell

**Dependencies:** t-doc8

---

