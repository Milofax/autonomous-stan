# Framework-Synthese: autonomous-stan v2

**Datum:** 2026-02-16 | **Autor:** STAN | **Basiert auf:** 10 Detail-Analysen + erste Synthese

---

## Teil 1: Executive Summary

### Die 7 wichtigsten Erkenntnisse

**1. Context Rot ist das ungelöste Kernproblem.** Alle Frameworks kämpfen damit, dass Claude ab ~50% Context-Füllung in "Completion Mode" degradiert. GSD löst es am besten: Max 2-3 Tasks pro Sub-Agent, frische 200k-Fenster, Stop BEVOR Qualität sinkt. Ralph erzwingt es per Bash-Kill. autonomous-stan hat aktuell NULL Lösung dafür.

**2. Hooks die blocken = ~95% Compliance. Alles andere ≤ 40%.** Die brutale Wahrheit aus OpenClaw-Praxis: AGENTS.md-Regeln werden ignoriert (Graphiti-Gate übersprungen, Karte nicht zuerst erstellt, Browser-Hygiene missachtet — alles in MEMORY.md dokumentiert). Nur was technisch blockiert, wird zuverlässig eingehalten. **Enforcement durch Technik, nicht durch Prosa.**

**3. Kein Framework hat alles — aber die Kombination ist klar.** Superpowers: beste Enforcement-Philosophie. GSD: beste Context-Rot-Lösung. BMAD: beste Skalierung. Ralph: beste autonome Loop. PRPs: beste Codebase-Intelligence. Everything-CC: beste Quality Gates. Beads: bestes Task-Tracking. taming-stan: beste funktionierende Guards. OpenClaw: beste Produktionsreife.

**4. autonomous-stan v1 ist 80% Theorie, 30% Praxis.** 357 Unit Tests grün, aber nie in echtem Projekt getestet. hooks.json fehlt. Evaluator-Hook funktioniert experimentell, ist nicht integriert. **Praxis-Validierung vor weiterer Theorie.**

**5. Das Criteria-System ist der Unique Selling Point.** 24 Criteria in YAML mit atomaren Checks — hat KEIN anderes Framework. Superpowers hat Review-Agents (flexibler aber nicht reproduzierbar), BMAD hat Workflows (aber keine atomaren Gates). **Criteria behalten und härter enforcen.**

**6. Die 21 Techniques sind einzigartig und unterbewertet.** Kein Framework hat vergleichbare strukturierte Denkmethoden. BMAD hat 60+ Brainstorming-Techniken — aber nur für Ideation. autonomous-stans Techniques decken Root Cause, Perspective Shift, Decision Making, Self Reflection ab.

**7. Dual-Target (Claude Code + OpenClaw) ist machbar.** Criteria (YAML), Techniques (YAML), Templates (Markdown+YAML), Tasks (JSONL) — plattformagnostisch. Hooks = Claude-Code-spezifisch. Skills = OpenClaw-spezifisch. Kern sauber von Runtime trennen.

### Was hat uns am meisten überrascht?

- **BMAD's "21 Agents" sind nur 21 YAML-Dateien** — ein Koch mit 21 Kochmützen. OpenClaw hat 12 echte Köche.
- **GSD's Context-Rot-Curve ist quantifizierbar:** 0-30% = Peak, 30-50% = Good, 50-70% = Degrading, 70%+ = Rushed.
- **Superpowers' Anti-Rationalization Tables** nutzen Cialdini-Prinzipien — effektiver als jede Regel.
- **OpenClaw's Pre-Compaction Memory Flush** — Silent-Turn schreibt Learnings BEVOR Auto-Compaction den Context löscht.

---

## Teil 2: Feature-Matrix

| Feature | Super-powers | BMAD | Ralph | GSD | PRPs | Beads | Every-thing-CC | Open-Claw | taming-stan | auto-stan |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Brainstorming/Dialog | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Task-Tracking | ⚠️ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ |
| TDD | ✅ | ✅ | ❌ | ⚠️ | ❌ | ❌ | ✅ | ❌ | ❌ | ⚠️ |
| Memory/Learnings | ❌ | ❌ | ✅ | ⚠️ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| Guards/Enforcement | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ⚠️ |
| Subagents | ✅ | ⚠️ | ❌ | ✅ | ⚠️ | ❌ | ✅ | ✅ | ❌ | ⚠️ |
| Scale-Adaptive | ❌ | ✅ | ❌ | ⚠️ | ❌ | ❌ | ❌ | ❌ | ❌ | ⚠️ |
| Visual Verification | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ | ⚠️ | ❌ | ⚠️ |
| Code Review | ✅ | ⚠️ | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| Context Management | ⚠️ | ❌ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Criteria/Quality Gates | ⚠️ | ⚠️ | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ | ✅ |
| Templates | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Techniques/Thinking | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Git Integration | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ⚠️ |
| Multi-Agent | ⚠️ | ⚠️ | ❌ | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ | ⚠️ |
| Persistent Memory | ❌ | ❌ | ⚠️ | ⚠️ | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Context Rot Prev. | ⚠️ | ❌ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Autonomous Loop | ⚠️ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ⚠️ |

✅ = implementiert | ⚠️ = teilweise | ❌ = nicht vorhanden

---

## Teil 3: Compliance-Pyramide

### Die Compliance-Realität (3 Wochen Produktion mit 12 OpenClaw-Agents)

| Enforcement-Methode | Compliance | Beweis |
|---------------------|:----------:|--------|
| Hook der blockt (Tool-Deny, PreToolUse deny) | ~95% | taming-stan Credential-Guard, OpenClaw Tool-Deny |
| Persuasive Sprache + Rationalization Tables | ~70% | Superpowers' "Iron Law" + Excuse Tables |
| AGENTS.md Regel (!! Notation) | ~40% | MEMORY.md: "NIE raten"→3x geraten, "Karte zuerst"→oft vergessen |
| Lange Prosa in Skill-Docs | ~20% | BMAD's 17.835-Zeilen-Workflow de facto nicht nutzbar |
| Metakognition ("erkenne Warnsignale") | ~0% | taming-stan: type:prompt Hooks "beraten, durchsetzen NICHT" |

### Konsequenzen für v2

**Enforcement-Pyramide bestimmt Architektur.** Jedes Feature MUSS einer Stufe zugeordnet werden:
- **S1 (Hook blockt):** Credentials, Phase-Gates, Verification-Before-Completion
- **S2 (Rationalization Tables):** TDD, Debugging-Disziplin
- **S3 (PITH-Regel):** Workflows, Conventions
- **S4 (Doku):** Nice-to-have Guidance

**HARD-GATE = technischer Hook, nicht XML-Tag.** Superpowers' `<HARD-GATE>` funktioniert nur im frischen Context. Bei 70% Fill wirkt es nicht.

**~40% Compliance reicht für Conventions.** Git-Format? Guard fixt den Rest. Reserve S1 für Sicherheit.

**Metakognition = Zeitverschwendung.** Agent rationalisiert warum er nicht rationalisiert. 3-Strikes ist die mechanische Lösung.

---

## Teil 4: Synthese-Empfehlung

### CRITICAL: Sofort übernehmen (~20-27h)

| # | Feature | Quelle | h | Begründung |
|---|---------|--------|---|------------|
| C1 | **Context Rot Prevention** — Max 2-3 Tasks/Sub-Agent, Hauptsession ≤40%, frische 200k für Sub-Agents | GSD + Ralph | 4-6 | NULL Lösung heute. Qualitätskurve ist real und messbar. |
| C2 | **Verification-Before-Completion Gate** — Kein Success ohne `run + read output`. "Should work" = Lüge. | Superpowers + Everything-CC | 3-4 | OpenClaw-Praxis: "Done!" ohne Verifikation → Bugs in Production. |
| C3 | **Credential-Schutz Guard** — 903 Regex-Patterns, 3-Strikes. Blockiert Graphiti-Writes mit Secrets. | taming-stan | 2 | Code existiert in taming-stan. Nur portieren. |
| C4 | **3-Strikes Loop-Breaker** — 3 gleiche Fehler → Block → Learnings suchen → Perspective Shift. | taming-stan | 3 | MEMORY.md: Agent bleibt in Loops. STAN.FLUX verbal, 3-Strikes mechanisch. |
| C5 | **Praxis-Validierung** — hooks.json + Test-Projekt + Full Workflow. | current-state | 8-12 | 80% Theorie, 30% Praxis. Keine weitere Theorie ohne Test. |

### HIGH: Nächste Iteration (~24-30h)

| # | Feature | Quelle | h | Begründung |
|---|---------|--------|---|------------|
| H1 | **Scale-Adaptive Routing** — Auto-Detection: Quick (≤3), Standard (4-10), Complex (>10 Stories). | BMAD | 6-8 | Config-Fix braucht keinen PRD. |
| H2 | **Two-Stage Review** — Erst Spec-Compliance, dann Code-Quality. Zwei Sub-Agents. | Superpowers | 4-5 | Verhindert "guter Code der Falsches tut." |
| H3 | **Patterns-to-Mirror** — Bestehende Patterns mit file:line VOR Implementation dokumentieren. | PRPs | 2-3 | Verhindert #1-Problem: Agent erfindet neue Patterns. |
| H4 | **Anti-Rationalization Tables** — Excuse→Reality in TDD, Debugging, Verification Skills. | Superpowers | 2 | ~70% Compliance — zweitstärkste Methode nach Hooks. |
| H5 | **ADRs** — Template mit Context/Decision/Consequences. Pflicht bei >5 Stories. | BMAD + Everything-CC | 3 | Verhindert Agent-Konflikte bei paralleler Arbeit. |
| H6 | **Discuss-Phase** — Graubereiche klären, Entscheidungen in CONTEXT.md locken. | GSD | 4-5 | DEFINE→PLAN springt ohne systematische Klärung. |
| H7 | **Git Worktrees** — Default für Features. Safety-Check .gitignore. | Superpowers | 3 | Parallele Isolation ohne Branch-Switching. |

### MEDIUM: Nice-to-have (~23-30h)

| # | Feature | Quelle | h |
|---|---------|--------|---|
| M1 | Systematic Debugging (4-Phase statt STAN.FLUX) | Superpowers + PRPs | 3-4 |
| M2 | Atomic Git Commits (1 Task = 1 Commit) | GSD + taming-stan | 2 |
| M3 | Wave-basierte Parallel Execution | GSD | 6-8 |
| M4 | Deviation Rules (Bug=Auto, Arch=Ask) | GSD | 2 |
| M5 | Brownfield Analysis (`/stan analyze-codebase`) | BMAD | 4-5 |
| M6 | Pre-Compaction Memory Flush | OpenClaw | 3-4 |
| M7 | Completion Signal (`<promise>COMPLETE</promise>`) | Ralph | 1 |
| M8 | Research-Hierarchie Guard (Graphiti→Codebase→Web) | taming-stan | 2-3 |

### LOW: Später evaluieren (~50h+)

| # | Feature | Quelle | h |
|---|---------|--------|---|
| L1 | Erweiterte Brainstorming-Techniken (40+ von BMAD) | BMAD | 4 |
| L2 | Hierarchische Task-IDs (Epic.Task.Subtask) | Beads | 6 |
| L3 | Task-Compaction (Memory Decay) | Beads | 8 |
| L4 | Eval-Driven Development (pass@k Metriken) | Everything-CC | 8-10 |
| L5 | Multi-Agent Code Review (7 Spezialisten) | PRPs | 10 |
| L6 | TUI Visualisierung (Kanban im Terminal) | BDUI | 15+ |

---

## Teil 5: Architektur-Vorschlag autonomous-stan v2

### Dateistruktur

```
autonomous-stan/
├── .claude-plugin/
│   ├── plugin.json              # Plugin-Manifest
│   └── marketplace.json
│
├── core/                        # PLATTFORMAGNOSTISCHER KERN
│   ├── criteria/                # 24+ YAML Criteria
│   │   ├── strategy/            # goal-quality, story-size, feasibility
│   │   ├── code/                # code-quality, test-coverage, security
│   │   ├── text/                # text-quality, conciseness
│   │   ├── design/              # responsive, a11y, ux-quality
│   │   └── meta/                # meta-criteria-valid
│   ├── techniques/              # 21+ YAML Techniques
│   │   ├── purposes/            # 9 Purpose-Einstiegspunkte
│   │   └── *.yaml              # Atomic Techniques
│   ├── templates/
│   │   ├── prd.md.template
│   │   ├── plan.md.template     # mit Patterns-to-Mirror Section
│   │   ├── adr.md.template      # Architecture Decision Records
│   │   └── codebase-analysis.md.template
│   ├── rationalization/         # Anti-Rationalization Tables
│   │   ├── tdd.md
│   │   ├── verification.md
│   │   └── debugging.md
│   └── deviation-rules.md       # Auto-Fix vs Ask
│
├── hooks/                       # CLAUDE-CODE-SPEZIFISCH
│   ├── hooks.json               # ${CLAUDE_PLUGIN_ROOT} Pfade
│   └── autonomous-stan/
│       ├── stan_context.py      # SessionStart/UserPromptSubmit
│       ├── stan_track.py        # PostToolUse (Test-Tracking)
│       ├── stan_gate.py         # PreToolUse (Phase-Gates, Verification)
│       ├── credential_guard.py  # 903-Pattern Credential-Schutz
│       ├── retry_guard.py       # 3-Strikes Loop-Breaker
│       └── lib/
│           ├── session_state.py
│           ├── secret_patterns.py
│           └── context_rot.py   # Context-Fill-Monitor
│
├── commands/stan/               # CLAUDE-CODE SLASH-COMMANDS
│   ├── init.md, define.md, plan.md, create.md
│   ├── verify.md               # Verification Loop
│   ├── think.md, complete.md
│   └── analyze-codebase.md     # Brownfield
│
├── agents/                      # Sub-Agent-Definitionen
│   ├── spec-reviewer.md         # Stage 1: Spec Compliance
│   ├── quality-reviewer.md      # Stage 2: Code Quality
│   ├── architect.md             # ADRs, System-Design
│   └── security-reviewer.md     # OWASP, Race Conditions
│
├── skills/                      # OPENCLAW-SPEZIFISCH
│   ├── techniques/SKILL.md
│   ├── criteria-check/SKILL.md
│   ├── brainstorming/SKILL.md
│   ├── tdd-enforcement/SKILL.md
│   ├── scale-adaptive/SKILL.md
│   ├── verification/SKILL.md
│   └── context-rot/SKILL.md
│
├── .stan/                       # RUNTIME STATE
│   ├── tasks.jsonl
│   ├── session.json
│   ├── config.yaml
│   └── learnings/
│       ├── recent.json
│       ├── hot.json
│       └── archive.json
│
└── docs/
    ├── plan.md
    ├── adr/
    └── analysis/
```

**Kern-Prinzip:** `core/` ist plattformagnostisch (YAML, Markdown, JSONL). `hooks/` ist Claude-Code. `skills/` ist OpenClaw. Alles was in `core/` lebt, funktioniert auf beiden Plattformen.

### Hook-System: Was funktioniert, was nicht

**Funktioniert (aus taming-stan + OpenClaw Praxis):**

| Hook-Typ | Beispiel | Compliance |
|-----------|---------|:----------:|
| PreToolUse deny | Credential-Guard blockiert Graphiti-Write mit Secrets | ~95% |
| PreToolUse deny | Phase-Gate blockiert Code vor Plan-Approval | ~95% |
| PostToolUse tracking | 3-Strikes zählt Fehler, blockiert nach 3 | ~95% |
| PreToolUse deny | Git-Guard blockiert non-conventional Commits | ~95% |

**Funktioniert NICHT (aus taming-stan plan.md Experimenten):**

| Hook-Typ | Beispiel | Warum nicht |
|-----------|---------|-------------|
| type:prompt (beratend) | "Hast du Graphiti gesucht?" | Kann nicht blocken, nur warnen. Agent ignoriert. |
| systemMessage | "Spawne Subagent für Review" | Claude spawnt nicht autonom, nur wenn User fragt. |
| Metakognition | "Erkenne wenn du rationalisierst" | Agent rationalisiert warum er nicht rationalisiert. |

**Design-Regel für v2:** Jeder Hook MUSS entweder `deny` zurückgeben können oder er ist kein Hook sondern Dokumentation. Dokumentation → in `core/rationalization/` oder AGENTS.md.

### State Management

**Zwei-Schichten-State:**

| Schicht | Datei | Lebensdauer | Inhalt |
|---------|-------|-------------|--------|
| Session | `.stan/session.json` | Pro Session | Flags (graphiti_searched, tests_run), Error-Counts, Context-Fill |
| Persistent | `.stan/tasks.jsonl` | Projektlebensdauer | Tasks, Status, Dependencies, Acceptance Criteria |
| Persistent | `.stan/learnings/` | Projektlebensdauer | recent (rolling 50), hot (promoted), archive (permanent) |
| Persistent | `docs/` | Projektlebensdauer | PRD, Plan, ADRs, Codebase-Analysis |

**Session-State (`.stan/session.json`):**
```json
{
  "graphiti_searched": false,
  "firecrawl_attempted": false,
  "error_counts": {"npm_test": 0, "typecheck": 0},
  "context_fill_estimate": 0.35,
  "tasks_completed_this_session": 2,
  "verification_ran": false,
  "last_technique_used": null
}
```

**NEU in v2: Context-Fill-Tracking.** Der Context-Rot-Guard schätzt die Context-Füllung basierend auf Tool-Call-Count und Message-Length. Bei >50% → Warnung. Bei >70% → Block und Empfehlung: "Dispatche restliche Tasks an frische Sub-Agents."

### Plugin-Format: Claude Code Plugin vs OpenClaw Skill

| Dimension | Claude Code Plugin | OpenClaw Skill |
|-----------|-------------------|----------------|
| **Discovery** | YAML Frontmatter in SKILL.md | SKILL.md in skills/ Verzeichnis |
| **Loading** | On-demand (Skill Tool) | Pre-loaded via Project Context |
| **Enforcement** | Hooks (Python, deny/allow) | PITH-Regeln (Prompt-Level) |
| **Sub-Agents** | Task Tool (native) | sessions_spawn (OpenClaw) |
| **State** | session.json + hooks lib | Graphiti + memory/*.md |
| **Distribution** | Plugin Marketplace | Git + NFS shared skills |

**Dual-Target-Strategie:**
1. `core/` Inhalte werden von BEIDEN Plattformen gelesen
2. Claude Code: Hooks enforcen, Commands triggern, Agents reviewen
3. OpenClaw: Skills wrappen core/ Inhalte, PITH-Regeln in AGENTS.md

**Beispiel: Criteria-Check auf beiden Plattformen:**

Claude Code:
```
stan_gate.py → liest core/criteria/code/test-coverage.yaml → deny wenn nicht erfüllt
```

OpenClaw:
```
skills/criteria-check/SKILL.md → Agent liest core/criteria/*.yaml → prüft und reportet
```

Gleiche Criteria-YAML, verschiedene Enforcement-Mechanismen.

---

## Teil 6: OpenClaw-Rückportierung

Was können die 12 OpenClaw-Agents SOFORT als Skills übernehmen?

### 6.1 Techniques als Skill

**SKILL.md Format:**
```markdown
---
name: thinking-techniques
description: 21 strukturierte Denkmethoden für Root Cause, Ideation, Perspective Shift
trigger: stuck, nachdenken, analyse, brainstorming, perspektive, entscheidung
---

## Wann nutzen
- Vor jeder komplexen Entscheidung
- Bei Stuck/Loop (nach 3-Strikes)
- Bei kreativen Aufgaben (Design, Naming, Architecture)

## Verfügbare Techniques nach Purpose

### Root Cause Analysis
- Five Whys: 5x "Warum?" mit Evidence-Chain (file:line)
- First Principles: Annahmen zerlegen bis Grundwahrheiten
- Assumption Reversal: Jede Annahme umkehren und prüfen

### Perspective Shift
- Six Thinking Hats: 6 Perspektiven durchgehen (Fakten, Emotionen, Risiken, Chancen, Kreativität, Prozess)
- Alien Anthropologist: Feature erklären als wäre man Außerirdischer

### Decision Making
- Superposition Collapse: Alle Optionen gleichzeitig halten, dann zwingen zu kollabieren
- First Principles: Warum MUSS es so sein? Was wenn nicht?

## Anwendung
1. Purpose identifizieren (was brauche ich?)
2. Technique wählen (oder empfohlen bekommen)
3. Technique-Steps durcharbeiten
4. Ergebnis dokumentieren in memory/YYYY-MM-DD.md
```

**Trigger-Words:** stuck, nachdenken, analyse, brainstorming, perspektive, entscheidung, alternativen, warum

### 6.2 Brainstorming-Workflow

**SKILL.md Format:**
```markdown
---
name: brainstorming
description: Strukturiertes Brainstorming mit Socratic Refinement
trigger: brainstorming, ideen, design, konzept, feature-idee
---

## Workflow
1. Problem definieren (1 Satz)
2. Graubereiche identifizieren (Was ist NICHT klar?)
3. Fragen stellen (One-at-a-Time, nicht Fragenkatalog)
4. Design präsentieren in Chunks (nicht alles auf einmal)
5. Approval pro Chunk einholen
6. Erst nach vollem Approval: Implementation planen

## HARD-GATE
Kein Code, kein Scaffold, keine Implementation BEVOR Design approved.
Wenn du dich dabei ertappst Code zu schreiben → STOP → zurück zu Schritt 2.

## Rationalization Table
| Excuse | Realität |
|--------|---------|
| "Ist eh klar, brauche kein Brainstorming" | Dann dauert es 5 Min. Mach es trotzdem. |
| "Kann ich während dem Coden klären" | Nein. Design-Fehler kosten 10x mehr als Coding-Fehler. |
| "User hat ja schon gesagt was er will" | User weiß was er WILL, nicht was er BRAUCHT. |
```

**Trigger-Words:** brainstorming, ideen, design, konzept, feature-idee, kreativ

### 6.3 TDD-Enforcement

**SKILL.md Format:**
```markdown
---
name: tdd-enforcement
description: Test-Driven Development mit Iron Law und Anti-Rationalization
trigger: test, tdd, testing, tests schreiben, test first
---

## The Iron Law
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST.
Write code before the test? Delete it. Start over.

## RED-GREEN-REFACTOR
1. RED: Schreibe Test der fehlschlägt. Verifiziere dass er KORREKT fehlschlägt.
2. GREEN: Schreibe MINIMALEN Code damit Test grünt. Nicht mehr.
3. REFACTOR: Verbessere Code. Tests müssen grün bleiben.

## Rationalization Table
| Excuse | Realität |
|--------|---------|
| "Zu simpel für Test" | Simple Code bricht auch. Test dauert 30 Sekunden. |
| "Teste ich danach" | Tests die sofort passen beweisen nichts. |
| "Ist nur Config" | Config-Fehler verursachen 30% aller Production Incidents. |
| "Nur einmal, schnell" | "Nur einmal" × 100 = technische Schulden. |
| "Bin mir sicher" | Dein Confidence-Level korreliert nicht mit Korrektheit. |
```

**Trigger-Words:** test, tdd, testing, tests schreiben, test first, unit test

### 6.4 Scale-Adaptive Planning

**SKILL.md Format:**
```markdown
---
name: scale-adaptive
description: Planungstiefe automatisch an Projektkomplexität anpassen
trigger: plan, projekt, feature, implementierung, architektur
---

## Complexity Detection
- ≤3 Stories → QUICK (kein PRD, direkt Plan, skip Architecture)
- 4-10 Stories → STANDARD (PRD, Plan, optional Architecture)
- >10 Stories oder >2 Epics → COMPLEX (PRD, Architecture REQUIRED, ADRs, Plan)

## Quick Flow (5-15 Min)
1. Problem in 2-3 Sätzen
2. Tasks auflisten (max 3)
3. Implementieren

## Standard Flow (30-60 Min)
1. DEFINE: PRD light (Hypothesis, JTBD, Stories)
2. PLAN: Tasks mit Dependencies
3. CREATE: Implementieren mit Verification

## Complex Flow (1-3h)
1. DEFINE: Full PRD (Evidence, MoSCoW, Feasibility)
2. ARCHITECTURE: ADRs für Tech-Decisions
3. PLAN: Tasks mit Phases + Wave-Zuordnung
4. CREATE: Sub-Agents mit Two-Stage Review
```

**Trigger-Words:** plan, projekt, feature, implementierung, architektur, neues feature

### 6.5 Criteria-Checks

**SKILL.md Format:**
```markdown
---
name: criteria-check
description: YAML-basierte Quality Gates für Deliverables
trigger: qualität, review, check, fertig, done, abnahme
---

## Verfügbare Criteria

### Strategy
- goal-quality: Ist das Ziel klar, messbar, erreichbar?
- story-size: Passt in eine Iteration? ≤5 Files? 2-3 Sätze beschreibbar?
- hypothesis-testable: Kann die Hypothese verifiziert werden?

### Code
- code-quality: Clean Code, keine Duplikation, gute Names
- test-coverage: Alle kritischen Pfade getestet
- security: Keine Secrets, keine Injection, Race Conditions geprüft

### Text
- text-quality: Klar, präzise, keine Füllwörter
- conciseness: Auf den Punkt, keine Wiederholungen

## Anwendung
Für JEDES Deliverable: Relevante Criteria identifizieren → Checks durchgehen → Bei FAIL: fixen vor Abgabe.
```

**Trigger-Words:** qualität, review, check, fertig, done, abnahme, quality gate

### 6.6 Context Rot Prevention

**SKILL.md Format:**
```markdown
---
name: context-rot-prevention
description: Verhindere Qualitätsverlust bei langen Sessions
trigger: lange session, viel gemacht, context, komplex, sub-agent
---

## Quality Degradation Curve
- 0-30% Context: Peak Quality — arbeite normal
- 30-50% Context: Good — letzte große Tasks starten
- 50-70% Context: WARNUNG — nur noch kleine Tasks oder Sub-Agents spawnen
- 70%+ Context: STOP — alle restlichen Tasks an Sub-Agents delegieren

## Regeln
1. Max 2-3 Tasks selbst erledigen, dann Sub-Agent für weitere
2. Hauptsession nur für Orchestration (≤40% Context)
3. Sub-Agents bekommen frische Context-Fenster
4. NIEMALS "noch schnell diesen einen Task" bei >50%

## Signale dass Context Rot eintritt
- Antworten werden kürzer
- Details werden übersprungen
- "Sollte funktionieren" statt Verification
- Wiederholungen in Erklärungen
```

**Trigger-Words:** lange session, viel gemacht, context, sub-agent, delegieren

### 6.7 Verification-Before-Completion

**SKILL.md Format:**
```markdown
---
name: verification
description: Kein Success-Claim ohne bewiesene Verifikation
trigger: fertig, done, abgeschlossen, funktioniert, erledigt
---

## Regel
KEIN Success-Claim ohne: 1. Command ausführen 2. Output lesen 3. Ergebnis zitieren.

## Verboten
- "Should work" — das ist eine LÜGE
- "Looks correct" — das ist eine VERMUTUNG
- "I'm confident" — Confidence korreliert nicht mit Korrektheit
- "Based on the changes" — basiere auf OUTPUT, nicht auf CHANGES

## Erlaubt
- "[RAN: npm test] [SAW: 47/47 pass] All tests pass."
- "[RAN: curl localhost:3000/api/health] [SAW: 200 OK] Endpoint works."
- "[RAN: python -m pytest] [SAW: FAILED test_auth.py] 2 failures found."

## Verification Loop (Everything-CC Muster)
1. Build: Kompiliert es?
2. Types: Type-Check fehlerfrei?
3. Lint: Lint fehlerfrei?
4. Tests: Alle grün + Coverage ≥80%?
5. Security: Keine Secrets, keine console.log in prod?
6. Diff: Nur erwartete Dateien geändert?
```

**Trigger-Words:** fertig, done, abgeschlossen, funktioniert, erledigt, ready, ship it

---

## Teil 7: Was NICHT übernehmen (und warum)

### Explizite NEIN-Liste

| Feature | Framework | Begründung |
|---------|-----------|------------|
| **Mandatory Brainstorming für ALLES** | Superpowers | "Every project goes through this process. A todo list, a config change." — Das ist Dogma. Ein 1-Line-Fix braucht kein Brainstorming. Scale-Adaptive (H1) löst das besser: Quick Flow für Triviales. |
| **TDD ohne Escape Hatch** | Superpowers | "Thinking 'skip TDD just this once'? Stop." — Es gibt legitime Ausnahmen: Generated Code, Config-Dateien, Throwaway Prototypes. Die Iron Law ist gut als Guideline (~70% Compliance), nicht als Hook (~95% wäre zu rigid). |
| **Party Mode (Multi-Agent-Theater)** | BMAD | Es ist IMMER das gleiche LLM. Kein echter Konflikt, keine echte Perspektive. OpenClaw hat 12 ECHTE Agents — das ist die bessere Lösung für Multi-Perspektiven. |
| **Persona-System (YAML-Rollen)** | BMAD | 21 YAML-Dateien ≠ 21 Agents. OpenClaw hat echte Agents mit eigenen Sessions, Memory, Tools. Personas als Prompt-Swaps sind inferior. |
| **NPM-Tooling für Distribution** | BMAD | `npx bmad-method@alpha install` kopiert nur Dateien. Git Submodule oder Plugin Marketplace sind sauberer. |
| **Fresh Context per Bash-Kill** | Ralph | Das ist zu teuer für OpenClaw (Session-Overhead). Besser: Sub-Agents mit frischen Fenstern (GSD-Pattern) innerhalb bestehender Session-Infrastruktur. |
| **Flat progress.txt** | Ralph | Tiered Learnings (recent/hot/archive) ist überlegen. progress.txt wächst unbegrenzt, keine Promotion, kein Heat-Scoring. |
| **prd.json statt tasks.jsonl** | Ralph | `passes: true/false` ist zu simpel. JSONL mit Status/Dependencies/Acceptance Criteria ist mächtiger und bereits implementiert. |
| **17.835-Zeilen-Workflows** | BMAD | Context Pollution. LLM muss Wall of Text parsen. OpenClaw Skills: kleine, fokussierte Dateien. |
| **Continuous Learning (Auto-Extract)** | Everything-CC | WAS ist ein "Learning"? Algorithmus entscheidet, nicht Mensch → Noise. Graphiti + `!!save_immediately` ist besser: User entscheidet bewusst was wertvoll ist. |
| **Strategic Compact (Tool-Counter)** | Everything-CC | Tool-Call-Zählung ≠ logische Phase. 50 Calls können mitten im Task sein. Phase-basierte Erkennung wäre besser, ist aber zu komplex. OpenClaw's Auto-Compaction + Pre-Flush ist die pragmatischere Lösung. |
| **Context-Injection Modes** | Everything-CC | dev.md, review.md, research.md — autonomous-stan hat Phasen (DEFINE/PLAN/CREATE) die spezifischer sind. Redundant. |
| **`--dangerously-skip-permissions`** | GSD | Security-Risiko. Agent könnte DB-Schema-Migration autonom durchführen. Deviation Rules (M4) sind die kontrollierte Alternative. |
| **Stealth Mode** | Beads | Lokale Nutzung ohne Commits — für autonomous-stan irrelevant, da Git-Tracking gewünscht ist. |
| **Multi-Repo Routing** | Beads | Kein OSS-Contributor Use Case erkennbar. Nur relevant wenn autonomous-stan als Framework für externe Projekte genutzt wird. |
| **TUI Visualisierung** | BDUI | 15h+ Aufwand für Terminal-Kanban. Markdown tasks.md + BusinessMap reichen. Visualisierung ist nicht autonomous-stans Kern-Value. |
| **Hierarchische Task-IDs** | Beads | `t-a3f8.1.1` Format ist schön, aber autonomous-stans flache Hash-IDs (`t-a1b2`) mit Dependencies reichen. Hierarchie durch Dependencies, nicht durch ID-Format. |
| **7 spezialisierte Review-Agents** | PRPs | 10h Aufwand. Two-Stage Review (H2) deckt 90% des Werts ab. 7 Spezialisten sind Overkill für Solo-Dev / kleines Team. |
| **Eval-Driven Development** | Everything-CC | pass@k Metriken sind elegant aber 8-10h Aufwand. Nur sinnvoll für kritische Features (Auth, Payments). Criteria-System deckt den Alltagsbedarf. |
| **Workflow-Continuation (Pause/Resume)** | BMAD | Memory-System erlaubt bereits das Fortsetzen über Sessions. Expliziter Workflow-State in YAML wäre Over-Engineering. |
| **Slash-Command-Menüs pro Agent** | BMAD | autonomous-stan nutzt `/stan` CLI. Pro-Agent-Menüs sind redundant. |

### Die wichtigste Nicht-Entscheidung

**Multi-Agent für autonomous-stan: NEIN (vorerst).**

autonomous-stan ist ein Single-Agent-Framework. Multi-Agent-Orchestration (wie OpenClaw's 12 Agents) ist ein anderes Paradigma:
- OpenClaw hat Multi-Agent als **Core Feature** (Sessions, Routing, Isolation)
- autonomous-stan hat Multi-Agent als **Sub-Agent-Pattern** (Task Tool, Worktrees)
- Die Kombination funktioniert: autonomous-stan's Kern (Criteria, Techniques, Templates) auf OpenClaw's Multi-Agent-Infrastruktur

Statt Multi-Agent in autonomous-stan zu bauen, nutze OpenClaw's Infrastruktur und portiere autonomous-stans Kern als Skills zurück (Teil 6).

---

## Anhang: Gesamtaufwand-Schätzung

| Priorität | Features | Stunden | Timeline |
|-----------|----------|---------|----------|
| CRITICAL | C1-C5 | 20-27h | Woche 1 |
| HIGH | H1-H7 | 24-30h | Woche 2-3 |
| MEDIUM | M1-M8 | 23-30h | Woche 4-6 |
| LOW | L1-L6 | 50h+ | Backlog |
| **Gesamt (CRITICAL+HIGH)** | **12 Features** | **44-57h** | **~3 Wochen** |

**Empfehlung:** CRITICAL zuerst (besonders C5: Praxis-Validierung). Dann HIGH parallel. MEDIUM nach Praxis-Feedback priorisieren. LOW nur bei Bedarf.

---

*Dieses Dokument ist eigenständig lesbar ohne die 10 Detail-Analysen. Für tiefere Einblicke: `docs/analysis/*.md`*
