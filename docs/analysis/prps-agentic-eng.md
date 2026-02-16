# PRPs (Product Requirement Prompts) — Framework-Analyse

## Kern-Idee (1 Satz)

PRPs sind strukturierte, kontext-reiche Implementierungspläne, die einem AI-Agenten ermöglichen, Features "in einem Durchgang" von der Idee bis zum produktionsreifen Code zu liefern, indem sie Problem + Codebase-Intelligence + executable Validierungen kombinieren.

---

## Architektur (Wie funktionieren PRPs?)

### Konzept: PRP = PRD + Codebase-Intelligence + Agent/Runbook

Das Framework verfolgt einen **sequenziellen 3-Phasen-Workflow**:

```
/prp-prd → /prp-plan → /prp-implement (oder /prp-ralph für autonome Loops)
```

### Phase 1: PRD-Erstellung (`/prp-prd`)

Ein **interaktiver Product Manager**, der durch gezielte Fragen führt:

1. **Foundation Questions**: Wer, Was, Warum, Warum jetzt, Wie messen?
2. **Grounding via Research**: Market/Competitor-Analyse (WebSearch) + Codebase-Exploration
3. **Deep Dive**: Vision, Primary User, Job-to-be-Done, Constraints
4. **Grounding via Technical Feasibility**: Codebase-Patterns, Infrastruktur-Check
5. **Decisions**: MVP-Definition, MoSCoW-Priorisierung, Hypothese, Out-of-Scope

**Output**: PRD-Dokument (`.claude/PRPs/prds/`) mit:
- Hypothesen-basierte Zielsetzung ("We believe X will solve Y for Z. We'll know when...")
- Evidence-First (keine Annahmen ohne Belege)
- **Implementation Phases Tabelle** mit Status-Tracking (pending/in-progress/complete), Dependencies, Parallelismus

**Besonderheit**: Phases haben Dependencies + Parallelismus-Info → ermöglicht worktree-basierte parallele Entwicklung

### Phase 2: Plan-Erstellung (`/prp-plan`)

Ein **systematischer Codebase-Explorer**, der vor jeder Recherche die **Codebase ZUERST** analysiert:

#### Ablauf:

1. **Input Detection**: PRD-Datei (wählt automatisch nächste Phase) ODER Free-form Feature-Beschreibung
2. **EXPLORE Phase** (via Task tool mit `subagent_type="Explore"`):
   - Findet **ähnliche Implementierungen** mit `file:line`-Referenzen
   - Extrahiert **echte Code-Patterns** (Naming, Error Handling, Logging, Testing)
   - Dokumentiert in Tabellen mit SOURCE-Referenzen
3. **RESEARCH Phase** (erst NACH Explore):
   - WebSearch für Library-Docs (versioniert zu package.json)
   - Best Practices, Gotchas, Security
4. **DESIGN Phase**:
   - ASCII Before/After Diagramme (UX-Transformation)
   - Data Flow Visualisierung
5. **ARCHITECT Phase**:
   - Approach-Entscheidung mit Rationale
   - Risk/Mitigation
   - Explicit Scope Limits
6. **GENERATE Phase**:
   - Plan-Datei (`.claude/PRPs/plans/{feature-name}.plan.md`)
   - **Updates PRD** (Phase → `in-progress`, verlinkt Plan)

#### Plan-Struktur (Kernsektionen):

```markdown
## Mandatory Reading
- P0/P1/P2 Files mit file:line + Begründung "Why Read This"
- External Docs (versioniert, mit #anchor)

## Patterns to Mirror
- NAMING_CONVENTION (SOURCE: file:line)
- ERROR_HANDLING (SOURCE: file:line)
- LOGGING_PATTERN (SOURCE: file:line)
- etc. — IMMER mit echtem Code-Snippet aus Codebase

## Step-by-Step Tasks
- Jeder Task: ACTION, IMPLEMENT, MIRROR, IMPORTS, GOTCHA, VALIDATE
- Dependency-Order (top-to-bottom executable)

## Validation Commands
- Level 1: Static Analysis (lint + type-check)
- Level 2: Unit Tests
- Level 3: Full Suite + Build
- Level 4: Database Validation (MCP)
- Level 5: Browser Validation (MCP)
- Level 6: Manual Validation

## Acceptance Criteria
- Checkboxen für alle Anforderungen
```

**Kernprinzip**: **Context is King** — jeder Task muss ohne Nachfragen ausführbar sein.

### Phase 3: Implementation (`/prp-implement` oder `/prp-ralph`)

Ein **rigoros validierender Executor**:

#### `/prp-implement` (Standard):

1. **DETECT**: Package Manager + Validation Scripts identifizieren
2. **LOAD**: Plan laden + Key Sections parsen
3. **PREPARE**: Git-Branch-Setup
4. **EXECUTE**: Tasks sequenziell abarbeiten
   - Nach **JEDEM** File-Change: Type-Check
   - Fix → Re-Check → Erst dann nächster Task
5. **VALIDATE**: Full Suite (Static + Tests + Build + Integration)
6. **REPORT**: Implementation Report + PRD-Update (Phase → `complete`) + Plan archivieren

#### `/prp-ralph` (Autonomous Loop):

```bash
/prp-ralph .claude/PRPs/plans/my-feature.plan.md --max-iterations 20
```

- Loop: Implement → Validate → Fix → Re-Validate
- Exit bei "all validations pass" ODER max-iterations
- Fire-and-forget ("Go make coffee")

**Golden Rule**: "Never accumulate broken state" → jeder Fehler wird sofort gefixt.

---

## Einzigartige Stärken

### 1. **Context-First, Code-Second**

Kein anderes Framework erzwingt so rigoros **"Codebase ZUERST, Research ZWEITER"**:
- Explore Agent findet echte Patterns VOR jeder externen Recherche
- Patterns werden mit `file:line`-Referenzen dokumentiert
- Neuer Code **spiegelt exakt** bestehende Conventions

**Effekt**: Konsistenz by Design, kein "AI erfindet neue Patterns".

### 2. **One-Pass Implementation**

Die Pläne sind so kontext-dicht, dass ein Agent ohne Rückfragen ausführen kann:
- Jeder Task hat: ACTION, MIRROR (Vorbild-Code), GOTCHA (Fallstricke), VALIDATE (Prüfung)
- "No Prior Knowledge Test": "Könnte ein Agent OHNE Codebase-Kenntnis nur mit Plan arbeiten?"

**Effekt**: Drastisch höhere Erfolgsrate bei erstem Versuch.

### 3. **Validation Loops als First-Class Citizen**

6 Ebenen von Validierung + Executable Commands:
- Nicht "schreib Tests", sondern "run `npm test src/feature` — expect 100% pass"
- Agent weiß GENAU, wie Erfolg gemessen wird

**Effekt**: Self-correcting implementation, weniger menschliches Debugging.

### 4. **Evidence-Based PRDs**

PRD-Generator fragt nach **Evidence** vor Solution:
- "What data supports this hypothesis?"
- Open Questions explizit dokumentiert (statt erfunden)
- Hypothesis-Driven ("We believe X will solve Y. We'll know when Z")

**Effekt**: Weniger Feature-Bloat, fokussierte Entwicklung.

### 5. **Phase Dependency + Parallelismus**

PRDs haben Implementation Phases mit:
- Dependencies (welche Phase muss vorher fertig sein?)
- Parallelismus (welche Phases können gleichzeitig laufen?)
- Worktree-Empfehlungen für parallele Arbeit

**Effekt**: Große Features werden planbar + parallelisierbar.

### 6. **Root Cause Analysis mit 5 Whys**

`/prp-debug` erzwingt Evidence-Chain:
- Jedes "Because" braucht `file:line`-Proof
- Git Blame + History-Analyse
- Causation/Necessity/Sufficiency-Tests

**Effekt**: Findet echte Ursachen, nicht Symptome.

### 7. **Multi-Agent Review Workflow**

`/prp-review-agents` orchestriert spezialisierte Agenten:
- `comment-analyzer`: Comment-Genauigkeit
- `silent-failure-hunter`: Error Handling
- `type-design-analyzer`: Type Encapsulation
- `code-simplifier`: Klarheit
- `docs-impact-agent`: Stale Docs updaten

**Effekt**: Comprehensive Review ohne Overload für einen einzelnen Agent.

### 8. **Artifact-First (Dokumentation IST die Spec)**

Alle Workflows erstellen persistente Artefakte:
- `.claude/PRPs/prds/` → PRDs
- `.claude/PRPs/plans/` → Implementation Plans
- `.claude/PRPs/reports/` → Implementation Reports
- `.claude/PRPs/issues/` → Issue Investigations
- `.claude/PRPs/reviews/` → PR Reviews

**Effekt**: Traceability, Wiederverwendbarkeit, Lessons Learned.

---

## Schwächen/Limitierungen

### 1. **Hoher Upfront-Investment**

PRD + Plan-Erstellung kann 10-20 Minuten dauern:
- Nur lohnenswert für Features, nicht für "Quick Fixes"
- Für kleine Bugfixes Overhead

**Mitigation im Framework**: `/prp-issue-fix` überspringt PRD → direkt zu Plan

### 2. **Claude-Code-Spezifisch**

Tief in Claude Code's Ökosystem integriert:
- `/plugin` System
- Task tool
- Agents als `.md`-Files mit YAML Frontmatter

**Portierbarkeit**: Konzepte übertragbar, aber Code nicht.

### 3. **Keine Multi-Repo-Unterstützung**

PRPs gehen von einem Codebase aus:
- Keine Cross-Repo Dependencies
- Monorepo-Workflows nicht explizit adressiert

### 4. **Git-Workflow Assumptions**

Setzt voraus:
- GitHub als Git-Host
- `gh` CLI installiert
- Feature-Branch-Workflow
- PRs als Standard-Review-Mechanismus

**Nicht für**: GitLab, Bitbucket, Trunk-Based Development ohne PRs.

### 5. **Keine CI/CD-Integration**

PRPs triggern keine Pipelines:
- Kein Auto-Deploy nach Merge
- Kein Status-Feedback von CI in den Plan

**Konsequenz**: Human muss CI-Status manuell prüfen.

### 6. **Pattern Discovery begrenzt auf Textsuche**

Explore Agent nutzt Grep + Read:
- Findet keine semantischen Patterns (AST-basiert)
- Kann Code-Duplication nicht erkennen
- Keine "dead code"-Analyse

### 7. **Keine Rollback-Strategie**

Was passiert, wenn `/prp-ralph` nach 15 Iterationen immer noch nicht grün ist?
- Plan sagt "stop" → aber WIE rollback?
- Kein Checkpoint-System

### 8. **Human-in-the-Loop fehlt für kritische Entscheidungen**

Ralph Loop ist "fire and forget":
- Keine Genehmigung für Breaking Changes
- Keine Warnung bei riskanten Operationen

**Risk**: Agent könnte DB-Schema-Migration autonom durchführen.

### 9. **MoSCoW-Priorisierung ohne Business-Metrics**

PRDs haben MoSCoW (Must/Should/Could/Won't), aber:
- Keine ROI-Kalkulation
- Keine Cost-of-Delay
- Keine Stakeholder-Priorisierung

**Konsequenz**: Technische Sicht dominiert Business-Sicht.

### 10. **Keine Real-Time Collaboration**

Alle Artefakte sind File-basiert:
- Keine Live-Editing wie Google Docs
- Merge Conflicts bei parallelen Phases
- Keine Notifications bei Status-Changes

---

## Key Features

### Commands (12)

| Kategorie | Command | Funktion |
|-----------|---------|----------|
| **Core Workflow** | `/prp-prd` | Interactive PRD generator (Q&A → Hypothesis → Evidence → Phases) |
|  | `/prp-plan` | Codebase-first Plan (Explore → Research → Design → Plan) |
|  | `/prp-implement` | Validation-Loop Executor (Detect → Load → Execute → Validate → Report) |
|  | `/prp-ralph` | Autonomous Loop (bis alle Validations pass) |
| **Issue Workflow** | `/prp-issue-investigate` | GitHub Issue → Analysis → Plan (+ Post to GH) |
|  | `/prp-issue-fix` | Execute Investigation Artifact |
|  | `/prp-debug` | 5 Whys Root Cause Analysis |
| **Git & Review** | `/prp-commit` | Smart Commit (natural language file targeting) |
|  | `/prp-pr` | PR Creation (Template-aware) |
|  | `/prp-review` | Single-Agent PR Review |
|  | `/prp-review-agents` | Multi-Agent PR Review |
|  | `/prp-ralph-cancel` | Stop autonomous loop |

### Agents (11)

| Typ | Agent | Fokus |
|-----|-------|-------|
| **Codebase Analysis** | `codebase-analyst` | HOW code works (Implementation Details, Data Flow, file:line refs) |
|  | `codebase-explorer` | WHERE code lives + HOW implemented (File Locations + Patterns) |
|  | `web-researcher` | Docs, APIs, Best Practices (external) |
| **Review Workflow** | `code-reviewer` | Guidelines, Bugs, Type/Module checks |
|  | `comment-analyzer` | Comment accuracy, maintainability |
|  | `pr-test-analyzer` | Test coverage quality, gaps |
|  | `silent-failure-hunter` | Error handling, silent failures |
|  | `type-design-analyzer` | Type encapsulation, invariants |
|  | `code-simplifier` | Clarity, maintainability |
|  | `docs-impact-agent` | Stale docs update |

### Artifact Structure

```
.claude/PRPs/
├── prds/              # PRD documents
├── plans/             # Implementation plans
│   └── completed/     # Archived completed plans
├── reports/           # Implementation reports
├── issues/            # Issue investigations
│   └── completed/     # Archived completed investigations
└── reviews/           # PR review reports
```

### Installation

3 Wege:
1. **From GitHub**: `/plugin marketplace add Wirasm/PRPs-agentic-eng`
2. **Local Dev**: Marketplace add + install via absolute path
3. **Team Automatic**: `.claude/settings.json` mit `extraKnownMarketplaces` + `enabledPlugins`

---

## Was autonomous-stan davon fehlt

### 1. **Strukturierte Codebase-Intelligence-Gathering**

**PRPs**: Explore Agent wird **zwingend** VOR Research aufgerufen → findet `file:line`-Patterns
**autonomous-stan**: Graphiti-Search + manuelle Datei-Reads → kein systematisches Pattern-Extraction

**Gap**: Kein "Mirror Pattern from X:Y" Workflow.

### 2. **Validation Commands als First-Class Concept**

**PRPs**: Jeder Plan-Task hat `VALIDATE: npm test` → Agent weiß genau, wie Erfolg aussieht
**autonomous-stan**: Skills haben teilweise Tests, aber kein Framework-weites "Validation Level 1-6"

**Gap**: Kein standardisiertes Self-Verification Protocol.

### 3. **PRD mit Implementation Phases + Dependencies**

**PRPs**: PRDs haben Tabelle mit Status/Parallel/Depends → große Features werden phasiert
**autonomous-stan**: PRD-Template existiert (`templates/prd.md.template`), aber **keine Phase-Dependency-Tracking**

**Gap**: Keine systematische Zerlegung großer Features in parallelisierbare Phasen.

### 4. **Autonomous Loop mit Max-Iterations**

**PRPs**: `/prp-ralph --max-iterations 20` → Agent iteriert bis grün ODER Limit
**autonomous-stan**: Keine `/ralph`-Equivalent → Agent wartet auf User-Input

**Gap**: Kein "Fire-and-Forget" Mode für längere Implementation-Loops.

### 5. **Root Cause Analysis mit 5 Whys**

**PRPs**: `/prp-debug` erzwingt Evidence-Chain (jedes "Because" braucht `file:line`)
**autonomous-stan**: Debugging-Skills vorhanden, aber kein formalisiertes 5-Whys-Template

**Gap**: Kein strukturiertes RCA-Protokoll.

### 6. **Multi-Agent Review Workflow**

**PRPs**: `/prp-review-agents` orchestriert 7 spezialisierte Review-Agenten
**autonomous-stan**: Multi-Agent-Skill (`skills/multi-agent/SKILL.md`), aber **kein Code-Review-Orchestrator**

**Gap**: Keine PR-Review-Automatisierung mit spezialisierten Agenten.

### 7. **Git-Flow-Commands**

**PRPs**: `/prp-commit` (natural language), `/prp-pr` (Template-aware)
**autonomous-stan**: Git-Workflow-Skill (`skills/git-workflow/SKILL.md`), aber **keine Shell-Commands dafür**

**Gap**: Git-Befehle müssen manuell gemacht werden, kein User-Convenience-Layer.

### 8. **Issue-Investigation → Implementation Pipeline**

**PRPs**: `/prp-issue-investigate 123` → Plan → Post zu GitHub → `/prp-issue-fix 123`
**autonomous-stan**: GitHub Issues können gelesen werden, aber **kein automatisches Investigation→Implementation Flow**

**Gap**: Keine End-to-End GitHub Issue Automation.

### 9. **Plan-Archivierung + Status-Tracking**

**PRPs**: Plans → `completed/` nach Fertigstellung, PRD-Status wird automatisch upgedatet
**autonomous-stan**: BusinessMap-Tracking, aber **kein File-basiertes Plan-Lifecycle-Management**

**Gap**: Keine automatische Archivierung abgeschlossener Implementierungspläne.

### 10. **Patterns to Mirror als Standard-Section**

**PRPs**: Jeder Plan hat "Patterns to Mirror" mit SOURCE-Code
**autonomous-stan**: Templates existieren, aber **kein "Copy from X:Y"-Convention in Plan-Templates**

**Gap**: Pattern-Konsistenz ist manuelle Aufgabe.

---

## Was autonomous-stan schon hat (Templates, PRD)

### ✅ PRD-Template

**Datei**: `templates/prd.md.template`

**Ähnlichkeiten mit PRPs**:
- Hypothesis-driven ("We believe that X will achieve Y")
- Jobs to Be Done (JTBD)
- Evidence-Section
- MoSCoW-Priorisierung
- Success Metrics mit Baseline/Target
- Open Questions + Decisions Log

**Unterschiede zu PRPs**:
- **KEINE** Implementation Phases Tabelle mit Dependencies/Parallelismus
- Criteria-Checklist (YAML frontmatter) — PRPs haben das nicht
- Mehr "Enterprise": Feasibility-Rating (1-5), Traceability-Links

**Fazit**: autonomous-stan PRD ist **sogar umfassender** als PRP-PRD in manchen Aspekten (Criteria, Feasibility), aber **fehlt Phase-Dependency-Tracking**.

### ✅ Plan-Template

**Datei**: `templates/plan.md.template`

**Hat**:
- Implementation Steps
- Acceptance Criteria
- Testing Strategy
- Dependencies

**Fehlt gegenüber PRPs**:
- Mandatory Reading (file:line Priority-Liste)
- Patterns to Mirror (SOURCE-Code-Snippets)
- 6-Level Validation Commands
- Explicit GOTCHA-Warnings pro Task

**Fazit**: Grundstruktur da, aber **weniger kontext-reich** als PRP-Plans.

### ✅ Git-Workflow-Skill

**Datei**: `skills/git-workflow/SKILL.md`

**Hat**: Commit-Messages (SemVer), Branch-Naming, PR-Beschreibungen

**Fehlt**: Keine Shell-Commands wie `/prp-commit` — User muss manuell Git nutzen.

### ✅ Multi-Agent-Skill

**Datei**: `skills/multi-agent/SKILL.md`

**Hat**: Sub-Agent-Spawning, Session-Communication

**Fehlt**: Kein Code-Review-Orchestrator wie `/prp-review-agents`.

### ✅ Graphiti (Persistent Knowledge)

**PRPs haben das nicht**: Graphiti ist autonomous-stan's Langzeitgedächtnis
- Learnings, Entscheidungen, Preferences persistent speichern
- Search vor Aufgaben ("Graphiti Gate")

**Vorteil**: autonomous-stan hat **besseres Organisational Memory** als PRPs.

### ✅ Skills-System

**autonomous-stan hat ~25 Skills** (Firecrawl, Mermaid, PDF, Summarize, TDD, Security Review, etc.)

**PRPs fokussieren nur**: Code-Workflow (PRD → Plan → Implement → Review)

**Vorteil**: autonomous-stan ist **General-Purpose Agent**, PRPs ist **Code-Delivery-Framework**.

---

## Vergleich mit OpenClaw Skills

### OpenClaw Skills (allgemein)

OpenClaw Skills sind **Markdown-Files mit YAML Frontmatter** (`SKILL.md`), die:
- Tools/APIs beschreiben
- Workflows definieren
- Best Practices festhalten
- Von Agents geladen + befolgt werden

**Ähnlich zu PRP Agents**: `.md`-Files mit Frontmatter (`name`, `description`, `model`, `color`)

**Unterschied**:
- OpenClaw Skills sind **statische Dokumentation** (Agent liest sie)
- PRP Agents sind **ausführbare Sub-Agents** (Agent spawned sie via Task tool)

### autonomous-stan Skills vs. PRPs

| Aspekt | autonomous-stan Skills | PRPs |
|--------|------------------------|------|
| **Scope** | General-Purpose (Firecrawl, PDF, Summarize, Web-Dev, TDD, Security) | Code-Delivery-fokussiert (PRD, Plan, Implement, Review) |
| **Workflow** | Skill-per-Domain | End-to-End Pipeline (PRD → Code) |
| **Agent-Architektur** | Main Agent + Sub-Agents (multi-agent/SKILL.md) | Specialized Review-Agents (7 für Code-Review) |
| **Memory** | Graphiti (persistent Knowledge Graph) | File-based Artifacts (.claude/PRPs/) |
| **Git-Integration** | Manual (Git-Workflow-Skill) | Automated (/prp-commit, /prp-pr) |
| **Validation** | TDD-Workflow-Skill (test-first) | 6-Level Validation Protocol (Static → Unit → Full → DB → Browser → Manual) |
| **Context-Gathering** | Graphiti-Search + Manual Reads | Explore Agent (systematisch, file:line refs) |
| **PRD** | Template mit Criteria | Interactive Generator (Q&A → Evidence → Phases) |
| **Plan** | Template mit Steps | Codebase-first (Mirror Patterns) |
| **Review** | Visual-Lint-Skill (Design) | Multi-Agent-Review (7 spezialisierte Agenten) |

### Was autonomous-stan Skills haben, PRPs nicht:

1. **Domain-Expertise außerhalb Code**: Firecrawl (Web-Scraping), PDF-Handler, Summarize, Context7 (Live-Docs)
2. **Visual/Design**: Mermaid-Diagrams (PRPs nutzen ASCII), Visual-Lint (Accessibility)
3. **Organizational Memory**: Graphiti (PRPs haben keine persistente KB)
4. **Multi-Channel**: Discord, Message-Tool (PRPs nur GitHub)
5. **Business-Integration**: BusinessMap (Kanban-Tracking), Morgen (Kalender), n8n (Automation)
6. **Security**: Security-Review-Skill (OWASP, Auth, Secrets)

### Was PRPs haben, autonomous-stan Skills nicht:

1. **Atomic Commands für Code-Delivery**: `/prp-prd`, `/prp-plan`, `/prp-implement`, `/prp-ralph`
2. **Systematic Pattern Mirroring**: Explore Agent → `file:line` → Mirror-Section in Plan
3. **6-Level Validation Framework**: Standardisiertes Protocol
4. **Autonomous Loop**: `/prp-ralph` (fire-and-forget)
5. **Phase-Dependency-Tracking**: PRD mit Parallelismus-Info
6. **Multi-Agent Code-Review**: 7 spezialisierte Review-Agents

---

## Konkrete Übernahme-Empfehlungen

### 🟢 HOCH PRIORITÄT (Quick Wins)

#### 1. **Validation Protocol als Skill**

**Was**: 6-Level Validation Framework von PRPs adoptieren

**Wie**:
- Neuer Skill: `skills/validation-protocol/SKILL.md`
- Definiert Level 1-6 (Static → Unit → Full → DB → Browser → Manual)
- Jeder Plan/Task muss Validation-Level angeben
- Agent checkt nach jedem Task: "Validation passed?"

**Aufwand**: 1-2h

**Impact**: ✅ Self-verifying implementation, weniger menschliches Debugging

#### 2. **Patterns to Mirror in Plan-Template**

**Was**: Plan-Template um "Patterns to Mirror"-Section erweitern

**Wie**:
- In `templates/plan.md.template` neue Section:
  ```markdown
  ## Patterns to Mirror
  
  **NAMING_CONVENTION:**
  - SOURCE: `file.ts:10-15`
  - PATTERN: `{actual code snippet}`
  
  **ERROR_HANDLING:**
  - SOURCE: `file.ts:50-67`
  - PATTERN: `{actual code snippet}`
  ```
- Agents müssen VOR Implementation diese Section füllen (via File-Reads)

**Aufwand**: 30min

**Impact**: ✅ Code-Konsistenz, Agent "erfindet" keine neuen Patterns

#### 3. **Codebase-Explorer als Sub-Agent**

**Was**: Formalisierter "Explore Agent" für Pattern Discovery

**Wie**:
- Neuer Skill: `skills/codebase-explorer/SKILL.md`
- Agent-Prompt: "Find WHERE + HOW" (copy from PRP codebase-explorer.md)
- Stan spawned ihn via `multi-agent/SKILL.md` bei Plan-Erstellung
- Output: Tabelle mit File-Locations + Code-Patterns

**Aufwand**: 2-3h (Agent-Prompt schreiben + Multi-Agent-Integration)

**Impact**: ✅ Systematisches Pattern-Extraction, bessere Pläne

#### 4. **Issue-Investigation → Implementation Pipeline**

**Was**: GitHub Issue → Analysis → Plan → Execution Flow

**Wie**:
- Neuer Skill: `skills/github-issue-workflow/SKILL.md`
- Commands (via Stan's Channel):
  - `!investigate-issue <number>` → erstellt Plan, postet zu GitHub
  - `!fix-issue <number>` → liest Investigation-Artifact, führt aus
- Integration mit Discord (Issue-Nummer → Investigation)

**Aufwand**: 3-4h

**Impact**: ✅ End-to-End GitHub Issue Automation

#### 5. **Plan-Archivierung + Status-Tracking**

**Was**: Abgeschlossene Pläne automatisch archivieren

**Wie**:
- Ordner: `docs/plans/` und `docs/plans/completed/`
- Nach Implementation: Plan → `completed/` + PRD-Status-Update
- Heartbeat-Task: "Check for completed plans → move to archive"

**Aufwand**: 1h

**Impact**: ✅ Saubere Dateistruktur, bessere Traceability

---

### 🟡 MEDIUM PRIORITÄT (Strategisch wertvoll)

#### 6. **PRD Implementation Phases Tracking**

**Was**: PRD-Template um Phases-Tabelle erweitern

**Wie**:
- In `templates/prd.md.template` neue Section:
  ```markdown
  ## Implementation Phases
  
  | # | Phase | Description | Status | Parallel | Depends | Plan |
  |---|-------|-------------|--------|----------|---------|------|
  | 1 | Auth  | User login  | pending | - | - | - |
  | 2 | API   | Endpoints   | pending | - | 1 | - |
  ```
- Stan updated Status + verlinkt Pläne automatisch

**Aufwand**: 2h (Template + Update-Logic)

**Impact**: ✅ Große Features werden planbar + parallelisierbar

#### 7. **Root Cause Analysis mit 5 Whys**

**Was**: `/prp-debug`-Equivalent für autonomous-stan

**Wie**:
- Neuer Skill: `skills/root-cause-analysis/SKILL.md`
- Workflow: 5 Whys + Evidence-Chain (`file:line` für jedes "Because")
- Output: `.claude/debug/rca-{issue}.md`

**Aufwand**: 2-3h

**Impact**: ✅ Findet echte Ursachen statt Symptome

#### 8. **Autonomous Loop (Ralph-Equivalent)**

**Was**: "Fire-and-Forget" Implementation Mode

**Wie**:
- Neuer Sub-Agent: `skills/autonomous-executor/SKILL.md`
- Stan spawned ihn für langwierige Implementierungen
- Loop: Implement → Validate → Fix → Re-Validate (max-iterations)
- Progress-Updates via Discord

**Aufwand**: 4-5h (Sub-Agent + Progress-Tracking)

**Impact**: ✅ Stan kann nachts Features implementieren

#### 9. **Git-Commands für User-Convenience**

**Was**: Shell-Commands wie `/prp-commit`, `/prp-pr` für Discord

**Wie**:
- Discord-Bot-Commands: `!commit <target>`, `!pr <base-branch>`
- Stan führt Git-Befehle aus + postet Ergebnis
- Template-aware PR-Creation (liest `.github/PULL_REQUEST_TEMPLATE.md`)

**Aufwand**: 3h

**Impact**: ✅ Mathias muss weniger manuell Git machen

---

### 🔴 NIEDRIG PRIORITÄT (Nice-to-Have)

#### 10. **Multi-Agent Code-Review**

**Was**: 7 spezialisierte Review-Agenten wie PRPs

**Wie**:
- Sub-Agents: `comment-analyzer`, `silent-failure-hunter`, `type-design-analyzer`, etc.
- Stan orchestriert sie via `multi-agent/SKILL.md`
- Output: Review-Report mit Findings pro Agent

**Aufwand**: 8-10h (7 Agent-Prompts schreiben + Orchestrator)

**Impact**: 🔶 Comprehensive Reviews, aber ROI unk