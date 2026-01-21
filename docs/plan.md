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

## Dateistruktur (Ziel: ~25 Dateien)

```
autonomous-stan/
├── .claude/
│   ├── hooks/
│   │   ├── stan-context.py     # UserPromptSubmit
│   │   ├── stan-track.py       # PostToolUse (Bash)
│   │   └── stan-gate.py        # PreToolUse
│   ├── skills/
│   │   └── stan/SKILL.md       # /stan Skill
│   └── rules/
│       └── taming-stan/        # Bestehende Regeln (Symlink)
│
├── criteria/
│   ├── code/
│   │   ├── tests.yaml
│   │   ├── typecheck.yaml
│   │   ├── lint.yaml
│   │   └── build.yaml
│   ├── text/
│   │   ├── spelling.yaml
│   │   └── tone.yaml
│   ├── design/
│   │   ├── responsive.yaml
│   │   └── a11y.yaml
│   └── strategy/
│       └── logic.yaml
│
├── templates/
│   ├── stan.md.template
│   ├── prd.md.template
│   └── plan.md.template
│
├── docs/
│   └── README.md
│
└── vendor/                     # Referenz-Frameworks (Submodules)
    ├── BMAD-METHOD/
    ├── ralph/
    ├── PRPs-agentic-eng/
    └── claude-agent-sdk/

# Zusätzlich: Globales Learnings-Verzeichnis (User Home)
~/.stan/
└── learnings/
    ├── recent.json             # Rolling ~50, FIFO
    ├── hot.json                # Oft genutzt, weighted
    └── archive.json            # Permanent, komprimiert
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

### Phase 4: Testing & Enforcement
9. **Worktree-Enforcement in stan-gate** - Git-Projekte: Feature-Arbeit nur in Worktree
10. **Unit Tests für Hooks** - pytest mit stdin/stdout Mocking
11. **Interaktive Criteria-Tests** - LLM-as-Judge Pattern:
    - Evaluator Templates erstellen
    - Golden Examples (gut/schlecht) für jedes Criteria
    - Integration in /stan healthcheck --eval-criteria

### Phase 5: Tiered Storage
12. Recent → Hot Promotion (bei Mehrfachnutzung)
13. Recent → Archive Rotation (bei Overflow)
14. Heat Map / Usage Tracking

### Phase 6: Polish
15. Weitere Criteria Packs
16. README Dokumentation
17. E2E Test mit echtem Feature

**Hinweis:** Graphiti-Integration existiert bereits via taming-stan Hooks. STAN nutzt das für Query, schreibt aber nur lokal während der Arbeit.

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

---

## Referenz-Material

- `vendor/ralph/CLAUDE.md` - Progress-Tracking, Codebase Patterns
- `vendor/ralph/skills/ralph/SKILL.md` - Task-Sizing, Acceptance Criteria
- `.claude/rules/taming-stan/stanflux.md` - STAN.FLUX Verhaltensregeln
- Context7: `/anthropics/claude-code` - Hook-Dokumentation
