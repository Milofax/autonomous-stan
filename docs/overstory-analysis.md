# Overstory Framework — Deep Analysis für autonomous-stan

**Analysiert:** 2026-02-17  
**Quelle:** `/home/node/openclaw/workspace/repos-github/autonomous-stan/vendor/overstory`  
**Ziel:** Konzepte identifizieren, die für autonomous-stan (Claude Code Plugin) übernommen werden können

---

## 1. Architektur-Überblick

### Was ist Overstory?

Overstory ist ein **Multi-Agent Orchestration Framework** für Claude Code. Es verwandelt eine einzige Claude-Code-Session in ein Swarm-System: Agents laufen in parallelen `tmux`-Sessions, jeder in einem eigenen git Worktree, koordiniert über ein SQLite-basiertes Mail-System.

### Schichten-Architektur

```
User (Human)
    │
    ▼
Orchestrator (Claude Code Session im Projektroot)
    │  hooks: SessionStart → overstory prime
    │  hooks: UserPromptSubmit → overstory mail check --inject
    │
    ├── Coordinator (depth 0) — tmux Session
    │       └── Lead Agents (depth 1) — je ein tmux + git Worktree
    │               ├── Scout (depth 2) — read-only Exploration
    │               ├── Builder (depth 2) — implementiert Code
    │               └── Reviewer (depth 2) — validiert (read-only)
    │
    └── Merge Queue (SQLite FIFO)
            └── 4-Tier Resolution:
                1. Clean Merge (git)
                2. Auto-Resolve (konfliktmarker → incoming)
                3. AI-Resolve (claude --print)
                4. Re-imagine (neu implementieren)
```

### Kernkomponenten

| Komponente | Technologie | Zweck |
|---|---|---|
| Mail-System | SQLite (WAL mode) | Async-Kommunikation zwischen Agents |
| Session-Store | SQLite | Agent-State (booting→working→completed→zombie) |
| Events-Store | SQLite | Observability (Tool-Events, Timeline) |
| Merge-Queue | SQLite FIFO | Serialisierte Branch-Merges |
| Watchdog | Node.js Interval | Process-Monitoring mit progressivem Nudging |
| Hooks | settings.local.json | PreToolUse Guards per Capability |
| Worktrees | git worktree | Isolation pro Agent |
| tmux | Terminal Multiplexer | Parallele Claude-Sessions |

### Zwei-Schichten-Modell für Agent-Definitionen

Jeder Agent erhält zwei Instruktions-Layer:
- **Layer 1 (Base):** `agents/*.md` — das HOW (Workflow, Constraints, Capabilities) — wiederverwendbar
- **Layer 2 (Overlay):** Per-Task generiertes `CLAUDE.md` — das WHAT (Task-ID, File-Scope, Branch-Name)

Das Overlay wird von `overstory sling` generiert und in den Worktree geschrieben. Der Agent bekommt so genau das, was er für seine aktuelle Aufgabe braucht — nicht mehr.

### Agent-Rollen und ihre Constraintis

| Rolle | Read | Write | Spawn | Git Commit |
|---|---|---|---|---|
| Coordinator | ✅ | ❌ | Leads only | ❌ |
| Lead | ✅ | Specs only | Scout/Builder/Reviewer | ✅ (Worktree) |
| Scout | ✅ | `overstory spec write` only | ❌ | ❌ |
| Builder | ✅ | File-Scope only | ❌ | ✅ (Worktree) |
| Reviewer | ✅ | ❌ | ❌ | ❌ |
| Merger | ✅ | ✅ | ❌ | ✅ (Merge-Commit) |

---

## 2. Stärken — Was Overstory besser macht als autonomous-stan

### 2.1 Strukturierte Typed Message Protocol

Overstory hat ein **typisiertes Message-Protokoll** mit semantischen und protokollären Typen:

```typescript
type MailSemanticType = "status" | "question" | "result" | "error";
type MailProtocolType = "worker_done" | "merge_ready" | "merged" | "merge_failed" | 
                        "escalation" | "health_check" | "dispatch" | "assign";
```

Jeder Nachrichtentyp hat ein definiertes Payload-Schema (`WorkerDonePayload`, `MergeReadyPayload` etc.). Das macht Kommunikation **maschinenverarbeitbar**, nicht nur human-readable.

**autonomous-stan:** Kein vergleichbares strukturiertes Protokoll — alles ad-hoc.

### 2.2 Named Failure Modes

Jede Agent-Definition listet explizit **named failure modes** — konkrete, benannte Muster die schief gehen können:

- `HIERARCHY_BYPASS` — Coordinator spawnt Builder direkt (code-enforced)
- `SPEC_WITHOUT_SCOUT` — Specs schreiben ohne Exploration
- `REVIEW_SKIP` — merge_ready senden ohne Reviewer-PASS
- `SILENT_FAILURE` — Fehler nicht melden
- `PATH_BOUNDARY_VIOLATION` — Schreibzugriff außerhalb Worktree
- `MISSING_MULCH_RECORD` — Sitzung beenden ohne Learnings festzuhalten

**Warum das wertvoll ist:** Named Failures trainieren das Modell explizit, die typischen Fallen zu erkennen und zu benennen bevor es reinläuft. Die Agent-Definitionen sagen nicht nur WAS zu tun ist, sondern benennen explizit WAS NICHT getan werden darf und warum.

**autonomous-stan:** Failure Modes sind implizit in Criteria/Techniques versteckt.

### 2.3 "Propulsion Principle" als expliziter Anti-Zögerlichkeits-Mechanismus

Jede Agent-Rolle hat am Ende das "Propulsion Principle":

> _"Read your assignment. Execute immediately. Do not ask for confirmation, do not propose a plan and wait for approval, do not summarize back what you were told. Start [doing X] within your first tool call."_

Das ist **mechanisch erzwungen** als Teil jeder Rollendefiniton. Es bekämpft den häufigsten LLM-Bias: Bestätigung suchen statt handeln.

**autonomous-stan:** Phase-Enforcement via stan_gate, aber kein explizites Anti-Zögerlichkeits-Konstrukt in den Slash Commands.

### 2.4 Capability-basierte Tool-Guards via Hooks

Der `hooks-deployer.ts` generiert **capability-spezifische PreToolUse Guards** die mechanisch durchgesetzt werden:

- Scout/Reviewer: Write/Edit geblockt, Bash mit Whitelist
- Builder/Merger: Path-Boundary Check (Worktree-Isolation)
- Alle: git push zu canonical branch geblockt
- Alle: Claude native Team-Tools geblockt (Task, TeamCreate etc.)

**Besonders clever:** Der ENV_GUARD `[ -z "$OVERSTORY_AGENT_NAME" ] && exit 0` — Hooks sind nur aktiv wenn der ENV-Var gesetzt ist. User-Sessions bleiben unberührt.

**autonomous-stan:** Hooks sind global (kein capability-spezifisches Routing).

### 2.5 Progressive Escalation (Watchdog)

Das Watchdog-System implementiert **progressives Nudging** statt sofortiger Eskalation:

- Level 0: Warning (nur log)
- Level 1: tmux nudge ("you appear stalled")
- Level 2: AI Triage (claude --print analysiert Logs)
- Level 3: Session terminieren

Die Eskalationsstufe ist zeitbasiert (`nudgeIntervalMs`) und persistent (sessionStore). Failure wird via `mulch record` festgehalten für zukünftige Sessions.

**autonomous-stan:** loop_breaker ist ähnlich konzipiert, aber nur für Edit→Test-Paare, nicht für allgemeine Stall-Erkennung.

### 2.6 INSIGHT-Pattern für Read-Only Agents

Scouts und Reviewer können kein `mulch record` ausführen (read-only). Overstory löst das elegant:

> _"Prefix reusable findings with `INSIGHT:` in your result mail so your parent can record them."_

Format: `INSIGHT: <domain> <type> — <description>`

Das Parent-Agent nimmt die INSIGHTs aus der Mail und führt `mulch record` aus. Kein Write-Zugriff nötig, Wissen wird trotzdem persistent.

**autonomous-stan:** Kein vergleichbares Pattern. Learnings gehen oft verloren.

### 2.7 Conflict History Learning

Das Merge-System lernt aus vergangenen Konflikten via `mulch`:
- Wenn Tier X für Datei Y 2+ mal scheitert → Tier X für Y überspringen
- Erfolgreiche Resolutions werden als Kontext für AI-Resolver eingebettet
- Vorhergesagte Konfliktdateien aus historischen Patterns

Das ist **adaptive conflict resolution** — das System wird besser mit der Zeit.

### 2.8 Agent Identity (CVs) über Sessions hinweg

Jeder Agent hat eine persistente `identity.yaml` mit:
- Sessions completed
- Expertise domains
- Recent tasks (was wurde gemacht?)

Ein Builder-Agent mit 20 abgeschlossenen Sessions kann anders primed werden als einer mit 0.

---

## 3. Schwächen / Risiken

### 3.1 Eigene ehrliche Risikoanalyse (STEELMAN.md)

Overstory liefert im `STEELMAN.md` die besten Argumente **gegen sich selbst**. Zusammenfassung:

| Risiko | Kernproblem |
|---|---|
| Compounding Error Rates | 5% Fehler × 20 Agents = signifikant höhere Gesamtfehlerrate an Integration Boundaries |
| Cost Amplification | Echte Messung: $60 Swarm vs. $9 Single Agent für gleiche Arbeit |
| Coherent Reasoning verloren | Keine globale Konsistenz: userId vs user_id vs uid in parallel |
| Debugging = Forensics | git blame + Sessions-DB + Mail-Threads = teuer |
| Premature Decomposition | Zerlegung vor Verständnis ist oft falsch |
| Merge Conflicts normal | Shared files (types.ts, config) → unvermeidlich |

**Eigene Einschätzung:** Das Framework ist sich dieser Probleme bewusst. Die STEELMAN-Sektion ist ungewöhnlich ehrlich und schreibt explizit: "Most day-to-day engineering work is better served by a single focused agent."

### 3.2 Infrastructure-Komplexität als Hauptrisiko

Das System braucht: tmux + git worktrees + 4 SQLite-DBs + Watchdog-Daemon + Hooks + Dashboard TUI. Jeder Layer ist ein potenzieller Failure Mode. Die `overstory doctor` Checks decken 9 Kategorien ab — das gibt einen Hinweis auf die Komplexität.

### 3.3 Zero-Runtime-Dependencies als Constraint

"Zero runtime dependencies" ist ein explizites Hard Rule. Das bedeutet: eigener YAML-Parser (~200 Zeilen), eigene SQLite-Wrapper, kein npm-Paket verwenden. Das ist wartungsintensiv.

### 3.4 Mulch als kritische Abhängigkeit

`mulch` (externes CLI-Tool für structured expertise) ist tief integriert: `mulch prime`, `mulch record`, `mulch search` überall. Wer mulch nicht nutzt, verliert viel vom System.

### 3.5 Skalierungsgrenzen

Der eigene STEELMAN sagt: "Target 2-5 leads per batch, 2-5 builders per lead = 4-25 effective workers." Mit 25 Agents und 4 SQLite-DBs gleichzeitig im WAL-Modus — das ist ambitioniert.

---

## 4. Übernehmbare Konzepte für autonomous-stan

### P1 — Sofort übernehmbar

#### P1.1 Named Failure Modes in Slash Commands

**Konzept:** Jede `/stan` Command-Definition listet explizit die typischen Failure Modes.

**Umsetzung in autonomous-stan:**
```markdown
## Failure Modes (in /stan create)
- SCOPE_CREEP: Task Definition erweitert sich während Umsetzung → STOP, /stan define erneut
- SILENT_FAILURE: Fehler ignorieren und weitermachen → Immer surfaen
- QUALITY_GATE_SKIP: Criteria abgehakt ohne Evidenz → Evaluator greift ein
- LOOP_TRAP: 3x gleicher Fix → Systematic Debugging erzwingen
- RESEARCH_BYPASS: Technische Behauptungen ohne Recherche → Research Guard
```

**Warum P1:** Kein neues Tooling nötig. Nur Ergänzung der Command-Prompts. Hohe Wirkung weil LLMs explizit benannte Anti-Patterns besser erkennen.

---

#### P1.2 Propulsion Principle in /stan create und /stan plan

**Konzept:** Explizite Anti-Zögerlichkeits-Instruktion am Ende jeder Command-Definition.

**Umsetzung:**
```markdown
## Propulsion Principle
Lies das PRD/den Plan. Handle sofort. Frage NICHT nach Bestätigung, 
schlage KEINEN Plan vor und warte auf Approval, fasse NICHT zusammen was gesagt wurde.
Starte mit dem ersten sinnvollen Tool-Call. Wenn unklar: Minimal-Viable-Annahme treffen, 
handeln, im Evaluator-Check aufdecken.
```

**Warum P1:** Direkter Copy-Adapt aus Overstory. Bekämpft den häufigsten LLM-Bias bei autonomous-stan Nutzung.

---

#### P1.3 INSIGHT-Pattern für Research-Findings

**Konzept:** Wenn der Agent während `/stan create` relevante technische Erkenntnisse findet, soll er sie explizit als `INSIGHT:` taggen, damit sie in `MEMORY.md` oder Graphiti landen.

**Umsetzung in stan_context.py oder als Ergänzung zum Evaluator-Prompt:**
```
Wenn du während der Arbeit Erkenntnisse findest die zukünftigen Sessions nützen:
Prefix sie mit "INSIGHT: <domain> <type> — <description>" in deiner Zusammenfassung.
Stan wird sie in sein Langzeit-Gedächtnis übertragen.
```

**Warum P1:** Löst das Problem, dass Learnings aus autonomen Sessions verloren gehen. Aktuell wird das in autonomous-stan nicht systematisch gelöst.

---

#### P1.4 Capability-spezifische Hook-Guards (Erweiterung von research_guard)

**Konzept:** Der `research_guard.py` in autonomous-stan ist ein Universalguard. Overstory zeigt: Guards können nach Phase/Capability differenziert werden.

**Umsetzung:** In `stan_gate.py` oder separaten Hooks:
- Im `define`-Phase: Recherche-Tools erlaubt, kein Edit/Write
- Im `plan`-Phase: Nur Read+Task-Management, kein Edit
- Im `create`-Phase: Alles erlaubt, aber mit Loop-Breaker und Credential-Guard

**Warum P1:** Die Phase-Enforcement-Logik existiert bereits (stan_gate.py). Erweiterung um capability-spezifische Tool-Restriktionen wäre eine natürliche Ergänzung.

---

#### P1.5 Strukturierte Message Types im /stan complete Workflow

**Konzept:** Wenn Sub-Tasks (im /stan plan Output) von verschiedenen Sessions bearbeitet werden, sollte das Completion-Signal strukturiert sein.

**Umsetzung als Konvention (kein SQLite nötig):**
```yaml
# In task YAML oder Markdown
completion_signal:
  type: worker_done | review_pass | escalation
  from_phase: create | review
  files_modified: [...]
  gate_results:
    tests: pass | fail
    lint: pass | fail
    typecheck: pass | fail
```

**Warum P1:** Selbst ohne Multi-Agent-Infrastruktur macht strukturierte Completion bessere Auditierbarkeit möglich. Der Evaluator und Final Gate können gezielt prüfen.

---

### P2 — Mittelfristig wertvoll

#### P2.1 Tiered Conflict Resolution Pattern (konzeptuell)

**Konzept:** Overstory's 4-Tier-Merge-System ist elegant graduell:
1. Versuche das Einfachste (clean merge)
2. Automatische Auflösung (keep incoming)
3. AI-assisted
4. Re-imagine (neu von Grund auf)

**Konzeptuell für autonomous-stan:** Wenn ein `/stan create` Task scheitert, stufenweise Eskalation:
1. Retry mit demselben Approach
2. Systematic Debugging Technique erzwingen (loop_breaker tut das schon!)
3. AI-Triage: Claude analysiert selbst was schiefläuft
4. Task neu definieren (/stan define erneut mit neuem Scope)

**Warum P2:** Das loop_breaker.py implementiert bereits Level 1-2. Level 3-4 bräuchte mehr Prompting-Arbeit.

---

#### P2.2 Session Checkpointing für lange autonomous-stan Sitzungen

**Konzept:** Overstory's `SessionCheckpoint` speichert vor Compaction oder Handoff:
- Progress Summary (was wurde getan?)
- Files Modified
- Pending Work (was bleibt?)
- Current Branch

**Konzeptuell für autonomous-stan:** Vor kontext-intensiven langen Sessions könnte `/stan` einen Checkpoint in `memory/YYYY-MM-DD.md` schreiben:
```markdown
## Session Checkpoint [2026-02-17 14:30]
**Task:** Feature X
**Done:** Komponenten A, B erstellt, Tests grün
**Remaining:** Komponente C, Integration Tests
**Modified Files:** src/a.ts, src/b.ts
**Blockers:** Keine
```

**Warum P2:** Braucht eine neue Command-Ergänzung (`/stan checkpoint`), aber kein externes Tooling. Würde Continuity bei langen Sitzungen dramatisch verbessern.

---

#### P2.3 Tool Event Filtering (Smart Observability)

**Konzept:** Overstory's `tool-filter.ts` reduziert Tool-Event-Payloads von ~20KB auf ~200 Bytes durch Smart-Filtering:
- Bash: nur `command` + `description`, kein stdout
- Write: nur `file_path`, kein Content
- Edit: nur `file_path`, kein old/new string

**Konzeptuell für autonomous-stan:** Der `stan_track.py` trackt bereits Tool-Events. Eine ähnliche Filtering-Logik würde den Context-Overhead reduzieren und gezieltere Auswertung ermöglichen.

**Warum P2:** Technische Umsetzung erfordert Änderungen an stan_track.py. Mittelgroßer Aufwand.

---

#### P2.4 Capability-spezifische Agent-Definitionen für Sub-Agents

**Konzept:** Wenn autonomous-stan Sub-Agents nutzt (Claude Code hat Task-Tool), könnten die Rollen analog zu Overstory definiert werden:
- `scout`: Read-only Exploration, sammelt Context für Hauptagent
- `reviewer`: Unabhängige Validation (was der Evaluator-Hook jetzt als Prompt macht)

**Warum P2:** Sub-Agent-Nutzung in autonomous-stan ist noch nicht entwickelt. Das wäre ein größeres Feature.

---

### P3 — Nice-to-Have

#### P3.1 Named Capability Constants

**Konzept:** Overstory definiert Capabilities als TypeScript-Konstante:
```typescript
export const SUPPORTED_CAPABILITIES = ["scout", "builder", "reviewer", ...] as const;
```

Compile-time Validation verhindert Tippfehler.

**Für autonomous-stan:** YAML-Schema für Criteria und Techniques mit Validation würde ähnliche Sicherheit geben.

---

#### P3.2 Conflict History Pattern (Learning-Loop)

Das Pattern, aus vergangenen Merge-Konflikten zu lernen (welche Tiers für welche Dateien scheitern), wäre für autonomous-stan interessant als "welche Techniques für welche Problem-Typen funktionieren" — aber das ist sehr spezifisch und braucht Infrastruktur.

---

#### P3.3 Broadcast-Group-Adressen (@all, @builders)

Das `@capability`-Pattern für Broadcast-Messaging ist elegant für Multi-Agent-Systeme. Für autonomous-stan (single-session) irrelevant, aber interessant falls Sub-Agents später kommen.

---

## 5. Nicht übernehmbar — Overstory-spezifisch

### 5.1 tmux Session Management

Overstory's `worktree/tmux.ts` managed tmux-Sessions komplett: erstellen, attachen, Liveness-Check, kill. 

**Warum nicht:** autonomous-stan ist ein Single-Session Claude Code Plugin. Kein tmux, keine parallelen Sessions. Das ist ein fundamentaler Architektur-Unterschied.

### 5.2 Git Worktree Management

Jeder Agent lebt in einem eigenen git Worktree. `worktree/manager.ts` erstellt, listet und löscht sie. Path-Boundary-Guards prüfen ob Writes im korrekten Worktree landen.

**Warum nicht:** Keine Worktrees in autonomous-stan. single-branch, single-directory.

### 5.3 SQLite Mail-System

Das gesamte `mail/` Modul mit SQLite-Backend, WAL-Modus, Thread-Support, Priority-Queuing ist für inter-process Kommunikation zwischen echten parallelen Agents gebaut.

**Warum nicht:** Kein inter-process Messaging nötig. autonomous-stan läuft in einer Session.

### 5.4 Merge Queue + 4-Tier Resolver

Die FIFO Merge Queue mit tiered conflict resolution ist für parallele Branches die gemerget werden müssen.

**Warum nicht:** Kein Branch-based Parallelismus in autonomous-stan.

### 5.5 Watchdog Daemon (Tier 0 / Tier 1)

Process monitoring, PID liveness checks, tmux session liveness — alles für externe Prozesse.

**Warum nicht:** Kein externer Process zu monitoren. autonomous-stan lebt im Claude Code Process selbst.

### 5.6 Beads Issue Tracking Integration

Overstory ist tief mit `bd` (beads) integriert für Issue Lifecycle. 

**Warum nicht:** Wir nutzen BusinessMap (Kanban), nicht beads. Das Interface ist komplett anders.

### 5.7 Mulch CLI Integration

`mulch` ist ein separates CLI-Tool für structured expertise management (records, domains, search). 

**Warum nicht:** Wir nutzen Graphiti als Langzeit-Gedächtnis. Ähnliche Funktion, andere Technologie. Das Konzept (strukturiertes Wissen persistieren) haben wir schon.

---

## 6. Bewertung und Fazit

### Was macht Overstory wirklich gut?

Overstory ist durchdacht, reif (self-aware genug um STEELMAN.md zu schreiben) und gut strukturiert. Besonders beeindruckend:

1. **Explizite Named Failures** — jede Rolle kennt ihre Fallen beim Namen
2. **Propulsion Principle** — anti-zögerlichkeit als explizites Design-Element
3. **INSIGHT-Pattern** — Wissensweitergabe auch ohne Write-Zugriff
4. **ENV_GUARD Pattern** — Hooks nur aktiv für Agents, User-Sessions unberührt
5. **Progressive Escalation** — keine sofortige Termination, stufenweise Reaktion
6. **Honesty über Grenzen** — STEELMAN.md ist ein Zeichen von Reife

### Wichtigste Learnings für autonomous-stan

**Sofort umsetzbar (P1):**
1. Named Failure Modes in `/stan create`, `/stan plan`, `/stan define` Definitionen ergänzen
2. Propulsion Principle als Abschnitt in jeden Command einbauen  
3. INSIGHT-Pattern für Learnings aus autonomen Sessions etablieren
4. Phase-spezifische Tool-Restriktionen verfeinern (Erweiterung stan_gate)
5. Strukturiertes Completion-Signal für Task-Handoff

**Konzeptuell wertvoll (P2):**
- Tiered Escalation Pattern (loop_breaker → systematic debugging → re-scope)
- Session Checkpointing für lange autonomous-stan Sitzungen
- Tool Event Filtering für sauberes Tracking

**Nicht relevant:**
- Alles was tmux, git worktrees, SQLite DBs, oder externe CLI-Tools braucht

### Paradigma-Unterschied

Overstory und autonomous-stan lösen verschiedene Probleme:

- **Overstory:** Wie koordiniere ich 20 parallele Claude-Instanzen?
- **autonomous-stan:** Wie denke und arbeite ich als einzelner Claude-Agent besser?

Der Paradigma-Unterschied bedeutet: die **Infrastruktur** ist nicht übertragbar, aber die **Denkmuster** sind es — besonders die explizite Benennung von Failure Modes, Anti-Zögerlichkeit und strukturiertes Wissens-Capture.

---

*Erstellt durch Deep-Analysis Sub-Agent, autonomous-stan v2*
