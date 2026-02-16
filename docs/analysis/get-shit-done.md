# Get-Shit-Done — Framework-Analyse

## Kern-Idee (1 Satz)

**Meta-Prompting-System für Claude Code, das Context Rot durch aggressive Plan-Atomisierung, frische Sub-Agent-Kontexte und XML-strukturierte Prompts löst.**

---

## Architektur

### Drei-Schichten-Modell

**1. Command Layer** (`.claude/commands/gsd/*.md`)
- Dünne Slash-Command-Wrapper mit YAML-Frontmatter
- Delegieren sofort an Workflows, führen KEINE schwere Logik aus
- Beispiel: `/gsd:execute-phase` → `workflows/execute-phase.md`

**2. Workflow Layer** (`get-shit-done/workflows/*.md`)
- Orchestratoren mit `<step>`-basierten Prozessen
- Spawnen spezialisierte Agents (Planner, Executor, Verifier)
- Bleiben selbst dünn (~30-40% Context), Arbeit passiert in Sub-Agents
- Batch-Execution mit Wellen-System (Wave 1, 2, 3... für Parallelisierung)

**3. Agent Layer** (`agents/gsd-*.md`)
- Spezialisierte Arbeiter mit frischen 200k-Context-Fenstern
- **gsd-executor**: Führt PLAN.md aus, erstellt SUMMARY.md, atomare Commits
- **gsd-planner**: Erstellt 2-3-Task-Pläne mit XML-Struktur
- **gsd-verifier**: Prüft Deliverables gegen Goals
- **gsd-debugger**: Root-Cause-Analyse bei Fehlern

### Datei-Struktur als Langzeit-Gedächtnis

```
.planning/
├── PROJECT.md           # Vision, immer geladen
├── ROADMAP.md           # Phasen, Status, Progress
├── STATE.md             # Session-Memory: Position, Decisions, Blocker
├── REQUIREMENTS.md      # V1/V2-Scope mit Phase-Mapping
├── research/            # Domain-Wissen (Stack, Features, Architektur)
├── phases/
│   ├── 01-foundation/
│   │   ├── 01-01-PLAN.md      # Executable Prompt (XML)
│   │   ├── 01-01-SUMMARY.md   # Maschinen-lesbar mit Frontmatter
│   │   ├── 01-CONTEXT.md      # User-Entscheidungen aus discuss-phase
│   │   └── 01-RESEARCH.md     # Wie implementieren?
│   └── 02-auth/...
└── config.json          # Mode, Depth, Model Profile, Git-Branching
```

### Execution Flow

```
/gsd:new-project
  ↓ Fragen → Research → Requirements → Roadmap
  
/gsd:discuss-phase 1
  ↓ Grau-Zonen identifizieren → User-Entscheidungen → CONTEXT.md
  
/gsd:plan-phase 1
  ↓ Research → 2-3 Pläne erstellen → Verify → PLAN.md
  
/gsd:execute-phase 1
  ↓ Wave-Analyse → Parallel Sub-Agents → Atomic Commits → SUMMARY.md
  
/gsd:verify-work 1
  ↓ User testet → Bei Fehlern: Auto-Debug → Fix-Pläne
```

---

## Einzigartige Stärken (besonders Context Rot Lösung!)

### 1. **Context Rot Prevention — Das Kern-Feature**

**Problem erkannt:**
Claude degradiert in "completion mode" wenn Context >50-70% voll ist:
- 0-30%: Peak Quality
- 30-50%: Gutes Arbeiten
- 50-70%: Efficiency Mode beginnt
- 70%+: Rushed, minimal

**GSD-Lösung (3-stufig):**

**a) Aggressive Plan-Atomisierung**
- MAXIMUM 2-3 Tasks pro Plan
- Geschätzt ~50% Context-Verbrauch pro Plan
- Bei >3 Tasks oder >5 Files: Sofortiges Split
- "Stop BEFORE degradation" statt "nutze 80% aus"

**b) Fresh Sub-Agent Contexts**
```
Orchestrator (main):  ~30-40% Context (nur Koordination)
  ↓ spawnt
Executor (subagent): 200k FRISCH → führt Plan aus → SUMMARY → stirbt
  ↓ parallel
Executor 2:          200k FRISCH → anderer Plan → stirbt
```
→ **KEINE akkumulierte Garbage**, jeder Plan in Peak-Quality-Zone

**c) XML-strukturierte PLAN.md als Direct Prompt**
```xml
<task type="auto">
  <name>Create login endpoint</name>
  <files>src/api/auth/login.ts</files>
  <action>
    Use jose for JWT (not jsonwebtoken - CommonJS issues).
    Validate against users table.
    Return httpOnly cookie.
  </action>
  <verify>curl POST /api/auth/login returns 200 + Set-Cookie</verify>
  <done>Valid credentials → 200+cookie. Invalid → 401.</done>
</task>
```

**PLAN.md IST der Prompt**, nicht ein Dokument das transformiert wird.
→ Null Interpretation-Overhead, präzise Instruktionen

### 2. **Spec-Driven Development Pattern**

**Nicht "vibe coding" sondern systematischer Flow:**

1. **Discovery** (`/gsd:new-project`, `/gsd:discuss-phase`)
   - Fragen bis 100% Verständnis
   - Grau-Zonen identifizieren (UI-Density, API-Format, Error-Handling)
   - **CONTEXT.md** sperrt User-Entscheidungen → Planner MUSS diese einhalten

2. **Planning** (`/gsd:plan-phase`)
   - Research (Domain-spezifisch, optional)
   - Plan Creation (2-3 Tasks)
   - **Plan Checker** (verify gegen Requirements, loop bis pass)

3. **Execution** (`/gsd:execute-phase`)
   - Wave-basierte Parallel-Execution
   - Atomic Commits pro Task
   - Auto-Deviation-Handling (Rule 1-4)

4. **Verification** (`/gsd:verify-work`)
   - User testet Deliverables
   - Bei Fehlern: **Auto-Debug** → Fix-Pläne

**CONTEXT.md Fidelity ist brutal:**
```markdown
## Decisions (Locked)
- Use library X (not Y)
- Card layout (not table)

## Deferred Ideas
- Search functionality → DARF NICHT in Plan erscheinen
```
Planner muss self-check: Jede locked decision hat Task, keine deferred idea wird implementiert.

### 3. **Deviation Rules — Autonome Bug-Fixes**

**RULE 1-3: Fix sofort, track für SUMMARY**
- Bug (falsche Logik, Crashes, Security): Auto-fix
- Missing Critical (Error Handling, Validation, Auth): Auto-add
- Blocker (Dependencies, Types, Imports): Auto-fix

**RULE 4: Architectural Changes → Checkpoint**
- Neue DB-Tabelle, Schema-Change, Framework-Switch
- STOP → User Decision → Continue

→ **Keine Permission für Basics**, User-Input nur bei Design-Impact

### 4. **Atomic Git Commits als Context Source**

```bash
abc123f feat(01-02): add email confirmation flow
def456g feat(01-02): implement password hashing
hij789k feat(01-02): create registration endpoint
```

**Jeder Task = 1 Commit** (sofort nach Completion)
- Git bisect findet exakten failing Task
- Jeder Task independently revertable
- Git history = klare Kontext-Quelle für zukünftige Sessions

### 5. **Multi-Agent Orchestration mit Wellen**

**Dependency Graph → Wave Assignment:**
```
Task A (User model): needs nothing → Wave 1
Task B (Product model): needs nothing → Wave 1
Task C (User API): needs Task A → Wave 2
Task D (Product API): needs Task B → Wave 2
Task E (Dashboard): needs C+D → Wave 3
```

**Parallel Execution innerhalb Wave:**
- Wave 1: A + B gleichzeitig (beide Sub-Agents frisch)
- Wave 2: C + D gleichzeitig
- Wave 3: E allein

**File Ownership Prevention:**
- `files_modified` in Frontmatter
- Overlap → Sequential dependency
- No overlap → Parallel

### 6. **Automation-First Checkpoints**

**Claude macht ALLES mit CLI/API, User nur für:**
- **human-verify** (90%): Visuelles/UX testen (Claude startet dev server vorher)
- **decision** (9%): Tech/Design-Wahl
- **human-action** (1%): Unavoidable Manual (2FA, Email-Link)

**Anti-Pattern vermieden:**
"Bitte führe `npm run dev` aus" → FALSCH
"Dev server läuft auf http://localhost:3000, bitte teste Layout" → RICHTIG

---

## Schwächen/Limitierungen

### 1. **Nur für Claude Code / OpenCode / Gemini CLI**
- Installiert Commands in `~/.claude/` oder `./.claude/`
- OpenClaw müsste eigene Adapter bauen

### 2. **Overhead für Simple Tasks**
- Full Planning (discuss → research → plan → execute → verify) zu schwer für "add config file"
- **Quick Mode** existiert, aber dokumentiert weniger

### 3. **Keine Brownie-Points für Team Work**
- Explizit Solo-Developer-fokussiert
- "No enterprise patterns" → RACI, Stakeholder, Sprints verboten
- Multi-Dev-Teams müssten eigene Wrapper bauen

### 4. **Git-Branching erst seit v1.11**
- Früher: Alles auf current branch
- Jetzt: `phase` / `milestone` / `none` Strategien
- Aber: Squash-Merge bei completion → atomic commits gehen verloren (optional)

### 5. **Research-Abhängigkeit von Context7 MCP**
- Planner nutzt `mcp__context7__*` für Library-Docs
- Ohne Context7: Manuelles Research nötig

### 6. **STATE.md nicht versioniert im Detail**
- STATE.md ist "living memory"
- Wenn verloren: Reconstruct möglich, aber Decisions/Blocker weg
- Keine dedizierte Backup-Strategie

### 7. **Keine dedizierte Memory-Compaction**
- SUMMARY.md Frontmatter als "Dependency Graph"
- Aber: Keine explizite Flush-Strategie wie OpenClaw
- Altes Phase-Zeug bleibt in `.planning/phases/`

---

## Key Features

| Feature | Beschreibung |
|---------|--------------|
| **Context Rot Solution** | 2-3 Tasks/Plan, Sub-Agents mit fresh 200k, Stop bei 50% |
| **XML Plans as Prompts** | `<task><action><verify><done>` direkt executable |
| **Spec-Driven Flow** | discuss → plan → execute → verify mit locked decisions |
| **Atomic Commits** | 1 Task = 1 Commit, Git als Context Source |
| **Wave Execution** | Dependency Graph → Parallel Sub-Agents |
| **Auto Deviation Handling** | Rules 1-3 = auto-fix, Rule 4 = Checkpoint |
| **Automation-First Checkpoints** | Claude startet Server, User testet UI |
| **Model Profiles** | quality/balanced/budget für Planner/Executor/Verifier |
| **Git Branching** | phase/milestone/none strategies |
| **Quick Mode** | Ad-hoc Tasks ohne full Planning |
| **TDD Plans** | Dedicated 1-Feature-Plan mit RED-GREEN-REFACTOR |
| **User Setup Detection** | External Services → Env Vars/Secrets identifiziert |
| **Codebase Mapping** | `/gsd:map-codebase` vor new-project für Brownfield |

---

## Was autonomous-stan davon fehlt

### 1. **Systematische Context Rot Prevention**
- Stan hat Skills, aber keine enforcierte 2-3-Task-Limits
- Keine Sub-Agent-Spawns mit guaranteed fresh context
- Keine Quality-Degradation-Curve als Design-Constraint

### 2. **Spec-Driven Development Workflow**
- Stan hat keine `/gsd:discuss-phase` → CONTEXT.md Pipeline
- User-Entscheidungen werden nicht gelockt und gegen Pläne verified
- Kein enforced "Plan Checker" Loop

### 3. **Atomic Git Commits pro Task**
- Stan committet, aber nicht systematisch 1:1 Task→Commit
- Keine `feat(phase-plan): task-name` Convention

### 4. **PLAN.md als Direct Prompt**
- Stan arbeitet ad-hoc, keine XML-strukturierten Execution Files
- Skills sind Guidance, keine executable task lists

### 5. **Wave-basierte Parallel Execution**
- Stan kann Multi-Agent (skills/multi-agent/SKILL.md)
- Aber: Keine automatische Dependency-Graph-Analyse → Wave-Assignment

### 6. **Deviation Rules (Auto-Fix)**
- Stan fixt Bugs, aber keine expliziten Rules 1-4
- Kein "Bug/Critical/Blocker = auto, Architectural = ask"

### 7. **Automation-First Checkpoint Protocol**
- Stan pausiert bei Checkpoints, aber nicht systematisiert
- Keine "Claude starts server, User tests UI" Garantie

### 8. **STATE.md als Session Memory**
- Stan hat `memory/YYYY-MM-DD.md` + `MEMORY.md`
- Aber: Kein `Position | Decisions | Blockers | Progress-Bar` Format

### 9. **Model Profiles für Sub-Agents**
- Stan spawnt alle mit default model
- GSD: quality=Opus Planner, balanced=Sonnet Executor, budget=Haiku Verifier

---

## Was autonomous-stan schon hat

| Feature | GSD | autonomous-stan | Wie implementiert |
|---------|-----|-----------------|-------------------|
| **Sub-Agent Spawning** | ✅ | ✅ | `skills/multi-agent/SKILL.md` |
| **Session Memory** | `STATE.md` | `memory/*.md` + `MEMORY.md` | Täglich + kuratiert |
| **Long-Term Knowledge** | `.planning/research/` | **Graphiti** | Graph-basiert, besser für Relationen |
| **Skills/Workflows** | `workflows/*.md` | `skills/*/SKILL.md` | Ähnliches Konzept |
| **Git Integration** | Atomic commits | Git-Workflow | `skills/git-workflow/SKILL.md` |
| **Checkpoints** | XML-basiert | Implicit in Skills | Weniger formalisiert |
| **External Tool Discovery** | Context7 MCP | Firecrawl, Context7 | Multiple Sources |
| **PITH Notation** | ❌ | ✅ `skills/pith/SKILL.md` | Kompakte Rules |
| **Discord/External Comm** | ❌ | ✅ | `skills/discord/SKILL.md` + message tool |
| **Kalender/Email** | ❌ | ✅ | Morgen MCP, n8n Pipeline |
| **BusinessMap** | ❌ | ✅ | `skills/businessmap/SKILL.md` |

**Hauptunterschied:**
- **GSD:** Context Rot Prevention + Spec-Driven Development
- **Stan:** Generalist + Integration (Discord, Kalender, Email, Graphiti)

---

## Vergleich mit OpenClaw (Compaction, Memory Flush)

### OpenClaw Session Management

**Aus AGENTS.md:**
```
!!session_hygiene:NIEMALS `sessions_list` ohne `limit`!
  |immer:limit≤5|große_responses:ERST mit kleinem Limit testen
```

→ **Limit als Context-Schutz**, aber keine automatische Compaction

### GSD vs OpenClaw Memory

| Aspekt | GSD | OpenClaw/Stan |
|--------|-----|---------------|
| **Short-Term** | STATE.md (Position, Decisions) | `memory/YYYY-MM-DD.md` |
| **Long-Term** | `.planning/research/` + SUMMARY.md | **Graphiti** (graph-based) |
| **Compaction** | ❌ Keine explizite Strategie | ❌ "Memory Maintenance" (manuell) |
| **Flush** | ❌ Sub-Agents sterben, kein global flush | ❌ Keine automatische Flush |
| **Context Limit Enforcement** | ✅ 2-3 Tasks, 50% Stop | ⚠️ Tool limits, aber kein Task-Limit |

### Was beide NICHT haben: Automatische Memory Compaction

**GSD-Ansatz:**
- Sub-Agents sterben nach Plan → "Flush by death"
- SUMMARY.md als kompakte Representation
- Aber: Keine Regel "Alte SUMMARY.md nach X Tagen archivieren"

**Stan-Ansatz:**
- "Alle paar Tage `memory/*.md` → `MEMORY.md` destillieren" (AGENTS.md)
- Graphiti als Langzeit-Knowledge-Graph
- Aber: **Manuell getriggert**, nicht automatisch

**Beide Systeme fehlt:**
```
if memory_size > THRESHOLD:
  trigger_compaction()
  archive_old_context()
```

### Graphiti als Überlegenheit bei Stan

**GSD `.planning/research/`:**
- Markdown-Files mit Domain-Wissen
- Statisch, nicht relational

**Stan Graphiti:**
- Graph-basiert (Entities + Relations)
- `search_nodes(query, group_ids: ["main"])`
- **Besser für:** "Welche Leads hängen mit Projekt X?" vs "Lies research.md"

**Trade-off:**
- GSD: Simpler, file-based, git-trackable
- Stan: Komplexer, aber mächtiger für Knowledge Retrieval

---

## Konkrete Übernahme-Empfehlungen

### 🔥 PRIORITÄT 1: Context Rot Prevention

**Übernehmen:**
1. **Aggressive Task-Atomisierung**
   ```
   !!task_limits:MAX 2-3 Tasks pro Sub-Agent-Call
     |bei_>3_tasks:Sofort Split in mehrere Sub-Agents
     |bei_>5_files:Split Signal
     |stop_bei:~50% Context statt 80%
   ```
   
2. **Fresh Sub-Agent Pattern**
   ```
   skills/multi-agent/SKILL.md erweitern:
   - Sub-Agents IMMER für execution spawnen
   - Main-Session bleibt bei ~30-40% (nur Orchestration)
   - Batch-Workflows mit Wave-System
   ```

3. **Quality Degradation Curve dokumentieren**
   ```markdown
   ## AGENTS.md oder TOOLS.md
   !!context_quality:Claude Quality Curve
     |0-30%:Peak|30-50%:Good|50-70%:Degrading|70%+:Poor
     |regel:Stop BEFORE degradation
     |split_signal:>50% Usage, >3 Tasks, >5 Files
   ```

### 🔥 PRIORITÄT 2: Spec-Driven Development Workflow

**Übernehmen:**
1. **CONTEXT.md Pattern für User-Entscheidungen**
   ```
   Neues Skill: skills/spec-driven/SKILL.md
   
   Workflow:
   1. Grau-Zonen identifizieren (UI, API, Error Handling)
   2. User-Entscheidungen sammeln → CONTEXT.md
   3. CONTEXT.md in Sub-Agent-Prompts laden
   4. Self-Check: Locked decisions implementiert? Deferred ideas vermieden?
   ```

2. **PLAN.md als Executable Prompt**
   ```xml
   .work/TASK_ID/PLAN.md:
   
   <task type="auto">
     <name>Task 1: Create login endpoint</name>
     <files>src/api/auth/login.ts</files>
     <action>POST /api/auth/login, bcrypt validate, jose JWT, httpOnly cookie</action>
     <verify>curl POST /api/auth/login returns 200 + Set-Cookie</verify>
     <done>Valid → 200+cookie, Invalid → 401</done>
   </task>
   ```

### 🔥 PRIORITÄT 3: Deviation Rules

**Übernehmen in AGENTS.md:**
```
!!deviation_rules:Auto-Fix vs Ask
  |rule_1:Bug(broken logic, crashes, security)→Auto-fix, track SUMMARY
  |rule_2:Missing Critical(error handling, validation, auth)→Auto-add
  |rule_3:Blocker(deps, types, imports)→Auto-fix
  |rule_4:Architectural(new table, schema change, framework switch)→ASK
  |priority:4>1-3|unsure→4
```

### 🟡 PRIORITÄT 4: Atomic Commits

**Übernehmen in git-workflow/SKILL.md:**
```
!!atomic_commits:1 Task = 1 Commit
  |format:`{type}({task-id}): {description}`
  |types:feat|fix|test|refactor|docs|chore
  |beispiel:`feat(task-001): add login endpoint with JWT`
  |stage:Einzeln (NIEMALS `git add .`)
```

### 🟡 PRIORITÄT 5: Wave-basierte Execution

**Übernehmen in multi-agent/SKILL.md:**
1. **Dependency Graph analysieren**
   ```javascript
   tasks = [
     {id: "A", needs: [], creates: ["user.model"]},
     {id: "B", needs: [], creates: ["product.model"]},
     {id: "C", needs: ["user.model"], creates: ["user.api"]},
   ]
   
   waves = build_dependency_waves(tasks)
   // Wave 1: [A, B]  (parallel)
   // Wave 2: [C]     (depends on Wave 1)
   ```

2. **Parallel Sub-Agent Spawns**
   ```
   for each wave:
     spawn_batch(tasks_in_wave)  # Alle gleichzeitig
     wait_for_all_complete()
     proceed_to_next_wave()
   ```

### 🟢 PRIORITÄT 6: STATE.md Format

**Optional, aber nützlich:**
```markdown
# STATE.md

## Current Position
Phase: 2 of 5 (Authentication)
Task: 3 of 8 (JWT implementation)
Status: In progress
Last activity: 2026-02-16 - Completed task-002

Progress: ████████░░░░░░░░░░░░ (40%)

## Decisions Made
| Date | Decision | Impact | Context |
|------|----------|--------|---------|
| 02-15 | Use jose not jsonwebtoken | Auth | Edge runtime compatibility |

## Blockers/Concerns
- None

## Session Continuity
Last session: 2026-02-16 10:00 CET
Stopped at: Task 3 in progress
Resume file: .work/task-003/.continue-here.md
```

### ❌ NICHT übernehmen

1. **Claude Code Slash Commands** → Stan nutzt OpenClaw, andere Command-Struktur
2. **`.planning/` Verzeichnis** → Stan hat `.work/` für temporär, `docs/` für permanent
3. **Research via Context7 allein** → Stan hat Firecrawl + Context7
4. **ROADMAP.md im GSD-Format** → Stan nutzt BusinessMap als Single Source of Truth

---

## Zusammenfassung: Was lernen wir?

### 3 Kern-Learnings

**1. Context Rot ist real und systematisch lösbar**
- GSD beweist: 2-3 Tasks + Fresh Sub-Agents + 50%-Stop funktioniert
- Stan sollte das sofort übernehmen

**2. Spec-Driven Development verhindert "Vibe Coding Garbage"**
- CONTEXT.md lockt User-Entscheidungen
- PLAN.md ist executable prompt, nicht "Dokument das wird prompt"
- Stan hat Skills, aber keine enforced Spec-Phase

**3. Meta-Prompting ist Engineering-Disziplin**
- XML-Struktur für Machine Parsing
- Frontmatter für Dependency Graphs
- Git Commits als Context Source
- Stan hat Pieces (Skills, Graphiti, Git-Workflow), fehlt Systematic Integration

### Was GSD NICHT hat, aber Stan schon

- **Graphiti** > Research-Files (relational vs static)
- **Discord/Kalender/Email** (GSD ist rein Code-fokussiert)
- **BusinessMap Integration** (GSD hat nur lokales ROADMAP.md)
- **PITH Notation** (GSD nutzt XML + Markdown, aber kein PITH)

### Finale Empfehlung

**Übernimm von GSD:**
1. Context Rot Prevention (2-3 Tasks, fresh Sub-Agents, 50% Stop) — **SOFORT**
2. Spec-Driven Workflow (CONTEXT.md → PLAN.md → Execute) — **WICHTIG**
3. Deviation Rules (Auto-fix vs Ask) — **WICHTIG**
4. Atomic Commits (1 Task = 1 Commit) — **NÜTZLICH**

**Behalte von Stan:**
1. Graphiti (besser als static research files)
2. Multi-Tool-Integration (Discord, Kalender, n8n)
3. PITH Notation (kompakter als GSD-XML für Rules)
4. BusinessMap (besser als lokales ROADMAP.md)

**Das Beste aus beiden Welten:**
- **GSD-Disziplin** (Context Rot, Spec-Driven, Atomic Commits)
- **Stan-Integration** (Graphiti, Discord, Kalender, BusinessMap)

→ **Autonomous-Stan wird unschlagbar: GSD-Systematik + Stan-Tooling**
