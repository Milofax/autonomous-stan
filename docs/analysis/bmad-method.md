# BMAD-METHOD — Framework-Analyse

**Analysiert:** 2026-02-16  
**Quelle:** `/vendor/BMAD-METHOD/`  
**Version:** v6 (Alpha)

---

## Kern-Idee (1 Satz)

BMAD ist ein **prompt-getriebenes Workflow-Framework** mit 10 spezialisierten Agent-Personas (keine echten autonomen Agents!), 34+ geführten Workflows über 4 Phasen hinweg, und einem scale-adaptiven System, das die Planungstiefe automatisch an die Projektkomplexität anpasst — alles als **lokale Markdown/YAML-Dateien** verpackt, die vom User per Slash-Command in seinem AI-Chat geladen werden.

---

## Architektur

### Dateistruktur

```
BMAD-METHOD/
├── src/
│   ├── core/                          # Kern-System
│   │   ├── agents/
│   │   │   └── bmad-master.agent.yaml # Master-Agent (Koordinator)
│   │   └── workflows/                 # Domain-agnostische Workflows
│   │       ├── brainstorming/         # 60+ Kreativtechniken
│   │       └── party-mode/            # Multi-Agent-Dialog-Simulation
│   ├── bmm/                           # BMad Method Module (Haupt-Content)
│   │   ├── agents/                    # 9 Agents (PM, Dev, Architect, etc.)
│   │   ├── workflows/                 # 34+ Workflows in 4 Phasen
│   │   │   ├── 1-analysis/           # Phase 1: Exploration
│   │   │   ├── 2-plan-workflows/     # Phase 2: Requirements
│   │   │   ├── 3-solutioning/        # Phase 3: Architecture
│   │   │   ├── 4-implementation/     # Phase 4: Building
│   │   │   └── bmad-quick-flow/      # Schnellspur (Bug Fixes)
│   │   └── testarch/                 # Test-Architekt Sub-System
│   └── utility/                       # Agent-Komponenten (wiederverwendbar)
├── docs/                              # 93 MD-Dateien Dokumentation
├── tools/
│   └── cli/                          # npx bmad-method@alpha install
└── website/                          # Statische Doku-Website
```

### Scale-Adaptive Levels (0-4)

| Level | Planning | Wann |
|-------|----------|------|
| **0** | Keine | Trivial Fix |
| **1** | Minimal | Bug Fix |
| **2** | Standard | Feature |
| **3** | Detailliert | Komplexes Feature |
| **4** | Comprehensive | Enterprise/Compliance |

**Wichtig:** Das ist **keine Laufzeit-Intelligenz**. Der User (oder Agent) wählt manuell den Track/Level basierend auf Projektgröße. Es gibt keine Auto-Erkennung.

### Drei Tracks

| Track | Zeit bis Story-Coding | Phases | Zielgruppe |
|-------|----------------------|--------|------------|
| **Quick Flow** | 5-30 min | 2 (tech-spec) → 4 (implement) | Bug Fixes, kleine Features |
| **BMad Method** | 30 min - 2h | 1 → 2 (PRD) → 3 (arch) → 4 | Produkte, Plattformen |
| **Enterprise** | 1-3h | 1 → 2 → 3+ → 4 | Compliance-lastige Systeme |

### Agent-System: **Personas, keine echten Agents!**

**BMAD hat 10 Agent-Definitionen**, aber das sind **YAML-basierte Personas** (Role-Prompts), die der User manuell per Slash-Command lädt.

**Core Agents:**
1. **BMad Master** 🧙 — Workflow-Orchestrator, Aufgaben-Executor
2. **Mary (Analyst)** 📊 — Business Analyst, Research
3. **John (PM)** 📋 — Product Manager, PRD-Erstellung
4. **Winston (Architect)** 🏗️ — System Architect, ADRs
5. **Sally (UX Designer)** 🎨 — UX/UI-Spezialist
6. **Bob (Scrum Master)** 🏃 — Story-Vorbereitung, Sprint-Planung
7. **Amelia (Developer)** 💻 — Code-Implementierung
8. **Murat (Test Architect)** 🧪 — Test-Strategie, CI/CD
9. **Tech Writer** 📚 — Dokumentation
10. **Barry (Quick Flow Solo Dev)** 🚀 — All-in-One für Quick Flow

**Jeder Agent hat:**
- **Persona** (Role, Identity, Communication Style, Principles)
- **Menu** (Slash-Commands mit Trigger + Workflow-Path)
- **Critical Actions** (Verhaltensregeln)

**Wie es funktioniert:**
1. User startet Chat: `/bmad-help` → Master lädt sich selbst
2. Master empfiehlt Agent: "Für PRD → lade *PM*"
3. User tippt: `*create-prd` → John (PM) übernimmt
4. Workflow lädt sich in Context → PM führt User durch PRD-Erstellung
5. Am Ende: Master empfiehlt nächsten Schritt

**Es gibt KEINE persistent laufenden Agents**, keine Auto-Koordination, keine Hintergrund-Tasks. Alles manuell getriggert.

### Party Mode: Pseudo-Multi-Agent

**Party Mode** (`*party-mode`) ist eine **Simulation** eines Multi-Agent-Dialogs:
- Lädt alle Agents aus `agent-manifest.csv` in EINEN Chat
- Master orchestriert: Wählt 2-3 relevante Agents pro Message
- Agents "antworten" in Character (aber es ist immer das gleiche LLM)
- Nützlich für: Retrospectives, Brainstorming, Entscheidungen

**Kein echtes Multi-Agent-System**, sondern **theater play**.

---

## Einzigartige Stärken

### 1. **Geführte Discovery statt Template-Filling**

Workflows sind **interaktive Interviews**, nicht Blanko-Formulare:
- PM fragt "WHY?" wie ein Detective
- Architect diskutiert Trade-Offs mit User
- PRD entsteht aus Conversation, nicht aus Copy-Paste

**Beispiel:** `create-prd` Workflow:
```
PM: "Was ist das Kernproblem?"
User: "Checkout-Prozess dauert zu lang"
PM: "Was heißt zu lang? Wie viele Schritte?"
User: "5 Schritte, User brechen ab"
PM: "Was ist die Ziel-Duration?"
[...10 weitere Fragen...]
→ PRD mit 15 FRs + 8 NFRs
```

### 2. **Architecture Decision Records (ADRs)**

Jede technische Entscheidung wird dokumentiert mit:
- **Context** (Warum brauchen wir das?)
- **Options** (REST vs GraphQL vs gRPC)
- **Decision** (GraphQL)
- **Rationale** (PRD braucht flexible Queries)
- **Consequences** (Caching-Komplexität, N+1-Risiko)

**Das verhindert Agent-Konflikte bei Multi-Epic-Projekten.**

### 3. **Phase 3: Solutioning (The Missing Middle)**

Ralph und autonomous-stan springen von **Planning** direkt zu **Implementation**.

BMAD fügt **Solutioning** dazwischen ein:
- Übersetzt "Was" (PRD) in "Wie" (Architektur)
- Erstellt ADRs für kritische Tech-Decisions
- Bricht PRD in Epics + Stories runter **NACHDEM** Architektur steht
- Verhindert: API-Style-Konflikte, DB-Design-Chaos, State-Management-Inkonsistenz

**Beispiel ohne Solutioning:**
```
Agent 1 implementiert Epic 1 mit REST
Agent 2 implementiert Epic 2 mit GraphQL
→ Integration Nightmare
```

**Mit Solutioning:**
```
Architecture Workflow entscheidet: "GraphQL für alle APIs"
Alle Agents folgen ADR-001
→ Konsistente Implementierung
```

### 4. **60+ Brainstorming-Techniken als Skill-Bibliothek**

`brainstorming` Workflow hat **on-demand-loading** von Techniken:
- **Collaborative** (Team-Dynamik)
- **Creative** (Paradigm Shifts)
- **Deep** (Root Cause)
- **Theatrical** (Playful Perspectives)
- **Biomimetic** (Nature-inspired)
- **Quantum** (Innovation)

**Progressive Flow:** User wählt Technik-Sequenz oder lässt AI empfehlen.

### 5. **Test-First mit Test Architect Agent**

**Murat (TEA)** hat **eigenes Sub-System** mit Knowledge Base:
- Konsultiert `tea-index.csv` für relevante Test-Fragmente
- Lädt nur benötigte Docs aus `testarch/knowledge/`
- Cross-checkt mit aktueller Playwright/Cypress-Doku
- Workflows: `test-framework`, `atdd`, `automate`, `test-design`, `trace`, `nfr-assess`, `ci`

**ATDD Workflow:** Tests BEVOR Code (TDD auf Story-Ebene).

### 6. **Scale-Adaptive PRD-Struktur**

PRD-Template passt sich an Projektkomplexität an:

| Scale | Seiten | Focus |
|-------|--------|-------|
| Light | 10-15 | Fokussierte FRs/NFRs |
| Standard | 20-30 | Comprehensive FRs/NFRs |
| Comprehensive | 30-50+ | Stakeholder-Analyse, Phasen |

### 7. **Brownfield-First Thinking**

`document-project` Workflow:
- Analysiert existierende Codebases
- Erkennt Tech-Stack, Patterns, Test-Frameworks
- Fragt: "Soll ich diese Konventionen folgen?"
- Generiert Context für alle nachfolgenden Workflows

**Das fehlt komplett in Ralph und autonomous-stan.**

### 8. **Implementation Readiness Gate**

**Gate Check BEVOR Phase 4:**
- Architect validiert: PRD + UX + Architecture + Epics/Stories aligned?
- Verhindert: Mid-Sprint-Überraschungen

---

## Schwächen/Limitierungen (EHRLICH!)

### 1. **Keine echten autonomen Agents — nur Personas**

**BMAD ist kein Multi-Agent-System.** Es sind 10 YAML-Dateien mit Role-Prompts.
- User muss jeden Agent manuell laden
- Keine Agent-zu-Agent-Kommunikation (außer simuliertem Party Mode)
- Keine asynchronen Tasks, keine Hintergrund-Arbeit
- **Es ist ein Prompt-Library mit Extra Steps.**

**Vergleich:**
- **BMAD:** User tippt `*create-prd` → PM-Persona lädt sich → User chattet mit PM → PRD entsteht
- **OpenClaw (autonomous-stan):** 12 echte Agents laufen persistent, kommunizieren via MCP, haben eigene Channels, können parallel arbeiten

**BMAD ist näher an "Copilot mit Rollen-Switching" als an echtem Multi-Agent.**

### 2. **Workflows sind Copy-Paste-Marathons**

Workflows sind **gigantische Markdown-Dateien** (manche >1000 Zeilen), die komplett in den Context geladen werden.

**Beispiel:** `run-automate.md` ist **17.835 Zeilen**. Das ist größer als manche Codebases.

**Probleme:**
- Context Pollution (LLM muss durch Wall of Text parsen)
- Keine echte Modularität
- Schwer wartbar
- User kann nicht "Schritt 3 von 12" direkt anspringen

**OpenClaw Vorteil:** Skills sind kleine, fokussierte Dateien mit klaren Interfaces.

### 3. **Keine echte Scale-Adaptive Automation**

"Scale-Adaptive" klingt nach ML/Intelligence, ist aber **User-Auswahl**:
- User muss Track wählen (Quick Flow vs BMad Method)
- User muss Level wählen (0-4)
- Keine automatische Erkennung von Projektkomplexität

**Was fehlt:**
- "Erkenne, dass dieses Projekt 5 Epics hat → Auto-Route zu BMad Method"
- "Erkenne, dass User 3 Files ändert → Quick Flow"

### 4. **Party Mode ist Theater, nicht echte Kollaboration**

**Party Mode** lädt alle Agents in einen Chat, aber:
- Es ist IMMER das gleiche LLM
- Master wählt manuell 2-3 "Agents" zum "Antworten"
- Keine parallele Arbeit
- Kein echter Konflikt-Resolution-Mechanismus

**Es ist Role-Play, keine echte Multi-Agent-Koordination.**

**OpenClaw Vorteil:** 12 echte Agents mit eigenen Sessions, die parallel laufen und koordiniert werden.

### 5. **Keine Memory über Workflows hinweg**

Jeder Workflow startet mit **"Start a fresh chat"**.
- Keine Learnings aus vorherigen Sprints
- Keine "Hot Patterns" aus letztem PRD
- User muss Context manuell weitergeben

**autonomous-stan Vorteil:** Tiered Learnings (recent/hot/archive) + Graphiti für Knowledge Retention.

### 6. **Keine Integration mit echten Tools**

BMAD hat:
- ❌ Keine Kalender-Integration
- ❌ Keine GitHub Issue-Creation
- ❌ Keine Discord-Notifications
- ❌ Keine n8n-Automationen
- ❌ Keine 1Password-Secrets

**Es ist ein reines Prompt-System.** Outputs sind Markdown-Dateien, die User manuell weiterverarbeiten muss.

### 7. **Installation ist NPM-Tooling-Overhead**

```bash
npx bmad-method@alpha install
```

Das kopiert Dateien in `_bmad/` Folder. Das war's. Kein Runtime, keine Services.

**Warum NPM?** Könnte auch Git Submodule sein. Es gibt keine echte "Installation" — nur Datei-Kopie.

### 8. **Keine Visual Verification (Ralph hat das!)**

Ralph verlangt für JEDE UI-Story: `[ ] Verify in browser using dev-browser skill`

**BMAD hat das nicht.** Dev-Workflow hat keine Browser-Automation-Checks.

### 9. **Story Size Guidance fehlt (Ralph hat das!)**

Ralph: **"Story muss in EINEM Iteration completable sein"**

BMAD: Keine explizite Regel. Stories können zu groß werden → Context Overflow.

### 10. **Solutioning ist Over-Engineering für Small Projects**

Für **Simple Features** (1-3 Stories) ist Phase 3 (Solutioning) **Zeitverschwendung**:
- ADRs schreiben für "Füge Login-Button hinzu"? Overkill.
- Quick Flow existiert, aber User muss wissen, wann er es nutzen soll

**BMAD pendelt zwischen zwei Extremen:**
- Quick Flow: Zu lean (keine Architektur)
- BMad Method: Zu umfangreich (ADRs für alles)

**Fehlt:** Mittlerer Track für "Standard Feature mit 5-10 Stories".

---

## Key Features

| Feature | Beschreibung |
|---------|--------------|
| **4 Phasen** | Analysis → Planning → Solutioning → Implementation |
| **34+ Workflows** | Von Brainstorming bis CI-Setup |
| **10 Agent-Personas** | PM, Architect, Dev, QA, UX, Analyst, Scrum Master, etc. |
| **ADRs** | Architecture Decision Records für Tech-Decisions |
| **Scale-Adaptive** | Planungstiefe passt sich Komplexität an (Level 0-4) |
| **3 Tracks** | Quick Flow (5 min), BMad Method (15 min), Enterprise (30 min) |
| **Party Mode** | Multi-Agent-Dialog-Simulation |
| **60+ Brainstorming-Techniken** | Strukturierte Kreativitäts-Sessions |
| **Test Architect** | Eigenes Sub-System für Test-Strategie |
| **Brownfield Support** | `document-project` Workflow für existierende Codebases |
| **Implementation Readiness Gate** | Quality Gate vor Phase 4 |
| **Retrospective Workflow** | Continuous Improvement |

---

## Was autonomous-stan davon fehlt

### HIGH Priority (Übernehmen!)

1. **Phase 3: Solutioning / Architecture Workflow**
   - ADRs für Tech-Decisions
   - FR/NFR → Technical Approach Mapping
   - Standards & Conventions Document
   - **Warum:** Verhindert Agent-Konflikte bei Multi-Epic-Projekten

2. **Implementation Readiness Gate**
   - Gate Check BEVOR CREATE-Phase
   - Validiert: PRD + UX + Arch + Stories aligned?
   - **Warum:** Verhindert Mid-Sprint-Überraschungen

3. **Brownfield Analysis Workflow**
   - Codebase-Analyse für existierende Projekte
   - Erkennt Stack, Patterns, Test-Frameworks
   - **Warum:** autonomous-stan hat keine "Document Existing Project"-Logik

4. **Test Architect Agent + Test-First Workflows**
   - ATDD (Tests BEVOR Code)
   - Test Framework Setup
   - NFR Assessment
   - **Warum:** autonomous-stan hat keine Test-Strategie-Workflows

### MEDIUM Priority (Nice to Have)

5. **Scale-Adaptive Levels für Projekte**
   - Zusätzlich zu `skill_level` (User-Präferenz)
   - `project_complexity: 0-4` (Auto-Routing)
   - **Warum:** Verhindert Over-Engineering für simple Features

6. **Party Mode für Retrospectives**
   - Multi-Agent-Dialog für Sprint-Reviews
   - **Warum:** autonomous-stan hat `/stan think retrospective`, aber kein Multi-Agent-Format

7. **Brainstorming-Techniken-Bibliothek**
   - autonomous-stan hat 21 Techniques
   - BMAD hat 60+ mit Progressive Flow
   - **Warum:** Mehr Techniken = bessere Ideation

### LOW Priority (Nett, aber nicht kritisch)

8. **Slash-Command-Menüs pro Agent**
   - Jeder Agent hat eigenes Menu (z.B. `*create-prd`)
   - **Warum:** autonomous-stan nutzt `/stan` CLI — braucht kein Menü-System

9. **Web Bundles / Distribution-System**
   - BMAD kann Workflows als NPM-Packages verteilen
   - **Warum:** autonomous-stan ist Git-basiert — braucht kein NPM

---

## Was autonomous-stan schon hat

| Feature | STAN | BMAD | Unterschied |
|---------|------|------|-------------|
| **Phasen-System** | DEFINE → PLAN → CREATE | Analysis → Planning → Solutioning → Implementation | BMAD hat extra "Solutioning"-Phase |
| **Templates** | 3 (PRD, Arch-Doc, Post-Mortem) | 50+ | BMAD hat mehr Variety |
| **Criteria Packs** | 24+ | N/A (implizit in Workflows) | STAN hat modulare Criteria-System |
| **Tiered Learnings** | recent/hot/archive mit Heat Scoring | ❌ Keine Session-Memory | STAN überlegen |
| **Quality Gates** | stan-gate Hook | Implementation Readiness Gate | Ähnlich, aber andere Trigger-Points |
| **Thinking Techniques** | 21 | 60+ (in Brainstorming) | BMAD hat mehr |
| **Agent-System** | 12 echte Agents (MCP, Sessions) | 10 Personas (YAML-Prompts) | STAN hat echtes Multi-Agent |
| **Tool-Integration** | 1Password, GitHub, Discord, n8n, Morgen | ❌ Keine | STAN weit überlegen |
| **Visual Verification** | ❌ Fehlt | ❌ Fehlt | Ralph hat das, beide nicht |
| **Story Size Rule** | ❌ Fehlt | ❌ Fehlt | Ralph hat das, beide nicht |
| **Brownfield Support** | ❌ Fehlt | ✓ `document-project` | BMAD überlegen |
| **Test-First** | ❌ Fehlt | ✓ ATDD Workflow | BMAD überlegen |
| **ADRs** | ❌ Fehlt | ✓ Architecture Workflow | BMAD überlegen |

---

## Vergleich mit OpenClaw Multi-Agent (12 echte Agents vs 21 Personas)

### OpenClaw (autonomous-stan) — 12 Echte Agents

**Architektur:**
- 12 **persistent laufende Agents** (Stan, Patrick, Tony, Klaus, Andrew, Dave, etc.)
- Jeder Agent: Eigene Session, eigener Channel, eigener Memory
- **Agent-zu-Agent-Kommunikation:** `sessions_send(sessionKey:"agent:patrick:main")`
- **Parallele Arbeit:** Andrew analysiert Finanzen WÄHREND Stan Code schreibt
- **MCP-Tools:** calendar, github, discord, n8n, 1password, morgen
- **Graphiti Knowledge Graph:** Persistente Learnings über Sessions hinweg
- **Heartbeats:** Periodische Background-Tasks

**Koordination:**
- Main Agent (Stan) orchestriert via `sessions_send`
- Agents antworten in eigene Channels (z.B. `#andrew-finanzen`)
- User sieht Multi-Agent-Arbeit in Discord
- Sub-Agents für temporäre Tasks (z.B. Research)

**Beispiel:**
```
User: "Analysiere Projekt X und erstelle PRD"
Stan: sessions_send(patrick:main, "Research market for X")
      sessions_send(klaus:main, "Draft PRD outline")
[Patrick arbeitet parallel in #patrick-research]
[Klaus arbeitet parallel in #klaus-dokumente]
→ Nach 10 min: Beide senden Ergebnisse zurück
Stan: Konsolidiert → PRD fertig
```

### BMAD — 10 Personas (keine echten Agents)

**Architektur:**
- 10 **YAML-Dateien** mit Role-Prompts
- **KEINE persistent laufenden Agents**
- User lädt Agent manuell per Slash-Command (`*create-prd`)
- Agent-Persona übernimmt Current Chat
- **Keine parallele Arbeit**
- **Keine Tool-Integration**
- **Keine Session-Memory** (jeder Workflow: "Start fresh chat")

**Koordination:**
- **Es gibt keine echte Koordination.**
- Party Mode simuliert Multi-Agent-Dialog (aber es ist immer das gleiche LLM)
- User muss manuell zwischen Agents wechseln

**Beispiel:**
```
User: "Analysiere Projekt X und erstelle PRD"
User: *bmad-help
Master: "Für PRD → lade *PM"
User: *create-prd
PM: [Startet PRD-Interview]
[...10 Fragen später...]
PM: "PRD fertig. Nächster Schritt: *architecture"
User: *architecture
Architect: [Startet Architecture-Interview]
```

### Kritischer Unterschied: Agent-Definition vs Agent-Runtime

| Aspekt | OpenClaw (autonomous-stan) | BMAD |
|--------|----------------------------|------|
| **Was ist ein "Agent"?** | Persistent laufende Session mit eigenem Memory, Channel, Tools | YAML-Datei mit Role-Prompt, die in Context geladen wird |
| **Anzahl** | 12 echte Agents | 10 Personas (+ 11 weitere in Creative Intelligence Suite Module) |
| **Parallel Execution** | ✓ Ja (Andrew analysiert WÄHREND Stan coded) | ❌ Nein (User arbeitet sequenziell mit Personas) |
| **Agent-zu-Agent-Komm** | ✓ `sessions_send` via MCP | ❌ Keine (außer simuliertem Party Mode) |
| **Tool Access** | ✓ calendar, github, discord, n8n, 1password | ❌ Keine Tools |
| **Memory** | ✓ Graphiti, Tiered Learnings, memory/*.md | ❌ Keine (jeder Workflow: fresh context) |
| **Background Tasks** | ✓ Heartbeats, Crons | ❌ Keine |
| **User Interaction** | Agents posten in eigene Discord Channels | User chattet mit einer Persona zur Zeit |

### Fazit: Zwei komplett verschiedene Paradigmen

**OpenClaw** ist ein **echtes Multi-Agent-System** mit:
- Persistent laufenden Agents
- Paralleler Arbeit
- Tool-Integration
- Memory-Retention

**BMAD** ist ein **Prompt-Library mit Role-Switching** — näher an:
- "Copilot mit Experten-Modi"
- "Guided Workflows mit Personas"
- "Template-System mit extra steps"

**BMAD nennt sich "21 specialized agents"**, aber das sind **21 YAML-Dateien**. Das ist wie wenn ein Restaurant sagt "Wir haben 10 Köche", aber es ist ein Koch mit 10 Kochmützen.

**OpenClaw hat 12 echte Köche in der Küche, die parallel arbeiten.**

---

## Konkrete Übernahme-Empfehlungen (was + wie + Priorität)

### 🔴 KRITISCH (T-029: Sofort angehen)

#### 1. Phase 3: Solutioning / Architecture Workflow

**Was:**
- Neuer Phase zwischen PLAN und CREATE: **ARCHITECTURE**
- Workflow: `/stan architecture` (interaktives Interview)
- Output: `docs/architecture.md` mit ADRs

**Format (übernehmen von BMAD):**
```markdown
# Architecture Document

## System Architecture
[High-Level Diagram, Component Interactions]

## Data Architecture
[Database Design, State Management, Caching]

## API Architecture
[REST/GraphQL/gRPC, Auth, Versioning]

## Architecture Decision Records (ADRs)

### ADR-001: Use GraphQL for All APIs
**Status:** Accepted | **Date:** 2026-02-16

**Context:** PRD requires flexible querying across multiple epics

**Options Considered:**
1. REST - Familiar but requires multiple endpoints
2. GraphQL - Flexible querying, learning curve
3. gRPC - High performance, poor browser support

**Decision:** Use GraphQL for all client-server communication

**Rationale:**
- PRD requires flexible data fetching (Epic 1, 3)
- Mobile app needs bandwidth optimization (Epic 2)

**Consequences:**
- Positive: Flexible querying, reduced versioning
- Negative: Caching complexity, N+1 query risk
- Mitigation: Use DataLoader for batching

## FR/NFR-Specific Guidance
[Technical Approach per Requirement]

## Standards and Conventions
[Directory Structure, Naming, Testing Patterns]
```

**Template:**
- Erstelle `templates/architecture.md.template`
- Criteria Pack: `criteria/strategy/architecture-quality.yaml`

**Wann:**
- **Trigger:** Multi-Epic-Projekte (>5 Stories)
- **Skip:** Single-Epic, Quick Fixes

**Wie integrieren:**
```
/stan define → PRD entsteht
/stan plan → Stories entstehen
[NEU] /stan architecture → Arch-Doc entsteht (wenn >5 Stories)
/stan create → Implementation
```

**Priorität:** 🔴 **KRITISCH** — Verhindert Agent-Konflikte bei großen Projekten.

#### 2. Implementation Readiness Gate

**Was:**
- Gate Check BEVOR `/stan create` startet
- Validiert: PRD + Stories + (optional) Arch-Doc aligned?

**Checks:**
- [ ] Alle Stories haben verifiable Acceptance Criteria
- [ ] Dependencies sind dokumentiert
- [ ] (Falls Arch-Doc existiert) Stories referenzieren relevante ADRs
- [ ] Keine konfligierenden Tech-Decisions

**Wie:**
- Erstelle Criteria Pack: `criteria/strategy/implementation-readiness.yaml`
- Integriere in `/stan create` (vor Story-Start)

**Priorität:** 🔴 **KRITISCH** — Verhindert Mid-Sprint-Überraschungen.

#### 3. Brownfield Analysis Workflow

**Was:**
- Neuer Command: `/stan analyze-codebase`
- Analysiert existierenden Code
- Output: `docs/codebase-analysis.md`

**Was analysieren:**
- Tech-Stack (Framework-Versionen)
- Patterns (Naming Conventions, Directory Structure)
- Test-Frameworks (Jest/Vitest, Playwright/Cypress)
- Code Style (ESLint Config, Prettier)
- Dependencies (package.json)

**Output-Format:**
```markdown
# Codebase Analysis

## Detected Stack
- Framework: Next.js 13.4.7
- State Management: Redux Toolkit
- Database: PostgreSQL + Prisma
- Testing: Jest + Playwright

## Existing Patterns
- API Routes: `/pages/api/[resource]/[action].ts`
- Components: Barrel Exports in `/components/index.ts`
- Naming: camelCase für Files, PascalCase für Components

## Recommendations
- Follow existing Redux patterns for new features
- Use Playwright for E2E tests (already set up)
```

**Wann:**
- User startet `/stan define` für existierendes Projekt
- Vor PRD-Erstellung

**Priorität:** 🔴 **KRITISCH** — autonomous-stan hat KEINE Brownfield-Support.

---

### 🟡 WICHTIG (T-030: Nächster Sprint)

#### 4. Test Architect Agent + ATDD Workflow

**Was:**
- Neuer Agent: **Nathanael (Test Architect)**
- Workflow: `/stan test-design` (BEVOR `/stan create`)
- Output: `docs/test-strategy.md` + Test Scenarios pro Story

**ATDD = Acceptance Test-Driven Development:**
1. `/stan plan` → Stories mit Acceptance Criteria
2. `/stan test-design` → Nathanael erstellt Test Scenarios
3. `/stan create` → Dev schreibt Tests ZUERST, dann Code

**Nathanael Skills:**
- Test Framework Setup
- ATDD (Automated Test Design)
- NFR Assessment (Performance, Security)
- CI/CD Pipeline Design
- Test Review (Flakiness Detection)

**Wie:**
- Erstelle Agent-Profil: `AGENTS.md` Eintrag für Nathanael
- Skill: `skills/test-architect/SKILL.md`
- Templates: `test-strategy.md.template`, `test-scenarios.md.template`

**Priorität:** 🟡 **WICHTIG** — Test-First erhöht Code-Qualität drastisch.

#### 5. Project Complexity Auto-Detection

**Was:**
- System erkennt Projektkomplexität automatisch
- Route zu richtigem Workflow-Level

**Detection-Logik:**
```python
def detect_complexity(prd):
    story_count = count_stories(prd)
    epic_count = count_epics(prd)
    integration_count = count_integrations(prd)
    
    if story_count <= 3:
        return "QUICK_FLOW"  # Skip Architecture
    elif story_count <= 10 and epic_count <= 2:
        return "STANDARD"    # Optional Architecture
    elif story_count > 10 or epic_count > 2:
        return "COMPLEX"     # Architecture Required
    
    return "STANDARD"
```

**Wann:**
- Nach `/stan plan` (Stories sind bekannt)
- Vor `/stan create`

**Output:**
```
✓ PRD erstellt: 15 Stories, 3 Epics
→ Projektkomplexität: COMPLEX
→ Empfehlung: `/stan architecture` vor `/stan create`
```

**Priorität:** 🟡 **WICHTIG** — Verhindert Over-Engineering für kleine Projekte.

#### 6. Enhanced Brainstorming Techniques

**Was:**
- Erweitere `skills/thinking-techniques/SKILL.md`
- Übernehme 40+ zusätzliche Techniken von BMAD

**BMAD hat:**
- **Biomimetic** (Nature-inspired)
- **Quantum** (Quantum principles)
- **Cultural** (Cross-cultural approaches)
- **Theatrical** (Playful perspectives)

**autonomous-stan hat:**
- 21 Techniques in 9 Purposes

**Wie:**
- Extrahiere BMAD Brainstorming-Techniken
- Mappe auf autonomous-stan Purpose-System
- Füge hinzu zu `thinking-techniques/library/`

**Priorität:** 🟡 **WICHTIG** — Mehr Techniken = bessere Ideation.

---

### 🟢 NICE-TO-HAVE (T-031+: Später)

#### 7. Party Mode für Retrospectives

**Was:**
- Multi-Agent-Dialog-Simulation für Sprint-Reviews
- Alle Agents "diskutieren" in einem Thread

**Beispiel:**
```
/stan retrospective --party-mode

Stan: "Sprint 3 abgeschlossen. Was lief gut?"
Patrick: "Research war schnell, aber PRD hatte Lücken"
Klaus: "Dokumentation wurde erst am Ende gemacht"
Andrew: "Budget wurde eingehalten"
→ Konsolidiertes Retro-Dokument
```

**Wie:**
- Integriere in `/stan think retrospective`
- Option: `--party-mode` aktiviert Multi-Agent-Dialog

**Priorität:** 🟢 **NICE-TO-HAVE** — autonomous-stan hat bereits Retrospective, Party Mode ist Bonus.

#### 8. Scale-Adaptive Workflow-Levels

**Was:**
- 3 Workflow-Varianten pro Phase
- User oder System wählt Level

| Level | PRD | Architecture | Story Detail |
|-------|-----|--------------|--------------|
| **Quick** | Tech-Spec (1 Seite) | Skip | Minimal |
| **Standard** | PRD (5-10 Seiten) | Optional | Medium |
| **Comprehensive** | PRD (20+ Seiten) | Required | Detailed |

**Wann:**
- User-Präferenz: `config.yaml` → `workflow_level: quick|standard|comprehensive`
- Auto-Detection: Basierend auf Projektkomplexität

**Priorität:** 🟢 **NICE-TO-HAVE** — Nützlich, aber nicht kritisch.

#### 9. Workflow-Continuation-System

**Was:**
- BMAD verlangt: "Start fresh chat" für jeden Workflow
- autonomous-stan hat Memory — kann Workflows fortsetzen

**Idee:**
- Workflow-State in `memory/workflow-state.yaml`
- User kann unterbrechen und später fortsetzen

**Beispiel:**
```
/stan architecture
[...5 ADRs erstellt...]
User: "Pause"
→ State saved: `docs/architecture.md.draft`, `memory/workflow-state.yaml`

[Nächster Tag]
/stan continue
→ "Du warst bei ADR-006 (API Versioning). Weiter?"
```

**Priorität:** 🟢 **NICE-TO-HAVE** — Memory-System erlaubt das bereits teilweise.

---

## Zusammenfassung: Was WIRKLICH übernehmen?

### Sofort (T-029)
1. ✅ **Architecture Workflow mit ADRs** (🔴 KRITISCH)
2. ✅ **Implementation Readiness Gate** (🔴 KRITISCH)
3. ✅ **Brownfield Analysis Workflow** (🔴 KRITISCH)

### Nächster Sprint (T-030)
4. ✅ **Test Architect Agent + ATDD** (🟡 WICHTIG)
5. ✅ **Project Complexity Auto-Detection** (🟡 WICHTIG)
6. ✅ **Erweiterte Brainstorming-Techniken** (🟡 WICHTIG)

### Später (Nice-to-Have)
7. ❓ **Party Mode für Retrospectives** (🟢 NICE-TO-HAVE)
8. ❓ **Scale-Adaptive Workflow-Levels** (🟢 NICE-TO-HAVE)
9. ❓ **Workflow-Continuation** (🟢 NICE-TO-HAVE)

### NICHT übernehmen
- ❌ **NPM-Tooling** (autonomous-stan ist Git-basiert)
- ❌ **Slash-Command-Menüs** (autonomous-stan nutzt `/stan` CLI)
- ❌ **Persona-System** (autonomous-stan hat echte Agents)
- ❌ **Fresh Context per Workflow** (autonomous-stan hat Memory)

---

## Abschließende Bewertung

**BMAD-METHOD ist:**
- ✅ **Exzellentes Prompt-Engineering** — Workflows sind hervorragend strukturiert
- ✅ **Starke Methodologie** — 4 Phasen + ADRs + Scale-Adaptive = solide
- ✅ **Reichhaltige Bibliothek** — 60+ Brainstorming-Techniken, 34+ Workflows
- ❌ **KEIN Multi-Agent-System** — 10 YAML-Personas ≠ 12 echte Agents
- ❌ **Keine Tool-Integration** — Nur Markdown-Outputs
- ❌ **Keine Memory** — Jeder Workflow startet fresh

**autonomous-stan sollte übernehmen:**
1. **Solutioning-Phase** (Architecture + ADRs) → Verhindert Agent-Konflikte
2. **Implementation Readiness Gate** → Verhindert Mid-Sprint-Überraschungen
3. **Brownfield Analysis** → Codebase-Analyse für existierende Projekte
4. **Test Architect Agent** → Test-First Workflows

**autonomous-stan ist bereits überlegen in:**
- Echtes Multi-Agent-System (12 Agents vs 10 Personas)
- Tool-Integration (1Password, GitHub, Discord, n8n, Morgen)
- Memory-Retention (Tiered Learnings + Graphiti)
- Parallele Arbeit (Agents arbeiten gleichzeitig)

**Der größte Lerneffekt:**
- **Phase 3: Solutioning** ist DAS fehlende Puzzleteil für Multi-Epic-Projekte
- **ADRs** sind der Schlüssel zur Vermeidung von Agent-Konflikten
- **Brownfield-Support** ist kritisch für Real-World-Adoption

---

**Ende der Analyse.**
