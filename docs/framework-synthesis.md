# Framework-Synthese: autonomous-stan v2

**Datum:** 2026-02-16  
**Autor:** STAN  
**Basiert auf:** 10 Detail-Analysen + erste Synthese  
**Zweck:** Finales Entscheidungsdokument für autonomous-stan v2

---

## Teil 1: Executive Summary

### Die 7 wichtigsten Erkenntnisse

**1. Context Rot ist das ungelöste Kernproblem.**
Alle Frameworks kämpfen damit, dass Claude ab ~50% Context-Füllung in "Completion Mode" degradiert. GSD löst es am besten: Max 2-3 Tasks pro Sub-Agent, frische 200k-Fenster, Stop BEVOR Qualität sinkt. Ralph erzwingt es per Bash-Kill. autonomous-stan hat aktuell NULL Lösung dafür.

**2. Hooks die blocken = ~95% Compliance. Alles andere ≤ 40%.**
Die brutale Wahrheit aus der OpenClaw-Praxis: AGENTS.md-Regeln werden ignoriert (Graphiti-Gate übersprungen, Karte nicht zuerst erstellt, Browser-Hygiene missachtet — alles in MEMORY.md dokumentiert). Nur was technisch blockiert (Tool-Deny, Pre-Tool-Use Hook mit `deny`), wird zuverlässig eingehalten. Das ist die wichtigste Designentscheidung für v2: **Enforcement durch Technik, nicht durch Prosa.**

**3. Kein Framework hat alles — aber die Kombination ist klar.**
- **Superpowers** hat die beste Enforcement-Philosophie (HARD-GATES, Anti-Rationalization)
- **GSD** hat die beste Context-Rot-Lösung (frische Sub-Agents, Task-Atomisierung)
- **BMAD** hat die beste Skalierung (Level 0-4, drei Tracks)
- **Ralph** hat die beste autonome Loop (Fresh Context, Completion Signal)
- **PRPs** hat die beste Codebase-Intelligence (Explore before Research, Patterns to Mirror)
- **Everything-CC** hat die besten Quality Gates (6-Phase Verification Loop)
- **Beads** hat das beste Task-Tracking (Hash-IDs, Dependency Graph, Compaction)
- **taming-stan** hat die besten funktionierenden Guards (Credential-Schutz, 3-Strikes)
- **OpenClaw** hat die beste Produktionsreife (Pre-Compaction Flush, Session Pruning, Multi-Agent)

**4. autonomous-stan v1 ist zu 80% Theorie, 30% Praxis.**
357 Unit Tests grün, aber nie in einem echten Projekt außerhalb seiner selbst getestet. hooks.json für Plugin-Distribution fehlt. Das Evaluator-Hook-Experiment funktioniert, ist aber nicht integriert. Der kritischste Blocker: **Praxis-Validierung vor weiterer Theorie-Arbeit.**

**5. Das Criteria-System ist autonomous-stans Unique Selling Point.**
24 Criteria in YAML mit atomaren Checks, required-Flags und Evaluator-Model-Angabe — das hat KEIN anderes Framework. Superpowers hat Review-Agents (flexibler aber nicht reproduzierbar), BMAD hat Workflows (aber keine atomaren Quality Gates), Ralph hat gar nichts. **Das Criteria-System behalten und härter enforcen** ist die richtige Strategie.

**6. Die 21 Techniques sind einzigartig und unterbewertet.**
Kein anderes Framework hat ein vergleichbares System strukturierter Denkmethoden. BMAD hat 60+ Brainstorming-Techniken, aber die sind nur für Ideation. autonomous-stans Techniques decken Root Cause Analysis, Perspective Shift, Decision Making, Self Reflection ab. **Techniques + Criteria = die Kombination die kein Competitor hat.**

**7. Dual-Target (Claude Code + OpenClaw) ist machbar — aber nur wenn der Kern plattformagnostisch bleibt.**
Criteria (YAML), Techniques (YAML), Templates (Markdown+YAML), Tasks (JSONL) — all das ist plattformagnostisch. Hooks sind Claude-Code-spezifisch. Skills sind OpenClaw-spezifisch. Der Kern muss sauber von der Runtime getrennt werden.

### Was hat uns am meisten überrascht?

- **BMAD's "21 Agents" sind nur 21 YAML-Dateien.** Kein Multi-Agent-System — ein Koch mit 21 Kochmützen. OpenClaw hat 12 echte Köche.
- **GSD's Context-Rot-Curve ist quantifizierbar:** 0-30% = Peak, 30-50% = Good, 50-70% = Degrading, 70%+ = Rushed. Das erklärt VIELE Probleme die wir "Fehler" nannten.
- **Superpowers' Anti-Rationalization Tables funktionieren psychologisch**, weil sie Cialdini-Prinzipien nutzen. "Thinking 'skip TDD just this once'? Stop. That's rationalization." — effektiver als jede Regel.
- **OpenClaw's Pre-Compaction Memory Flush ist genial** — ein Silent-Turn schreibt Learnings auf Disk BEVOR Auto-Compaction den Context löscht. autonomous-stan verliert Learnings bei jedem Compact.

---

## Teil 2: Feature-Matrix

| Feature | Superpowers | BMAD | Ralph | GSD | PRPs | Beads | Everything-CC | OpenClaw | taming-stan | autonomous-stan |
|---------|:-----------:|:----:|:-----:|:---:|:----:|:-----:|:-------------:|:--------:|:-----------:|:---------------:|
| **Brainstorming/Dialog** | ✅ Socratic | ✅ 60+ Techniken | ❌ | ✅ discuss-phase | ✅ PRD-Interview | ❌ | ❌ | ❌ | ❌ | ✅ DEFINE Phase |
| **Task-Tracking** | ⚠️ TodoWrite | ⚠️ Workflow-Docs | ✅ prd.json | ✅ ROADMAP.md | ✅ PRD Phases | ✅ JSONL+Graph | ❌ | ✅ BusinessMap | ❌ | ✅ tasks.jsonl |
| **TDD** | ✅ Iron Law | ✅ ATDD/TEA | ❌ | ⚠️ TDD Plans | ❌ | ❌ | ✅ TDD Workflow | ❌ | ❌ | ⚠️ Criteria only |
| **Memory/Learnings** | ❌ | ❌ | ✅ progress.txt | ⚠️ STATE.md | ❌ | ❌ | ✅ Auto-Extract | ✅ Markdown+Vector | ✅ Graphiti | ✅ Tiered Storage |
| **Guards/Enforcement** | ✅ HARD-GATE | ❌ Prompt only | ❌ | ❌ | ❌ | ❌ | ✅ Hooks | ✅ Tool-Deny | ✅ Python Guards | ⚠️ Designed only |
| **Subagents** | ✅ 3 pro Task | ⚠️ Party Mode | ❌ | ✅ Wave-Parallel | ⚠️ Review Agents | ❌ | ✅ 9 Agents | ✅ sessions_spawn | ❌ | ⚠️ Geplant |
| **Scale-Adaptive** | ❌ | ✅ Level 0-4 | ❌ | ⚠️ Quick Mode | ❌ | ❌ | ❌ | ❌ | ❌ | ⚠️ Levels definiert |
| **Visual Verification** | ❌ | ❌ | ✅ Browser-Pflicht | ❌ | ✅ Level 5 Valid. | ❌ | ❌ | ⚠️ Browser-Skill | ❌ | ⚠️ Criteria exists |
| **Code Review** | ✅ Two-Stage | ⚠️ TEA | ❌ | ❌ | ✅ Multi-Agent | ❌ | ✅ Code-Reviewer | ❌ | ❌ | ❌ |
| **Context Management** | ⚠️ CSO | ❌ | ✅ Fresh Context | ✅ 2-3 Tasks/Plan | ❌ | ✅ Compaction | ✅ Strategic Compact | ✅ Auto-Compact+Flush | ❌ | ❌ |
| **Criteria/Quality Gates** | ⚠️ Review-based | ⚠️ Readiness Gate | ❌ | ❌ | ✅ 6-Level Valid. | ❌ | ✅ Verification Loop | ❌ | ❌ | ✅ 24 YAML Criteria |
| **Templates** | ❌ | ✅ 50+ | ❌ | ❌ | ✅ PRD+Plan | ❌ | ❌ | ❌ | ❌ | ✅ 3 Templates |
| **Techniques/Thinking** | ❌ | ✅ 60+ Brainstorm | ❌ | ❌ | ✅ 5 Whys | ❌ | ❌ | ❌ | ✅ STAN.FLUX | ✅ 21 Techniques |
| **Git Integration** | ✅ Worktrees | ❌ | ✅ Branch+Archive | ✅ Atomic Commits | ✅ gh CLI | ✅ Git-backed DB | ✅ Git Workflow | ❌ | ✅ Conv. Commits | ⚠️ Geplant |
| **Multi-Agent** | ⚠️ Subagents | ⚠️ Personas (fake) | ❌ | ✅ Wave-Parallel | ✅ Review Agents | ❌ | ✅ 9 Agents | ✅ 12 echte Agents | ❌ | ⚠️ Geplant |
| **Persistent Memory** | ❌ | ❌ | ⚠️ Git only | ⚠️ .planning/ | ⚠️ .claude/PRPs/ | ✅ JSONL+SQLite | ✅ Learned Skills | ✅ Graphiti+Markdown | ✅ Graphiti | ✅ Tiered+Graphiti |
| **Context Rot Prevention** | ⚠️ CSO only | ❌ | ✅ Fresh per Iter. | ✅ 2-3 Tasks+Fresh | ❌ | ✅ Compaction | ✅ Strategic Compact | ✅ Pruning+Flush | ❌ | ❌ |
| **Autonomous Loop** | ⚠️ Subagent Loop | ❌ | ✅ Bash Loop | ✅ Wave Execution | ✅ /prp-ralph | ❌ | ❌ | ✅ Heartbeats | ❌ | ⚠️ Max Iterations |

**Legende:** ✅ = vollständig implementiert | ⚠️ = teilweise/geplant | ❌ = nicht vorhanden

---

## Teil 3: Compliance-Pyramide (Ehrliche Selbstreflexion)

### Die Compliance-Realität

Basierend auf 3 Wochen Produktionserfahrung mit 12 OpenClaw-Agents und den Erkenntnissen aus allen analysierten Frameworks:

| Enforcement-Methode | Compliance-Rate | Quelle/Beweis |
|---------------------|:--------------:|---------------|
| **Hook der blockt** (Tool-Deny, PreToolUse deny) | ~95% | taming-stan Credential-Guard, OpenClaw Tool-Deny. Nur umgehbar durch Bug oder bewusstes Workaround. |
| **Persuasive Sprache + Rationalization Tables** | ~70% | Superpowers' "Iron Law" + Excuse Tables. Effektiv weil sie das LLM's eigene Argumentation antizipieren. |
| **AGENTS.md Regel mit !! Notation** | ~40% | OpenClaw MEMORY.md: "NIE raten" → 3x geraten. "Karte zuerst" → oft vergessen. "Browser-Hygiene" → 40+ Tabs. |
| **Lange Prosa in Skill-Docs** | ~20% | Alles >500 Worte wird selektiv gelesen. BMAD's 17.835-Zeilen-Workflow ist Zeitverschwendung. |
| **Metakognition** ("erkenne deine Warnsignale") | ~0% | taming-stan plan.md Experiment: type:prompt Hooks "beraten, aber durchsetzen NICHT". Claude argumentiert gegen dumme Blocks statt zu gehorchen. |

### Was bedeutet das für autonomous-stan v2?

**1. Die Enforcement-Pyramide bestimmt die Architektur.**

Jedes Feature MUSS einer dieser Enforcement-Stufen zugeordnet werden:

| Stufe | Methode | Wann nutzen | autonomous-stan v2 |
|-------|---------|-------------|---------------------|
| **S1** | Hook der blockt | Sicherheit, Credentials, Phase-Gates | `stan_gate.py` (existiert) |
| **S2** | Persuasive Rationalization Tables | TDD, Code-Before-Test, Debugging | In Skills einbetten |
| **S3** | PITH-Regel in AGENTS.md | Workflows, Conventions | Bestehende `!!` Regeln |
| **S4** | Dokumentation in Skill-Docs | Nice-to-have Guidance | Techniques, Best Practices |

**2. "HARD-GATE" ist ein Design Pattern, kein Tag.**

Superpowers' `<HARD-GATE>` funktioniert weil es im FRISCHEN Skill-Context geladen wird. In einer langen Session mit 70% Context-Fill wirkt es nicht mehr. Die Lektion: **HARD-GATES müssen technische Hooks sein, nicht XML-Tags.**

**3. Die ~40% AGENTS.md-Compliance ist gut genug für Conventions.**

Nicht alles muss 95% Compliance haben. Git-Message-Format? 40% reicht — der Guard fixt den Rest. Browser-Tab-Limit? 40% reicht — ein Heartbeat räumt auf. **Reserve harte Enforcement für das was WIRKLICH zählt:** Credentials, Phase-Gates, Verification-Before-Completion.

**4. Metakognition ist Zeitverschwendung.**

"Erkenne wenn du in einem Loop bist" → Agent erkennt es nicht. "Frage dich ob du gerade rationalisierst" → Agent rationalisiert warum er nicht rationalisiert. **3-Strikes ist die mechanische Lösung:** Nach 3 gleichen Fehlern → Block → Perspective Shift. Kein Philosophie-Kurs.

### Die brutale Wahrheit für autonomous-stan v2

Was wir heute *wirklich* enforcen können:
- ✅ Credential-Schutz (taming-stan Guard → Port nach v2)
- ✅ Phase-Wechsel-Gates (stan_gate.py → existiert, muss getestet werden)
- ✅ Commit-Blocking bei offenen Learnings (stan_gate.py → existiert)
- ✅ 3-Strikes bei Fehler-Loops (taming-stan Pattern → Port nach v2)

Was wir *nicht* enforcen können und akzeptieren müssen:
- ❌ "Denke erst nach bevor du codest" — Agent codiert trotzdem
- ❌ "Nutze immer die richtige Technique" — Agent nutzt seine Standardmethode
- ❌ "Erkenne deine Limitierungen" — Agent überschätzt sich systematisch
- ❌ "Schreibe gute Commit Messages" — ~60% sind generisch (Guard für Conventional Commits hilft)

---

## Teil 4: autonomous-stan v2 — Synthese-Empfehlung

### CRITICAL: Sofort übernehmen

#### C1: Context Rot Prevention System
**Beschreibung:** Max 2-3 Tasks pro Sub-Agent-Aufruf. Hauptsession bleibt bei ≤40% Context (nur Orchestration). Sub-Agents bekommen frische 200k-Fenster. Stop-Signal bei >50% Context.  
**Quelle:** GSD (Kern-Feature) + Ralph (Fresh Context Pattern)  
**Priorität:** CRITICAL  
**Aufwand:** 4-6h  
**Begründung:** autonomous-stan hat aktuell NULL Lösung für Context Rot. GSD beweist: die Qualitätskurve ist real und messbar. Ohne diese Lösung degradiert jede lange Session unweigerlich. Aus der GSD-Analyse: "Claude degradiert in completion mode wenn Context >50-70% voll ist: 0-30% Peak Quality, 50-70% Efficiency Mode, 70%+ Rushed."

#### C2: Verification-Before-Completion Gate
**Beschreibung:** Kein Success-Claim ohne `run command + read output`. "Should work" = Lüge. Nur erlaubt: "[RAN npm test] [SAW: 47/47 pass] All tests pass." Integriert als Hook in stan_gate.py.  
**Quelle:** Superpowers (Verification Before Completion) + Everything-CC (6-Phase Verification Loop)  
**Priorität:** CRITICAL  
**Aufwand:** 3-4h  
**Begründung:** Aus der Superpowers-Analyse: "'Should pass' = Lying." Aus der OpenClaw-Praxis: Mehrfach "Done!" gesagt ohne zu verifizieren → Bugs in Production. Everything-CC's 6-Phase-Loop (Build → Types → Lint → Tests → Security → Diff) ist das konkrete Template.

#### C3: Credential-Schutz Guard
**Beschreibung:** 903 Regex-Patterns für API-Keys, Tokens, Passwörter. 3-Strikes-System bei Violations. Blockiert Graphiti-Writes die Secrets enthalten.  
**Quelle:** taming-stan (graphiti-guard.py, secret_patterns.py)  
**Priorität:** CRITICAL  
**Aufwand:** 2h (direkter Port aus taming-stan)  
**Begründung:** Aus der taming-stan-Analyse: "Credential-Schutz ist KRITISCH — 903 Patterns + 3-Strikes funktioniert." Ein Leak eines API-Keys in Graphiti wäre ein Security-Incident. Der Code existiert bereits in taming-stan — nur portieren.

#### C4: 3-Strikes Fehler-Loop-Breaker
**Beschreibung:** PostToolUse Guard der identische Fehler zählt. Nach 3 gleichen Fehlern → BLOCK → "Suche erst in Graphiti/Learnings nach bekannten Lösungen." Danach → Perspective Shift Technique erzwingen.  
**Quelle:** taming-stan (graphiti-retry-guard.py) + autonomous-stan Techniques  
**Priorität:** CRITICAL  
**Aufwand:** 3h  
**Begründung:** Aus der taming-stan-Analyse: "3-Strikes-Pattern bricht Loops — nach 3 Fehlern: Graph durchsuchen statt Retry." Aus MEMORY.md: Agent bleibt in Fehler-Loops stecken statt Perspektive zu wechseln. STAN.FLUX adressiert das verbal, 3-Strikes enforced es mechanisch.

#### C5: Praxis-Validierung (Test-Projekt + hooks.json)
**Beschreibung:** hooks.json mit ${CLAUDE_PLUGIN_ROOT} erstellen. Plugin in echtem Projekt installieren. Full Workflow durchlaufen (DEFINE → PLAN → CREATE). Edge Cases dokumentieren.  
**Quelle:** current-state Analyse (80% Theorie, 30% Praxis)  
**Priorität:** CRITICAL  
**Aufwand:** 8-12h  
**Begründung:** Aus der Current-State-Analyse: "357 Unit Tests grün, aber nie in echtem Projekt außerhalb autonomous-stan verwendet." und "hooks.json fehlt — Plugin nicht installierbar." Keine weitere Theorie-Arbeit ohne Praxis-Validierung. Das ist der kritischste Blocker.

---

### HIGH: Nächste Iteration

#### H1: Scale-Adaptive Workflow-Routing
**Beschreibung:** Projektkomplexität automatisch erkennen (Story-Count, Epic-Count, Integration-Count). Route zu richtigem Track: Quick Flow (≤3 Stories, skip Architecture), Standard (4-10 Stories), Complex (>10 Stories, Architecture required).  
**Quelle:** BMAD (Level 0-4, drei Tracks)  
**Priorität:** HIGH  
**Aufwand:** 6-8h  
**Begründung:** Aus der BMAD-Analyse: "Das ausgereifteste Scaling-System aller Frameworks." autonomous-stan behandelt aktuell alle Projekte gleich — ein Config-Fix braucht keinen PRD. Complexity-Levels (0-4) sind definiert aber nicht enforced. BMAD zeigt wie: Auto-Detection nach `/stan plan` basierend auf Story-Count.

#### H2: Two-Stage Code Review (Spec → Quality)
**Beschreibung:** Bei jedem Task erst Spec-Compliance (nichts fehlt, nichts extra), dann Code-Quality (erst nach Spec-Approval). Zwei separate Sub-Agents. Issue-Severity: Critical/Important/Minor.  
**Quelle:** Superpowers (requesting-code-review, receiving-code-review)  
**Priorität:** HIGH  
**Aufwand:** 4-5h  
**Begründung:** Aus der Superpowers-Analyse: "Stage 1: Spec-Compliance (nichts fehlt, nichts extra). Stage 2: Code Quality (erst nachdem Spec grün ist!). Verhindert, dass gut geschriebener Code shipped wird, der das Falsche tut." Unsere bisherigen Reviews prüfen beides gleichzeitig → Spec-Gaps werden übersehen.

#### H3: Patterns-to-Mirror in Plan-Template
**Beschreibung:** Plan-Template um "Patterns to Mirror"-Sektion erweitern. Jedes Pattern mit SOURCE (`file:line`) und Code-Snippet. Agent MUSS vor Implementation bestehende Patterns finden und dokumentieren.  
**Quelle:** PRPs (Codebase-Intelligence, Explore Agent)  
**Priorität:** HIGH  
**Aufwand:** 2-3h  
**Begründung:** Aus der PRPs-Analyse: "Kein anderes Framework erzwingt so rigoros 'Codebase ZUERST, Research ZWEITER'." und "Neuer Code spiegelt exakt bestehende Conventions." Verhindert das #1-Problem: Agent erfindet neue Patterns statt bestehende zu nutzen.

#### H4: Anti-Rationalization Tables in kritischen Skills
**Beschreibung:** Systematische Excuse→Reality Tabellen in TDD-Skill, Debugging-Skill und Verification-Skill. "Thinking 'skip TDD just this once'? Stop. That's rationalization."  
**Quelle:** Superpowers (Rationalization Tables, persuasion-principles.md)  
**Priorität:** HIGH  
**Aufwand:** 2h  
**Begründung:** Aus der Compliance-Pyramide: Persuasive Sprache = ~70% Compliance. Das ist die zweitstärkste Enforcement-Methode nach Hooks. Superpowers nutzt Cialdini-Prinzipien bewusst — Commitment/Consistency, Social Proof ("Every great developer tests first"). Kein anderes Framework macht das so systematisch.

#### H5: Architecture Decision Records (ADRs)
**Beschreibung:** Template `docs/adr/ADR-XXX-template.md` mit Context, Decision, Consequences, Alternatives, Status. Pflicht bei Multi-Epic-Projekten (>5 Stories). Verhindert Agent-Konflikte bei paralleler Arbeit.  
**Quelle:** BMAD (Architecture Workflow) + Everything-CC (architect.md Agent)  
**Priorität:** HIGH  
**Aufwand:** 3h  
**Begründung:** Aus der BMAD-Analyse: "Phase 3: Solutioning ist DAS fehlende Puzzleteil für Multi-Epic-Projekte." und "ADRs sind der Schlüssel zur Vermeidung von Agent-Konflikten." Beispiel ohne ADRs: Agent 1 nutzt REST, Agent 2 nutzt GraphQL → Integration Nightmare. Mit ADR-001: "GraphQL für alle APIs" → Konsistenz.

#### H6: Discuss-Phase (Graubereich-Erkennung)
**Beschreibung:** VOR dem Planning: Graubereiche identifizieren basierend auf Feature-Typ (Visual → Layout-Fragen, API → Error-Handling-Fragen, Data → Schema-Fragen). User-Entscheidungen in CONTEXT.md locken. Planner MUSS gegen CONTEXT.md validieren.  
**Quelle:** GSD (discuss-phase, CONTEXT.md)  
**Priorität:** HIGH  
**Aufwand:** 4-5h  
**Begründung:** Aus der GSD-Analyse: "CONTEXT.md lockt User-Entscheidungen. PLAN.md muss self-check: Jede locked decision hat Task, keine deferred idea wird implementiert." autonomous-stan springt von DEFINE direkt zu PLAN ohne systematische Graubereich-Klärung. Das führt zu Annahmen die der User nicht getroffen hat.

#### H7: Git Worktrees als Standard-Workflow
**Beschreibung:** Default für Feature-Development: Worktree statt Branch-Switching. Safety-Check: `.worktrees` in `.gitignore`. Automatische Directory-Selection (existing → CLAUDE.md → ask). Integration in CREATE-Phase.  
**Quelle:** Superpowers (using-git-worktrees)  
**Priorität:** HIGH  
**Aufwand:** 3h  
**Begründung:** Aus der Superpowers-Analyse: "Parallel Development ohne Branch-Switching, saubere Isolation." Superpowers macht Worktrees zum Default — nicht optional, nicht "wenn du willst", sondern Standard. autonomous-stan hat es als Konzept, Superpowers hat es als enforced Workflow.

---

### MEDIUM: Nice-to-have

#### M1: Systematic Debugging (4-Phase Protocol)
**Beschreibung:** STAN.FLUX durch strukturiertes 4-Phase-Protocol ersetzen: Root Cause Investigation (MUSS abgeschlossen sein) → Pattern Analysis → Hypothesis Testing → Implementation. Regel: 3+ failed fixes = question architecture.  
**Quelle:** Superpowers (systematic-debugging) + PRPs (5 Whys)  
**Priorität:** MEDIUM  
**Aufwand:** 3-4h  
**Begründung:** STAN.FLUX ist fuzzy ("stuck, raten, Fehler-Loops"). Superpowers' Debugging ist strukturierter: Phase 1 MUSS vor Fixes abgeschlossen sein. PRPs ergänzt 5 Whys mit Evidence-Chain (jedes "Because" braucht `file:line`-Proof).

#### M2: Atomic Git Commits pro Task
**Beschreibung:** 1 Task = 1 Commit. Format: `{type}({task-id}): {description}`. Types: feat|fix|test|refactor|docs|chore. Staging einzeln (NIE `git add .`). Git bisect wird möglich.  
**Quelle:** GSD (Atomic Commits) + taming-stan (git-workflow-guard.py)  
**Priorität:** MEDIUM  
**Aufwand:** 2h  
**Begründung:** Aus der GSD-Analyse: "Jeder Task = 1 Commit. Git bisect findet exakten failing Task. Jeder Task independently revertable." taming-stan hat bereits einen Git-Workflow-Guard der Conventional Commits erzwingt — direkt portierbar.

#### M3: Wave-basierte Parallel Execution
**Beschreibung:** Dependency Graph analysieren → Tasks in Waves gruppieren (Wave 1: keine Dependencies parallel, Wave 2: depends on Wave 1, etc.). File-Ownership Prevention: Overlap → sequential, no overlap → parallel.  
**Quelle:** GSD (Wave Execution)  
**Priorität:** MEDIUM  
**Aufwand:** 6-8h  
**Begründung:** Aus der GSD-Analyse: "Task A (User model): Wave 1 → Task C (User API): needs A → Wave 2". autonomous-stan hat Multi-Agent als Konzept aber keine automatische Dependency-Graph→Wave-Zuordnung.

#### M4: Deviation Rules (Auto-Fix vs Ask)
**Beschreibung:** Explizite Rules für autonome Bug-Fixes: Rule 1-3 (Bug, Missing Critical, Blocker) = Auto-fix + Track. Rule 4 (Architectural Change: neue Tabelle, Schema, Framework-Switch) = STOP → Ask User.  
**Quelle:** GSD (Deviation Rules 1-4)  
**Priorität:** MEDIUM  
**Aufwand:** 2h  
**Begründung:** Aus der GSD-Analyse: "Keine Permission für Basics, User-Input nur bei Design-Impact." autonomous-stan hat keine expliziten Deviation Rules — Agent fragt entweder zu viel oder zu wenig.

#### M5: Brownfield Analysis Workflow
**Beschreibung:** Neuer Command `/stan analyze-codebase`. Analysiert existierenden Code: Tech-Stack, Patterns (Naming, Directory), Test-Frameworks, Code Style (Linter Config), Dependencies. Output: `docs/codebase-analysis.md`.  
**Quelle:** BMAD (document-project Workflow)  
**Priorität:** MEDIUM  
**Aufwand:** 4-5h  
**Begründung:** Aus der BMAD-Analyse: "Brownfield-Support ist kritisch für Real-World-Adoption." autonomous-stan hat KEINE "Document Existing Project"-Logik. Die meisten echten Projekte sind Brownfield, nicht Greenfield.

#### M6: Pre-Compaction Memory Flush
**Beschreibung:** Silent-Turn vor Auto-Compaction der Learnings auf Disk schreibt. Verhindert Wissens-Verlust bei Context-Rotation. NO_REPLY Flag damit User keine Spam-Messages bekommt.  
**Quelle:** OpenClaw (Pre-Compaction Flush Architektur)  
**Priorität:** MEDIUM  
**Aufwand:** 3-4h  
**Begründung:** Aus der OpenClaw-Analyse: "Pre-Compaction Memory Flush ist genial — ein Silent-Turn schreibt Learnings auf Disk BEVOR Auto-Compaction den Context löscht." autonomous-stan's Learnings-System verliert alles was seit dem letzten expliziten Save passiert ist. OpenClaw hat das Problem gelöst — autonomous-stan sollte das Pattern portieren.

#### M7: Activity Log (Session-Level Debugging)
**Beschreibung:** Automatisches Logging: Was wurde getan, welche Dateien geändert, welche Tests liefen. Output: `docs/activity.md` als Debug-Hilfe.  
**Quelle:** Ralph (activity.md Pattern)  
**Priorität:** MEDIUM  
**Aufwand:** 2-3h  
**Begründung:** Aus der Ralph-Analyse: "Activity Log fehlt — nur Learnings. Session-Level-Debugging ist blind ohne Log."

---

### LOW: Später evaluieren

#### L1: Beads-Integration (Graph-basiertes Task-Tracking)
**Beschreibung:** JSONL Task-Storage mit Hash-based IDs, Dependency-Graph, `--json` API. Alternative zu `.stan/tasks.jsonl`.  
**Quelle:** Beads  
**Priorität:** LOW  
**Aufwand:** 8-12h  
**Begründung:** Beads ist mächtiger als unser JSONL, aber die Migration wäre aufwendig und autonomous-stan's Task-System funktioniert.

#### L2: Confidence Scoring für Learnings
**Beschreibung:** Jedes Learning bekommt Confidence (0.3-0.9), steigt bei Bestätigung, sinkt bei Widerlegung. Decay (-0.02/Woche ohne Beobachtung).  
**Quelle:** Everything-CC (continuous-learning-v2)  
**Priorität:** LOW  
**Aufwand:** 6-8h  
**Begründung:** Interessantes Konzept, aber widerspricht Zettelkasten-Prinzip. Alternative: `last_validated` Timestamp für Such-Ranking.

#### L3: Model Profiles (Quality/Balanced/Budget)
**Beschreibung:** Verschiedene Model-Profiles für Planner (Opus), Executor (Sonnet), Verifier (Haiku).  
**Quelle:** GSD (Model Profiles) + autonomous-stan Criteria (evaluator_model)  
**Priorität:** LOW  
**Aufwand:** 2-3h  
**Begründung:** autonomous-stan hat `evaluator_model` in Criteria — das Konzept existiert. Vollständige Profile sind Nice-to-have.

#### L4: BDUI-Style TUI für Task-Visualisierung
**Beschreibung:** Terminal-basierte Visualisierung des Task-Status, Dependencies, Phase-Progress.  
**Quelle:** BDUI  
**Priorität:** LOW  
**Aufwand:** 8-12h  
**Begründung:** Cool aber nicht essentiell. `/stan statusupdate` reicht für den Anfang.

---

## Teil 5: Architektur-Vorschlag autonomous-stan v2

### Dateistruktur

```
autonomous-stan/
├── .claude-plugin/
│   └── plugin.json              # Claude Code Plugin Manifest
├── commands/
│   └── autonomous-stan/         # /stan Commands (Claude Code)
│       ├── init.md              # Projekt starten
│       ├── define.md            # DEFINE Phase (Dialog)
│       ├── plan.md              # PLAN Phase (Tasks ableiten)
│       ├── create.md            # CREATE Phase (Autonom)
│       ├── think.md             # Techniques (Standalone)
│       ├── verify.md            # NEU: Verification Gate
│       └── analyze-codebase.md  # NEU: Brownfield Analysis
├── hooks/
│   ├── hooks.json               # Hook-Konfiguration
│   └── autonomous-stan/
│       ├── stan_context.py      # UserPromptSubmit: Phase-Reminder
│       ├── stan_gate.py         # PreToolUse: Phase-Gates + Blocks
│       ├── stan_track.py        # PostToolUse: Learnings + 3-Strikes
│       └── lib/                 # Shared Python Libraries
├── criteria/                    # Quality Gates (YAML)
├── techniques/                  # Denkmethoden (YAML)
│   └── purposes/                # 9 Einstiegspunkte
├── templates/                   # Dokument-Vorlagen
│   ├── adr.md.template          # NEU: ADRs
│   └── context.md.template      # NEU: Discuss-Phase Output
├── skills/                      # NEU: OpenClaw Skills (Dual-Target)
│   ├── techniques/SKILL.md
│   ├── brainstorming/SKILL.md
│   ├── verification/SKILL.md
│   └── tdd/SKILL.md
├── .stan/                       # Runtime State
│   ├── tasks.jsonl
│   └── session.json
└── docs/
    └── analysis/                # Diese Analysen
```

### Dual-Target: Claude Code + OpenClaw

```
┌─────────────────────────────────────────────────┐
│         PLATTFORM-AGNOSTISCHER KERN             │
│  Criteria (YAML) + Techniques (YAML)            │
│  Templates (Markdown) + Tasks (JSONL)           │
│  Learnings (JSON/JSONL)                         │
├─────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────────┐│
│  │ CLAUDE CODE      │  │ OPENCLAW             ││
│  │ .claude-plugin/  │  │ skills/              ││
│  │ commands/        │  │ AGENTS.md            ││
│  │ hooks/ (Python)  │  │ Graphiti             ││
│  │ settings.json    │  │ sessions_spawn       ││
│  └──────────────────┘  └──────────────────────┘│
└─────────────────────────────────────────────────┘
```

---

## Teil 6: OpenClaw-Rückportierung

### Was die 12 Agents SOFORT übernehmen können

| # | Skill | Trigger | Für wen | Aufwand |
|---|-------|---------|---------|---------|
| 1 | **Techniques** | "stuck", "problem", "think" | ALLE | 3-4h |
| 2 | **Brainstorming** | "brainstorm", "idee", "konzept" | Stan, Patrick, Klaus | 2-3h |
| 3 | **Verification-Before-Completion** | "fertig", "done", "review" | ALLE | 2h |
| 4 | **TDD-Enforcement** (verbessert) | "test", "TDD", "bug fix" | Stan, Patrick | 1-2h |
| 5 | **Scale-Adaptive Planning** | "plan", "projekt", "feature" | Stan, Klaus | 3-4h |
| 6 | **Context Rot Prevention** | Automatisch bei langen Sessions | ALLE | 1h |
| 7 | **Criteria-Checks** | "quality check", "criteria" | Stan, Patrick, Klaus | 4-5h |

**Gesamtaufwand Rückportierung: ~17-21h**

---

## Teil 7: Was NICHT übernehmen (und warum)

| Feature | Quelle | Warum NICHT |
|---------|--------|-------------|
| **21 Agent-Personas** | BMAD | OpenClaw hat 12 ECHTE Agents. Personas sind Theater. |
| **Session-End Hook** | Everything-CC | Graphiti löst das Problem besser. |
| **Strategic Compact Counter** | Everything-CC | Dummer Counter = Noise. OpenClaw hat Auto-Compact. |
| **Full Beads Integration** | Beads | JSONL reicht. Migration ohne klaren Benefit. |
| **BDUI TUI** | BDUI | Cool aber nicht essentiell. |
| **60+ Brainstorming-Techniken** | BMAD | 21 Techniques reichen. Qualität > Quantität. |
| **Installer-Script** | taming-stan | Claude Code hat Plugins. OpenClaw hat Skills. |
| **group_id Logik** | taming-stan | Direktive: "Nur main." |
| **Confidence Scoring** | Everything-CC | Widerspricht Zettelkasten. `last_validated` reicht. |
| **Claude Agent SDK** | SDK | OpenClaw sessions_spawn ist überlegen. |
| **Metakognitions-Regeln** | Diverse | 0% Compliance. 3-Strikes stattdessen. |

---

## Anhang: Quellen

Detail-Analysen unter `docs/analysis/`:
1. `superpowers.md` (557 Zeilen)
2. `bmad-method.md` (847 Zeilen)
3. `ralph.md` (642 Zeilen)
4. `get-shit-done.md` (575 Zeilen)
5. `prps-agentic-eng.md` (696 Zeilen)
6. `beads-bdui.md` (629 Zeilen)
7. `everything-claude-code.md` (822 Zeilen)
8. `openclaw-architecture.md` (511 Zeilen)
9. `taming-stan-and-sdk.md` (533 Zeilen)
10. `current-state.md` (747 Zeilen)

**Gesamtvolumen:** ~6.500 Zeilen Analyse, ~52KB Synthese

---

*Erstellt: 2026-02-16 | Autor: STAN | Karte: Board 5 #205*
