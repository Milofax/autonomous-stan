# Beads + BDUI — Framework-Analyse

## Kern-Idee (1 Satz pro Tool)

- **Beads (bd):** Git-basierter, verteilter Issue Tracker mit JSONL-Datenformat, der Dependencies als Dependency-Graph modelliert und speziell für AI Agents optimiert ist (JSON-Output, Auto-Sync, Conflict-Free Hash-IDs).
- **BDUI:** Terminal User Interface (TUI) für Beads mit Echtzeit-Visualisierung (Kanban, Tree, Dependency Graph, Stats), File-Watching, Search/Filter, Notifications und direkter SQLite-Anbindung.

## Architektur (JSONL, Git-backed, Graph-Struktur)

### Three-Layer Data Model

```
┌────────────────────────────────────────────────┐
│ CLI Layer (bd commands, --json support)       │
├────────────────────────────────────────────────┤
│ SQLite Database (.beads/beads.db, gitignored) │
│ - Fast queries, indexes, foreign keys         │
│ - Auto-sync (5s debounce)                     │
├────────────────────────────────────────────────┤
│ JSONL File (.beads/issues.jsonl, tracked)     │
│ - Git source of truth                         │
│ - One JSON line per entity                    │
│ - Merge-friendly (additions rarely conflict)  │
├────────────────────────────────────────────────┤
│ Remote Repository (GitHub/GitLab)             │
└────────────────────────────────────────────────┘
```

**Write Path:** `CLI Command → SQLite Write → Mark Dirty → 5s Debounce → JSONL Export → Git Commit`

**Read Path:** `Git Pull → Auto-Import → SQLite Update → CLI Query`

### Hash-Based Collision Prevention

- **Problem:** Sequential IDs (bd-1, bd-2, bd-3) verursachen Kollisionen bei parallelen Agents
- **Lösung:** UUID-basierte Hash-IDs (bd-a1b2, bd-f14c) mit progressiver Skalierung (4-6 chars)
- **Content Hashing:** Jedes Issue hat einen Content-Hash → gleiche ID + unterschiedlicher Hash = Update, nicht Duplikat
- **Resultat:** Zero-conflict merges, kein zentraler Koordinator notwendig

### Daemon Architecture

- **Pro Workspace ein Daemon** (LSP-like model)
- **RPC Server** (Unix domain socket `.beads/bd.sock`)
- **Auto-Sync Manager** batcht Operationen, hält DB-Connection offen
- **CLI-Fallback:** Direkt SQLite-Zugriff wenn Daemon nicht verfügbar

### BDUI Architecture

```
Database Reading (bd/parser.ts)
    ↓
File Watching (bd/watcher.ts, 100ms debounce)
    ↓
Zustand Store (state/store.ts)
    ↓
React/Ink Components (UI Layer)
```

- **Direkter SQLite-Zugriff** via `bun:sqlite` (kein CLI-Aufruf für Read)
- **Pub/Sub Pattern** für DB-Änderungen
- **Per-Column Pagination** (jede Status-Spalte hat eigene Scroll-Position)
- **Modal Input Handling** (Search, Filter, Forms haben exklusiven Input)

## Einzigartige Stärken (Agent-optimiertes Task-Tracking!)

### Beads (bd)

1. **Agent-First Design**
   - JSON-Output für alle Commands (`--json` Flag)
   - `bd ready` zeigt Tasks ohne Blocker (direkter Agent-Entry-Point)
   - Dependency-basiertes Blocking (Agents können autonomen Workflow folgen)
   - Auto-sync nach Session (`bd sync` erzwingt sofortigen Commit/Push)

2. **Distributed by Design**
   - Git als Database → offline-fähig, keine zentrale Infrastruktur
   - Hash-based IDs → zero-conflict bei parallelen Agents
   - Content-based Deduplication → deterministische Merges

3. **Molecular Chemistry (Templates)**
   - **Proto** (Solid): Template-Issues mit `template` Label
   - **Mol** (Liquid): Persistent instances via `bd mol pour`
   - **Wisp** (Vapor): Ephemeral instances (nicht nach JSONL exportiert!)
   - **Bonding:** Dependencies zwischen Molekülen (`bd mol bond A B`)
   - **Squash/Burn:** Wisp → Digest oder Discard

4. **Multi-Repo Routing**
   - Automatische Rolle-Detection (Maintainer vs Contributor)
   - Auto-routing basierend auf SSH/HTTPS URLs
   - Planning-Repo für Contributor (z.B. `~/.beads-planning`)
   - Discovered Issues erben `source_repo` vom Parent

5. **Git-Integration**
   - JSONL ist diff-freundlich (eine Zeile pro Entity)
   - Protected Branch Support via Sync-Branch
   - Git Hooks für Auto-Commit
   - Stealth Mode (lokal nutzen ohne Commits)

6. **Dependency Graph als Execution Model**
   - `blocks`, `parent-child`, `conditional-blocks`, `waits-for` = blocking
   - `related`, `discovered-from`, `replies-to` = non-blocking
   - Children sind **parallel by default** (nur explizite Deps erzeugen Sequenz)
   - Agents traversieren Graph bis alles blocked oder closed

### BDUI

1. **Echtzeit-Visualisierung**
   - File Watching mit 100ms Debounce (SQLite WAL Mode)
   - Automatisches Reload bei DB-Änderungen
   - Notification bei Status-Änderungen (OS-native)

2. **Multiple Views**
   - **Kanban:** 4-Spalten (Open, In Progress, Blocked, Closed)
   - **Tree:** Hierarchische Parent-Child-Relationships
   - **Dependency Graph:** ASCII-Art Visualisierung
   - **Stats:** Analytics Dashboard mit Bar Charts

3. **Direct SQLite Access**
   - Keine CLI-Aufrufe für Reads → schneller
   - Bun-native SQLite binding (`bun:sqlite`)
   - Schema: `issues`, `labels`, `dependencies` Tables

4. **Issue Management via TUI**
   - Create/Edit Forms direkt im TUI
   - Export (Markdown, JSON, Plain Text)
   - Search & Filter (Full-Text + Meta-Filter)
   - Themes (5 built-in color schemes)

## Schwächen/Limitierungen

### Beads (bd)

1. **Komplexität für Humans**
   - Molecular Chemistry Metapher ist erklärungsbedürftig
   - Viele Befehle (`bd mol pour`, `bd mol bond`, `bd mol squash`, etc.)
   - Dependency-Richtung kann verwirren ("B depends on A" → `bd dep add B A`)

2. **Keine Built-in UI**
   - CLI-only ohne BDUI
   - Humans brauchen separates Tool für Visualisierung
   - Markdown-Export verfügbar aber statisch

3. **Git-Abhängigkeit**
   - Funktioniert nur in Git-Repos
   - Sync erfordert Git-Knowledge
   - Protected Branches brauchen Workarounds (Sync Branch)

4. **Schema-Limitierungen**
   - Keine Custom Fields ohne Schema-Migration
   - Kein KV-Store (geplant aber noch nicht implementiert)
   - Issue-Types sind fixed (bug, feature, task, epic, chore)

5. **Multi-Repo Hydration Complexity**
   - Erfordert zusätzliche Config (`repos.additional`)
   - Daemons müssen in allen Repos laufen für aktuelle Daten
   - Auto-routing + Hydration nicht intuitiv ohne `bd init --contributor`

6. **Wisp Garbage Collection**
   - Wisps akkumulieren wenn nicht squashed/burned
   - `bd mol wisp gc` muss manuell aufgerufen werden
   - Keine automatische Cleanup-Policy

### BDUI

1. **Bun-Abhängigkeit**
   - Funktioniert nur mit Bun Runtime (nicht Node.js)
   - Nutzt Bun-spezifische APIs (`bun:sqlite`)
   - Deployment erfordert Bun-Installation

2. **Read-Only Limitation** (teilweise)
   - Create/Edit via BD CLI (`bd new`, `bd edit`)
   - Keine direkte SQLite-Write-Operationen für komplexe Felder
   - Forms rufen CLI-Commands auf (Overhead)

3. **Notification-Platform-Abhängigkeit**
   - macOS: volle Unterstützung
   - Linux: freedesktop.org spec
   - Windows: Toast Notifications
   - Custom Icons funktionieren nicht überall

4. **Terminal Size Constraints**
   - Minimum 80x24 (recommended 120x30)
   - Detail Panel nur bei ≥160 cols
   - Sehr kleine Terminals kaum nutzbar

5. **Keine Remote Access**
   - TUI läuft lokal, keine Web-UI
   - Kein Multi-User Collaboration
   - Keine Remote-Viewing-Optionen

## Key Features

### Beads (bd)

| Feature | Beschreibung |
|---------|--------------|
| **Hash-Based IDs** | UUID-basierte IDs (bd-a1b2) für conflict-free merges |
| **JSONL Storage** | Eine Zeile pro Entity, git-freundlich |
| **Auto-Sync** | 5s Debounce, automatischer Export zu JSONL |
| **Dependency Graph** | `blocks`, `parent-child`, `related`, `discovered-from` |
| **Molecular Chemistry** | Proto → Mol/Wisp → Digest (Template-System) |
| **Multi-Repo Routing** | Auto-routing basierend auf Role-Detection |
| **Stealth Mode** | Lokale Nutzung ohne Git-Commits |
| **Protected Branch Support** | Sync via separate Branch |
| **JSON Output** | `--json` Flag für alle Commands |
| **Daemon Mode** | Background-Daemon pro Workspace |
| **Orphan Detection** | `bd orphans` findet Issues in Git-Commits |
| **Duplicate Detection** | `bd duplicates --auto-merge` |
| **Compaction** | Memory Decay für alte Issues |
| **Editor Integration** | Hooks für Claude Code, Cursor, Aider, etc. |
| **State Management** | `bd state` + `bd set-state` für Labels als Cache |

### BDUI

| Feature | Beschreibung |
|---------|--------------|
| **Kanban View** | 4-Spalten (Open, In Progress, Blocked, Closed) |
| **Tree View** | Hierarchische Parent-Child-Visualisierung |
| **Dependency Graph** | ASCII-Art Graph mit Levels |
| **Stats Dashboard** | Analytics (Status, Priority, Type Distribution) |
| **Real-Time Updates** | File Watching mit 100ms Debounce |
| **Search & Filter** | Full-Text + Meta-Filter (Assignee, Tags, Priority, Status) |
| **Themes** | 5 built-in color schemes |
| **Notifications** | OS-native Notifications bei Status-Änderungen |
| **Create/Edit Forms** | Direkte Issue-Manipulation via TUI |
| **Export** | Markdown, JSON, Plain Text (Clipboard oder File) |
| **Per-Column Pagination** | Jede Spalte hat eigene Scroll-Position |
| **Responsive Layout** | Adapts to terminal size (1-4 columns) |
| **Vim-Style Navigation** | hjkl + arrow keys |
| **Single Binary** | Bun compile → ~50-60 MB standalone executable |

## Was autonomous-stan davon fehlt (vs .stan/tasks.jsonl)

**Aktuell hat autonomous-stan KEIN `.stan/tasks.jsonl`** (Verzeichnis existiert nicht).

**Aber basierend auf `docs/tasks.md` (generiert aus hypothetischem `.stan/tasks.jsonl`):**

### Was Beads bietet, autonomous-stan aber nicht:

1. **Dependency Graph**
   - autonomous-stan hat Phase-basierte Progression (DEFINE → PLAN → CREATE)
   - Aber: Keine granulare Task-Dependencies (Task A blocks Task B)
   - Beads: `bd dep add <child> <parent>` mit Types (blocks, parent-child, etc.)

2. **Git-Integration**
   - autonomous-stan nutzt Markdown-Dateien (`docs/plan.md`, `docs/tasks.md`)
   - Keine automatische Sync mit Git
   - Beads: JSONL ist git-tracked, auto-commit/push

3. **Hash-Based IDs**
   - autonomous-stan hat String-IDs (`t-abcd`)
   - Kollisionspotential bei parallelen Agents?
   - Beads: UUID-basierte Hashes → conflict-free

4. **Multi-Repo Support**
   - autonomous-stan ist single-repo
   - Beads: Routing + Hydration für externe Planning-Repos

5. **Molecular Templates**
   - autonomous-stan hat Templates (PRD, Plan, etc.)
   - Aber: Keine Template-basierte Task-Hierarchien
   - Beads: Proto → Mol/Wisp System

6. **Auto-Ready Detection**
   - autonomous-stan hat Status (pending, in_progress, done, blocked)
   - Aber: Kein `bd ready` Äquivalent (welche Tasks sind ohne Blocker?)
   - Beads: `bd ready` zeigt Tasks mit no open blockers

7. **JSON API**
   - autonomous-stan nutzt Markdown + YAML
   - Kein programmatisches API für Task-Management
   - Beads: `--json` Flag für alle Commands

8. **Daemon Mode**
   - autonomous-stan hat keine Background-Prozesse
   - Beads: Daemon pro Workspace für Auto-Sync

9. **Discovered Work Tracking**
   - autonomous-stan hat keine explizite "discovered-from" Dependency
   - Beads: `bd create "Bug" --deps discovered-from:<parent-id>`

10. **Duplicate Detection**
    - autonomous-stan hat keine Auto-Merge-Logic
    - Beads: `bd duplicates --auto-merge`

11. **Compaction/Memory Decay**
    - autonomous-stan hat keine automatische Archivierung alter Tasks
    - Beads: `bd admin compact --auto`

12. **State Management (Labels as Cache)**
    - autonomous-stan hat keine State-Dimensions (patrol, mode, health)
    - Beads: `bd state <id> <dimension>` + `bd set-state`

## Was autonomous-stan schon hat

1. **Phase-Workflow (DEFINE → PLAN → CREATE)**
   - Enforced durch Hooks (analog zu Beads Dependencies)
   - Nicht granular wie Beads, aber strukturiert

2. **Criteria-System**
   - YAML-basierte Quality Gates
   - Verknüpfung mit Templates via Frontmatter
   - Analog zu Beads Acceptance Criteria (aber flexibler)

3. **Templates**
   - Dokument-Templates mit Frontmatter
   - Wiederverwendbar, nicht instance-basiert wie Beads Protos

4. **Techniques (21 Denktechniken)**
   - Purpose-basierte Organisation
   - Standalone nutzbar (`/stan think`)
   - Kein Äquivalent in Beads

5. **Learnings System**
   - Lokal (`~/.stan/learnings/`) + optional Graphiti
   - Two-System Memory (Arbeitsgedächtnis + Langzeitgedächtnis)
   - Beads hat keine Learning-Extraktion

6. **Hook-basiertes Enforcement**
   - Claude Code Hooks (PostToolUse, SessionStart)
   - Automatic Criteria-Checks
   - Beads hat Editor-Integration aber nicht so deep

7. **Parallelisierung**
   - Git Worktrees + Subagents
   - File-basierte Conflict-Detection
   - Beads hat Multi-Repo aber nicht explizite Parallelisierung

8. **Markdown als Source of Truth**
   - Human-readable, diff-freundlich
   - Kein SQLite-Overhead
   - Trade-off: Keine schnellen Queries

## Vergleich mit OpenClaw (BusinessMap MCP, Cron-Jobs)

| Aspekt | Beads | autonomous-stan | OpenClaw |
|--------|-------|-----------------|----------|
| **Storage** | JSONL + SQLite | Markdown | BusinessMap API |
| **Sync** | Git (auto-commit/push) | Manuell | HTTP Requests |
| **Dependencies** | Graph (blocks, parent-child, etc.) | Phase-basiert | Workflow-Lanes |
| **Multi-Agent** | Hash-IDs, conflict-free | Worktrees + Subagents | Separate Cards |
| **Templates** | Proto → Mol/Wisp | Dokument-Templates | Card Templates? |
| **Automation** | Daemon (auto-sync) | Hooks (enforcement) | Cron-Jobs |
| **Visualisierung** | BDUI (TUI) | Markdown → HTML? | BusinessMap UI |
| **API** | `--json` Flag | YAML Parsing | MCP Server |
| **Offline** | Ja (git-backed) | Ja (file-based) | Nein (API-dependent) |
| **Queries** | SQLite (fast) | File I/O (slow) | API Calls (latency) |
| **Learning** | Nein | Ja (`~/.stan/learnings/`) | Nein |
| **Quality Gates** | Acceptance Criteria | Criteria-System | Nein |
| **Discovery** | `discovered-from` | Implicit | Nein |

### OpenClaw Specific

**BusinessMap MCP:**
- Board 5: "Stan's Projekte"
- Workflows: Initiatives (9), Cards (8)
- Skill: `skills/businessmap/SKILL.md` (Silver Partner)
- **Pro:** GUI, Collaboration, Visual Workflows
- **Contra:** API-Latency, keine Offline-Fähigkeit, kein Dependency-Graph

**Cron-Jobs:**
- Heartbeats 08:00–22:00 (Vienna)
- Periodische Aufgaben via `HEARTBEAT.md`
- **Pro:** Exact Timing, Isolation
- **Contra:** Nicht event-driven, kein Agent-Collaboration-Model

**autonomous-stan + OpenClaw Hybrid:**
- autonomous-stan für **lokale Entwicklung** (DEFINE, PLAN, CREATE)
- OpenClaw/BusinessMap für **Team-Coordination** (Public Roadmap, Epics)
- Beads könnte **Bridge** sein (local planning → remote coordination)

## Konkrete Übernahme-Empfehlungen

### 1. JSONL als Storage Layer (HIGH PRIORITY)

**Why:**
- Git-friendly (eine Zeile pro Task)
- Maschinell lesbar (kein Markdown-Parsing)
- Konfliktfrei bei Merges
- Schnelle Queries (via SQLite-Import optional)

**How:**
```jsonl
{"id":"t-abc","title":"Test","status":"done","phase":"CREATE","created_at":"2026-01-25T22:25:38Z"}
```

**Migration:**
- `docs/tasks.md` → generiert aus `.stan/tasks.jsonl`
- Markdown bleibt human-readable, JSONL ist source of truth
- Analog zu Beads: SQLite optional für Queries

**Effort:** Medium (Parser schreiben, Schema definieren)

---

### 2. Dependency Graph (MEDIUM PRIORITY)

**Why:**
- Granulare Task-Dependencies (nicht nur Phase-basiert)
- Agent kann `ready` Tasks erkennen (keine Blocker)
- Parallelisierung wird explizit (nicht file-basiert)

**How:**
```yaml
# tasks.jsonl
{"id":"t-1","title":"Design API","status":"pending"}
{"id":"t-2","title":"Implement API","status":"pending","depends_on":["t-1"]}
{"id":"t-3","title":"Write Tests","status":"pending","depends_on":["t-2"]}
```

**Commands:**
- `stan task ready` → zeigt Tasks ohne Blocker
- `stan task blocked` → zeigt geblockte Tasks
- `stan dep add <child> <parent>`

**Effort:** High (Dependency-Logic, Ready-Detection)

---

### 3. Hash-Based IDs (LOW PRIORITY)

**Why:**
- Conflict-free bei parallelen Agents
- Keine zentrale ID-Vergabe nötig

**Why NOT:**
- autonomous-stan hat aktuell keine Multi-Agent-Parallelität
- String-IDs (`t-abc`) sind human-friendlier
- Nur relevant bei Multi-Repo oder parallel Agents

**When:** Wenn Multi-Agent-Support kommt

**Effort:** Medium (ID-Generation, Collision-Detection)

---

### 4. Molecular Templates (MEDIUM PRIORITY)

**Why:**
- autonomous-stan hat Templates, aber keine Instance-basierte Workflows
- Proto → Mol System passt zu DEFINE → PLAN → CREATE
- Wisp = Ephemeral Tasks (z.B. für Experimentation)

**How:**
```bash
# Template definieren
stan template create "Feature Template" --proto

# Instanz erzeugen
stan template pour "Feature Template" --var name="OAuth"

# Ephemeral Instance (nicht committen)
stan template wisp "Spike Template"
```

**Use Case:**
- Feature Template → pour → Feature Tasks
- Spike Template → wisp → Experimentation (discard oder squash)

**Effort:** High (Template-Engine, Instance-Management)

---

### 5. Auto-Sync via Daemon (LOW PRIORITY)

**Why:**
- autonomous-stan nutzt Hooks (synchron)
- Daemon wäre async Background-Process
- Auto-commit/push nach jeder Task-Änderung

**Why NOT:**
- Hooks sind ausreichend für Single-Agent
- Daemon braucht Process-Management
- Git-Auto-Commit kann störend sein (noise in history)

**When:** Wenn Multi-Agent-Support + Remote-Sync nötig

**Effort:** High (Daemon-Architecture, Auto-Sync-Logic)

---

### 6. CLI mit `--json` Flag (HIGH PRIORITY)

**Why:**
- Programmatisches API für Task-Management
- Agent kann Output parsen (keine Markdown-Parsing)
- Konsistent mit Beads Design

**How:**
```bash
stan task list --json
# Output: [{"id":"t-abc","title":"Test","status":"done"}]

stan task create "New Task" --json
# Output: {"id":"t-xyz","title":"New Task","status":"pending"}
```

**Effort:** Low (CLI-Framework + JSON-Serializer)

---

### 7. Discovered Work Tracking (MEDIUM PRIORITY)

**Why:**
- Beads hat `discovered-from` Dependency
- autonomous-stan hat keine explizite Discovery-Tracking
- Nützlich für: "Während Task A entdeckte ich Bug B"

**How:**
```bash
# Während t-1 bearbeitet, Bug entdeckt
stan task create "Fix Auth Bug" --discovered-from t-1

# Erzeugt:
# - Neuen Task t-xyz mit `discovered_from: t-1`
# - Optional: Auto-link zu parent task
```

**Effort:** Low (Metadata-Field + CLI-Flag)

---

### 8. State Management (Labels as Cache) (LOW PRIORITY)

**Why:**
- Beads nutzt Labels für operational state (patrol, mode, health)
- autonomous-stan hat keine State-Dimensions
- Nützlich für: Agent-Status, Health-Checks

**Why NOT:**
- autonomous-stan ist kein long-running Agent-System
- State ist eher für Orchestrators (gastown, witness)

**When:** Wenn autonomous-stan Agent-Orchestration braucht

**Effort:** Medium (State-Dimensions definieren, Event-Log)

---

### 9. BDUI-ähnliches TUI (LOW PRIORITY)

**Why:**
- Visualisierung von Tasks (Kanban, Tree, Graph)
- Real-time Updates bei File-Changes
- Search & Filter

**Why NOT:**
- autonomous-stan zielt auf Agents, nicht Humans
- Markdown ist human-readable genug
- TUI braucht separates Projekt

**When:** Wenn Human-Collaboration wichtig wird

**Effort:** Very High (TUI-Framework, Visualisierung)

---

### 10. Multi-Repo Routing (LOW PRIORITY)

**Why:**
- Beads hat Auto-routing für Contributor vs Maintainer
- autonomous-stan ist single-repo

**Why NOT:**
- Kein OSS-Contributor Use Case erkennbar
- Routing braucht Role-Detection + Config

**When:** Wenn autonomous-stan als Framework für externe Projekte genutzt wird

**Effort:** High (Routing-Logic, Role-Detection)

---

## Priorisierte Roadmap

### Phase 1: Foundation (JETZT)
1. **JSONL Storage** (`.stan/tasks.jsonl` als source of truth)
2. **CLI mit `--json` Flag** (programmatisches API)
3. **Discovered Work Tracking** (`--discovered-from`)

**Warum:** Low Effort, High Impact, kein Breaking Change

---

### Phase 2: Graph Model (SPÄTER)
4. **Dependency Graph** (`depends_on` + `ready` detection)
5. **Molecular Templates** (Proto → Mol/Wisp System)

**Warum:** High Effort, aber fundamentale Workflow-Verbesserung

---

### Phase 3: Scaling (OPTIONAL)
6. **Hash-Based IDs** (nur wenn Multi-Agent nötig)
7. **Auto-Sync Daemon** (nur wenn Remote-Sync nötig)
8. **Multi-Repo Routing** (nur wenn OSS-Workflow nötig)

**Warum:** Nur relevant bei Scale-up

---

## Fazit

**Beads ist ein Agent-optimiertes Issue-Tracking-System, das Git als Database nutzt und Dependency-Graphen als Execution-Model modelliert.**

**autonomous-stan ist ein Workflow-Framework mit Criteria-basierter Quality-Assurance und Template-basierter Strukturierung.**

**Die beiden sind komplementär:**
- Beads = **Task-Tracking + Execution** (Was muss wann gemacht werden?)
- autonomous-stan = **Quality + Structure** (Wie wird es richtig gemacht?)

**Die größte Lücke in autonomous-stan:**
- Kein Dependency Graph (nur Phase-basiert)
- Kein maschinell lesbares API (nur Markdown)
- Keine Discovery-Tracking

**Die größte Stärke von autonomous-stan:**
- Criteria-System (Quality Gates)
- Techniques (Denktechniken)
- Learnings (Memory)

**Hybrid-Ansatz:**
- **JSONL Storage** übernehmen (git-friendly, maschinell lesbar)
- **Dependency Graph** integrieren (granulare Task-Dependencies)
- **CLI mit `--json`** bauen (programmatisches API)
- **Criteria-System behalten** (unique feature)
- **Techniques behalten** (unique feature)
- **BDUI inspirieren lassen** (aber nicht nachbauen)

**Das würde autonomous-stan zu einem vollständigen Agent-Framework machen: Structure + Quality + Execution.**
