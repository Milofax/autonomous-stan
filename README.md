# autonomous-stan

**Autonomes Workflow-Framework mit modularen Denkwerkzeugen für Claude Code.**

Templates, Criteria, Techniques - zusammen ein stringenter Workflow, einzeln nutzbare Denkwerkzeuge.

## Was ist autonomous-stan?

autonomous-stan ermöglicht **autonome, qualitativ hochwertige Implementierung** mit wenig Korrektur. Das Framework besteht aus modularen Komponenten die zusammen oder einzeln funktionieren:

- **Templates** - Wiederverwendbare Dokument-Vorlagen (PRD, Plan, Style Guide)
- **Criteria** - Qualitätsprüfungen als YAML, verknüpfbar mit Templates
- **Techniques** - 21 Denktechniken, organisiert nach 9 Purposes
- **Phasen** - DEFINE → PLAN → CREATE Workflow mit Enforcement
- **Learnings** - Lokales Arbeitsgedächtnis + optionales Langzeitgedächtnis

Das Kernprinzip: **Hooks enforce Rules. Der User muss sich nichts merken.**

## Features

### Modulare Templates

Erstelle eigene Dokument-Templates mit Frontmatter.
Templates verknüpfen sich mit Criteria - bei jedem Dokument werden automatisch die relevanten Quality Gates geprüft.

```yaml
---
type: prd
criteria:
  - goal-quality
  - text-quality
---
```

### Flexible Criteria

Definiere Qualitätsprüfungen als atomare YAML-Dateien.
Ein Criteria kann von mehreren Templates genutzt werden. Criteria werden zu Checklisten - alle required Checks müssen bestehen.

```yaml
name: Goal Quality
checks:
  - id: concrete
    question: "Is the goal specific and measurable?"
    required: true
```

### Purpose-basierte Techniques

21 Denktechniken, organisiert nach 9 Purposes (Einstiegspunkten):

| Purpose | Frage |
|---------|-------|
| Root Cause Analysis | Warum passiert das? |
| Ideation | Welche Möglichkeiten gibt es? |
| Perspective Shift | Wie sehen andere das? |
| Structured Problem Solving | Wie zerlege ich das systematisch? |
| Decision Making | Welche Option wähle ich? |

`/stan think` funktioniert auch standalone - ohne Projekt, ohne Workflow.

### Phasen-Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   [DEFINE] ──────────> [PLAN] ──────────> [CREATE]         │
│   Interaktiv           Interaktiv         Autonom           │
│   PRD erstellen        Tasks planen       Ausführen         │
│                                                             │
│   ▲                                           │             │
│   └───────── Reconciliation ◄─────────────────┘             │
│              (bei fundamentalen Änderungen)                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

Phasen-Übergänge werden durch Hooks enforced:
- DEFINE → PLAN: PRD muss `status: approved` haben
- PLAN → CREATE: Mindestens 1 Task muss `status: ready` haben

### Parallelisierung

autonomous-stan unterstützt parallele Ausführung:

- **Git Worktrees** für isolierte Feature-Branches
- **Subagents** für parallele Task-Bearbeitung
- **Dependency-Tracking** verhindert Konflikte

Tasks mit verschiedenen Dateien können parallel bearbeitet werden. Der Hauptagent orchestriert.

### Two-System Learnings

| System | Zweck | Wann |
|--------|-------|------|
| Lokal (`~/.stan/learnings/`) | Arbeitsgedächtnis, schnell | Während der Arbeit |
| Graphiti (optional) | Langzeitgedächtnis, kuratiert | Am Projekt-Ende |

Learnings werden automatisch erkannt (Test ROT→GRÜN) und müssen vor Commit gespeichert werden.

## Standalone-Nutzung

Jede Komponente funktioniert auch einzeln:

| Komponente | Standalone-Nutzung |
|------------|-------------------|
| `/stan think` | Denktechniken für jedes Problem - ohne Projekt |
| `/stan build-template` | Template erstellen - ohne Phase-Workflow |
| `/stan build-criteria` | Criteria erstellen - ohne Projekt |
| Templates | Als Markdown-Vorlagen in jedem Kontext |
| Criteria | Als manuelle Checklisten |
| Techniques | Als YAML-Dateien lesbar, manuell anwendbar |

## Pro Tips: Denkwerkzeuge nutzen

### "Nutze Techniques"

Steckst du fest? `/stan think` zeigt passende Denktechniken.
Funktioniert für JEDES Problem - Code, Text, Entscheidungen, Architektur.

### "Nutze Purpose als Einstieg"

Weißt du nicht wo anfangen?
- "Warum passiert das?" → Root Cause Analysis
- "Welche Optionen habe ich?" → Ideation
- "Wie sieht das aus Sicht X aus?" → Perspective Shift

### "Gedanklicher Criteria-Check"

Bevor du etwas abschließt:
> "Wenn ich Criteria dafür anlegen würde - würde das bestehen?"

Das funktioniert für PRDs, Code, Texte, Entscheidungen - alles.

## Quick Start

```bash
# Repository klonen
git clone https://github.com/Milofax/autonomous-stan.git
cd autonomous-stan

# Submodules initialisieren
git submodule update --init --recursive
```

### Erster Schritt

```bash
# In einem Projekt mit autonomous-stan:
/stan init           # Projekt initialisieren
/stan define         # PRD erstellen
/stan plan           # Tasks ableiten
/stan create         # Autonom ausführen
```

Oder standalone:
```bash
/stan think          # Bei jedem Problem - Techniques nutzen
```

## Skills

| Skill | Beschreibung |
|-------|--------------|
| `/stan init` | Projekt starten, stan.md erstellen |
| `/stan define` | DEFINE Phase - PRD, Style Guide, etc. |
| `/stan plan` | PLAN Phase - Tasks ableiten |
| `/stan create` | CREATE Phase - autonom ausführen |
| `/stan statusupdate` | Status anzeigen + manuell ändern |
| `/stan healthcheck` | Konsistenz prüfen |
| `/stan think` | Denktechniken anwenden (standalone) |
| `/stan build-template` | Template interaktiv bauen |
| `/stan build-criteria` | Criteria interaktiv bauen |
| `/stan ready` | Tasks ohne Blocker anzeigen |
| `/stan complete` | Projekt abschließen (Land the Plane) |

## Struktur

```
autonomous-stan/
├── .claude/
│   ├── hooks/stan/        # Enforcement Hooks
│   ├── commands/stan/     # /stan Skills
│   └── rules/             # Verhaltensregeln
├── criteria/              # Qualitätskriterien (YAML)
├── templates/             # Dokument-Templates (Markdown)
├── techniques/            # Denktechniken (YAML)
│   └── purposes/          # 9 Purpose-Einstiegspunkte
├── .stan/                 # Session State + Tasks
│   ├── tasks.jsonl        # Source of Truth für Tasks
│   └── session.json       # Persistent Session State
└── docs/
    ├── plan.md            # Implementierungsplan
    └── tasks.md           # Generated from JSONL
```

## Dokumentation

- [Implementierungsplan](docs/plan.md)
- [Tasks](docs/tasks.md)

## Status

🚧 **Initial Development (0.x.x)**

## Lizenz

MIT License - siehe [LICENSE](LICENSE)
