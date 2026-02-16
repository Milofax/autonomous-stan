# Ralph — Framework-Analyse

**Analysiert:** 2026-02-16  
**Quelle:** `/home/node/openclaw/workspace/repos-github/autonomous-stan/vendor/ralph/`

---

## Kern-Idee (1 Satz)

Ralph ist ein **autonomer Agent-Loop**, der AI-Coding-Tools (Amp oder Claude Code) wiederholt in **frischem Kontext** ausführt, bis alle PRD-Items erledigt sind — Memory persistiert nur via Git-History, `progress.txt` und `prd.json`.

---

## Architektur (Wie funktioniert der Loop? Fresh Context Pattern?)

### Der Ralph-Loop (ralph.sh)

```bash
for i in 1..MAX_ITERATIONS:
  1. Spawn fresh AI instance (Amp/Claude Code) with clean context
  2. AI reads: prd.json, progress.txt, git history
  3. AI picks highest priority story where passes=false
  4. AI implements that ONE story
  5. AI runs quality checks (typecheck, lint, test)
  6. If checks pass → commit + update prd.json (passes=true)
  7. AI appends learnings to progress.txt
  8. If ALL stories have passes=true → output "<promise>COMPLETE</promise>" → EXIT
  9. Otherwise → kill AI instance, loop continues
```

### Fresh Context Pattern (Kern-Prinzip)

- **Jede Iteration = neue AI-Instanz** (kein context carry-over)
- **Einziges Memory zwischen Iterationen:**
  - Git commits (Code + commit messages)
  - `progress.txt` (Learnings, konsolidierte Patterns)
  - `prd.json` (Task-Status: `passes: true/false`)
- **Warum?** Verhindert Context-Overflow, erzwingt dokumentiertes Wissen statt implizitem Context

### Datenfluss

```
Iteration 1:                    Iteration 2:
┌────────────────┐             ┌────────────────┐
│ Amp/Claude     │             │ Amp/Claude     │
│ (fresh context)│             │ (fresh context)│
└────────┬───────┘             └────────┬───────┘
         │ reads                        │ reads
         ▼                              ▼
    ┌────────────────────────────────────────┐
    │  prd.json  │  progress.txt  │  git log │
    └────────────────────────────────────────┘
         ▲                              ▲
         │ writes                       │ writes
         │                              │
    US-001 done                    US-002 done
    commit + update                commit + update
```

---

## Einzigartige Stärken

### 1. **Radikale Einfachheit**
- 1 Bash-Script (100 Zeilen), 2 Prompt-Templates, 2 Skills
- Keine Datenbank, keine API, keine Infrastruktur
- Funktioniert mit 2 verschiedenen AI-Tools (Amp, Claude Code)

### 2. **Fresh Context Enforcement**
- Erzwingt **dokumentiertes Wissen** statt "das steht noch im Context"
- Verhindert Context-Pollution und Drift
- AI muss sich auf Git + progress.txt verlassen → Learnings MÜSSEN gut sein

### 3. **Story Size Rule (DIE Killer-Feature)**
```
"Each story must be completable in ONE iteration (one context window)."
```
- Konkrete Heuristik: "Wenn du den Change nicht in 2-3 Sätzen beschreiben kannst, ist er zu groß"
- Praktisch: Max. 5 Files pro Story
- Verhindert #1 Problem autonomer Agents: Zu große Tasks → Context-Overflow → broken code

### 4. **Browser Verification (UI Stories)**
- **Pflicht** für alle UI-Stories: "Verify in browser using dev-browser skill"
- AI muss Browser öffnen, navigieren, interagieren, Screenshot machen
- Verhindert "sieht im Code gut aus, aber UI ist kaputt"

### 5. **Completion Signal (`<promise>COMPLETE</promise>`)**
- Klares Stop-Signal für autonome Loops
- Verhindert "Wann ist es fertig?"-Problem
- Machine-readable, grep-bar

### 6. **Archivierung (Automatisch)**
- Wenn `branchName` in `prd.json` wechselt → automatisches Archiv
- Format: `archive/YYYY-MM-DD-feature-name/`
- Verhindert vermischen von Feature-Runs

### 7. **Consolidate Patterns Section**
- Top-of-File "Codebase Patterns" Sektion in `progress.txt`
- AI destilliert wichtigste Learnings nach oben
- Zuerst gelesen bei jeder Iteration

### 8. **Thread URL Tracking (Amp-spezifisch)**
```markdown
## 2026-02-16 - US-003
Thread: https://ampcode.com/threads/$AMP_CURRENT_THREAD_ID
```
- Future Iterations können `read_thread` nutzen
- Ermöglicht Referenz auf vorherige Arbeit trotz Fresh Context

---

## Schwächen/Limitierungen

### 1. **Keine Story-Abhängigkeiten (nur Priorität)**
- `prd.json` hat nur `priority`, keine expliziten Dependencies
- Muss manuell über Reihenfolge geregelt werden (Schema → Backend → UI)
- Keine Validierung, dass Dependency-Order stimmt

### 2. **Keine Skill-Level-Anpassung**
- Ein Prompt für alle
- Keine Anpassung an User-Expertise (Beginner/Expert)
- Keine Projekt-Komplexitäts-Level (Quick/Standard/Enterprise)

### 3. **Keine Qualitäts-Checks der PRD/Stories**
- Kein LLM-as-Judge
- Keine Meta-Criteria
- AI muss selbst erkennen, wenn Stories schlecht sind

### 4. **Kein Multi-Agent-Support**
- Ein Agent für alles (Full-Stack)
- Keine Spezialisierung (Backend/Frontend/DB/Testing)
- Keine parallele Arbeit

### 5. **Fehler-Handling rudimentär**
- Nur "Checks failed → kein Commit"
- Keine 3-Strikes-Rule
- Keine Error-Pattern-Detection
- Keine STUCK-Detection

### 6. **Progress.txt = flat file**
- Keine strukturierte Learnings-Hierarchie (recent/hot/archive)
- Keine Heat-Scores
- Wächst unbegrenzt (keine Rotation)

### 7. **Keine Integration mit Project Management**
- Kein BusinessMap
- Kein GitHub Projects
- Kein Jira
- Nur lokale JSON-Datei

### 8. **Keine User-Interaktion während Loop**
- Loop läuft komplett autonom
- Keine Notifications
- Keine Approval-Gates
- Keine Clarifying Questions mid-run

### 9. **Resource-Limits nur via MAX_ITERATIONS**
- Keine Cost-Budgets
- Keine Token-Tracking
- Keine Time-Budgets
- Nur "stoppe nach N Iterationen"

### 10. **Claude Code: Kein Thread-Tracking**
- Amp hat `$AMP_CURRENT_THREAD_ID`
- Claude Code hat keinen äquivalenten Mechanismus
- Schwieriger, vorherige Arbeit zu referenzieren

---

## Key Features (Progress.txt, Story Size Rule, Completion Signal, etc.)

| Feature | Was | Warum wichtig |
|---------|-----|---------------|
| **prd.json** | User Stories mit `passes: true/false` | Single source of truth für Task-Status |
| **progress.txt** | Append-only Learnings + Consolidate Patterns | Memory zwischen Fresh Contexts |
| **Story Size Rule** | "One iteration, 2-3 sentences, max 5 files" | #1 Schutz gegen Context-Overflow |
| **Browser Verification** | Pflicht-Kriterium für UI Stories | Verhindert broken UIs |
| **`<promise>COMPLETE</promise>`** | Machine-readable completion signal | Klares Loop-Ende |
| **Codebase Patterns** | Konsolidierte Learnings at top of progress.txt | Schneller Kontext-Aufbau |
| **Archivierung** | Auto-Archive bei Branch-Wechsel | Saubere Trennung von Feature-Runs |
| **Quality Checks** | Typecheck/Lint/Test vor Commit | Kein broken code im Repo |
| **Thread URL** | Amp: Link zu vorheriger Arbeit | Referenzierbarkeit trotz Fresh Context |
| **Max Iterations** | Hard Stop nach N Loops | Cost Control |
| **Branch Enforcement** | Feature-Branch aus prd.json | Isolation, saubere PRs |

---

## Was autonomous-stan davon fehlt

### 🔴 HIGH Priority (Kritische Gaps)

1. **Story Size Rule & Enforcement**
   - STAN hat keine explizite Größen-Heuristik
   - Keine "2-3 Sätze"-Regel
   - Keine "Max 5 Files"-Regel
   - Keine Story-Size-Criteria

2. **Browser Verification für UI Stories**
   - STAN hat keine Pflicht-Verifikation
   - Kein Browser-Skill in Standard-CREATE-Phase
   - Risk: UI Ships kaputt

3. **Completion Signal Pattern**
   - STAN hat kein `<promise>COMPLETE</promise>`
   - Schwieriger für autonome Loops zu erkennen: "Bin ich fertig?"

4. **Activity Log (session_id.md)**
   - STAN hat nur Learnings, keine Session-Activity-Logs
   - Schwieriger zu debuggen: "Was hat Iteration 3 gemacht?"

### 🟡 MEDIUM Priority (Nice to Have)

5. **Consolidate Patterns Section**
   - STAN hat tiered learnings (recent/hot/archive), aber keine "Top-of-File Patterns"
   - Ralph's Ansatz ist expliziter: "Das HIER lesen ZUERST"

6. **Archivierung (explizit)**
   - STAN hat Lifecycle (draft/approved/in-progress/done/archived)
   - Aber: Keine automatische "Previous Run"-Archivierung wie Ralph

7. **Thread/Session URL Tracking**
   - STAN hat session_id, aber keine explizite Thread-URL in Progress
   - Schwieriger, vorherige Arbeit zu referenzieren

### 🟢 LOW Priority (Unterschiede, keine Gaps)

8. **Fresh Context Enforcement**
   - Ralph: Erzwungen durch Bash-Script (kill AI nach Iteration)
   - STAN: Context-Compaction, aber kein Hard-Reset
   - Trade-off: Ralph = sauber, STAN = effizienter

9. **prd.json vs. PRD.md**
   - Ralph: Nur JSON (machine-readable)
   - STAN: Markdown (human-readable) + YAML-Frontmatter
   - Trade-off: JSON einfacher zu parsen, Markdown besser lesbar

---

## Was autonomous-stan schon hat (und besser macht)

### ✅ Überlegene STAN-Features (Ralph hat diese NICHT)

1. **LLM-as-Judge Criteria-Packs**
   - 24+ Criteria mit Golden Examples
   - Meta-Criteria (Quality Checks für Criteria selbst)
   - Ralph: Keine Quality-Gates für PRD/Stories

2. **Tiered Learnings (recent/hot/archive)**
   - Heat-Scores, automatische Promotion/Demotion
   - Ralph: Flat file, nur manuel consolidation

3. **21 Thinking Techniques**
   - 9 Purposes, structured problem-solving
   - Ralph: Keine Thinking-Tools

4. **Skill_level (beginner/intermediate/expert)**
   - Anpassbare Kommunikation
   - Ralph: One-size-fits-all

5. **3-Strikes Rule & Error Pattern Detection**
   - STAN stoppt bei wiederholten Fehlern
   - Ralph: Läuft blind weiter bis MAX_ITERATIONS

6. **Worktree Enforcement**
   - STAN: Git-Worktree-Isolation für CREATE-Phase
   - Ralph: Nur Branch (einfacher, aber weniger Isolation)

7. **Template-Criteria-Linking**
   - Templates referenzieren applicable Criteria
   - Ralph: Keine Template-System

8. **Config System (user preferences, language settings)**
   - STAN: Strukturierte Config, mehrsprachig
   - Ralph: Hardcoded Prompts

9. **Multi-Agent Support**
   - STAN: Agent-to-Agent Communication, Sub-Agents
   - Ralph: Single-Agent

10. **Integration mit BusinessMap**
    - STAN: Karten-Management, Board-Sync
    - Ralph: Nur lokale Datei

11. **Retrospective Workflows**
    - STAN: `/stan think retrospective`
    - Ralph: Keine expliziten Retros

12. **PRD Quality Requirements**
    - STAN: Hypothesis, Evidence, JTBD, MoSCoW, Feasibility
    - Ralph: Nur User Stories + Acceptance Criteria

### ⚖️ Trade-Offs (Beide haben es, unterschiedliche Ansätze)

| Feature | Ralph | STAN | Besser bei |
|---------|-------|------|-----------|
| Memory | progress.txt (flat) | recent/hot/archive (tiered) | STAN |
| Context | Fresh per iteration | Compaction | Ralph (sauberer), STAN (effizienter) |
| Story Format | JSON (machine) | Markdown (human) | Depends |
| Agent Model | Single-Agent Loop | Multi-Agent + Sub-Agents | STAN |
| Tool Support | Amp + Claude Code | OpenClaw (Claude-only) | Ralph (flexibler) |
| Quality Checks | Typecheck/Test | Typecheck/Test + Criteria-Packs | STAN |
| Browser Verification | Pflicht für UI | Skill verfügbar, nicht enforced | Ralph |

---

## Vergleich mit OpenClaw (Cron-Jobs, Heartbeats, sessions_spawn)

### Ralph's Loop vs. OpenClaw Scheduling

| Dimension | Ralph | OpenClaw (STAN) |
|-----------|-------|-----------------|
| **Loop-Mechanismus** | Bash `for i in 1..N` | Heartbeats (Cron: `*/X * * * *`) |
| **Iteration Trigger** | Sequenziell, synchron | Zeitbasiert, asynchron |
| **Fresh Context** | Hard-enforced (kill AI) | Context-Compaction (soft) |
| **Max Runtime** | `MAX_ITERATIONS * (context window time)` | 24/7, nur Heartbeat-Intervall |
| **Cost Control** | Via MAX_ITERATIONS | Via Cron-Intervall + Budget-Tracking (TODO) |
| **Error Handling** | Kein Commit bei Checks-Fail, loop weiter | 3-Strikes → Pause |
| **User Interaction** | Keine während Loop | Jederzeit via Discord/Message |

### Session Management

| Feature | Ralph | OpenClaw |
|---------|-------|----------|
| **Session Model** | Keine Sessions, nur Iterations | `agent:main:$CHANNEL`, `agent:$NAME:main` |
| **Sub-Agents** | ❌ Nicht vorhanden | ✅ `sessions_spawn`, Sub-Agent-Skill |
| **Agent Communication** | ❌ Nicht vorhanden | ✅ `sessions_send` (fire-and-forget) |
| **Session Lifecycle** | Iteration = kurzlebig | Session = langlebig (Heartbeats) |
| **Memory Isolation** | Vollständig (Fresh Context) | Shared Memory (Graphiti, Markdown) |

### Scheduling-Paradigmen

#### Ralph (Bash Loop)
```bash
for i in 1..10:
  spawn_ai
  do_work
  kill_ai
  # Next iteration starts IMMEDIATELY
```
- **Vorteile:** Einfach, deterministisch, sequenziell
- **Nachteile:** Keine Pausen, keine externe Triggers, keine parallele Arbeit

#### OpenClaw (Cron + Heartbeats)
```yaml
heartbeat_main:
  cron: "*/15 * * * *"  # Every 15 min
  trigger: check_work → spawn_sub_agent if needed
  
heartbeat_session_XYZ:
  on_demand: true
  trigger: user_message / agent_send
```
- **Vorteile:** Flexibel, 24/7, multi-threaded, event-driven
- **Nachteile:** Komplexer, non-deterministisch, Context-Carry-Over

### Autonomy Levels

| Level | Ralph | OpenClaw (STAN) |
|-------|-------|-----------------|
| **Fully Autonomous** | ✅ Ja (bis MAX_ITERATIONS) | ⚠️ Möglich, aber nicht default |
| **Supervised** | ❌ Nicht während Loop | ✅ Ja (User kann jederzeit eingreifen) |
| **Interactive** | ❌ Nein | ✅ Ja (Discord, Sub-Agent-Komm) |
| **Scheduled** | ❌ Nein (nur one-shot) | ✅ Ja (Cron-Heartbeats) |

### Wo OpenClaw's Model passt

**Ralph-Style Loop mit OpenClaw:**
```bash
# In CREATE-Phase
autonomous-loop:
  1. Heartbeat checkt: Noch offene Tasks?
  2. Wenn ja → spawn_sub_agent(label: "create-task-US-001")
  3. Sub-Agent arbeitet → commit → meldet DONE
  4. Heartbeat checkt: Alle Tasks done?
  5. Wenn ja → `<promise>COMPLETE</promise>` → Archive PRD
```

**Unterschied zu Ralph:**
- Ralph: Synchroner Loop, blockiert bis fertig
- STAN: Asynchroner Loop, Heartbeat checkt periodisch, User kann unterbrechen

---

## Konkrete Übernahme-Empfehlungen

### 🟢 SOFORT übernehmen (Low Effort, High Impact)

#### 1. Story Size Criteria (T-030)
**Erstelle:** `criteria/strategy/story-size.yaml`
```yaml
name: Story Size
checks:
  - id: one-iteration-rule
    question: "Kann dieser Task in EINER Iteration (einem Context Window) erledigt werden?"
    golden_yes: "Add 'status' column to tasks table (migration + typecheck)"
    golden_no: "Build entire user dashboard (needs: schema, backend, 5+ components, tests)"
    required: true
  
  - id: two-sentence-rule
    question: "Kann der Change in 2-3 Sätzen beschrieben werden?"
    required: true
  
  - id: max-files-rule
    question: "Betrifft der Task maximal 5 Dateien?"
    required: false  # Warning, nicht hard fail
```

#### 2. Visual Verification Criteria (T-030)
**Erstelle:** `criteria/code/visual-verification.yaml`
```yaml
name: Visual Verification
checks:
  - id: browser-verification
    question: "Wurde die UI-Änderung im Browser verifiziert?"
    golden_yes: "Screenshot in docs/screenshots/, Browser-Test im Activity Log"
    golden_no: "Nur Code-Review, kein Browser geöffnet"
    required: true  # Nur für UI-Tasks
  
  - id: screenshot-evidence
    question: "Gibt es einen Screenshot der Änderung?"
    required: false
```

**Integration in `/stan create`:**
- Bei UI-Tasks: Browser-Skill laden
- Nach Implementation: Browser öffnen, navigieren, Screenshot
- Acceptance Criteria: "Verify in browser using dev-browser skill"

#### 3. Completion Signal Pattern
**Dokumentiere in:** `techniques/completion-signal.md`
```markdown
# Completion Signal Pattern

Wenn ALLE Tasks eines PRDs erledigt sind:
```
<promise>COMPLETE</promise>
```

Dies signalisiert:
- Autonomen Loops: Stop condition
- Heartbeats: Archive PRD, move to next
- User: Feature ist fertig
```

**Integration:**
- `/stan create` Final-Check: Alle Acceptance Criteria done? → `<promise>COMPLETE</promise>`
- Heartbeat: grep nach Signal → wenn found → Archive + Notification

#### 4. Activity Log Pattern
**Dokumentiere in:** `docs/workflows/activity-log.md`
```markdown
# Activity Log (session_id.md)

Während CREATE-Phase: Führe `docs/activity/{session_id}.md`

Format:
```markdown
# Activity Log: {session_id}
Started: {timestamp}

## Task US-001: Add status field
**Changes:**
- `db/schema.sql` - added status column
- `db/migrations/001_status.sql` - migration

**Learnings:**
- Must use `IF NOT EXISTS` for idempotent migrations
- Status enum values: 'pending' | 'in_progress' | 'done'

**Thread:** openclaw session {session_id}
---

## Task US-002: ...
```
```

**Warum separate von progress.txt?**
- `activity.md` = WAS wurde gemacht (debugging)
- `progress.txt` / learnings = WARUM + PATTERNS (teaching)

### 🟡 KURZFRISTIG übernehmen (T-031, Medium Effort)

#### 5. Consolidate Patterns Section
**Erweitere:** `learnings/recent/*.md`

Füge jeweils Top-Section hinzu:
```markdown
# Recent Learnings: {topic}

## 🔥 Key Patterns (Read First)
- Pattern 1 (used in 5+ sessions)
- Pattern 2 (critical gotcha)

## Detailed Learnings
[rest of file]
```

**Automatisierung:** Heartbeat-Task "Promote top 5 hot learnings to Patterns section"

#### 6. Archive Mechanism (explizit)
**Erstelle:** `/stan archive` command

```bash
/stan archive [prd-name]
# → moves docs/prd-{name}.md to archive/YYYY-MM-DD-{name}/
# → archives associated activity logs, screenshots
# → updates PRD status to "archived"
```

#### 7. Browser Skill Integration (CREATE-Phase)
**Erweitere:** `/stan create` Workflow

```markdown
For UI Tasks:
1. Implement changes
2. **Load browser skill** (`skills/browser/SKILL.md`)
3. **Navigate** to affected page
4. **Interact** with changed elements
5. **Screenshot** before/after
6. **Log** in activity.md: "Browser verified: {url} - {screenshot-path}"
```

### 🔵 LANGFRISTIG evaluieren (T-032+, High Effort)

#### 8. Fresh Context Mode (optional für autonomous loops)
**Idee:** Flag `--fresh-context` für `/stan create`

```bash
/stan create --fresh-context
# → Sub-Agent wird nach JEDEM Task killed + respawned
# → Erzwingt dokumentiertes Wissen
# → Verhindert Context-Pollution
```

**Trade-Off:**
- ✅ Sauberere Learnings (wie Ralph)
- ❌ Langsamere Execution (kein Context-Reuse)
- ❌ Mehr Token-Verbrauch

**Empfehlung:** Nur für kritische/hochkomplexe Features nutzen

#### 9. Amp/Claude Code Support (Multi-Tool)
**Aktuell:** STAN = OpenClaw = Claude-only

**Ralph:** Unterstützt Amp + Claude Code via `--tool` flag

**Überlegung:** OpenClaw Multi-Model-Support?
- Derzeit: `anthropic/claude-sonnet-4-5` hardcoded
- Potenzial: `--model anthropic/claude-opus-4-6` oder `--model openai/gpt-4`

**Aufwand:** Hoch (OpenClaw Core-Feature)

#### 10. Project Complexity Levels (0-4)
**Aktuell:** `skill_level` (user) — beginner/intermediate/expert

**Gap:** Keine Project-Complexity-Einstellung

**BMAD hat:**
- Level 0 (trivial) → keine Planung
- Level 1 (simple) → minimal
- Level 2 (standard) → standard PRD
- Level 3 (complex) → detailed PRD + ADRs
- Level 4 (enterprise) → comprehensive + compliance

**Überlegung für STAN:**
```yaml
# config/project.yaml
complexity_level: 2  # standard

# Beeinflusst:
# - PRD Template (0: keins, 4: full BMAD)
# - Criteria Packs (0: basic, 4: full security/compliance)
# - Planning Phase Duration (0: skip, 4: multi-day)
```

**Aufwand:** Hoch (Workflow-Change)

---

## Zusammenfassung: Ralph's DNA

### Was Ralph ausmacht (3 Kern-Prinzipien)

1. **Fresh Context Enforcement**
   - Kein Context-Carry-Over
   - Erzwingt dokumentiertes Wissen
   - Verhindert Drift

2. **Story Size Rule**
   - One iteration, 2-3 sentences, max 5 files
   - Schützt vor Context-Overflow
   - #1 Erfolgsrezept für autonome Loops

3. **Browser Verification**
   - UI-Changes MÜSSEN visuell verifiziert werden
   - Kein "looks good in code"-Shipping

### Was STAN davon übernehmen sollte (EHRLICH)

**HIGH Priority (sofort):**
- ✅ Story Size Criteria + Enforcement
- ✅ Visual Verification für UI Stories
- ✅ Completion Signal Pattern
- ✅ Activity Log (session-level)

**MEDIUM Priority (nächste Wochen):**
- ⚠️ Consolidate Patterns Section
- ⚠️ Archive Mechanism (explizit)
- ⚠️ Browser Skill in CREATE-Phase (Standard)

**LOW Priority (evaluieren):**
- 🤔 Fresh Context Mode (opt-in)
- 🤔 Multi-Tool Support (Amp/Claude)
- 🤔 Project Complexity Levels

### Was STAN NICHT übernehmen sollte

- ❌ **Bash-Loop statt Heartbeats** — OpenClaw's Scheduling ist überlegen für 24/7-Agent
- ❌ **Flat progress.txt** — Tiered Learnings besser
- ❌ **Keine LLM-Judge** — Criteria-Packs sind Killer-Feature
- ❌ **Single-Agent only** — Multi-Agent ist STAN's Stärke
- ❌ **JSON-only PRDs** — Markdown ist lesbarer

---

## Finale Bewertung

**Ralph ist ein exzellentes Referenz-Framework für:**
- Autonome Loops (Fresh Context Pattern)
- Story-Sizing (konkrete Heuristiken)
- Browser-Verification (UI-Quality)

**STAN hat bereits überlegene Features in:**
- Quality Assurance (LLM-Judge, Criteria-Packs)
- Memory Management (tiered learnings)
- Agent Architecture (Multi-Agent, Sub-Agents)
- Integration (BusinessMap, Discord, etc.)

**Empfehlung:**
Übernehme Ralph's **praktische Heuristiken** (Story Size, Browser Verification), aber behalte STAN's **strukturelle Überlegenheit** (Criteria-System, Multi-Agent, Tiered Memory).

**Konkret:** T-030 sollte Story Size + Visual Verification Criteria implementieren. Das sind Quick Wins mit hohem Impact für autonome Execution-Qualität.
