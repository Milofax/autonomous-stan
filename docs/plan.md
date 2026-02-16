# STAN Framework - Finaler Implementation Plan

**Ziel:** Leichtgewichtiges Framework für autonome, qualitativ hochwertige Implementierung mit wenig Korrektur.

**Kernprinzip:** Hooks enforced Rules. Der User muss sich nichts merken.

---

## Architektur-Übersicht

```
┌─────────────────────────────────────────────────────────────┐
│                     STAN Framework                          │
├─────────────────────────────────────────────────────────────┤
│  3 Hooks (Enforcement)                                      │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │stan-context │ │ stan-track  │ │  stan-gate  │           │
│  │UserPrompt   │ │ PostToolUse │ │ PreToolUse  │           │
│  │Submit       │ │ (Bash)      │ │             │           │
│  └─────────────┘ └─────────────┘ └─────────────┘           │
├─────────────────────────────────────────────────────────────┤
│  Two-Layer State                                            │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │ Session State        │  │ Manifest (persistent)│        │
│  │ /tmp/claude-*.json   │  │ stan.md + docs/*.md  │        │
│  │ (flüchtig)           │  │ (Git-tracked)        │        │
│  └──────────────────────┘  └──────────────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  Learnings Storage (Zwei-System-Architektur)                │
│  ┌──────────────────────┐  ┌──────────────────────┐        │
│  │ LOKAL (immer)        │  │ GRAPHITI (optional)  │        │
│  │ ~/.stan/learnings/   │  │ Kuratiert, am Ende   │        │
│  │ recent/hot/archive   │  │ via taming-stan Hook │        │
│  └──────────────────────┘  └──────────────────────┘        │
├─────────────────────────────────────────────────────────────┤
│  Criteria Packs (modular)                                   │
│  code_quality | text_quality | responsive | strategy        │
└─────────────────────────────────────────────────────────────┘
```

---

## Entity Model

### Übersicht aller Entitäten

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           STAN ENTITY MODEL                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  DOKUMENTE & VORLAGEN                    QUALITÄTSSICHERUNG              │
│  ════════════════════                    ══════════════════              │
│                                                                          │
│  Template ──1:n──> Document              Criteria ──1:n──> Check         │
│  (templates/)      (docs/)               (criteria/)                     │
│       │                │                      ▲                          │
│       │                │                      │                          │
│       └── criteria ────┴──────────────────────┘                          │
│           (frontmatter)                                                  │
│                                                                          │
│  PROJEKT-STATUS                          AUFGABEN                        │
│  ══════════════                          ════════                        │
│                                                                          │
│  stan.md ◄─────────────────────────────► Task                           │
│  (Manifest)    phase, current_task       (.stan/tasks.jsonl)            │
│                                               │                          │
│                                               ├── acceptance_criteria    │
│                                               │   ├── {criteria-name}    │
│                                               │   └── "free text"        │
│                                               │        (Success Criteria)│
│                                               └── dependencies           │
│                                                                          │
│  DENKMETHODEN                                                            │
│  ════════════                                                            │
│                                                                          │
│  Purpose ──n:m──> Technique                                              │
│  (purposes/)      (techniques/)                                          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Entitäten im Detail

| Entität | Pfad | Beschreibung | Format |
|---------|------|--------------|--------|
| **Template** | `templates/*.template` | Vorlage für Dokumente | Markdown + YAML Frontmatter |
| **Document** | `docs/*.md` | Erstelltes Dokument (PRD, Plan) | Markdown + YAML Frontmatter |
| **stan.md** | `stan.md` (Root) | Projekt-Manifest mit Status | Markdown + YAML Frontmatter |
| **Task** | `.stan/tasks.jsonl` | Arbeitseinheit | JSONL (1 Zeile = 1 Task) |
| **Criteria** | `criteria/*.yaml` | Qualitätsprüfungen | YAML |
| **Check** | (Teil von Criteria) | Einzelner Prüfpunkt | YAML (in Criteria) |
| **Purpose** | `techniques/purposes/*.yaml` | Einstiegspunkt für Denkmethoden | YAML |
| **Technique** | `techniques/*.yaml` | Konkrete Denkmethode | YAML |

### Beziehungen

#### Template → Document (1:n)

```
Template                          Document
═════════                         ════════
templates/prd.md.template   ──>   docs/prd.md
templates/plan.md.template  ──>   docs/plan.md (nur Referenz)
templates/stan.md.template  ──>   stan.md
```

**Hinweis:** `docs/plan.md` wird nicht aus Template generiert, sondern ist dieses Dokument.
Tasks kommen aus `.stan/tasks.jsonl`, nicht aus dem Plan-Template.

#### Document/Task → Criteria (n:m)

**Zwei Ebenen der Criteria-Referenzierung:**

| Ebene | Wo | Syntax | Prüft |
|-------|-----|--------|-------|
| **Document-level** | Frontmatter | `criteria: [goal-is-smart]` | Dokument als Ganzes |
| **Task-level** | acceptance_criteria | `"Text {code-quality}"` | Einzelne Implementierung |

```yaml
# Document-level (prd.md Frontmatter)
---
criteria:
  - goal-is-smart      # Wird gegen das PRD geprüft
  - text-quality       # Wird gegen das PRD geprüft
---

# Task-level (.stan/tasks.jsonl)
{
  "acceptance_criteria": [
    "Tests pass {code-quality}",     # → Criteria YAML laden
    "User finds UI intuitive"        # → Success Criteria (Sonnet)
  ]
}
```

#### Criteria → Check (1:n)

```yaml
# criteria/code-quality.yaml
name: Code Quality
evaluator_model: haiku
checks:                           # 1 Criteria hat n Checks
  - id: tests-pass
    question: "Do all tests pass?"
    required: true
  - id: lint-pass
    question: "Does code pass linting?"
    required: true
```

#### Task Acceptance Criteria: Zwei Typen

| Typ | Syntax | Beispiel | Evaluator |
|-----|--------|----------|-----------|
| **Acceptance Criteria** | `{criteria-name}` | `"Lint OK {code-quality}"` | Model aus YAML |
| **Success Criteria** | Freier Text | `"User finds UI beautiful"` | Immer Sonnet |

#### Purpose ↔ Technique (n:m)

```yaml
# techniques/five-whys.yaml
purposes:                         # Technique gehört zu Purposes
  - root-cause-analysis
  - self-reflection

# techniques/purposes/root-cause-analysis.yaml
techniques:                       # Purpose empfiehlt Techniques
  - five-whys
  - fishbone-diagram
```

### Widersprüche aufgelöst

| Problem | Auflösung |
|---------|-----------|
| **Template zeigt Markdown-Tasks** | Template ist nur Referenz. Tasks kommen aus JSONL. Template aktualisieren. |
| **stan.md "Current Task"** | Wird dynamisch aus JSONL gelesen (erster `in_progress` Task) |
| **Document-level vs Task-level Criteria** | Beide valid! Document-level = Dokument-Qualität, Task-level = Implementierungs-Qualität |
| **Acceptance Criteria Format** | In JSONL: Strings. `{criteria-name}` Syntax für YAML-Referenz. |

### Dateisystem-Struktur

```
project/
├── stan.md                      # Manifest (Phase, Status)
├── docs/
│   ├── prd.md                   # Document (aus Template)
│   └── tasks.md                 # GENERATED from JSONL (read-only!)
├── .stan/
│   └── tasks.jsonl              # SOURCE OF TRUTH für Tasks
├── criteria/
│   ├── code-quality.yaml        # Criteria mit Checks
│   └── text-quality.yaml
└── techniques/
    ├── five-whys.yaml           # Technique
    └── purposes/
        └── root-cause-analysis.yaml  # Purpose
```

---

## Entity Syntax Specifications

### Template Syntax

**Datei:** `templates/*.template`

```markdown
---
type: prd|plan|manifest           # REQUIRED: Dokumenttyp
status: draft                     # Initial status
created: {{date}}                 # Placeholder, wird ersetzt
updated: {{date}}
criteria:                         # Document-level Criteria
  - goal-is-smart
  - text-quality
---

# {{title}}

Markdown content with {{placeholders}}...
```

| Feld | Typ | Required | Beschreibung |
|------|-----|----------|--------------|
| `type` | string | ✓ | `prd`, `plan`, `manifest` |
| `status` | string | ✓ | `draft`, `in_review`, `approved` |
| `criteria` | list | ✗ | Criteria-Namen für Document-level Prüfung |
| `{{placeholder}}` | - | - | Wird bei Erstellung ersetzt |

### Document Syntax

**Datei:** `docs/*.md`, `stan.md`

Identisch zu Template, aber mit ausgefüllten Werten:

```markdown
---
type: prd
status: approved
created: 2026-01-25
updated: 2026-01-25
criteria:
  - goal-is-smart
  - text-quality
---

# My Feature PRD

Actual content...
```

### Task Syntax (JSONL)

**Datei:** `.stan/tasks.jsonl` (Source of Truth)

```json
{
  "id": "t-a1b2",
  "subject": "Implement login form",
  "description": "Create login form with email/password fields",
  "status": "pending",
  "phase": "create",
  "dependencies": ["t-x9y8"],
  "acceptance_criteria": [
    "Tests pass {code-quality}",
    "Form validates input {code-quality}",
    "User finds flow intuitive"
  ],
  "owner": null,
  "created_at": "2026-01-25T10:00:00Z",
  "updated_at": "2026-01-25T10:00:00Z"
}
```

| Feld | Typ | Required | Beschreibung |
|------|-----|----------|--------------|
| `id` | string | ✓ | Hash-ID mit Prefix `t-` |
| `subject` | string | ✓ | Kurztitel |
| `description` | string | ✗ | Detaillierte Beschreibung |
| `status` | enum | ✓ | `pending`, `in_progress`, `done`, `blocked` |
| `phase` | enum | ✓ | `define`, `plan`, `create` |
| `dependencies` | list | ✗ | Task-IDs die vorher done sein müssen |
| `acceptance_criteria` | list | ✗ | Strings, optional mit `{criteria-name}` |
| `owner` | string | ✗ | Agent-Name bei Multi-Agent |
| `created_at` | ISO8601 | ✓ | Erstellungszeitpunkt |
| `updated_at` | ISO8601 | ✓ | Letzte Änderung |

**Acceptance Criteria Syntax:**

```
"Beschreibender Text {criteria-name}"   → Acceptance Criteria (YAML)
"Freier beschreibender Text"            → Success Criteria (Sonnet)
```

### Criteria Syntax (YAML)

**Datei:** `criteria/*.yaml`

```yaml
name: Code Quality                      # REQUIRED: Display name
description: Code quality checks        # Optional description
evaluator_model: haiku                  # haiku | sonnet | opus

checks:
  - id: tests-pass                      # REQUIRED: Unique ID
    question: "Do all tests pass?"      # REQUIRED: Evaluation question
    required: true                      # Default: true
    auto: true                          # Optional: Can be automated?
    commands:                           # Optional: Auto-check commands
      - pattern: "package.json"
        command: "npm test"
      - pattern: "pytest.ini"
        command: "pytest"

  - id: lint-pass
    question: "Does code pass linting?"
    required: true
```

| Feld | Typ | Required | Beschreibung |
|------|-----|----------|--------------|
| `name` | string | ✓ | Anzeigename |
| `description` | string | ✗ | Beschreibung |
| `evaluator_model` | enum | ✗ | `haiku` (default), `sonnet`, `opus` |
| `checks` | list | ✓ | Liste von Check-Objekten |
| `checks[].id` | string | ✓ | Eindeutige ID innerhalb Criteria |
| `checks[].question` | string | ✓ | Frage für Evaluator |
| `checks[].required` | bool | ✗ | Muss erfüllt sein? (default: true) |
| `checks[].auto` | bool | ✗ | Automatisierbar? |
| `checks[].commands` | list | ✗ | Commands für Auto-Check |

### Purpose Syntax (YAML)

**Datei:** `techniques/purposes/*.yaml`

```yaml
id: root-cause-analysis                 # REQUIRED: Unique ID
name: "Root Cause Analysis"             # REQUIRED: Display name
question: "Why did this happen?"        # REQUIRED: Trigger question

description: |                          # Optional: Longer description
  Techniques for systematically identifying
  the actual cause of a problem.

techniques:                             # REQUIRED: Recommended techniques
  - five-whys                           # Primary recommendation
  - fishbone-diagram
  - after-action-review

triggers:                               # Optional: When to suggest
  - "Error occurs repeatedly"
  - "Bug found, but why?"

recommended_start: five-whys            # Optional: Default technique
recommended_start_reason: "Quick, needs no tools"

escalation: |                           # Optional: When to switch
  If Five Whys doesn't work, try Fishbone.
```

| Feld | Typ | Required | Beschreibung |
|------|-----|----------|--------------|
| `id` | string | ✓ | Eindeutige ID |
| `name` | string | ✓ | Anzeigename |
| `question` | string | ✓ | Kernfrage des Purpose |
| `techniques` | list | ✓ | Empfohlene Techniques |
| `triggers` | list | ✗ | Wann diesen Purpose vorschlagen |
| `recommended_start` | string | ✗ | Standard-Technique |

### Technique Syntax (YAML)

**Datei:** `techniques/*.yaml`

```yaml
id: five-whys                           # REQUIRED: Unique ID
name: "Five Whys"                       # REQUIRED: Display name
description: "Get to root cause"        # REQUIRED: Short description

steps:                                  # REQUIRED: How to apply
  - "Formulate problem clearly"
  - "Ask: 'Why did this happen?'"
  - "Take answer as new statement"
  - "Repeat until root cause (typically 5x)"

purposes:                               # REQUIRED: Which purposes use this
  - root-cause-analysis
  - self-reflection

aliases:                                # Optional: Alternative names
  - "5 Whys"
  - "Why-Why Analysis"

source: "Toyota Production System"      # Optional: Origin
duration: "5-15 min"                    # Optional: Time estimate
participants: "Solo or team"            # Optional: Who

examples:                               # Optional: Usage examples
  - situation: "Bug in code"
    application: |
      1. Why crash? → Null pointer
      2. Why null? → Not initialized
      ...

when_to_use:                            # Optional: Good scenarios
  - "Problem occurs repeatedly"

when_not:                               # Optional: Bad scenarios
  - "Complex multi-cause systems"

tips:                                   # Optional: Pro tips
  - "Don't stop at exactly 5"

related:                                # Optional: Related techniques
  - fishbone-diagram

tags:                                   # Optional: Categorization
  - analysis
  - debugging
```

| Feld | Typ | Required | Beschreibung |
|------|-----|----------|--------------|
| `id` | string | ✓ | Eindeutige ID |
| `name` | string | ✓ | Anzeigename |
| `description` | string | ✓ | Kurzbeschreibung |
| `steps` | list | ✓ | Schritte zur Anwendung |
| `purposes` | list | ✓ | Zu welchen Purposes gehört diese Technique |
| `examples` | list | ✗ | Anwendungsbeispiele |
| `when_to_use` | list | ✗ | Wann nutzen |
| `when_not` | list | ✗ | Wann nicht nutzen |

---

## Phasen-Modell

```
[DEFINE] ──────> [PLAN] ──────> [CREATE]
Interaktiv      Interaktiv      Autonom
PRD erstellen   Tasks planen    Ausführen
```

### Phasen-Übergänge (via stan-gate enforced)

| Von | Nach | Bedingung |
|-----|------|-----------|
| DEFINE | PLAN | PRD `status: approved` |
| PLAN | CREATE | Min. 1 Task `status: ready` |
| CREATE | DEFINE | Fundamentale Änderung (Reconciliation) |

### Discovery/Onboarding

Ist **Teil von DEFINE**, keine separate Phase. Claude erkennt automatisch die Reife des User-Inputs:
- Vage Idee → Interview-Modus
- Klares Konzept → Direkt PRD strukturieren
- Fertiges PRD → Nur validieren

---

## Hook-Architektur (3 Hooks)

### 1. stan-context (UserPromptSubmit)

**Zweck:** Kontext in jede Nachricht injizieren

```python
def on_user_prompt_submit():
    # 1. Manifest lesen
    manifest = read_manifest("stan.md")

    # 2. Session State prüfen/erstellen
    session = get_or_create_session_state()

    # 3. Lokale Learnings laden (hot + recent)
    local_learnings = load_local_learnings()  # ~/.stan/learnings/

    # 4. Kontext injizieren
    # Graphiti Query passiert via bestehende taming-stan Hooks!
    return {
        "continue": True,
        "systemMessage": f"""
[STAN] Phase: {manifest.phase} | Task: {manifest.current_task}
[Lokale Learnings: {len(local_learnings)} geladen]
"""
    }
```

**Hinweis:** Graphiti Query passiert bereits via bestehende taming-stan Hooks (UserPromptSubmit). STAN fügt nur lokale Learnings hinzu.

### 2. stan-track (PostToolUse - Bash)

**Zweck:** Test-Ergebnisse tracken + Learnings AUTOMATISCH erkennen

```python
def on_post_tool_use(tool, result):
    if tool != "Bash":
        return

    session = get_session_state()

    # Test-Commands erkennen
    if is_test_command(result.command):
        previous_result = session.get_last_test_result(result.command)

        session.test_results.append({
            "command": result.command,
            "exit_code": result.exit_code,
            "timestamp": now()
        })

        # LEARNING DETECTION: Test war ROT, jetzt GRÜN
        if previous_result and previous_result.exit_code != 0 and result.exit_code == 0:
            session.pending_learnings.append({
                "type": "error_resolution",
                "command": result.command,
                "detected_at": now(),
                "saved": False
            })
            # Inject reminder
            return {"systemMessage": "[STAN] Learning erkannt! Vor Commit speichern."}

        save_session_state(session)
```

**Enforcement:** Wenn ein Test von ROT auf GRÜN wechselt, wird automatisch ein `pending_learning` erstellt. Ich MUSS dieses Learning speichern bevor ich committen kann.

### 3. stan-gate (PreToolUse)

**Zweck:** Phase-Enforcement + Quality Gates + Learnings-Enforcement + **Worktree-Enforcement** (BLOCKIERT)

```python
def on_pre_tool_use(tool, params):
    manifest = read_manifest("stan.md")
    session = get_session_state()

    # 0. WORKTREE ENFORCEMENT (nur bei Git-Projekten)
    if is_git_repo() and is_commit_tool(tool):
        if is_feature_work() and is_main_worktree():
            return deny("[STAN] Feature-Arbeit auf main! Erst Worktree erstellen:\n"
                       "git branch feature-name && git worktree add ../project-feature feature-name")

    # 1. LEARNINGS ENFORCEMENT (vor Commit)
    if is_commit_tool(tool):
        unsaved = [l for l in session.pending_learnings if not l["saved"]]
        if unsaved:
            return deny(f"[STAN] {len(unsaved)} ungespeicherte Learnings! Erst speichern.")

    # 2. Quality Gates (nur in CREATE)
    if manifest.phase == "create" and is_commit_tool(tool):
        if not session.tests_passed():
            return deny("Tests müssen erst grün sein")

    # 3. Phase-Wechsel Enforcement
    if is_phase_transition(params):
        if not can_transition(manifest, params.new_phase):
            return deny(f"Kann nicht zu {params.new_phase} wechseln")

    # 4. 3-Strikes Check
    if session.error_count >= 3:
        return deny("3 gleiche Fehler. Perspektivwechsel erforderlich.")

    return allow()

def is_main_worktree():
    """Prüft ob wir im Haupt-Worktree sind (nicht in einem Feature-Worktree)."""
    # git worktree list zeigt alle Worktrees
    # Haupt-Repo hat keine "(bare)" oder Feature-Branch Markierung
    result = run("git rev-parse --git-dir")
    return ".git" in result  # Haupt-Repo hat .git Verzeichnis, Worktrees haben .git Datei

def is_feature_work():
    """Heuristik: Ist das eine Feature-Arbeit oder triviale Änderung?"""
    # Trivial: < 3 Dateien geändert, keine neuen Dateien, kein src/
    staged = run("git diff --cached --name-only")
    if len(staged.split()) < 3 and "src/" not in staged:
        return False
    return True
```

**Enforcement Chain:**
```
stan-track: Test ROT→GRÜN erkannt → pending_learning erstellt
stan-gate:  Commit versucht → BLOCKIERT wenn pending_learnings
            → Ich MUSS save_local_learning() aufrufen
            → Dann darf ich committen
```

**Hinweis:** Graphiti Write passiert NICHT automatisch. Nur am Projekt-Ende bewusst kuratiert.

---

## Two-Layer State

### Session State (flüchtig)

**Pfad:** `/tmp/claude-session-{hash}.json`

```json
{
  "session_id": "abc123",
  "started_at": "2026-01-21T10:00:00Z",
  "learnings_queried": true,
  "pending_learnings": [],
  "test_results": [
    {"command": "npm test", "exit_code": 0, "timestamp": "..."}
  ],
  "error_count": 0,
  "last_error_type": null
}
```

### Manifest (persistent)

**Dateien:**
- `stan.md` - Hauptmanifest mit Quick Status
- `docs/prd.md` - PRD im Detail
- `docs/plan.md` - Task-Plan im Detail

**stan.md Format:**

```yaml
---
phase: create
current_task: T-003
graphiti_group: Milofax-featurename
criteria_packs:
  - code_quality
  - responsive
---
# Feature: Dark Mode

PRD: [docs/prd.md](docs/prd.md)
Plan: [docs/plan.md](docs/plan.md)

## Quick Status
- ✓ T-001: Next.js Setup
- ✓ T-002: Tailwind Config
- ► T-003: Theme Toggle Component
- · T-004: Persistence
- ⏸ GATE-1: MVP Review
```

---

## Task-Typen

| Typ | Wer | Wann weiter |
|-----|-----|-------------|
| `auto` | Claude autonom | Nach Acceptance Criteria |
| `manual` | User selbst | User markiert als done |
| `review` | Claude macht, User prüft | User bestätigt |
| `gate` | Checkpoint | User explizit approved |

---

## Criteria-Struktur

**Konzept:** 1 YAML = 1 Criteria (atomar, kombinierbar, wiederverwendbar)

### Struktur

```
criteria/
├── goal-quality.yaml        # Was macht ein gutes Ziel aus?
├── vision-quality.yaml      # Was macht eine gute Vision aus?
├── business-value-quality.yaml
├── user-stories-quality.yaml
├── text-quality.yaml        # Allgemeine Textqualität
├── code-quality.yaml        # Code-Standards
├── a11y.yaml                # Accessibility
├── responsive.yaml          # Responsive Design
└── brand-consistency.yaml   # Marken-Konsistenz
```

### Criteria-Typen

| Typ | Beschreibung | Beispiel |
|-----|--------------|----------|
| `self_check` | Claude prüft selbst | text-quality, goal-quality |
| `auto` | Automatischer Command | code-quality (npm test) |
| `manual` | User muss prüfen | responsive (auf Geräten testen) |

### Beispiel-Criteria

```yaml
# criteria/code-quality.yaml
name: Code-Qualität
description: Technische Code-Standards
type: auto

checks:
  - id: tests
    question: "Sind alle Tests grün?"
    command: npm test
    required: true

  - id: typecheck
    question: "Keine TypeScript-Fehler?"
    command: npm run typecheck
    required: true

  - id: lint
    question: "Keine Lint-Fehler?"
    command: npm run lint
    required: false
```

---

## Autonome Execution

### Dependency Management

Tasks werden als DAG (Directed Acyclic Graph) verwaltet:

```
T-001 ──┐
        ├──> T-003 ──> GATE-1
T-002 ──┘
```

Ein Task ist `ready` wenn:
- Status: `pending`
- Alle Dependencies: `done`

### Iterations-Limit

Nach 3 gleichen Fehlern:
1. STOP
2. Pattern dokumentieren
3. 6 Perspektiven durchgehen
4. Neue Hypothese (substantiell anders)

Bei Retry 2: Graphiti nach existierenden Learnings durchsuchen (falls verfügbar)

### Execution Modi

| Modus | Beschreibung |
|-------|--------------|
| `step` | Ein Task, dann Feedback |
| `until-gate` | Bis zum nächsten Gate |
| `fire-and-forget` | Alles Auto, nur bei Gate/Manual stoppen |

---

## Parallelisierung (Git Worktrees + Subagents)

**Prinzip:** Parallelisierung NUR in CREATE Phase, NUR nach Planung mit Dependencies.

### Voraussetzungen

1. PLAN Phase muss abgeschlossen sein
2. Task-Dependencies müssen klar sein
3. Datei-Berührungen pro Task müssen bekannt sein

### Task-Plan mit Parallelisierungs-Info

```yaml
tasks:
  - id: T-001
    name: "Auth Setup"
    touches: [src/auth.ts, src/config.ts]
    depends_on: []

  - id: T-002
    name: "API Routes"
    touches: [src/api.ts]
    depends_on: []
    parallel_with: [T-001]  # explizit erlaubt

  - id: T-003
    name: "Auth Middleware"
    touches: [src/auth.ts]  # gleiche Datei wie T-001!
    depends_on: [T-001]     # muss warten
```

### Hauptagent orchestriert

```
Hauptagent analysiert Task-Plan:

├── T-001 + T-002: Keine Überschneidung → PARALLEL
├── T-003: Abhängig von T-001, gleiche Datei → SEQUENTIELL nach T-001
└── T-004: Unabhängig → kann parallel zu T-003

Entscheidung:
1. Spawne Subagent 1 → T-001
2. Spawne Subagent 2 → T-002 (parallel)
3. Warte auf T-001
4. Spawne Subagent 3 → T-003
```

### Git-Projekte: Worktrees

```
main (Worktree 1)
  └── Subagent 1 → T-001

feature-api (Worktree 2)
  └── Subagent 2 → T-002 (parallel, isoliert)
```

**Vorteile:**
- Isolierte Branches
- Keine Merge-Konflikte während Arbeit
- Am Ende: PR/Merge

### Nicht-Git-Projekte

Auch möglich, aber:
- Hauptagent muss Datei-Konflikte verhindern
- Nur Tasks mit verschiedenen Dateien parallel
- Keine künstliche Aufteilung erzwingen

### Regeln

1. **Keine Parallelisierung vor PLAN** - Dependencies müssen klar sein
2. **Hauptagent entscheidet** - Keine automatische Parallelisierung
3. **Keine künstliche Aufteilung** - Nur wenn natürlich möglich
4. **Bei Unsicherheit: sequentiell** - Sicherheit vor Geschwindigkeit

---

## Learnings Storage (Zwei-System-Architektur)

**Prinzip:** Lokal = Arbeitsgedächtnis (schnell, dirty). Graphiti = Langzeitgedächtnis (kuratiert, wertvoll).

### System 1: Lokaler Tiered Storage (IMMER verfügbar)

```
~/.stan/learnings/
├── recent.json      # Rolling ~50 Learnings (aktuelle Session/Woche)
├── hot.json         # Oft genutzt, weighted by usage + recency
└── archive.json     # Komprimiert, historisch
```

**Tiered Retention (inspiriert von Protocol Harness):**

| Layer | Inhalt | Retention |
|-------|--------|-----------|
| Recent | Neue Learnings | Rolling ~50, FIFO |
| Hot | Oft genutzte | Promoted bei Mehrfachnutzung |
| Archive | Alle historischen | Permanent, komprimiert |

**Während autonomer Arbeit:**
- Alle Learnings → `recent.json` (schnell, kein Overhead)
- Bei Mehrfachnutzung → Promote zu `hot.json`
- Bei Overflow → Älteste zu `archive.json`

### System 2: Graphiti (Langzeitgedächtnis, OPTIONAL)

**Lesen:** Via bestehende taming-stan Hooks (UserPromptSubmit)
- Passiert automatisch bei Session-Start
- Kein Widerspruch zu bestehenden Hooks

**Schreiben:** Nur am ENDE, kuratiert
- Phase-Ende oder Projekt-Ende
- Review: "Welche Learnings sind wirklich wertvoll?"
- Bewusste Entscheidung: `main` (allgemein) oder `{Owner}-{Repo}` (projekt-spezifisch)

### Workflow

```
Session-Start:
  └─ Graphiti Query (via taming-stan Hook) ✓ existiert bereits

Während autonomer Arbeit (CREATE Phase):
  └─ Learnings → LOKAL (recent.json)
  └─ KEIN Graphiti-Write (kein Overhead)

Phase-Ende / Projekt-Ende:
  └─ Review lokale Learnings (~/.stan/learnings/)
  └─ Kuratieren: "Was ist wirklich wertvoll?"
  └─ Wertvolle Learnings → Graphiti
      ├─ Allgemeingültig → group_id: "main"
      └─ Projekt-spezifisch → group_id: "{Owner}-{Repo}"
```

### Vorteile dieser Trennung

| Aspekt | Lokal | Graphiti |
|--------|-------|----------|
| Verfügbarkeit | IMMER | Optional |
| Geschwindigkeit | Schnell | Langsamer (API) |
| Qualität | Dirty, alles | Kuratiert, wertvoll |
| Zweck | Arbeitsgedächtnis | Langzeitgedächtnis |
| Wann schreiben | Kontinuierlich | Nur am Ende |

---

## Skills

| Skill | Beschreibung |
|-------|--------------|
| `/stan init` | Projekt starten, stan.md erstellen |
| `/stan define` | DEFINE Phase starten/fortsetzen (PRD, Style Guide, etc.) |
| `/stan plan` | PLAN Phase starten/fortsetzen (Tasks ableiten) |
| `/stan create` | CREATE Phase starten (autonom ausführen) |
| `/stan statusupdate` | Status anzeigen + manuell ändern |
| `/stan healthcheck` | Konsistenz prüfen (Templates ↔ Criteria, offene Reviews) |
| `/stan build-template` | Template interaktiv bauen |
| `/stan build-criteria` | Criteria interaktiv bauen |

### Skills: Standalone vs. Projekt-Kontext

Skills funktionieren **beides:**

| Kontext | Verhalten |
|---------|-----------|
| **Mit stan.md** | Skill arbeitet im Projekt-Kontext, respektiert Phase |
| **Ohne stan.md** | Skill arbeitet standalone (z.B. "nur schnell ein PRD") |

### Widerworte bei Phase-Wechsel

Wenn Phase-Wechsel bedeutsam ist → **nachfragen, nicht blind akzeptieren:**

```
User ruft /stan define auf während CREATE läuft:

[STAN] Du bist gerade in CREATE (Task T-003 läuft).
       Zurück zu DEFINE = Reconciliation.

       Grund? (neues Feature / Problem erkannt / Abbruch)
```

### Lose Kopplung: Skills ↔ Templates

Skills sind **NICHT** fest an Templates gebunden:

```
/stan define
→ "Was willst du definieren?"
→ PRD? Style Guide? API Spec? Custom?
→ DANN passendes Template (wenn gewünscht)
```

Flexibel: Skill wählt Template basierend auf Bedarf, nicht hardcoded.

---

## Dynamische Denktechniken-Bibliothek

**Prinzip:** Techniken nach Zweck organisiert. "Was will ich erreichen?" → passende Techniken.

### Architektur

```
┌─────────────────────────────────────────────────────────────┐
│  Denktechniken-System                                       │
├─────────────────────────────────────────────────────────────┤
│  Atomare Techniken (einzeln gespeichert)                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ Five     │ │ Shadow   │ │ SCAMPER  │ │ First    │ ...   │
│  │ Whys     │ │ Work     │ │ Method   │ │ Principles│      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
├─────────────────────────────────────────────────────────────┤
│  Zweck-basierte Organisation (n:m Beziehung)                │
│                                                             │
│  Zweck erkannt → Techniken anzeigen → Empfehlung → User wählt│
├─────────────────────────────────────────────────────────────┤
│  Dynamisches Laden zur Laufzeit                             │
│  (NICHT als Rules - zu statisch)                            │
└─────────────────────────────────────────────────────────────┘
```

### Die 9 Zwecke (finale Entscheidung)

| Zweck | Frage | Techniken |
|-------|-------|-----------|
| **Ursachenanalyse** | Warum passiert X? | Five Whys, First Principles, Hypothesis Generation, Evidence-based Investigation, Anti-pattern Hunting, Assumption Reversal |
| **Ideenfindung** | Welche Möglichkeiten gibt es? | What If Scenarios, Analogical Thinking, Random Stimulation, SCAMPER, Nature's Solutions, Ecosystem Thinking, Evolutionary Pressure, Reversal Inversion, Provocation Technique, Chaos Engineering, Pirate Code Brainstorm |
| **Perspektivwechsel** | Wie sieht X aus Sicht Y aus? | Six Thinking Hats, Role Playing, Alien Anthropologist, Future Self Interview, Time Travel Talk Show |
| **Strukturierte Problemlösung** | Wie zerlege ich X systematisch? | Mind Mapping, Morphological Analysis, Resource Constraints, Systematic Decomposition |
| **Code-Review** | Ist dieser Code gut? | Systematic Review Checklist, Pattern Compliance Checking |
| **Big Picture** | Wie hängt alles zusammen? | Data Flow Tracing, Pattern Identification, Ecosystem Thinking |
| **Selbstreflexion** | Was will/fühle/denke ICH? | Inner Child Conference, Shadow Work Mining, Values Archaeology, Body Wisdom Dialogue, Permission Giving |
| **Teamarbeit** | Wie denken wir GEMEINSAM? | Yes And Building, Brain Writing Round Robin, Ideation Relay Race |
| **Entscheidungsfindung** | Welche Option wähle ich? | Six Thinking Hats, First Principles, Superposition Collapse |

### Überschneidungen (n:m bestätigt)

- Six Thinking Hats → Perspektivwechsel, Entscheidungsfindung
- First Principles → Ursachenanalyse, Entscheidungsfindung
- Ecosystem Thinking → Ideenfindung, Big Picture

### Nutzungs-Pattern

**Zwei Einstiegspunkte, gleicher Flow:**

1. **User ruft Zweck-Skill auf:** `/stan think ursachenanalyse`
2. **Claude erkennt Situation:** "Du steckst fest → Soll ich Techniken für Ursachenanalyse zeigen?"

**Flow (immer gleich):**
```
Zweck erkannt
    ↓
Passende Techniken anzeigen
    ↓
Eine empfehlen (mit Begründung)
    ↓
User wählt (oder lehnt ab)
    ↓
Technik anwenden (mit User-Consent)
```

### Kernideen

1. **Atomare Techniken:** Jede Technik einzeln gespeichert, erweiterbar
2. **n:m Beziehung:** Eine Technik kann mehreren Zwecken dienen
3. **Dynamisches Laden:** Skills laden Techniken zur Laufzeit basierend auf Zweck
4. **Transparenz:** Nie Technik überstülpen, immer zeigen was existiert
5. **Eigene Struktur:** Techniken im Projekt (BMAD als Quelle, dann unabhängig)

### Quellen

- **BMAD:** 62 Techniken in brain-methods.csv (explizit)
- **PRP:** Implizite Techniken in prp-debug.md, prp-review.md, codebase-analyst.md, silent-failure-hunter.md

---

## Dokument-Versionierung (Lifecycle)

**Prinzip:** Dokumente haben einen klaren Lebenszyklus. Status wird im Frontmatter getrackt.

### 5-Stufen Status-Modell

| Status | Bedeutung | Phase |
|--------|-----------|-------|
| `draft` | Dokument wird erstellt | DEFINE |
| `approved` | Dokument fertig, bereit zur Verwendung | DEFINE → PLAN |
| `in-progress` | Feature wird implementiert | CREATE |
| `done` | Feature fertig, Dokument hat Zweck erfüllt | Nach CREATE |
| `archived` | Historisch, aufgeräumt | Optional |

### Lifecycle-Flow

```
draft ──────> approved ──────> in-progress ──────> done ──────> archived
  │              │                  │                │            │
  │              │                  │                │            │
Dokument      User gibt         CREATE Phase      Feature      Optional:
wird          OK                startet           fertig       Aufräumen
geschrieben                                                    nach docs/archive/
```

### Status-Übergänge

| Übergang | Trigger | Wer |
|----------|---------|-----|
| draft → approved | User bestätigt Dokument | User (manuell) |
| approved → in-progress | CREATE Phase startet | Automatisch (stan-gate) |
| in-progress → done | Alle Tasks abgeschlossen | Automatisch (stan-gate) |
| done → archived | User räumt auf | User (manuell) |

### Frontmatter

```yaml
---
type: prd
status: draft  # draft | approved | in-progress | done | archived
created: 2026-01-22
updated: 2026-01-22
criteria:
  - goal-quality
---
```

### Archivierung

**Zwei Mechanismen (beide):**
1. Frontmatter-Status auf `archived` setzen (Source of Truth)
2. Optional: Datei nach `docs/archive/` verschieben (für Ordnung)

### Fertig-Kriterien

Nur Criteria-Checks. Keine separate "TODO-Platzhalter" Prüfung.

### Keine Zeit-basierte Archivierung

Dokumente veralten durch Kontext (Feature fertig), nicht durch Zeit. Keine automatische 24h-Regel.

### Entscheidungen (aus Recherche PRP/BMAD)

- PRP: 3 Status (pending/in-progress/complete), verzeichnis-basierte Archivierung
- BMAD: 5 Status für Stories, zeit-basierte Archivierung (24h - zu aggressiv)
- **STAN:** 5 Status, kontext-basierte Archivierung, Frontmatter als Source of Truth

---

## Templates

**Format:** Markdown-Dateien mit Frontmatter

```yaml
# templates/prd.md
---
type: prd
criteria:
  - goal-quality
  - business-value-quality
  - user-stories-quality
  - text-quality
---

# {Feature Name}

## Ziel

Beschreibe in einem Satz, was am Ende existieren soll.
Das Ziel sollte konkret und messbar sein.

## Warum

Erkläre den Business Value und welches Problem gelöst wird.

## Features

Liste die Hauptfeatures als User Stories:
- Als [Rolle] will ich [Aktion], damit [Nutzen]

## Einschränkungen

Was ist NICHT Teil? Technische Constraints?
```

**Prinzipien:**
- Templates sind lesbar (Markdown mit Beschreibungen)
- `criteria:` Liste verknüpft mit Criteria
- Verknüpfung passiert am Ende des Template-Makers

---

## Criteria

**Format:** 1 YAML = 1 Criteria (atomar, kombinierbar)

```yaml
# criteria/goal-quality.yaml
name: Ziel-Qualität
description: Was macht ein gutes Ziel aus?

checks:
  - id: concrete
    question: "Ist das Ziel konkret und spezifisch?"
    required: true

  - id: measurable
    question: "Ist messbar wann das Ziel erreicht ist?"
    required: true

  - id: one-sentence
    question: "Passt das Ziel in einen Satz?"
    required: false
```

**Prinzipien:**
- Atomar: Ein Criteria = ein Aspekt (Ziel, Vision, Text-Qualität...)
- Kombinierbar: Template hat mehrere Criteria
- Wiederverwendbar: `goal-quality` kann in PRD, Strategy, Pitch-Deck genutzt werden

**Criteria werden zu Checklisten:**
```
☐ Ist das Ziel konkret und spezifisch? (required)
☐ Ist messbar wann das Ziel erreicht ist? (required)
☐ Passt das Ziel in einen Satz? (optional)
```

**Gate:** Alle required Checks müssen abgehakt sein, sonst blockiert.

---

## Interaktive Criteria-Tests (LLM-as-Judge)

**Prinzip:** Claude testet sich selbst. Criteria werden zu Evaluation-Prompts.

### Struktur

```
tests/criteria-eval/
├── evaluators/
│   ├── goal_quality_eval.md      # Evaluation-Prompt für goal-quality.yaml
│   ├── text_quality_eval.md      # Evaluation-Prompt für text-quality.yaml
│   └── ...
├── golden/                        # Referenz-Beispiele (few shot)
│   ├── good_goal.md              # Beispiel für gutes Ziel
│   ├── bad_goal.md               # Beispiel für schlechtes Ziel
│   └── ...
└── runner.py                      # Test-Runner Script
```

### LLM-as-Judge Patterns (aus Recherche)

| Pattern | Beschreibung |
|---------|--------------|
| **Few shot prompting** | Beispiele geben was gut/schlecht ist |
| **Step decomposition** | Große Entscheidungen in kleine Schritte |
| **Criteria decomposition** | Eine Evaluation = ein Kriterium |
| **Grading rubric** | Klare 1-5 Skala mit Beschreibung pro Level |
| **Structured outputs** | JSON statt Freitext |
| **Provide explanations** | LLM erklärt WARUM |
| **Score smoothing** | Trends über Zeit, nicht einzelne Scores |

### Evaluator Template

```markdown
# Evaluation: {criteria_name}

## Kontext
Du evaluierst ein Artefakt gegen das Criteria "{criteria_name}".

## Grading Rubric
- 5 = Perfekt erfüllt
- 4 = Größtenteils erfüllt, kleine Mängel
- 3 = Teilweise erfüllt, deutliche Lücken
- 2 = Kaum erfüllt, große Probleme
- 1 = Nicht erfüllt

## Beispiele
### Gut (Score 5):
{golden/good_example.md}

### Schlecht (Score 1):
{golden/bad_example.md}

## Zu evaluieren
{artefakt}

## Output Format (JSON)
{
  "criteria": "{criteria_name}",
  "checks": [
    {"id": "check_id", "question": "...", "score": 1-5, "explanation": "..."}
  ],
  "overall_score": 1-5,
  "summary": "..."
}
```

### Test-Ablauf

1. Claude liest Criteria YAML
2. Claude generiert/erhält ein Artefakt (z.B. PRD-Ziel)
3. Claude evaluiert das Artefakt gegen jeden Check
4. Output: JSON mit Score (1-5) + Erklärung pro Check
5. Checks mit `required: true` müssen Score ≥4 haben

### Integration mit /stan healthcheck

```
/stan healthcheck --eval-criteria

[STAN] Evaluiere Criteria gegen Golden Examples...

goal-quality:
  ✓ concrete: 5/5 - Ziel ist spezifisch und eindeutig
  ✓ measurable: 4/5 - Messbar, aber Zeitrahmen fehlt
  ✗ one-sentence: 2/5 - Ziel ist zu lang (3 Sätze)

Overall: 3.7/5 (WARN: Check 'one-sentence' unter Threshold)
```

---

## /stan build-template (Template Maker)

**Workflow:**

```
1. Interaktiv Template bauen
   → "Was für ein Dokument?"
   → "Welche Abschnitte brauchst du?"
   → Template-Inhalt erstellen

2. User zufrieden mit Inhalt

3. Criteria verknüpfen (MultiSelect)
   → "Welche Criteria sollen gelten?"
   → Zeige alle existierenden Criteria
   → User wählt passende aus

4. Speichern
   → criteria: [...] im Template Frontmatter
   → Template in templates/ speichern
```

---

## /stan build-criteria (Criteria Maker)

**Workflow:**

```
1. Interaktiv Criteria bauen
   → "Was soll geprüft werden?"
   → "Welche Checks?"
   → Criteria-Inhalt erstellen

2. User zufrieden mit Checks

3. Templates identifizieren
   → "Diese bestehenden Templates könnten profitieren:"
   → style-guide.md, prd.md, ...
   → "Soll ich die Referenz dort ergänzen?"

4. Speichern
   → Criteria in criteria/ speichern
   → Optional: Templates aktualisieren
```

**Konsistenz-Check:**
- Bei Criteria-Änderung → Warnung welche Templates betroffen
- User entscheidet ob anpassen (keine automatische Kaskade)

---

## Document Discovery (Dynamischer Scan)

**KEINE statische Registry.** Stattdessen: Scan + Frontmatter.

**Bei Session-Start / Phase-Wechsel:**
```
1. Scanne docs/*.md
2. Lese Frontmatter jeder Datei
3. Vergleiche mit bekanntem State
4. "Neue Datei entdeckt: docs/style-guide.md (type: style_guide)"
```

**Dokument-Frontmatter:**
```yaml
# docs/prd.md
---
type: prd
status: approved
criteria:
  - goal-quality
  - text-quality
created: 2026-01-21
---
```

**Vorteile:**
- User erstellt Datei manuell → wird automatisch entdeckt
- Kein manuelles Eintragen in Registry
- Frontmatter = Source of Truth

---

## Reconciliation (CREATE → DEFINE)

**Trigger:** Manuell via User oder Claude wenn fundamental was nicht stimmt.

**Beispiele:**
- "Das geht technisch nicht wie spezifiziert"
- "Stakeholder-Feedback widerspricht PRD"

**Flow:**
```
CREATE (arbeitet)
    │
    ├─ Problem erkannt
    │
    ▼
[STAN] "Reconciliation nötig? Grund: [X]"
    │
    ├─ User bestätigt
    │
    ▼
Phase → DEFINE (betroffene Docs überarbeiten)
    ▼
Phase → PLAN (Tasks neu evaluieren)
    ▼
Phase → CREATE (Fortsetzung)
```

**Kein automatischer Trigger.** User/Claude entscheiden bewusst.

---

## File Structure (Plugin Format)

```
autonomous-stan/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
│
├── commands/
│   └── autonomous-stan/         # Slash commands (/stan ...)
│       ├── init.md
│       ├── define.md
│       ├── plan.md
│       ├── create.md
│       └── ...
│
├── hooks/
│   ├── hooks.json               # Hook configuration
│   └── autonomous-stan/
│       ├── stan_context.py      # UserPromptSubmit
│       ├── stan_track.py        # PostToolUse (Bash)
│       ├── stan_gate.py         # PreToolUse
│       └── lib/                 # Shared Python modules
│           ├── document.py
│           ├── learnings.py
│           ├── session_state.py
│           ├── task_schema.py
│           ├── task_generator.py
│           └── techniques.py
│
├── criteria/                    # Quality criteria (flat, with prefixes)
│   ├── code-quality.yaml
│   ├── text-quality.yaml
│   ├── goal-is-smart.yaml
│   └── ...
│
├── templates/
│   ├── stan.md.template
│   ├── prd.md.template
│   ├── plan.md.template
│   └── plugin-claude.md.template
│
├── techniques/                  # Thinking techniques
│   ├── *.yaml                   # 21+ techniques
│   ├── purposes/                # 9 entry points
│   └── schema.yaml
│
├── docs/
│   ├── plan.md                  # This file
│   └── tasks.md                 # Generated from .stan/tasks.jsonl
│
└── vendor/                      # Reference frameworks (submodules)
    ├── BMAD-METHOD/
    ├── ralph/
    └── claude-agent-sdk/

# Global learnings directory (user home)
~/.stan/
└── learnings/
    ├── recent.json              # Rolling ~50, FIFO
    ├── hot.json                 # Frequently used, promoted
    └── archive.json             # Permanent, compressed
```

---

## Implementierungs-Reihenfolge

### Phase 1: Foundation ✓
1. ✓ Templates erstellen (stan.md, prd.md, plan.md)
2. ✓ Criteria Pack Struktur + erste Packs (code_quality)
3. ✓ Lokales Learnings-System (`~/.stan/learnings/`)

### Phase 2: Core Hooks ✓
4. ✓ stan-context: Manifest lesen, lokale Learnings laden, Kontext injizieren
5. ✓ stan-track: Test-Ergebnisse tracken
6. ✓ stan-gate: Phase-Enforcement, Quality Gates, Learnings lokal speichern

### Phase 3: Skill ✓
7. ✓ /stan Skill: Init, Status, Phase-Navigation
8. ✓ Learnings-Review Command (für Projekt-Ende)

### Phase 4: Testing & Enforcement ✓
9. ✓ Worktree-Enforcement in stan-gate
10. ✓ Unit Tests für Hooks (357 Tests)
11. ✓ Interaktive Criteria-Tests (LLM-as-Judge Pattern)

### Phase 5: Tiered Storage ✓
12. ✓ Recent → Hot Promotion (bei Mehrfachnutzung)
13. ✓ Recent → Archive Rotation (bei Overflow)
14. ✓ Heat Map / Usage Tracking

### Phase 6-11: Weitere Phasen ✓
- ✓ Denktechniken-Bibliothek (21 Techniques, 9 Purposes)
- ✓ Dokument-Versionierung (5-Stufen Lifecycle)
- ✓ Criteria Packs (23 Criteria)
- ✓ E2E Integration Tests
- ✓ Internationalisierung (Commands auf Englisch)
- ✓ Pre-Launch Review (Ralph/BMAD Gap Analysis)

### Phase 12: Enforcement Completion ►
15. ✓ Acceptance Criteria Completion Check (Ralph-Style Loop)
    - Hook blockiert Commit wenn nicht alle Checkboxen abgehakt
    - Iteration Counter mit Max 10 (wie Ralph)
    - 357 Tests grün
16. · Test-Projekt für Hook-Aktivierung (separates Projekt)

### Phase 13: Gap-Analysis Items ✓
17. ✓ Project Complexity Levels (0-4) - in config.py implementiert
18. ✓ Max Iterations konfigurierbar (in session_state.py)
19. ~ `/stan archive` - Redundant, `/stan complete` archiviert bereits

### Phase 14: Version-Tracking & Auto-Updates ✓
20. ✓ CLAUDE.md erweitern mit Version-Tracking Sektion

### Phase 15: Autonomie-Features ✓
21. ✓ Loop-Logik in `/stan create` (autonome Execution-Loop)
22. ✓ Persistent Session State (`.stan/session.json`)
23. ✓ Model Auto-Selection (complexity-basiert + Escalation)

### Phase 16: Terminology Cleanup ✓
24. ✓ Rename "archived" to "completed"

### Phase 17: JSONL Task System ✓
25. ✓ JSONL Schema + Validator (T-047)
26. ✓ .stan/ Directory Structure (T-048)
27. ✓ Markdown Generator JSONL → docs/tasks.md (T-049)
28. ✓ Sync Layer: JSONL ↔ Claude Tasks (T-050, T-051)
29. ✓ /stan ready Skill (T-052)
30. ✓ /stan complete Skill - Land the Plane (T-053)
31. ✓ /stan plan + /stan create Integration (T-054)
32. ✓ E2E Integration Test (T-055)

---

## Detaillierte Task-Spezifikationen

> **Hinweis:** T-037 bis T-040 wurden durch Phase 17 (JSONL Task System) ersetzt.
> Die Implementierung erfolgte in `task_schema.py`, `task_sync.py`, `task_generator.py`.

### T-041: CLAUDE.md Version-Tracking

**Beschreibung:** CLAUDE.md mit Version-Tracking Sektion erweitern.

**Dependencies:** Keine

**Dateien:**
- `CLAUDE.md`

**Acceptance Criteria:**
- [ ] Sektion "Claude Code Version-Tracking"
- [ ] Feld `claude_code_version_checked` mit Datum
- [ ] Anweisung für automatische Prüfung bei Session-Start
- [ ] Tabelle "Relevante Features für STAN"

---

**CLAUDE.md Erweiterung (sofort umsetzen):**

```markdown
## Claude Code Version-Tracking

**Zuletzt geprüft:** v2.1.19 (2026-01-24)

### Automatische Prüfung

Bei Session-Start in diesem Projekt:
1. Prüfe aktuelle Claude Code Version (`claude --version`)
2. Wenn neuer als `claude_code_version_checked` → Changelog lesen
3. Analysiere Impact auf STAN:
   - Breaking Changes → Sofort informieren
   - Neue Features → Prüfen ob STAN profitieren kann
   - Bug Fixes → Relevanz für Hooks/Skills prüfen
4. Update `claude_code_version_checked` nach Analyse

### Relevante Features für STAN

| Version | Feature | Impact |
|---------|---------|--------|
| v2.1.16 | Claude Tasks System | Hybrid-Integration geplant |
| v2.1.19 | CLAUDE_CODE_ENABLE_TASKS env | Kann alte Todos wiederherstellen |
```

---

## Complexity Levels (0-4)

**Quelle:** BMAD Framework "Scale-Adaptive Levels"

### Die 5 Levels

| Level | Name | Planungstiefe | Beispiel |
|-------|------|---------------|----------|
| 0 | Trivial | Keine Planung, direkt umsetzen | Typo fixen |
| 1 | Minimal | Nur Ziel + Tasks | Button-Farbe ändern |
| 2 | Standard | PRD-Light (Ziel, Stories, Tasks) | Dark Mode |
| 3 | Detailed | Volles PRD | API-Redesign |
| 4 | Comprehensive | PRD + ADRs + Reviews | Compliance-Feature |

### Lifecycle

```
1. INITIAL ASSESSMENT (Transparent)
   ┌─────────────────────────────────────┐
   │ Meine Einschätzung: Level 2         │
   │ Grund: Betrifft ~5 Files, UI + Logic│
   │                                     │
   │ Passt das? (ja / Level anpassen)    │
   └─────────────────────────────────────┘

2. USER OVERRIDE
   User kann korrigieren: "Nee, Level 1 reicht"

3. RE-ASSESSMENT (während Arbeit)
   Wenn sich Komplexität ändert → User informieren:
   "Ursprünglich Level 1, jetzt Level 3 weil..."

4. ESCALATION (bei großem Sprung)
   Level 1 → Level 4 = Reconciliation vorschlagen
```

### Was beeinflusst das Level?

- **Datei-Anzahl:** 1-2 Files = niedrig, 10+ Files = hoch
- **Abhängigkeiten:** Standalone = niedrig, viele Dependencies = hoch
- **Risiko:** Nur UI = niedrig, Datenbank/Auth = hoch
- **Unbekannte:** Klares Konzept = niedrig, Exploration nötig = hoch

### Speicherung

```yaml
# stan.md
---
phase: create
complexity: 2  # 0-4
complexity_reason: "Dark Mode: UI + Theme-System"
---
```

**Hinweis:** Graphiti-Integration existiert bereits via taming-stan Hooks. STAN nutzt das für Query, schreibt aber nur lokal während der Arbeit.

---

## Archivierung

**Prinzip:** Expliziter Trigger, Feature-Name, User entscheidet.

### Wann archivieren?

**NICHT automatisch.** Archivierung passiert NUR wenn:
- User explizit sagt: "Das Feature ist fertig"
- User explizit sagt: "Kannst du das alte PRD archivieren?"
- Neues Feature startet und altes PRD stört

**NICHT nach CREATE Phase.** CREATE = implementiert, aber nicht zwingend "fertig" (könnte noch Iteration kommen).

### Wie archivieren?

1. **Frontmatter-Status ändern:**
   ```yaml
   status: archived
   archived_at: 2026-01-24
   ```

2. **Optional: Datei verschieben** nach `docs/archive/`

### Dateinamen

**Feature-Name, NICHT Datum:**
- ✓ `prd-dark-mode.md`
- ✓ `prd-auth-redesign.md`
- ✗ `prd-2026-01-24.md` (Datum allein sagt nichts)

Datum steckt im Frontmatter (`created`, `archived_at`).

### `/stan archive` Command (geplant)

```
/stan archive

[STAN] Aktive Dokumente mit status: done:
  - docs/prd.md (Dark Mode)
  - docs/plan.md

Welche archivieren? (alle / auswählen / abbrechen)
```

---

## JSONL Task System + Claude Tasks Integration

> **Entscheidung (2026-01-24):** JSONL als Source of Truth statt Markdown.
> Markdown wird generiert (read-only). Claude Tasks für Runtime-Koordination.
> Inspiriert von beads (vendor/beads/).

### Drei-Schichten-Architektur

```
┌─────────────────────────────────────────────────────────────┐
│  .stan/tasks.jsonl (Source of Truth)                        │
│  ════════════════════════════════════                       │
│  • Hash-basierte IDs (t-a1b2) - kollisionsfrei              │
│  • Ein Task pro Zeile (JSONL)                               │
│  • Git-tracked, merge-freundlich                            │
│  • Alle Felder: acceptance_criteria, dependencies, owner    │
├─────────────────────────────────────────────────────────────┤
│  docs/tasks.md (Generated - READ ONLY)                      │
│  ═══════════════════════════════════════                    │
│  • Human-readable Markdown                                  │
│  • Auto-generiert nach jeder JSONL-Änderung                 │
│  • Gruppiert nach Phase                                     │
│  • Status-Symbole (·, ►, ✓, §)                              │
├─────────────────────────────────────────────────────────────┤
│  Claude Tasks (Runtime)                                     │
│  ═══════════════════════                                    │
│  • Session-übergreifender State                             │
│  • Subagent-Owner (Multi-Agent)                             │
│  • Native Dependency Blocking (blockedBy)                   │
│  • Spinner Feedback (activeForm)                            │
└─────────────────────────────────────────────────────────────┘
```

### Synchronisation

**Session-Start (/stan create):**
```
.stan/tasks.jsonl → Claude Tasks
- Für jeden pending/in_progress Task: TaskCreate
- dependencies → blockedBy
- owner aus JSONL übernehmen
```

**Runtime (Task-Abschluss):**
```
Claude Tasks → .stan/tasks.jsonl → docs/tasks.md
- TaskUpdate (completed) → JSONL aktualisieren
- Markdown regenerieren
- Git-tracked bleibt aktuell
```

**Session-Ende (/stan complete):**
```
1. Alle Tasks done?
2. Alle Criteria erfüllt?
3. Tests grün?
4. docs/*.md → .stan/completed/
5. Git commit + push (Land the Plane)
```

### JSONL Task Schema

```json
{
  "id": "t-a1b2",
  "subject": "Task title",
  "description": "Detailed description",
  "status": "pending|in_progress|done|blocked",
  "phase": "define|plan|create",
  "dependencies": ["t-xxxx"],
  "acceptance_criteria": ["AC1", "AC2"],
  "owner": null,
  "created_at": "2026-01-24T10:00:00Z",
  "updated_at": "2026-01-24T10:00:00Z"
}
```

### Vorteile vs. Markdown-Only

| Aspekt | Markdown (alt) | JSONL (neu) |
|--------|----------------|-------------|
| **Merge-Konflikte** | Häufig in Worktrees | Selten (1 Zeile = 1 Task) |
| **ID-Kollisionen** | T-001 kollidiert | Hash-IDs (t-a1b2) |
| **Parsing** | Regex/Markdown-Parser | JSON.parse() |
| **Multi-Agent** | Manuelle Orchestration | owner-Feld nativ |
| **Human-readable** | Direkt editierbar | Generiert (read-only) |

### Neue Skills

| Skill | Funktion |
|-------|----------|
| `/stan ready` | Zeigt Tasks ohne offene Blocker |
| `/stan complete` | Land the Plane: Checks + Archiv + Push |

### Implementation

Phase 18 Tasks:
- T-047: JSONL Schema + Validator
- T-048: .stan/ Directory Structure
- T-049: Markdown Generator (JSONL → docs/tasks.md)
- T-050: Sync Layer Session Start (JSONL → Claude Tasks)
- T-051: Sync Layer Runtime (Claude Tasks → JSONL)
- T-052: /stan ready Skill
- T-053: /stan complete Skill (Land the Plane)
- T-054: /stan plan + /stan create Integration
- T-055: E2E Integration Test

---

## Max Iterations

**Prinzip:** Kosten-Kontrolle ohne Micromanagement.

### Default: 10 Iterationen

Wie Ralph. Ein Task darf max 10 Mal versucht werden bevor STOP.

### Konfigurierbar in stan.md

```yaml
# stan.md
---
phase: create
max_iterations: 15  # Optional, Default: 10
---
```

### Was zählt als Iteration?

Ein Versuch, die Acceptance Criteria zu erfüllen:
1. Code ändern
2. Tests laufen lassen
3. Wenn fehlgeschlagen → Iteration +1

### Bei Überschreitung

```
[STAN] Task T-003 nach 10 Iterationen nicht erfolgreich.
       → Perspective Shift erforderlich
       → Oder: Reconciliation (Requirements überdenken)
```

---

## Model Auto-Selection für Subagenten

**Prinzip:** Intelligente Modellwahl für Subagenten basierend auf Task-Komplexität.

### Task-Property: model

```yaml
# docs/tasks.md
- id: T-003
  name: "Theme Toggle Component"
  complexity: 2
  model: auto  # auto | haiku | sonnet | opus
```

### Auto-Selection Logik

| Komplexität | Modell | Begründung |
|-------------|--------|------------|
| 0-2 | sonnet | Ausreichend für Standard-Tasks |
| 3-4 | opus | Komplexe Tasks brauchen mehr Reasoning |

**Wichtig:** `haiku` wird NIE automatisch gewählt - nur bei explizitem Override.

### Manuelle Override

```yaml
model: haiku   # Explizit für sehr einfache Tasks
model: sonnet  # Explizit für mittlere Tasks
model: opus    # Explizit für komplexe Tasks
```

### Model-Escalation bei Fehlschlägen

```
haiku (explicit) → fehlgeschlagen nach N Versuchen
    ↓
sonnet (auto-escalate)
    ↓
opus (auto-escalate)
    ↓
STOP → Human Intervention
```

**Regeln:**
- Escalation nur bei explizitem haiku-Start
- Bei `auto` oder `sonnet` Start: Kein Downgrade, nur Escalation zu opus
- Bei opus-Fehlschlag: STOP (kein besseres Modell verfügbar)
- Escalation zählt als neue Iteration
- Notification an User bei Escalation

### Begründung

| Aspekt | Entscheidung | Warum |
|--------|--------------|-------|
| Default | sonnet | Balance zwischen Qualität und Kosten |
| Auto-Logic | Komplexitätsbasiert | Objektives Kriterium existiert bereits |
| Haiku | Opt-in only | Vermeidet unnötige Escalations |
| Escalation | Automatisch | Verhindert unnötige Fehlschläge bei "zu schwachem" Modell |

---

## Hybrid-Architektur: Skills + Commands

### Terminologie (Claude Code)

| Konzept | Verzeichnis | Struktur | Aktivierung |
|---------|-------------|----------|-------------|
| **Commands** | `.claude/commands/` | `name.md` | Explizit via `/name` |
| **Skills** | `.claude/skills/` | `skill-name/SKILL.md` | Automatisch via Trigger-Phrases |

### Das Problem

Aktuell hat STAN nur **Commands** (`.claude/commands/stan/*.md`).
- User muss `/stan define`, `/stan plan`, `/stan create` explizit aufrufen
- Kein fließender Workflow
- Keine automatische Erkennung der Situation

### Die Lösung: Hybrid-Ansatz

**Beide Systeme parallel:**

```
.claude/
├── skills/
│   └── stan/
│       ├── SKILL.md              # Automatisch: Phasen + Think erkennen
│       └── references/
│           ├── phase-define.md   # Detail-Instruktionen
│           ├── phase-plan.md
│           ├── phase-create.md
│           └── techniques.md     # Think-Logik
│
└── commands/
    └── stan/
        ├── init.md               # Explizit: /stan init
        ├── define.md             # Explizit: /stan define
        ├── plan.md               # Explizit: /stan plan
        ├── create.md             # Explizit: /stan create
        ├── think.md              # Explizit: /stan think
        └── ...
```

### Warum Hybrid?

| Aspekt | Skill | Command |
|--------|-------|---------|
| **Aktivierung** | Automatisch (Phrases) | Explizit (`/stan`) |
| **Entdeckbarkeit** | Unsichtbar | Sichtbar (Tab-Completion) |
| **Kontrolle** | Situationsabhängig | User entscheidet |
| **Neue User** | Verwirrend | Klar |
| **Erfahrene User** | Fließend | Umständlich |

**Fazit:** Beide Systeme ergänzen sich.

### Skill Trigger-Phrases (Entwurf)

```yaml
# .claude/skills/stan/SKILL.md
---
name: STAN Workflow
description: This skill should be used when the user asks to
  "build a feature", "implement something", "start a project",
  "create PRD", "plan tasks", "I'm stuck", "why is this happening",
  "what options do I have", "let's think about this",
  "was ist der Status", "neues Feature"...
---
```

### Workflow mit Hybrid

```
User: "Ich will Feature X bauen"
                │
    ┌───────────┴───────────┐
    ▼                       ▼
  Skill                  Command
(automatisch)           (explizit)
    │                       │
    ▼                       ▼
Erkennt: Kein stan.md   User: /stan init
→ Startet DEFINE        → Startet DEFINE
    │                       │
    └───────────┬───────────┘
                ▼
         Gleiche Logik
      (references/*.md)
```

### Redundanz vermeiden

Commands sollten **nicht** die volle Logik duplizieren. Stattdessen:
- Skill enthält Hauptlogik in `references/`
- Commands sind minimalistisch und verweisen auf Skill-Logik
- Oder: Commands bleiben als sie sind, Skill lädt sie bei Bedarf

---

## Erfolgskriterien

### Technische Kriterien

| Bereich | Erfolgskriterium |
|---------|------------------|
| **Hooks** | Alle 3 triggern korrekt, Blocking funktioniert |
| **Skills** | Jeder Skill macht was er soll |
| **Templates** | Interaktiv bauen + Criteria verknüpfen funktioniert |
| **Criteria** | Werden zu Checklisten, Gate blockiert wenn incomplete |
| **Phasen** | DEFINE → PLAN → CREATE Wechsel funktioniert |
| **Learnings** | ROT→GRÜN erkennen, lokal speichern, Commit-Block |
| **E2E** | Ein echtes Mini-Feature komplett durchführen |

### Qualitative Kriterien (Arbeitsweise)

| Kriterium | Beschreibung |
|-----------|--------------|
| **Selbstdisziplin** | Ich halte mich an meine eigenen Vorgaben |
| **Struktur** | Nicht verzetteln, nicht chaotisch werden |
| **Selbstkritik** | Reflektieren, nicht blind durchballern |
| **Innehalten** | Bei Unsicherheit STOP, nicht ignorieren |
| **Recherche** | Lieber mehr recherchieren als zu wenig |
| **Best Practices** | Frameworks (BMAD, Ralph, PRP) aktiv nutzen |
| **Team-Arbeit** | User = Product Manager, ich = ausführend mit Eigenverantwortung |
| **Offenheit** | Unsicherheit ≠ Hindernis, sondern Anlass für Klärung |

### E2E-Test: Bootstrap

**STAN mit STAN bauen:**

```
1. /stan init → Projekt starten
2. DEFINE → PRD für STAN selbst (aus diesem Plan)
3. PLAN → Tasks ableiten
4. CREATE → Hooks, Skills, Templates, Criteria implementieren
```

**Warum Bootstrap:**
- Meta-Test: Wenn ich mich nicht an STAN halte während ich STAN baue, ist es wertlos
- Zeigt Selbstdisziplin in der Praxis
- Alle Phasen werden durchlaufen
- Vendor-Frameworks als Referenz nutzen

---

## Entscheidungs-Log

| Entscheidung | Begründung |
|--------------|------------|
| 3 Hooks (nicht 2 oder 4) | Balance zwischen Enforcement und Komplexität |
| Two-Layer State | Session (flüchtig) vs. Manifest (persistent) trennen |
| Markdown für Manifest | Lesbar für Menschen, Git-tracked |
| Graphiti optional | Framework muss ohne funktionieren |
| DEFINE inkludiert Discovery | Keine separate Phase nötig |
| CREATE statt BUILD | Professionellere Sprache |
| Zwei-System Learnings | Lokal (Arbeitsgedächtnis) + Graphiti (Langzeit, kuratiert) |
| Lokal Tiered Storage | Inspiriert von Protocol Harness (recent/hot/archive) |
| Graphiti nur am Ende | Kein Overhead während autonomer Arbeit, kuratierte Qualität |
| Bestehende taming-stan Hooks | Kein Widerspruch - Graphiti Query läuft via existierende Hooks |
| 1 YAML = 1 Criteria | Atomar, kombinierbar, wiederverwendbar |
| Criteria im Template-Frontmatter | Verknüpfung am Ende des Template-Makers, nicht statisch |
| Dynamischer Document Scan | Keine manuelle Registry, Frontmatter = Source of Truth |
| Reconciliation manuell | User/Claude entscheiden bewusst, kein automatischer Trigger |
| Parallelisierung nur nach PLAN | Dependencies + Datei-Berührungen müssen bekannt sein |
| Hauptagent orchestriert | Keine automatische Parallelisierung, bewusste Entscheidung |
| `/stan` Namespace | STAN.FLUX umbenannt zu `/stanflux:*`, `/stan` für Workflow-Framework |
| 9 Zwecke für Denktechniken | Konsolidierung aus BMAD/PRP: Root Cause + Debugging = Ursachenanalyse, Naturinspiration + Kreativ + Unkonventionell = Ideenfindung. Big Picture statt Architektur-Analyse (allgemeiner). |
| n:m Technik-Zweck-Beziehung | Eine Technik kann mehreren Zwecken dienen (Six Thinking Hats → Perspektivwechsel + Entscheidung) |
| Transparenz bei Techniken | Nie Technik überstülpen, immer zeigen + empfehlen + User wählt |
| 5-Stufen Dokument-Status | draft → approved → in-progress → done → archived. Kein Review-Status (haben Gates dafür). |
| Kontext-basierte Archivierung | Keine Zeit-basierte Archivierung (BMAD 24h nervt). Dokumente veralten durch Kontext, nicht Zeit. |
| Frontmatter als Source of Truth | Status im Frontmatter, optional zusätzlich nach docs/archive/ verschieben |
| Feature-Name statt Datum | Archiv-Dateien heißen `prd-dark-mode.md` NICHT `prd-2026-01-24.md`. Datum steckt im Frontmatter. |
| Archivierung explizit | Archivierung NUR wenn User explizit "fertig" sagt. NICHT automatisch nach CREATE. User entscheidet. |
| Max Iterations = 10 | Default 10 Iterationen pro Task (wie Ralph). Optional in stan.md überschreibbar via `max_iterations: 15`. |
| Hybrid Commands + Skills | Commands bleiben für explizite Aufrufe (`/stan init`). Skills zusätzlich für automatische Erkennung. Keine Redundanz: Skills verweisen auf Command-Logik. |
| Complexity Lifecycle | Assessment transparent zeigen → User Override erlauben → Re-Assessment bei Änderung → Escalation bei großem Sprung (Level 1→4 = Reconciliation). |
| Claude Tasks Hybrid (SUPERSEDED) | ~~Claude Tasks als Runtime-Layer, docs/tasks.md als Source of Truth~~ → Ersetzt durch JSONL Task System (2026-01-24). |
| JSONL Task System | .stan/tasks.jsonl als Source of Truth, docs/tasks.md wird generiert (read-only), Claude Tasks als Runtime. Hash-IDs für Kollisionsfreiheit in Worktrees. Inspiriert von beads. |
| Activity Log: NICHT umsetzen | Bewusste Entscheidung gegen Activity Log (Ralph-Style). Redundant zu Claude Tasks und docs/tasks.md. Mehr Overhead als Value. |
| Multi-Agent Auto-Orchestration: Zukunft | Automatische Parallelisierung/Orchestration als "Future Optional". Basics (Subagents + Worktrees) existieren bereits. Vollautomatische Orchestration = Over-Engineering. |
| Model Auto-Selection | `model: auto` als Default. Auto-Logik: complexity < 3 → sonnet, complexity ≥ 3 → opus. Haiku nur bei explizitem Override. |
| Model Escalation | Bei Fehlschlägen: haiku → sonnet → opus → STOP. Nur bei explizitem haiku-Start. Verhindert unnötige Fehlschläge bei "zu schwachem" Modell. |
| Persistent Session State | Session State in `.stan/session.json` statt `/tmp/`. Überlebt Session-Wechsel, Git-tracked (optional). |
| Task Priority Default | All pending (·) tasks are REQUIRED by default. Only parked (~) or archived (§) are optional. Prevents Claude from labeling required tasks as "optional" or "enhancement". |

---

## Evaluator-Subagent Architektur (VALIDIERT)

> **Status:** ✅ Getestet und validiert
> **Datum:** 2026-01-25
> **Problem:** LLMs sind bei Selbst-Evaluation nicht ehrlich genug

### Das Problem

Claude neigt dazu, eigene Arbeit zu oberflächlich zu evaluieren:
- Checkboxen werden abgehakt ohne echte Prüfung
- "Sieht gut aus" statt rigoroser Analyse
- Bias zur eigenen Arbeit (Self-Serving Bias)

### Getestete Ansätze

| Ansatz | Ergebnis | Problem |
|--------|----------|---------|
| Prompt-Hook (type: prompt) | ⚠️ Funktioniert generisch | Kann keine Dateien lesen, $TRANSCRIPT_PATH ist nur String |
| Command-Hook + API | ❌ Braucht API-Token | User hat nur Subscription |
| **Command-Hook + Subagent** | ✅ **ERFOLG** | Kein API-Token nötig, unabhängige Evaluation |

### Lösung: Command-Hook + Subagent via Task Tool

**Schlüsselerkenntnis:** Hooks können keine Subagenten spawnen, aber sie können den Hauptagent triggern einen zu spawnen!

```
┌─────────────────────────────────────────────────────────┐
│                    Hauptagent                            │
│  (Arbeitet: editiert Dateien, checkt Checkboxen ab)     │
└──────────────────────────┬──────────────────────────────┘
                           │ Edit tool call
                           ▼
┌─────────────────────────────────────────────────────────┐
│           PostToolUse Hook (type: command)               │
│  stan-evaluate.py                                        │
│                                                          │
│  1. Liest aktuellen Task aus .stan/tasks.jsonl          │
│  2. Parst acceptance_criteria für {criteria-name}       │
│  3. Unterscheidet Acceptance vs Success Criteria        │
│  4. Wählt Model basierend auf Criteria-Typ              │
│                                                          │
│  Output: {continue: true, systemMessage:                │
│    "Spawne Evaluator: Task(model='sonnet', ...)"}       │
└──────────────────────────┬──────────────────────────────┘
                           │ systemMessage → Hauptagent
                           ▼
┌─────────────────────────────────────────────────────────┐
│              Hauptagent spawnt Subagent                  │
│  Task(subagent_type="Explore", model="{model}",         │
│       prompt="Evaluiere Edit gegen Criteria...")        │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│           Evaluator-Subagent (Haiku/Sonnet)              │
│  - Separater Kontext (nicht "committed" zum Edit)       │
│  - Skeptischer Prompt                                   │
│  - Gibt PASS / FAIL / WARN zurück                       │
└─────────────────────────────────────────────────────────┘
```

**Warum Subagent statt Prompt-Hook:**
- Prompt-Hooks können keine Dateien lesen ($TRANSCRIPT_PATH ist nur String-Pfad)
- Command-Hooks können Dateien lesen, aber brauchen eigene LLM-Logik
- Subagent via Task Tool: Kein API-Token, separater Kontext, unabhängig

**Test-Ergebnis (2026-01-25):**
Subagent (Haiku) erkannte korrekt als FAIL wenn Checkbox abgehakt wurde ohne echte Erfüllung:
> "This appears to be exactly the kind of self-serving bias the evaluation task is designed to catch"

### Model Selection: Acceptance vs Success Criteria

**Zwei Typen von Criteria in Tasks:**

| Typ | Syntax | Quelle | Evaluator Model |
|-----|--------|--------|-----------------|
| **Acceptance Criteria** | `{criteria-name}` | YAML-Datei | Aus YAML (`evaluator_model`) |
| **Success Criteria** | Freier Text | Task-Definition | Immer Sonnet (semantisch) |

**Beispiel Task in `.stan/tasks.jsonl`:**
```json
{
  "id": "t-abc1",
  "subject": "Login-Formular implementieren",
  "acceptance_criteria": [
    "Tests bestehen {code-quality}",      // → Acceptance: YAML laden → haiku
    "Lint ohne Fehler {code-quality}",    // → Acceptance: YAML laden → haiku
    "User findet UI intuitiv"             // → Success: freier Text → sonnet
  ]
}
```

**Model Selection Logic:**
```python
if has_success_criteria:  # Freier Text ohne {...}
    model = "sonnet"  # Semantische Evaluation nötig
elif all_acceptance_criteria_use_haiku:
    model = "haiku"   # Nur Code-Checks
else:
    model = "sonnet"  # Gemischt oder enthält Sonnet
```

**YAML Criteria Packs:**
```yaml
# criteria/code-quality.yaml
name: Code Quality
evaluator_model: haiku  # Fast model for rule-based checks
checks:
  - id: tests-pass
    question: "Do all tests pass?"
  - id: lint-pass
    question: "Does code pass linting?"

# criteria/text-quality.yaml
name: Text Quality
evaluator_model: sonnet  # Semantic understanding required
checks:
  - id: clarity
    question: "Is the text clear and understandable?"
```

**Workflow:**
1. Hook liest aktuellen `in_progress` Task aus `.stan/tasks.jsonl`
2. Für jedes `acceptance_criteria`:
   - Hat `{criteria-name}` → YAML laden → Model aus YAML
   - Kein `{...}` → Success Criteria → Sonnet
3. Primary Model = Sonnet wenn Success Criteria vorhanden, sonst aus YAMLs
4. Hook gibt systemMessage mit richtigem Modell:
   `Task(model="{primary_model}", ...)`

### Dateistruktur (analog taming-stan)

```
scripts/
├── lib/
│   └── session_state.py       # Cross-hook state management
└── prompts/
    ├── criteria-eval.md       # Evaluator-Prompt für Criteria-Check
    ├── learning-detection.md  # Prompt für Learning-Erkennung
    └── guess-detection.md     # Prompt für Guess-Erkennung

experiments/
└── evaluator-hook-test/       # Evaluator-Subagent Experiment
    ├── stan-evaluate.py       # Evaluator Hook (EXPERIMENTAL)
    ├── FINDINGS.md            # Test-Ergebnisse
    └── README.md              # Experiment-Dokumentation

hooks/
└── hooks.json                 # Konsolidierte Hook-Config mit ${CLAUDE_PLUGIN_ROOT}
```

**Prompt-Template Pattern:**
```markdown
# prompts/criteria-eval.md

Du bist der STAN Evaluator - unabhängiger Qualitätsprüfer.

## Zu prüfendes Edit
{edit_info}

## Acceptance Criteria
{criteria}

## Deine Aufgabe
1. Ist das Kriterium WIRKLICH erfüllt?
2. Sei skeptisch - der Hauptagent hat Self-Serving Bias
3. Gib PASS / FAIL / WARN zurück
```

### Hook Output Formate (VERIFIZIERT)

| Hook Event | Output Format | Blocking |
|------------|---------------|----------|
| PostToolUse | `{continue, systemMessage}` | `continue: false` |
| Stop | `{decision, reason, systemMessage}` | `decision: "block"` |
| PreToolUse | `{hookSpecificOutput, systemMessage}` | `permissionDecision: "deny"` |

### Konfigurationsformat (WICHTIG!)

**`.claude/settings.json`** - KEIN wrapper:
```json
{
  "PostToolUse": [...],
  "Stop": [...]
}
```

**`hooks/hooks.json`** (Plugin) - MIT wrapper:
```json
{
  "description": "...",
  "hooks": {
    "PostToolUse": [...],
    "Stop": [...]
  }
}
```

### Evaluator pro Phase

| Phase | Unit | Hook-Trigger | Evaluator prüft |
|-------|------|--------------|-----------------|
| DEFINE | PRD, Style Guide | PostToolUse(Edit) | Dokument-Qualität |
| PLAN | Plan.md | PostToolUse(Edit) | Task-Struktur, Dependencies |
| CREATE | Task | PostToolUse(Edit) + Stop | Code + Tests + AC erfüllt |

### Offene Fragen (BEANTWORTET)

1. **Feedback-Loop:** ✅ `systemMessage` wird ins Transcript geschrieben
2. **Checkbox-Manipulation:** ✅ Evaluator kann nicht editieren, aber Stop kann blockieren
3. **Context-Sharing:** ✅ `$TRANSCRIPT_PATH` gibt Zugriff auf vollständige History
4. **Infinite Loop Prevention:** ⚠️ Noch zu definieren (max_iterations?)

### Experiment-Status

| Experiment | Status | Ergebnis |
|------------|--------|----------|
| PostToolUse Prompt Hook | ✅ VALIDIERT | Funktioniert! Hook erkennt oberflächlich abgehakte Checkboxen |
| Stop Hook Blocking | ✅ Recherche | Unterstützt, `decision: "block"` verhindert Completion |
| systemMessage Feedback | ✅ VALIDIERT | Wird an Hauptagent weitergeleitet, erscheint im Transcript |

**VALIDIERT am 2026-01-24:** PostToolUse Prompt Hook in `.claude/settings.json` konfiguriert und getestet.

### Akzeptanzkriterien

- [x] Feedback-Mechanismus recherchiert → `systemMessage`
- [x] Architektur dokumentiert
- [x] **VALIDIERT:** PostToolUse Prompt Hook getestet - erkennt falsch abgehakte Checkboxen
- [x] **VALIDIERT:** Command-Hook + Subagent getestet (2026-01-25)
- [x] **VALIDIERT:** Subagent erkennt Self-Serving Bias korrekt
- [x] **VALIDIERT:** Feedback-Loop in Praxis verifiziert - systemMessage erscheint im Transcript
- [x] Kein API-Token nötig - nutzt Claude Code Subscription
- [ ] In Plugin-Struktur integrieren (scripts/prompts/*.md)
- [ ] hooks.json mit ${CLAUDE_PLUGIN_ROOT} erstellen

### STAN Integration (Vorgeschlagen)

```json
{
  "PostToolUse": [
    {
      "matcher": "Edit",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "STAN EVALUATOR: Check if acceptance criteria are genuinely met..."
        }
      ]
    }
  ],
  "Stop": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "STAN GATE: Review $TRANSCRIPT_PATH. Block if criteria incomplete..."
        }
      ]
    }
  ]
}
```

**Vorteil:** Ersetzt/ergänzt Python-basierte Hooks (stan-gate.py) mit LLM-basierter Evaluation.

---

## Reflexion: Hybrid Hook-Architektur (2026-01-24)

> **Erkenntnis:** Python-Hooks und Prompt-Hooks haben unterschiedliche Stärken.
> Optimale Nutzung = Kombination beider Typen.

### Was wir haben (aktueller Stand)

**3 Python-Hooks (command-basiert):**
| Hook | Event | Funktion |
|------|-------|----------|
| `stan_context.py` | UserPromptSubmit | Kontext injizieren, Learnings laden |
| `stan_track.py` | PostToolUse (Bash) | Test-Ergebnisse tracken, ROT→GRÜN erkennen |
| `stan_gate.py` | PreToolUse | Phase-Enforcement, Quality Gates, Commit-Blocking |

**11 Commands/Skills:**
`/stan init`, `/stan define`, `/stan plan`, `/stan create`, `/stan statusupdate`,
`/stan healthcheck`, `/stan think`, `/stan build-template`, `/stan build-criteria`,
`/stan ready`, `/stan complete`

**Workflow:**
```
DEFINE (interaktiv) → PLAN (interaktiv) → CREATE (autonom)
        ↑                                      │
        └──────── Reconciliation ◄─────────────┘
```

### Was wir heute gelernt haben

**Prompt-Hooks (type: prompt):**
- LLM-basierte Evaluation OHNE Tool-Zugriff
- Können semantische Qualität prüfen ("Ist das wirklich erfüllt?")
- Output: `{continue, systemMessage}` (PostToolUse), `{decision, reason}` (Stop)
- Variablen: `$TOOL_INPUT.*`, `$TRANSCRIPT_PATH`
- Erbt Session-Modell (kein separates `model`-Feld)

**Limitationen:**
- Prompt-Hooks können KEINE MCP-Aufrufe machen
- Prompt-Hooks können KEINE Dateien lesen (außer via $TRANSCRIPT_PATH)
- Prompt-Hooks sind reine Text-Evaluation

**Zwei Konfigurationsorte:**
| Ort | Zweck | Format |
|-----|-------|--------|
| `.claude/settings.json` | Lokale Entwicklung/Tests | Kein wrapper, absolute Pfade |
| `hooks/hooks.json` | Plugin-Distribution | Mit `"hooks"` wrapper, `${CLAUDE_PLUGIN_ROOT}` |

### Optimale Hybrid-Architektur

**Python-Hooks (command) für:**
- State Management (Session, Learnings)
- Datei-Parsing (Manifest, Tasks, Criteria)
- Komplexe Logik (Dependencies, Phase-Transitions)
- MCP-Integration (falls nötig via Shell)

**Prompt-Hooks für:**
- Semantische Evaluation ("Ist das Ziel wirklich konkret?")
- Acceptance Criteria Verification ("Ist das wirklich erfüllt?")
- Oberflächlich abgehakte Checkboxen erkennen
- Qualitative Prüfungen die Verständnis erfordern

### Neuer Hook-Aufbau (STAN v2)

```
┌─────────────────────────────────────────────────────────────┐
│  STAN Hook-System (Hybrid)                                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  UserPromptSubmit                                            │
│  └─ stan_context.py (command)                               │
│     → Kontext injizieren, Learnings laden, Phase anzeigen   │
│                                                              │
│  PreToolUse                                                  │
│  └─ stan_gate.py (command)                                  │
│     → Phase-Enforcement, Commit-Blocking, 3-Strikes         │
│                                                              │
│  PostToolUse (Bash)                                          │
│  └─ stan_track.py (command)                                 │
│     → Test-Tracking, ROT→GRÜN Detection, Learning-Trigger   │
│                                                              │
│  PostToolUse (Edit) ← NEU                                    │
│  └─ STAN Evaluator (prompt)                                 │
│     → Acceptance Criteria Verification                       │
│     → Oberflächliche Checkbox-Erkennung                      │
│     → Qualitative Dokumenten-Prüfung                         │
│                                                              │
│  Stop ← NEU                                                  │
│  └─ STAN Final Check (prompt)                               │
│     → Alle Criteria erfüllt?                                 │
│     → Keine offenen TODOs?                                   │
│     → Kann blockieren mit spezifischem Feedback              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Workflow mit Evaluator-Hooks

```
User: "/stan create"
        │
        ▼
┌───────────────────────────────────────┐
│ stan_context.py (UserPromptSubmit)    │
│ → Zeigt Phase, Task, injiziert Kontext│
└───────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────┐
│ Claude arbeitet (Edit, Bash, etc.)    │
│                                       │
│ Bei JEDEM Edit:                       │
│   ↓                                   │
│   PostToolUse(Edit) → Prompt-Hook     │
│   "Ist diese Änderung wirklich        │
│    vollständig und korrekt?"          │
│   → systemMessage mit Feedback        │
│                                       │
│ Bei Test-Commands:                    │
│   ↓                                   │
│   stan_track.py → ROT→GRÜN erkennen   │
│   → Learning-Reminder wenn nötig      │
└───────────────────────────────────────┘
        │
        ▼ (Claude will stoppen)
┌───────────────────────────────────────┐
│ Stop Hook → Prompt-Hook               │
│ "Prüfe $TRANSCRIPT_PATH:              │
│  - Alle Acceptance Criteria erfüllt?  │
│  - Keine offenen TODOs?               │
│  - Tests grün?"                       │
│                                       │
│ → approve: Task abgeschlossen         │
│ → block: Spezifisches Feedback        │
└───────────────────────────────────────┘
```

### Implementierungs-Schritte

**Phase 19: Evaluator-Hook Integration**

| Task | Beschreibung | Status |
|------|--------------|--------|
| E-001 | Prompt-Hook für PostToolUse(Edit) in hooks/hooks.json | · |
| E-002 | Prompt-Hook für Stop in hooks/hooks.json | · |
| E-003 | Prompt-Formulierung für STAN-spezifische Evaluation | · |
| E-004 | Integration mit Criteria-System (Criteria im Prompt referenzieren) | · |
| E-005 | Test in echtem Projekt (außerhalb autonomous-stan) | · |
| E-006 | Dokumentation aktualisieren | · |

### Prompt-Entwürfe (KORRIGIERT 2026-01-24)

> **WICHTIG:** Prompt-Hooks dürfen NIEMALS JSON-Output anfordern!
> Das System handled die Formatierung automatisch. Nur Analyse-Anweisungen geben.

**PostToolUse(Edit) Evaluator:**
```
You are the STAN EVALUATOR - independent quality checker.

The main agent just edited: $TOOL_INPUT.file_path
Change: "$TOOL_INPUT.old_string" → "$TOOL_INPUT.new_string"

Analyze critically:
1. If a checkbox was marked complete: Is the criterion ACTUALLY met? Look for real evidence in the file.
2. If code was written: Is it complete? Any TODOs, placeholder comments, missing imports, unfinished logic?
3. If acceptance criteria were checked: Does the actual implementation match?

Be skeptical. The main agent has self-serving bias and tends to check boxes prematurely.

If you find issues, state them specifically. If the edit is legitimate, confirm briefly.
```

**Stop Final Check:**
```
You are the STAN GATE - final quality barrier before task completion.

Review the transcript for this task.

Before allowing completion, verify:
1. ALL acceptance criteria are genuinely met (not just checked off)
2. No TODO comments or incomplete implementations remain
3. If tests were required, they must have passed
4. Document quality matches the stated requirements

If everything is genuinely complete, confirm approval.
If issues remain, list them specifically so the agent can address them.
```

### Offene Fragen

1. **Infinite Loop Prevention:** Was wenn Evaluator immer "needs_work" sagt?
   → Lösung: max_evaluator_iterations in stan.md (Default: 3)

2. **Performance:** Prompt-Hooks brauchen LLM-Aufruf (+ Latenz)
   → Lösung: Nur für Edit aktivieren, nicht für jedes Tool

3. **Criteria-Referenz:** Wie kommt der Prompt an die aktuellen Criteria?
   → Lösung: Python-Hook (stan_context) injiziert Criteria in Session-Context,
     Prompt-Hook sieht das via $TRANSCRIPT_PATH

### Nächste Schritte (priorisiert)

1. **JETZT:** Evaluator-Hooks in `hooks/hooks.json` für Plugin-Distribution vorbereiten
2. **DANN:** Test in separatem Projekt mit installiertem Plugin
3. **DANACH:** Feintuning der Prompts basierend auf Praxis-Erfahrung

---

## Referenz-Material

- `vendor/ralph/CLAUDE.md` - Progress-Tracking, Codebase Patterns
- `vendor/ralph/skills/ralph/SKILL.md` - Task-Sizing, Acceptance Criteria
- `vendor/beads/docs/ARCHITECTURE.md` - JSONL + SQLite drei-schichtige Architektur
- `vendor/beads/docs/MOLECULES.md` - Workflow-Patterns (Land the Plane, Wisps)
- `vendor/beads/AGENTS.md` - Agent Instructions (mandatory push)
- `.claude/rules/taming-stan/stanflux.md` - STAN.FLUX Verhaltensregeln
- Context7: `/anthropics/claude-code` - Hook-Dokumentation

---

### Phase 21: Smart Project Discovery & Architecture Consistency

**Motivation:** Factory/Eno Reyes zeigt: Skills die Source-of-Truth Docs einbinden produzieren drastisch bessere Ergebnisse. Aber statt manuell Notion-Docs zu kuratieren, soll autonomous-stan die Architektur-Patterns eines Projekts **selbst entdecken**.

**Kernidee:** `/stan init` wird intelligent. Es scannt das Projekt, erkennt Stack, Patterns, Konventionen und legt das als Context ab. Criteria und Techniques nutzen diesen Context automatisch.

| Task | Beschreibung | Status |
|------|--------------|--------|
| D-001 | **Project Discovery in `/stan init`**: Stack-Erkennung (package.json, Cargo.toml, pyproject.toml, etc.), Framework-Detection (Astro, Next, Django, etc.), Architektur-Patterns scannen (3-5 repräsentative Dateien analysieren), Ergebnis in `.stan/context/project-patterns.md` ablegen | · |
| D-002 | **Architecture Consistency Criterion**: Neues Criterion `architecture-consistency.yaml` — prüft ob Änderungen den entdeckten Patterns folgen. Checks: Dateistruktur, Import-Konventionen, Styling-Approach, Error-Handling-Pattern, Test-Patterns. Abweichung = nur mit dokumentiertem Grund erlaubt | · |
| D-003 | **Brownfield als Default**: Technique `brownfield-reality-check` wird automatisch bei `/stan create` getriggert. Vor jeder neuen Datei: 3 ähnliche bestehende Dateien lesen. Vor jedem neuen Pattern: prüfen ob es schon eins gibt | · |
| D-004 | **Iterative Spec-Validation**: Evaluator-Hook prüft Edits nicht nur gegen Code-Qualität, sondern auch gegen die aktuelle Spec (`.stan/prd.md`). Spec-Änderungen triggern Plan-Review. Spec ist lebendig, nicht eingefroren | · |
| D-005 | **Context Injection erweitern**: `stan_context.py` injiziert `.stan/context/project-patterns.md` in den System-Context bei jedem UserPrompt. Nicht den ganzen File — nur die relevanten Sections basierend auf dem aktuellen Task | · |
| D-006 | **Auto-Discovery bei bestehendem Projekt**: `/stan init` in einem Projekt das schon Code hat → analysiert bestehende Patterns statt Defaults anzunehmen. Erkennt: Component-Struktur, Routing-Pattern, State-Management, CSS-Approach, Test-Framework + Patterns | · |
| D-007 | **Living Architecture Doc**: `.stan/context/project-patterns.md` wird nach jedem `/stan complete` aktualisiert wenn sich Patterns geändert haben (z.B. neues Pattern eingeführt, Migration auf anderes Framework) | · |

**Architektur:**
```
/stan init (enhanced)
  ├── Stack Detection (package.json, config files)
  ├── Pattern Analysis (3-5 representative files)
  ├── Convention Extraction (naming, structure, imports)
  └── .stan/context/project-patterns.md (generated)

/stan create (enhanced)
  ├── Brownfield Check (automatic, before any new file)
  ├── Pattern Compliance (architecture-consistency criterion)
  ├── Spec Validation (evaluator checks against prd.md)
  └── Pattern Update (on /stan complete if patterns evolved)
```

**Inspiriert von:**
- Factory/Eno Reyes: Source-of-Truth Docs in Skills → dramatisch bessere Outputs
- Superpowers: Brownfield Reality Check Technique
- GSD: Context Rot Prevention (patterns.md = Anti-Context-Rot)
- Eigene Erfahrung: CSS-Basics-Krise (14.02.) — Agent kannte Projektkonventionen nicht

---

### Phase 20: Agent Teams Integration (Future)

**Voraussetzung:** CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS stable
**Abhängig von:** Phase 19 (Evaluator-Hooks) abgeschlossen

| Task | Beschreibung | Status |
|------|--------------|--------|
| T-001 | `/stan create --team` Modus: Lead + N Teammates | · |
| T-002 | Evaluator als eigener Teammate (statt Prompt-Hook) | · |
| T-003 | Researcher-Teammate für Codebase-Analyse vor Implementation | · |
| T-004 | Parallel-Debugging: N Hypothesen gleichzeitig testen | · |
| T-005 | Plan-Approval Integration mit Criteria-System | · |
| T-006 | Fallback: Ohne Teams graceful auf Single-Agent + Hooks | · |

**Architektur-Idee:**
```
/stan create --team
  ├── Lead (Delegate Mode): Koordiniert, prüft Criteria
  ├── Implementer: Baut Feature (eigener Context)
  ├── Evaluator: Prüft gegen Criteria (eigener Context, kein Self-Serving Bias)
  └── Researcher: Analysiert Codebase-Patterns vor Implementation
```

**Warum erst Phase 20:**
- Feature ist experimental (ENV Flag)
- Plugin muss OHNE Teams funktionieren (Hooks als Fallback)
- Token-Kosten: Jeder Teammate = separate Claude-Instanz
- Erst Praxis-Test (Phase 19, E-005) zeigt ob Hooks allein reichen

