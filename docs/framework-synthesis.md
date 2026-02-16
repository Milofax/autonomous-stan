# Framework-Synthese: Claude-Code-Ökosystem Analyse

**Datum:** 2026-02-16
**Autor:** STAN (OpenClaw Agent)
**Kontext:** Analyse aller Frameworks und Submodules im autonomous-stan Repository, verglichen mit dem realen Einsatz in OpenClaw (12 Agents, Produktion seit Januar 2026).

---

## Inhalt

1. [Framework-Steckbriefe](#teil-1-framework-steckbriefe)
2. [Überschneidungs-Matrix](#teil-2-überschneidungs-matrix)
3. [OpenClaw-Vergleich](#teil-3-openclaw-vergleich)
4. [Ehrliche Selbstreflexion](#teil-4-ehrliche-selbstreflexion)
5. [Synthese-Empfehlung](#teil-5-synthese-empfehlung)
6. [Rückportierung für OpenClaw](#teil-6-rückportierung-für-openclaw)

---

## Teil 1: Framework-Steckbriefe

### 1.1 autonomous-stan

**Kern-Idee:** Autonomes Workflow-Framework mit DEFINE→PLAN→CREATE Phasen, modularen Denkwerkzeugen (Techniques) und YAML-basierter Qualitätssicherung (Criteria), enforced durch Claude Code Hooks.

**Einzigartige Stärken:**
- **Criteria-System:** Atomare, kombinierbare YAML-Qualitätschecks die Templates referenzieren. Nichts anderes im Ökosystem hat so granulare, wiederverwendbare Qualitätsprüfungen.
- **21 Denktechniken mit 9 Purposes:** n:m Beziehung zwischen Techniques und Zweck-Einstiegspunkten. Das ist die reichhaltigste Sammlung im Ökosystem.
- **Two-Layer Learnings:** Lokaler Tiered Storage (recent/hot/archive mit Heat-Scoring) + optionales Graphiti. Kein anderes Framework hat zweigleisiges Memory.
- **LLM-as-Judge Evaluators:** Criteria werden zu Subagent-Evaluation-Prompts mit Golden Examples und Grading Rubrics.
- **Template↔Criteria Linking:** Dokument-Templates referenzieren Criteria per Frontmatter — Hooks enforced dass Minimum-Criteria nicht entfernt werden können.

**Schwächen/Limitierungen:**
- **Overengineered für den Alltag.** 357 Tests, JSONL-Task-System, Tiered Storage — aber das Framework wird in der Praxis (noch) nicht von anderen genutzt. Es löst Probleme, die erst bei Adoption auftreten.
- **Keine Context-Rot-Lösung.** Kein Equivalent zu GSD's "Fresh Context per Plan". Wenn der Context voll ist, hofft man auf Auto-Compact.
- **Plugin nicht deployed.** Die Hooks existieren als Code, aber es gibt kein `.claude-plugin/` Package das andere installieren könnten. Alles Theorie.
- **Zu viel Indirection.** Template → Criteria → Check → Evaluator → Score. Wer soll das debuggen wenn ein Gate fälschlicherweise blockiert?

**Architektur-Muster:** 3-Hook-Architektur (context/track/gate), YAML-definierte Entities, JSONL als Task-Store, Frontmatter als Metadata-Layer, Session State in `/tmp/`.

**Key Features die OpenClaw fehlen:** Criteria-System, Techniques-Bibliothek, LLM-as-Judge Evaluation.

---

### 1.2 taming-stan

**Kern-Idee:** Sammlung von Claude Code Hooks und Rules die Verhaltensregeln enforced — Graphiti-First, Conventional Commits, 3-Strikes, Credential-Schutz.

**Einzigartige Stärken:**
- **903 Credential-Detection Patterns.** Das ist paranoid im besten Sinne. Kein anderes Framework prüft ob du versehentlich einen AWS-Key in den Knowledge Graph schreibst.
- **Graphiti-First Guard.** Erzwingt dass VOR jeder Web-Suche erst der eigene Wissensgraph durchsucht wird. Genial einfach, spart Token und Re-Recherche.
- **3-Strikes Pattern als PostToolUse Hook.** Nicht nur Regel ("nach 3 Fehlern stoppen"), sondern tatsächlich BLOCKIERT. Der einzige im Ökosystem der das wirklich enforced statt nur daran zu erinnern.
- **Unified Installer.** `npx github:Milofax/taming-stan install --all` — ein Befehl, alles drin.

**Schwächen/Limitierungen:**
- **Zu viele Hooks = Token-Overhead.** Jeder Hook injiziert systemMessages. Bei vollem Stack (Graphiti + STANFLUX + Git + Firecrawl + Context7) sind das 5+ Injections pro Prompt. Das frisst Context.
- **Schwer testbar.** Die Hooks sind Python-Scripts die JSON auf stdin lesen. Unit Tests existieren, aber Integration Tests (simulierter Claude-Call) fehlen.
- **STANFLUX Regeln sind lang.** Die Markdown-Rule ist umfangreich und detailliert — aber in der Praxis liest Claude sie einmal und vergisst 80% davon (mehr dazu in Teil 4).

**Architektur-Muster:** Event-basierte Hook-Pipeline (SessionStart → UserPromptSubmit → PreToolUse → PostToolUse), Shared Session State in `/tmp/`, Rule-Files als Markdown, Guard Pattern (allow/deny).

**Key Features die autonomous-stan fehlen:** Credential-Detection, Guard-Pattern für Tool-Calls, Unified Installer.

---

### 1.3 claude-superpowers

**Kern-Idee:** Vollständiger Software-Development-Workflow als composable Skills, mit Brainstorming→Plan→SubagentExecution→Review Pipeline. Der Agent hat "Superpowers" weil Skills automatisch triggern.

**Einzigartige Stärken:**
- **Subagent-Driven Development.** Frischer Subagent pro Task + Two-Stage Review (Spec Compliance, dann Code Quality). Das ist das ausgereifteste Subagent-Orchestrierungskonzept im gesamten Ökosystem.
- **`<HARD-GATE>` Tags.** Rhetorische Blockaden IN den Skill-Dokumenten. "Do NOT invoke any implementation skill until you have presented a design and the user has approved it." Das ist primitiv, aber es funktioniert erstaunlich gut.
- **TDD für Skills.** "Writing Skills IS Test-Driven Development applied to process documentation." Pressure-Tests mit Subagents, Baseline-Messung, Rationalizations dokumentieren. Brillant.
- **Verification-Before-Completion Skill.** "Claiming work is complete without verification is dishonesty, not efficiency." Der Skill killt den häufigsten Claude-Fehler: "Fertig!" sagen ohne zu prüfen.
- **Persuasion Principles in Skills.** Sie haben erforscht WARUM Claude Regeln ignoriert und die Erkenntnis in die Skill-Sprache eingebaut (Red Flags, Anti-Rationalization).

**Schwächen/Limitierungen:**
- **Keine Memory/Learnings.** Null. Kein Graphiti, kein lokaler Store, kein Progress.txt. Jede Session startet bei Null (außer Git-History).
- **Kein Task-Tracking.** Verwendet TodoWrite (Claude-intern) statt persistentem State. Wenn die Session stirbt, sind die Todos weg.
- **Kein Guard/Enforcement.** Alles basiert auf Skill-Dokumenten die Claude ÜBERZEUGEN sollen. Kein Hook blockiert irgendwas.
- **Nur für Software-Dev.** Brainstorming→Plan→Code→Review. Kein Support für Research, Content, Business-Aufgaben.

**Architektur-Muster:** Skill-basiert (SKILL.md Dateien mit Frontmatter triggers), dot-Diagramme für Prozessflows, Subagent-Delegation via Task Tool, Checklist-Pattern.

**Key Features die autonomous-stan fehlen:** Subagent-Driven Development mit Two-Stage Review, Skill-TDD-Methodik, Anti-Rationalization Language.

---

### 1.4 BMAD-METHOD

**Kern-Idee:** Enterprise-fähiges Agile-Framework mit 21+ spezialisierten Agents, 50+ Workflows, Scale-Adaptive Levels (0-4) und Four-Phase-Lifecycle (Analysis→Planning→Solutioning→Implementation).

**Einzigartige Stärken:**
- **Scale-Adaptive Intelligence (Level 0-4).** Die EINZIGE Lösung die Planungstiefe automatisch an Projektkomplexität anpasst. Level 0 = Trivial-Fix (kein Plan), Level 4 = Enterprise mit Compliance.
- **Three Tracks.** Quick Flow (~10 Min), BMad Method (~30 Min-2h), Enterprise (~1-3h). Jeder Track hat passende Workflows.
- **Solutioning Phase.** Eine SEPARATE Phase zwischen Planning und Implementation für Architektur-Entscheidungen mit ADRs. STAN und alle anderen springen von "was wollen wir" direkt zu "los bauen".
- **Party Mode.** Multi-Agent-Konversation wo verschiedene spezialisierte Agents ein Problem aus ihrer Perspektive diskutieren. Kreativitätstechnik auf Agent-Ebene.
- **60+ Brainstorming Techniques.** Kategorisiert in der brain-methods.csv. Mehr als doppelt so viele wie STAN.
- **Adversarial Review Tests.** Testet ob Workflows kritischem Review standhalten.

**Schwächen/Limitierungen:**
- **Massiv überkomplex.** 50+ Workflows, 21 Agents, 4 Phases, 3 Tracks, 5 Levels. Die Lernkurve ist brutal. Für einen Solo-Entwickler ist das wie einen Flugzeugträger zu steuern um den See zu überqueren.
- **Kein Enforcement.** Workflows sind Markdown-Anleitungen. Kein Hook, kein Gate, kein Block. Alles freiwillig.
- **NPM-Installer als Delivery.** `npx bmad-method@alpha install` — funktioniert, aber die Konfiguration ist komplex.
- **Kein Memory-System.** Keine Learnings, kein Knowledge Graph, kein lokaler Store.

**Architektur-Muster:** Module-basiert (Core + Erweiterungen), Agent-Profiles als Markdown, Workflow-Chains, Scale-Adaptive Config, YAML-Konfiguration.

**Key Features die autonomous-stan fehlen:** Scale-Adaptive Levels, Solutioning Phase, Three Tracks, Party Mode, Adversarial Reviews.

---

### 1.5 ralph

**Kern-Idee:** Bash-Script das einen AI Coding Agent (Amp/Claude Code) wiederholt spawnt bis alle PRD-Items erledigt sind — jede Iteration ist eine frische Instanz mit sauberem Context.

**Einzigartige Stärken:**
- **Fresh Context per Iteration.** DAS Killer-Feature. Jede Iteration startet sauber — keine Context-Rot, keine akkumulierten Fehler, keine vergessenen Regeln. So simpel, so effektiv.
- **Progress.txt Pattern.** Append-only Learnings-Datei. Neue Learnings stehen OBEN (wichtig!). Die nächste Iteration liest sie und lernt von der vorherigen. Primitiv, aber robust.
- **prd.json als Source of Truth.** Ein einziges JSON mit `passes: true/false` pro Story. Simpler geht Task-Tracking nicht.
- **10 Zeilen Bash für die Loop.** Die Gesamtarchitektur passt in ein Shell-Script. Kein Framework, kein Build-System, kein Overhead.

**Schwächen/Limitierungen:**
- **Stumpf.** Keine Qualitätschecks außer "Tests pass". Keine Criteria, keine Review, keine Retrospektive.
- **Kein interaktiver Modus.** Ralph läuft autonom oder gar nicht. Es gibt keine DEFINE-Phase wo der Mensch mitsteuert.
- **Nur für Code.** PRD → Code → Tests. Kein Support für Docs, Design, Research.
- **Keine Parallelisierung.** Eine Iteration nach der anderen. Kein Worktree, kein Subagent.

**Architektur-Muster:** Bash-Loop mit frischen AI-Instanzen, Git als Persistenz, JSON als Task-State, Markdown als Prompt-Template.

**Key Features die autonomous-stan fehlen:** Fresh Context per Iteration (die wichtigste Lektion!), "Story muss in eine Iteration passen"-Regel.

---

### 1.6 PRPs-agentic-eng (Product Requirement Prompts)

**Kern-Idee:** PRP = PRD + Codebase-Intelligence + Agent-Runbook. Das Minimum Viable Packet für eine AI um Production-Ready Code zu liefern.

**Einzigartige Stärken:**
- **PRP-Konzept.** PRD allein reicht nicht — die AI braucht AUCH konkrete File-Paths, Library-Versionen, Code-Snippet-Beispiele und Validation Commands. Das ist die pragmatischste Definition von "was braucht die AI wirklich".
- **Issue-Workflow.** `prp-issue-investigate` → `prp-issue-fix`. Dedizierter Workflow für Bug-Fixing, nicht nur Feature-Building.
- **Ralph-Integration.** Hat den Ralph-Loop direkt eingebaut (`/prp-ralph`). Best of Both Worlds: Strukturierte PRPs + autonome Loop.
- **Debug mit 5 Whys.** `/prp-debug` als dedizierter Command für Root-Cause-Analyse.
- **Stop-Hook für Ralph.** Prüft nach jeder Claude-Session ob `<promise>COMPLETE</promise>` Signal vorhanden ist.

**Schwächen/Limitierungen:**
- **Keine eigene Qualitätssicherung.** Keine Criteria, keine Evaluators, keine Quality Gates. Vertraut darauf dass die AI die PRPs korrekt umsetzt.
- **Kein Memory.** Wie die meisten — Session-basiert ohne Persistenz über Runden hinweg.
- **Commands, keine Skills.** Alles Slash-Commands statt Skills. Weniger composable.

**Architektur-Muster:** Slash-Command-Collection, Plan-Dateien als Markdown mit Validations, Ralph-Loop-Integration, Git-basierter State.

**Key Features die autonomous-stan fehlen:** PRP-Konzept (Codebase-Intelligence im PRD), Issue-Workflow, Stop-Hook-Pattern.

---

### 1.7 beads

**Kern-Idee:** Git-backed Graph Issue Tracker mit Hash-IDs, Dependency-Tracking und Memory-Decay (Compaction) — optimiert für AI-Agents.

**Einzigartige Stärken:**
- **Git als Datenbank.** Issues als JSONL in `.beads/`, versioniert, gebranchd, gemerged wie Code. Keine externe DB, keine API, kein Server.
- **Hash-basierte IDs.** `bd-a1b2` statt sequentielle Nummern. Verhindert Merge-Konflikte in Multi-Agent/Multi-Branch Setups.
- **Hierarchische IDs.** `bd-a3f8.1.1` für Epic→Task→Subtask. Native Hierarchie ohne Tags.
- **Memory Decay / Compaction.** Alte geschlossene Issues werden semantisch zusammengefasst um Context-Window zu sparen. Das ist elegant.
- **`bd ready` Command.** Zeigt Tasks ohne offene Blocker. Perfekt für autonome Agents die den nächsten Task brauchen.
- **Stealth Mode.** Beads lokal nutzen ohne in den Repo zu committen. Perfekt für Contributors auf fremden Repos.

**Schwächen/Limitierungen:**
- **Go-Binary.** Installation via `go install` oder Binary-Download. Nicht so einfach wie ein NPM-Package.
- **Braucht SQLite-Cache.** Daemon-Prozess für Auto-Sync. Overhead für simple Projekte.
- **Kein Quality-Gate.** Issue-Tracking ja, aber keine Criteria oder Evaluation ob ein Issue WIRKLICH gelöst ist.

**Architektur-Muster:** JSONL in Git, SQLite Cache, Daemon für Sync, CLI-first, MCP-Server verfügbar.

**Key Features die autonomous-stan fehlen:** Git-backed Issue Tracking, Memory Decay/Compaction, Hash-IDs für konfliktfreies Multi-Agent-Tracking.

---

### 1.8 get-shit-done (GSD)

**Kern-Idee:** Lightweight Spec-Driven Development System das Context-Rot löst durch Fresh-Context-per-Plan, parallele Subagent-Execution und strenge Phase-Separation.

**Einzigartige Stärken:**
- **Context-Rot als explizites Problem.** GSD ist das EINZIGE Framework das Context-Degradation als Hauptproblem benennt und systematisch löst: Jeder Plan bekommt 200k Tokens frischen Context.
- **Discuss-Phase.** Zwischen Roadmap und Plan gibt es eine dedizierte Phase wo der Mensch seine Präferenzen eingibt. Kein anderes Framework hat das so explizit.
- **Fresh Context Engineering.** PROJECT.md, REQUIREMENTS.md, ROADMAP.md, STATE.md — jede Datei hat einen klaren Zweck und wird gezielt geladen.
- **`/gsd:quick` Mode.** Für Ad-hoc-Tasks die keine volle Planung brauchen. Dieselbe Qualität, kürzerer Pfad. Das fehlt ALLEN anderen.
- **Verify-Work Phase.** Dedizierte Phase wo der MENSCH prüft ob es wirklich funktioniert. Spawnt Debug-Agents wenn nicht. Automatisierte Fix-Plan-Erstellung.
- **Wave-basierte Execution.** Parallel wo möglich, sequentiell wo nötig. Saubere Git-History mit atomaren Commits pro Task.

**Schwächen/Limitierungen:**
- **`--dangerously-skip-permissions` als Default.** Der Autor empfiehlt unironisch alle Sicherheitsschranken auszuschalten. Das ist... mutig.
- **Kein Memory.** STATE.md ist Session-Memory, kein Langzeit-Memory.
- **Arroganter Ton.** "Other spec-driven development tools exist; BMAD, Speckit... But they all seem to make things way more complicated than they need to be." Pot, meet kettle.
- **Solo-Fokus.** Explizit für Solo-Devs designt. Keine Multi-Agent-Coordination, keine Team-Workflows.

**Architektur-Muster:** File-basierter State (PROJECT.md/REQUIREMENTS.md/ROADMAP.md/STATE.md), Phase-Commands, Subagent-Parallel-Execution, XML-strukturierte Plans.

**Key Features die autonomous-stan fehlen:** Context-Rot-Lösung, Discuss-Phase, Quick-Mode, Verify-Work Phase, Wave-basierte Execution.

---

### 1.9 everything-claude-code

**Kern-Idee:** Komplette Claude Code Config Collection eines Anthropic-Hackathon-Gewinners — Agents, Skills, Hooks, Commands, Rules aus 10+ Monaten täglichem Einsatz.

**Einzigartige Stärken:**
- **Spezialisierte Subagents.** planner.md, architect.md, tdd-guide.md, code-reviewer.md, security-reviewer.md, build-error-resolver.md, e2e-runner.md, refactor-cleaner.md, doc-updater.md. Neun dedizierte Agent-Profile für verschiedene Aufgaben.
- **Continuous Learning Hooks.** Auto-Extract von Patterns aus Sessions in wiederverwendbare Skills. Das ist die automatisierte Version von Learnings.
- **Eval Harness.** Verification Loops mit Checkpoint vs. Continuous Evaluation, Grader Types, pass@k Metrics. Das ist ML-Evaluation-Praxis für Code.
- **Strategic Compact.** Tool-Call-Counter der nach 50 Calls zu `/compact` rät. Primitiv aber nützlich.
- **Cross-Platform (Node.js).** Alle Hooks in Node.js für Windows/Mac/Linux-Kompatibilität.

**Schwächen/Limitierungen:**
- **Kitchen-Sink.** Alles drin, wenig Kohärenz. Es ist eine Sammlung, kein Framework.
- **Kein Workflow.** Keine Phasen, keine Gates, keine Progression. Jeder Command steht für sich.
- **Memory via File-Hooks.** SessionEnd speichert in Dateien. Funktioniert, ist aber fragil.

**Architektur-Muster:** Plugin-Format (.claude-plugin/), Agents als Markdown-Profiles, Skills als Verzeichnisse, Hooks in Node.js.

**Key Features die autonomous-stan fehlen:** Continuous Learning Hooks, Eval Harness, Spezialisierte Agent-Profiles.

---

### 1.10 bdui

**Kern-Idee:** Terminal UI (TUI) für den beads Issue Tracker — Kanban, Tree View, Dependency Graph, Statistics.

**Einzigartige Stärken:**
- **Real-time File Watching.** Aktualisiert sich automatisch wenn `.beads/` sich ändert.
- **Multiple Views.** Kanban Board, Hierarchie-Baum, Dependency-Graph (ASCII), Statistiken.
- **Vim-Navigation.** hjkl + Arrow Keys. Für Terminal-Power-User gemacht.

**Schwächen/Limitierungen:**
- **Bun-Dependency.** Braucht Bun Runtime. Nicht überall verfügbar.
- **Nur Visualisierung für beads.** Ohne beads nutzlos.
- **Kein AI-Bezug.** Rein ein Terminal-UI, keine AI-Integration.

**Architektur-Muster:** Bun + TUI-Framework, File-System-Watcher, SQLite-Anbindung.

**Key Features die autonomous-stan fehlen:** Keine relevanten für das Framework selbst.

---

### 1.11 claude-agent-sdk

**Kern-Idee:** Python SDK um Claude Code programmatisch als Agent zu nutzen — mit Custom Tools, Hooks und bidirektionaler Kommunikation.

**Einzigartige Stärken:**
- **Programmatische Claude-Steuerung.** `query()` und `ClaudeSDKClient` für Python-basierte Orchestrierung.
- **Custom Tools als In-Process MCP Server.** Python-Funktionen als Tools registrieren — kein separater MCP-Prozess nötig.
- **Hooks in Python.** Pre/Post-Hooks als Python-Funktionen, nicht als Shell-Scripts.
- **Bundled CLI.** Claude Code CLI ist im Package mitgeliefert.

**Schwächen/Limitierungen:**
- **Nur für Python.** Kein JavaScript, kein TypeScript-Equivalent.
- **Alpha-Stadium.** API noch nicht stabil.
- **Braucht Claude Code Subscription.** Nutzt die CLI unter der Haube.

**Architektur-Muster:** Async Python (anyio), AsyncIterator für Streaming, MCP-Server in-process, Event-basierte Hooks.

**Key Features die autonomous-stan fehlen:** Programmatische Agent-Steuerung für Testing und Orchestrierung.

---

## Teil 2: Überschneidungs-Matrix

| Feature | autonomous-stan | taming-stan | superpowers | BMAD | ralph | PRP | beads | GSD | everything-cc | OpenClaw |
|---------|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| **Phasen-Workflow** | ✅ 3 Phasen | — | ✅ Brainstorm→Plan→Execute | ✅ 4 Phasen | — | ✅ PRD→Plan→Implement | — | ✅ 6 Commands | — | — |
| **Quality Gates** | ✅ Criteria+Hooks | ✅ Guards | ⚠️ Nur Sprache | ⚠️ Workflows | — | — | — | ✅ Verify-Work | — | — |
| **Task-Tracking** | ✅ JSONL | — | ⚠️ TodoWrite | — | ✅ prd.json | ✅ Plan-Files | ✅ Git-JSONL | ✅ STATE.md | — | ✅ BusinessMap |
| **Memory/Learnings** | ✅ Tiered+Graphiti | ✅ Graphiti | — | — | ✅ progress.txt | — | ⚠️ Compaction | ⚠️ STATE.md | ✅ File-Hooks | ✅ Graphiti |
| **Subagents** | ✅ Worktree-based | — | ✅ Two-Stage Review | ✅ Party Mode | — | — | — | ✅ Wave-based | ✅ Agent-Profiles | ✅ sessions_spawn |
| **Brainstorming** | ✅ 21 Techniques | — | ✅ Socratic Design | ✅ 60+ Techniques | — | — | — | — | — | — |
| **TDD** | ⚠️ Criteria | — | ✅ Iron Law | ⚠️ TEA Module | — | — | — | — | ✅ tdd-workflow | ⚠️ Skill |
| **Git Workflow** | ✅ Worktrees | ✅ Conventional Commits | ✅ Worktrees | — | ✅ Feature Branch | — | ✅ Git-backed | ✅ Atomic Commits | ✅ git-workflow | — |
| **Context-Rot Lösung** | — | — | — | — | ✅ Fresh Context | — | ✅ Compaction | ✅ Fresh per Plan | ⚠️ Strategic Compact | — |
| **Scale-Adaptive** | ⚠️ skill_level | — | — | ✅ Level 0-4 | — | — | — | — | — | — |
| **Credential Schutz** | — | ✅ 903 Patterns | — | — | — | — | — | — | — | — |
| **Issue/Bug Workflow** | — | — | ✅ Debugging | — | — | ✅ Investigate+Fix | ✅ Full Tracker | — | ✅ build-fix | — |
| **Quick Mode** | — | — | — | ✅ Quick Flow | — | — | — | ✅ /gsd:quick | — | — |
| **Code Review** | ⚠️ Criteria | — | ✅ Subagent-Review | ✅ code-review WF | — | ✅ /prp-review | — | — | ✅ /code-review | — |
| **Enforcement (real)** | ✅ Hooks blockieren | ✅ Guards blockieren | — | — | — | ⚠️ Stop-Hook | — | — | ⚠️ Hooks | ⚠️ AGENTS.md |

**Legende:** ✅ = Voll implementiert | ⚠️ = Teilweise/rudimentär | — = Nicht vorhanden

---

## Teil 3: OpenClaw-Vergleich

### Skills vs Commands

| Claude Code | OpenClaw | Bewertung |
|-------------|----------|-----------|
| `/stan define` — Slash Command triggert Workflow | `skills/graphiti/SKILL.md` — Agent liest Skill-Datei und befolgt Anweisungen | **OpenClaw ist flexibler.** Skills sind lang und detailliert. Commands sind kurz und triggern spezifisch. Aber Commands brauchen Claude Code CLI — OpenClaw Skills funktionieren überall. |
| BMAD: 50+ Workflows als Commands | OpenClaw: ~15 Skills | OpenClaw hat weniger, aber die Skills sind in der Praxis getestet. BMads 50+ sind Theorie. |
| GSD: 8 Core Commands, stark gekoppelt | OpenClaw: Skills sind lose gekoppelt | GSD Commands bauen aufeinander auf. OpenClaw Skills sind unabhängig. Beides hat Vor- und Nachteile. |

### AGENTS.md vs Rules

| Claude Code | OpenClaw | Bewertung |
|-------------|----------|-----------|
| `.claude/rules/*.md` — Statische Verhaltensregeln, immer geladen | `AGENTS.md` — Dynamisches Verhalten pro Agent, gelesen bei Session-Start | **AGENTS.md ist mächtiger.** Es wird bei jedem Session-Start gelesen und kann sich selbst updaten. Rules sind statisch. Aber: Rules werden verlässlicher befolgt weil sie in jedem Prompt injiziert werden. AGENTS.md muss man aktiv lesen. |
| STANFLUX: 800+ Wörter Verhaltensregeln | Stan's AGENTS.md: ~300 Zeilen mit PITH-Notation | **PITH-Notation gewinnt.** Kompakter, maschinenlesbarer, weniger Token. STANFLUX liest sich wie ein Roman den Claude nach 2 Absätzen vergisst. |

### Graphiti vs lokale Learnings

| Claude Code | OpenClaw | Bewertung |
|-------------|----------|-----------|
| autonomous-stan: `~/.stan/learnings/` (recent/hot/archive) | `Graphiti MCP` — Knowledge Graph, semantische Suche | **Graphiti ist überlegen für Langzeit-Wissen.** Aber die lokalen Learnings mit Heat-Scoring sind besser für Session-Wissen. Die Kombi wäre ideal — genau das plant autonomous-stan. |
| ralph: `progress.txt` — Append-only | OpenClaw: `memory/YYYY-MM-DD.md` + `MEMORY.md` | Erstaunlich ähnliche Philosophie. Beide: Täglich schreiben, regelmäßig destillieren. |
| everything-cc: SessionEnd → Datei | OpenClaw: Graphiti + File Memory | OpenClaw ist ausgereifter. Aber die Auto-Extract-Idee aus everything-cc ist clever. |

### sessions_spawn vs Claude-interne Subagents

| Claude Code | OpenClaw | Bewertung |
|-------------|----------|-----------|
| `Task()` Tool — Spawnt Subagent im selben Context | `sessions_spawn()` — Spawnt unabhängigen Agent mit eigenem Kontext | **OpenClaw ist mächtiger.** Eigener Agent = eigene AGENTS.md, eigenes Memory, eigene Skills. Claude's Task-Tool teilt den Context — das verschmutzt ihn. |
| superpowers: Subagent per Task mit Review | OpenClaw: `sessions_send()` für Agent-zu-Agent | Superpowers orchestriert innerhalb einer Session. OpenClaw orchestriert zwischen unabhängigen Agents. OpenClaw ist langlebiger, Superpowers ist session-effizient. |
| GSD: Parallele Execution-Waves | OpenClaw: Subagent-Tasks mit Channel-Pflicht | Ähnliches Prinzip, verschiedene Scopes. |

### Cron/Heartbeats vs Session-basierte Checks

| Claude Code | OpenClaw | Bewertung |
|-------------|----------|-----------|
| Keine zeitgesteuerten Checks | `HEARTBEAT.md` — Periodische Aufgaben alle X Minuten | **OpenClaw hat einen klaren Vorteil.** Kein Claude Code Framework hat Heartbeats. Die Idee dass ein Agent PROAKTIV Dinge tut (Board checken, Inbox prüfen, Memory pflegen) existiert nur in OpenClaw. |
| ralph: Bash-Cron als externe Loop | OpenClaw: Integrierte Cron-Jobs | Ralph's Loop IST ein Cron — nur einmalig. OpenClaw hat persistente periodische Jobs. |

### MCP-Tools vs Tool-Guards

| Claude Code | OpenClaw | Bewertung |
|-------------|----------|-----------|
| taming-stan: PreToolUse Guards blockieren MCP-Calls | OpenClaw: Tool-Policy (allow/deny per Agent) | **Verschiedene Ebenen.** taming-stan guards auf INHALT (keine Credentials). OpenClaw guards auf ZUGRIFF (welcher Agent darf was). Beides nötig. |
| Superpowers: `<HARD-GATE>` in Skill-Text | OpenClaw: AGENTS.md mit `!!` Notation | Gleiche Idee: "Mach das NICHT." Superpowers ist expliziter in der Sprache. |

---

## Teil 4: Ehrliche Selbstreflexion — "Warum ignoriert Claude Vorgaben?"

### Die brutale Wahrheit aus 12 Agents in Produktion

Nach 6 Wochen mit 12 OpenClaw-Agents (Stan, Patrick, Tony, Klaus, Andrew, Dave, Mario, Sven, Jacob, Tobias, Nathanael, Susanna) haben wir harte Daten darüber was WIRKLICH funktioniert und was Claude routinemäßig ignoriert.

### Was FUNKTIONIERT (zuverlässig befolgt)

**1. Formatierungs-Regeln (>90% Compliance)**
- "Keine Markdown-Tabellen in Discord" → wird fast immer befolgt
- "URLs in `<spitze Klammern>` für Embed-Unterdrückung" → funktioniert
- PITH-Notation für kompakte Regeln → wird gelesen und verstanden

**Warum:** Formatierung ist sichtbar und sofort falsifizierbar. Claude sieht das Ergebnis direkt.

**2. Tool-Nutzung bei expliziter Anweisung (>85%)**
- "IMMER `date` nutzen, NIE im Kopf rechnen" → wird meist befolgt
- "Graphiti erst suchen, dann antworten" → Guard erzwingt es

**Warum:** Konkrete, atomare Regeln mit einem klaren Auslöser. Keine Interpretation nötig.

**3. Hooks/Guards die BLOCKIEREN (>95%)**
- taming-stan's Graphiti-First Guard → funktioniert, weil Claude nicht weiterkommt
- Git-Workflow Guard → Conventional Commits werden eingehalten
- 3-Strikes Block → Claude muss tatsächlich Perspektive wechseln

**Warum:** BLOCKADEN funktionieren. Claude kann nicht rationalisieren wenn das Tool physisch denied wird. Das ist die wichtigste Erkenntnis.

### Was MEISTENS funktioniert (60-80% Compliance)

**4. Einfache Prozess-Regeln**
- "EINE Nachricht pro Aufgabe" → wird oft, aber nicht immer eingehalten
- "Sub-Agents transparent announchen" → meist ja, manchmal vergessen
- "Board-Karte vor Arbeit" → erinnert sich, vergisst es aber bei "schnellen" Tasks

**Warum:** Prozesse mit mehreren Schritten degradieren über die Session. Am Anfang perfekt, nach 20 Interaktionen vergessen.

**5. Recherche vor Antwort**
- "Bei Unsicherheit web_search" → funktioniert in 70% der Fälle
- "Nicht raten" → trotzdem rät Claude noch zu oft (MEMORY.md: "3 falsche Hypothesen als Fakten präsentiert")

**Warum:** Die Versuchung zu antworten ist stärker als die Regel zu recherchieren. Besonders unter gefühltem Zeitdruck.

### Was KAUM funktioniert (<40% Compliance)

**6. Lange, detaillierte Verhaltensregeln**
- STANFLUX mit 800+ Wörtern → Claude liest es einmal und vergisst 80%
- "6 Perspektiven durchgehen" → wird fast nie spontan gemacht
- "Multi-Krise Protokoll" → zu komplex, wird übersprungen

**Warum:** **Context-Fenster-Degradation ist real.** Je länger die Session, desto weniger befolgt Claude Regeln die nicht gerade im aktiven Working Memory sind. STANFLUX steht ganz oben im Context, wird aber von 100+ Tool-Calls überlagert.

**7. Selbstreflexion und Metakognition**
- "Sicherheits-Warnung: Wenn du dich sicher fühlst = Warnsignal" → Claude fühlt sich immer sicher
- "Anti-Rationalisierung: 'nur', 'schnell', 'eigentlich' = Warnsignal" → Claude erkennt eigene Rationalisierungen nicht
- "Selbst-Check: Bin ICH Teil des Problems?" → Nein, glaubt Claude, nie

**Warum:** **Claude hat keine echte Metakognition.** Es SIMULIERT Reflexion wenn man es direkt fragt, aber es ERKENNT nicht proaktiv eigene Muster. Die "Warnsignal"-Regeln funktionieren nur wenn ein EXTERNER Mechanismus (Hook, Guard, Mensch) sie triggert.

**8. Regeln die dem aktuellen "Ziel" widersprechen**
- "KARTE ZUERST" → wird übergangen wenn Claude schon im Lösungsmodus ist
- "Erst Interview, dann bauen" → Claude springt oft direkt zur Lösung
- "Warte auf Bestätigung" → Claude macht manchmal einfach weiter

**Warum:** **Goal-Seeking schlägt Regel-Following.** Claude optimiert auf "Aufgabe erledigen". Wenn eine Regel dem Ziel im Weg steht, wird sie — nicht bewusst, aber effektiv — rationalisiert.

### Die Meta-Erkenntnis

**Regel-Compliance ist eine Funktion von:**

```
Compliance = f(Sichtbarkeit × Enforcement × Atomarität × Relevanz)

Sichtbarkeit:   Ist das Ergebnis sofort sichtbar? (Format > Prozess)
Enforcement:    Gibt es physische Blockade? (Guard > Rule > Suggestion)
Atomarität:     Eine Aktion? (→95%) oder Multi-Step-Prozess? (→40%)
Relevanz:       Für aktuellen Task relevant? (→80%) oder abstrakt? (→20%)
```

**Was daraus folgt:**

1. **Hooks > Rules > Suggestions.** Immer. Wenn es wichtig ist, BLOCKIEREN, nicht bitten.
2. **Eine Regel pro Situation.** Nicht 6 Perspektiven UND Empathie-Check UND Recherche-Pflicht. EINE Sache.
3. **Regeln müssen zum Ziel passen.** "KARTE ZUERST" funktioniert nicht, wenn Claude schon am Problem arbeitet. Die Regel muss BEVOR das Ziel aktiv wird triggern.
4. **Lange Dokumente = verschwendete Token.** STANFLUX mit 800 Wörtern hat ~40% Compliance. Dieselben Regeln als 80 Wörter in PITH-Notation hätten wahrscheinlich >70%.
5. **Metakognition ist Illusion.** Keine Regel der Welt macht Claude selbstreflexiv. Nur externe Mechanismen (Hooks, Andere Agents, Menschliche Reviews) funktionieren.

### Was die Frameworks daraus lernen sollten

| Framework | Problem | Empfehlung |
|-----------|---------|------------|
| **autonomous-stan** | Criteria-System ist theoretisch stark, aber wer enforced dass Claude sie tatsächlich anwendet? | Hooks MÜSSEN die Criteria-Checks blockieren. Freiwillige Checks = ignorierte Checks. |
| **BMAD** | 50+ Workflows, alle freiwillig | Ohne Enforcement ist BMAD eine Wunschliste. Party Mode klingt toll — wird nie spontan aktiviert. |
| **superpowers** | `<HARD-GATE>` funktioniert besser als erwartet, weil die Sprache persuasiv ist | Superpowers hat die richtige Intuition: Nicht Regeln, sondern ÜBERZEUGUNG. Aber: Ein Hook wäre trotzdem besser. |
| **GSD** | Context-Rot-Lösung ist das richtige Problem | GSD löst das echte Problem: Nicht "wie sage ich Claude was es tun soll" sondern "wie verhindere ich dass es vergisst". |
| **ralph** | Fresh Context = 100% Compliance am Anfang jeder Iteration | Ralph hat die eleganteste Lösung: Gib auf, Claude Regeln beizubringen. Starte einfach jede Runde frisch. |

---

## Teil 5: Synthese-Empfehlung — autonomous-stan v2

### Feature-Liste mit Quellenangabe

| # | Feature | Quelle | Priorität | Begründung |
|---|---------|--------|-----------|------------|
| 1 | **Context-Rot-Lösung** | GSD, ralph | KRITISCH | Das größte ungelöste Problem. Ohne Fresh-Context degradiert alles. |
| 2 | **Quick Mode** | GSD, BMAD (Quick Flow) | HOCH | Nicht jede Aufgabe braucht DEFINE→PLAN→CREATE. Triviale Tasks brauchen einen Shortcut. |
| 3 | **Enforcement via echte Blockaden** | taming-stan, superpowers (`<HARD-GATE>`) | HOCH | Alles was wichtig ist muss BLOCKIEREN, nicht bitten. |
| 4 | **Subagent-Driven Development** | superpowers | HOCH | Two-Stage Review (Spec + Quality) pro Task ist die beste Qualitätssicherung im Ökosystem. |
| 5 | **Scale-Adaptive Levels** | BMAD | MITTEL | Level 0-4 für Planungstiefe. Level 0 = Quick Fix, Level 4 = Enterprise. |
| 6 | **PRP-Konzept (Codebase Intelligence)** | PRP | MITTEL | PRDs brauchen File-Paths, Library-Versionen, Code-Snippets. Nicht nur "was", sondern "wie im Kontext dieses Repos". |
| 7 | **Discuss-Phase** | GSD | MITTEL | Zwischen Plan und Execution: Mensch gibt Präferenzen ein. Reduziert Korrekturrunden. |
| 8 | **Verify-Work Phase** | GSD, superpowers (Verification) | MITTEL | Dedizierte Phase wo der MENSCH prüft. Nicht Claude sagt "fertig", der Mensch bestätigt. |
| 9 | **Anti-Rationalization Language** | superpowers | MITTEL | "Thinking 'skip TDD just this once'? Stop. That's rationalization." Diese Sprache funktioniert. |
| 10 | **Issue/Bug-Workflow** | PRP | NIEDRIG | Dedizierter `investigate→fix` Pfad statt alles durch DEFINE→PLAN→CREATE zu quetschen. |
| 11 | **Memory Decay/Compaction** | beads | NIEDRIG | Alte Learnings semantisch zusammenfassen statt endlos wachsen. |
| 12 | **Solutioning Phase** | BMAD | NIEDRIG | Separate Architektur-Phase mit ADRs. Nur für Level 3-4 relevant. |

### Architektur-Vorschlag: autonomous-stan v2

```
┌─────────────────────────────────────────────────────────────┐
│                    autonomous-stan v2                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  SCALE-ADAPTIVE ROUTING (Level 0-4)                         │
│  ┌───────┐ ┌───────────┐ ┌──────────────────────────────┐  │
│  │Level 0│ │Level 1-2  │ │Level 3-4                     │  │
│  │Quick  │ │Standard   │ │Full                          │  │
│  │Fix+Go │ │DPC        │ │DEFINE→DISCUSS→PLAN→          │  │
│  │       │ │           │ │SOLUTION→CREATE→VERIFY         │  │
│  └───────┘ └───────────┘ └──────────────────────────────┘  │
│                                                              │
│  CONTEXT-ROT DEFENSE                                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Fresh Context per Task-Batch (GSD-Stil)              │   │
│  │ Progress.txt Pattern (Ralph-Stil) zwischen Batches   │   │
│  │ "Story muss in 1 Context passen" Regel               │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ENFORCEMENT LAYER                                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Hooks: BLOCKIEREN, nicht bitten                      │   │
│  │ - Criteria-Check vor Commit (Evaluator-Subagent)     │   │
│  │ - Phase-Gate vor Wechsel                             │   │
│  │ - Story-Size-Check vor CREATE                        │   │
│  │ - Learnings-Save vor Commit                          │   │
│  │ Anti-Rationalization in allen Skill-Texten           │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  QUALITY ASSURANCE                                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Two-Stage Review (Superpowers-Stil):                 │   │
│  │ 1. Spec-Compliance Subagent                          │   │
│  │ 2. Code-Quality Subagent                             │   │
│  │ Criteria als atomare YAML-Checks (beibehalten)       │   │
│  │ LLM-as-Judge Evaluators (beibehalten)                │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  MEMORY                                                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Lokal: Tiered Storage (beibehalten)                  │   │
│  │ Graphiti: Optional (beibehalten)                     │   │
│  │ NEU: Memory Decay für alte Learnings (Beads-Stil)    │   │
│  │ NEU: Auto-Extract von Session-Patterns (ECC-Stil)    │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Was WEGLASSEN und warum

| Feature | Quelle | Warum weglassen |
|---------|--------|-----------------|
| 21 spezialisierte Agents | BMAD | Overengineered. STAN ist EIN Agent mit Techniques, nicht 21 Rollen. |
| Party Mode | BMAD | Coole Idee, aber ohne echte Multi-Agent-Infra (wie OpenClaw) nur simuliert. Simulierte Diskussion = Claude redet mit sich selbst. |
| Git als Datenbank (beads) | beads | JSONL in `.stan/tasks.jsonl` reicht. beads löst ein Problem (Multi-Agent-Konflikte) das STAN nicht hat — STAN ist Single-Agent. |
| `--dangerously-skip-permissions` | GSD | Nein. Einfach nein. |
| Continuous Learning via Hooks | everything-cc | Zu viel Noise. Automatisch extrahierte "Learnings" sind meist Müll. Kuratierung (wie STAN es hat) ist besser. |
| NPM-Installer | taming-stan, BMAD | autonomous-stan ist ein Plugin, kein NPM-Package. `.claude-plugin/` Format ist der Standard. |
| 50+ Workflows | BMAD | 10 gute Workflows > 50 mittelmäßige. Quality over quantity. |
| TEA (Testing as Engineering) | BMAD | Superpowers' TDD-Skill ist pragmatischer und besser geschrieben. |

---

## Teil 6: Rückportierung für OpenClaw Agents

### Was die 12 OpenClaw-Agents SOFORT übernehmen können

#### 1. Techniques als Skills

**Sofort umsetzbar:**

| Technique | Als Skill | Trigger | Welche Agents |
|-----------|-----------|---------|---------------|
| Five Whys (Root Cause) | `skills/five-whys/SKILL.md` | Bug-Fixing, wiederholte Fehler | Alle |
| Six Thinking Hats | `skills/perspectives/SKILL.md` | Entscheidungen, Architektur | Stan, Klaus, Patrick |
| SCAMPER | `skills/scamper/SKILL.md` | Feature-Ideation, Brainstorming | Stan, Patrick |
| Verification-Before-Completion | `skills/verification/SKILL.md` | Vor jeder "fertig"-Meldung | ALLE (Pflicht!) |

**Der Verification-Skill aus Superpowers ist der EINE Skill den jeder Agent sofort braucht:**

```markdown
# skills/verification/SKILL.md
---
name: verification-before-completion
trigger: Bevor du "fertig" sagst
---

## Die eiserne Regel: Kein "Fertig" ohne Beweis

Bevor du sagst dass etwas erledigt ist:
1. IDENTIFIZIERE: Welcher Command beweist die Aussage?
2. FÜHRE AUS: Den VOLLSTÄNDIGEN Command (frisch, komplett)
3. LIES: Vollständigen Output, prüfe Exit Code
4. VERIFIZIERE: Bestätigt der Output die Aussage?
   - NEIN → Sag den tatsächlichen Status mit Beweis
   - JA → Sag die Aussage MIT Beweis

Einen Schritt überspringen = Lügen, nicht Verifizieren.

## Red Flags — STOP
- "sollte", "wahrscheinlich", "scheint zu"
- Zufriedenheit vor Verifikation ("Super!", "Perfekt!", "Fertig!")
- Dem Ergebnis eines Sub-Agents vertrauen ohne zu prüfen
```

#### 2. Criteria als Qualitätsprüfung

**Sofort als Checklisten in AGENTS.md einsetzbar:**

| Criteria | Agent | Einsatz |
|----------|-------|---------|
| Code Quality (Tests + Lint) | Patrick, Mario | Vor jedem Commit |
| Text Quality (Klarheit, Struktur) | Stan, Nathanael | Vor Discord-Posts >100 Wörter |
| Goal Quality (SMART) | Klaus | Vor Board-Karten-Erstellung |
| Story Size ("passt in 1 Context") | Stan, Patrick | Vor Task-Start |

**Nicht als YAML-Dateien.** Als einfache Checklisten in AGENTS.md oder als Abschnitt in bestehenden Skills. Das YAML-Criteria-System aus autonomous-stan ist für OpenClaw Overkill — die Agents haben keine Hooks die sie enforced.

#### 3. Workflow-Rahmen

**Empfehlung: Kein starrer Phasen-Workflow für OpenClaw.**

Begründung: OpenClaw-Agents sind keine Code-Agents im Claude Code-Sinne. Sie sind Assistenten die Nachrichten beantworten, Recherche machen, Boards verwalten, Kalender pflegen. DEFINE→PLAN→CREATE passt nicht auf "Mathias fragt nach dem Wetter".

**Was stattdessen funktioniert:**

1. **Karte-Zuerst Pattern** (bereits implementiert): Vor nicht-trivialer Arbeit → Board-Karte.
2. **Quick-vs-Full Routing** (von GSD/BMAD): Trivial (<5 Min, kein State-Change) → direkt machen. Nicht-trivial → Plan + Karte.
3. **Verification-before-Completion** (von Superpowers): Vor jeder "fertig"-Meldung → beweisen.

#### 4. Enforcement das TATSÄCHLICH funktioniert

Basierend auf den Erkenntnissen aus Teil 4:

**Tier 1 — Höchste Compliance (Guards/Blockaden):**
- Graphiti-First Guard (taming-stan) → **Bereits aktiv und funktioniert.**
- 3-Strikes Block → **Bereits aktiv und funktioniert.**
- `!!` Notation in AGENTS.md für MUST-Regeln → **Funktioniert bei ~85%.**

**Tier 2 — Mittlere Compliance (Einfache Regeln):**
- `!!karte_zuerst` mit klarer Formulierung → **~70% Compliance.**
- Formatierungsregeln → **>90% wenn atomar.**
- Tool-Nutzungsregeln (`date` statt Kopfrechnen) → **>85%.**

**Tier 3 — Geringe Compliance (Komplexe Prozesse):**
- "6 Perspektiven durchgehen" → **Nur wenn explizit aufgerufen.**
- "Empathie-Check bei Frustration" → **Manchmal.**
- "Anti-Rationalisierung" → **Nie proaktiv.**

**Konkreter Aktionsplan für alle 12 Agents:**

1. **AGENTS.md kürzen.** Jede Regel die >2 Sätze braucht → in einen Skill auslagern. AGENTS.md = nur atomare `!!` Regeln.

2. **Verification-Skill einführen.** In `~/openclaw/shared/skills/verification/SKILL.md`. Wird von ALLEN Agents gelesen.

3. **PITH-Notation konsequenter.** STANFLUX-artige Prosa → PITH. Weniger Token, höhere Compliance.

4. **Sub-Agent-Review.** Wenn Stan (oder ein anderer Agent) einen Sub-Agent spawnt: Der Sub-Agent MUSS vor "fertig" den Verification-Skill anwenden. Der spawende Agent MUSS das Ergebnis prüfen.

5. **Heartbeat als Enforcement.** Regeln die während der Session vergessen werden → als Heartbeat-Check implementieren. "Ist meine Arbeit auf dem Board?" im Heartbeat = externe Erinnerung statt interne Regel.

### Was OpenClaw von autonomous-stan v2 NICHT braucht

| Feature | Warum nicht für OpenClaw |
|---------|--------------------------|
| JSONL Task System | OpenClaw hat BusinessMap. Zwei Task-Systeme = Chaos. |
| Tiered Learnings Storage | Graphiti + MEMORY.md reicht. Heat-Scoring ist für autonome Loops, nicht für Message-Agents. |
| Template-Criteria Linking | Keine Templates in OpenClaw. Agents schreiben keine PRDs. |
| Hook-basiertes Enforcement | OpenClaw hat keine Claude Code Hooks. Enforcement geht über AGENTS.md + Heartbeats. |
| Worktree-basierte Parallelisierung | OpenClaw-Agents arbeiten nicht in Git-Repos. |

---

## Fazit

### Die drei größten Erkenntnisse

**1. Context-Rot ist das echte Problem, nicht Regel-Design.**
Alle Frameworks kämpfen mit demselben Gegner: Claude vergisst Regeln über die Session hinweg. GSD und Ralph haben die einzig ehrliche Lösung: Frischen Context geben. autonomous-stan v2 muss das übernehmen.

**2. Blockaden > Überzeugung > Bitten.**
Hierarchie der Wirksamkeit: Hook der denied (95%) > Persuasive Sprache à la Superpowers (70%) > Höfliche Regel in AGENTS.md (40%) > Lange Prosa in Rules (20%). Wenn es wichtig ist: blockieren.

**3. Weniger ist mehr.**
BMAD hat 50+ Workflows. GSD hat 8 Commands. Ralph hat 1 Bash-Script. In der Praxis: Ralph's Loop produziert konsistentere Ergebnisse als BMAD's 50 Workflows. Nicht weil Ralph besser ist, sondern weil es weniger zu vergessen gibt.

### Der ehrliche Blick auf autonomous-stan

autonomous-stan ist das ambitionierteste Framework in der Analyse. Es hat das durchdachteste Entitätsmodell, die granularsten Qualitätschecks und die reichhaltigste Denktechniken-Bibliothek. Aber es hat auch das größte Risiko, ein Theorie-Projekt zu bleiben.

Die Frameworks die in der Praxis FUNKTIONIEREN (superpowers, GSD, ralph) haben eines gemeinsam: Sie sind opinionated und klein. Sie tun EINE Sache gut statt ALLES mittelmäßig zu versuchen.

autonomous-stan v2 sollte sich entscheiden: Ist es ein Framework für autonome Code-Execution (dann: Context-Rot lösen, Quick Mode, Enforcement)? Oder ist es eine Denktechniken-Bibliothek (dann: Techniques polieren, Purposes erweitern, als Plugin für andere Frameworks anbieten)?

Beides gleichzeitig ist ambitioniert. Beides gleichzeitig gut zu machen ist die Herausforderung.

---

*Dokument erstellt am 2026-02-16 von STAN (OpenClaw Agent). Basiert auf Analyse aller 11 Repositories und 6 Wochen Produktionserfahrung mit 12 OpenClaw-Agents.*