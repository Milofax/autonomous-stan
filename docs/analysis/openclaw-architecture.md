# OpenClaw — Architektur-Analyse für autonomous-stan

**Erstellt:** 2026-02-16  
**Kontext:** Vergleich als Framework-Referenz für das autonomous-stan Projekt

---

## Kern-Idee (1 Satz)

OpenClaw ist ein **produktionsreifer Agent-Gateway**, der mehrere LLM-Agents mit persistenten Sessions, Multi-Channel-Messaging, Tool-Enforcement und Memory-Management verbindet — gebaut für **echte 24/7-Multi-User-Szenarien**, nicht für Einzel-Experimente.

---

## Architektur-Übersicht

### Agent Loop Lifecycle
- **Serialisierte Runs** pro Session (Queue-basiert, verhindert Race Conditions)
- **Lifecycle Events:** `start` → `tool` → `assistant` → `end`/`error`
- **Streaming:** Assistant-Deltas, Tool-Events, Reasoning (optional sichtbar)
- **Timeout-Kontrolle:** `agents.defaults.timeoutSeconds` (default 600s)
- **Compaction + Memory Flush:** Automatisches Pre-Compaction Memory Flush vor Context-Limit
- **Hook-Points:** `before_agent_start`, `agent_end`, `before/after_compaction`, `tool_result_persist`

### Sessions
- **Session Keys:** `agent:<agentId>:<mainKey>` (DM) oder `agent:<agentId>:<channel>:group:<id>`
- **Persistenz:** JSONL-Transcripts + SQLite Store (Token-Counts, Metadata)
- **Reset-Policies:** Daily (default 4:00 AM), Idle, Per-Type, Per-Channel Overrides
- **Secure DM Mode:** `dmScope: "per-channel-peer"` verhindert Cross-User Context Leakage
- **Pre-Compaction Flush:** Silent Memory-Turn kurz vor Auto-Compaction (NO_REPLY)
- **Session Pruning:** Alte Tool-Results werden aus Context entfernt (nicht aus JSONL), cache-aware

### Multi-Agent
- **12 echte Agents** bei Marakanda (Stan, Klaus, Patrick, Tony, etc.)
- **Isolation:** Pro Agent eigene `workspace`, `agentDir`, `sessions/`, Auth-Profiles
- **Bindings:** Routing per Channel/Account/Peer (deterministisch, most-specific wins)
- **Agent-to-Agent:** `sessions_send(sessionKey:"agent:<id>:main")` (allowlist-basiert)
- **Sub-Agents:** `sessions_spawn` für parallele Tasks, announce zurück, eigene Session, keine Session-Tools

### Tools
- **Core Tools:** read, write, edit, exec, process, browser, canvas, nodes, message, sessions_*, cron, memory_search, memory_get
- **Tool Policy:** Global allow/deny, per-agent override, per-provider restrict, tool profiles (minimal/coding/messaging/full)
- **Elevated Exec:** Approval-Flow für risikoreiche Commands, Sender-Allowlist
- **MCP Support:** Skills können MCP-Server wrappen (z.B. Graphiti, BusinessMap, Morgen Calendar)
- **Tool Result Persist Hook:** Plugins können Tool-Results transformieren bevor sie ins Transcript geschrieben werden

### Context Management
- **System Prompt:** OpenClaw-owned, kompakt, modular (Tooling, Safety, Skills, Workspace, Sandbox, Time, Runtime)
- **Bootstrap Injection:** AGENTS.md, SOUL.md, TOOLS.md, IDENTITY.md, USER.md, HEARTBEAT.md (per-file truncation 20k chars)
- **Compaction:** Auto-Compaction bei Context-Limit, `/compact` manual, persistiert in JSONL
- **Session Pruning:** Transiente Tool-Result Trimming (soft/hard), cache-ttl aware
- **Context Inspection:** `/status`, `/context list`, `/context detail`

### Memory System
- **Markdown-Files:** `MEMORY.md` (kuratiert, main-only), `memory/YYYY-MM-DD.md` (daily log)
- **Vector Search:** Hybrid BM25 + Embeddings (SQLite + sqlite-vec), Batch-Indexing (OpenAI/Gemini)
- **QMD Backend (experimental):** Lokaler Sidecar (Bun + node-llama-cpp), BM25 + Vectors + Reranking
- **Session Memory (opt-in):** JSONL-Transcripts indexieren, via `memory_search` durchsuchbar
- **Tools:** `memory_search` (snippets + citations), `memory_get` (file read)
- **Embedding Cache:** Chunk-Embeddings in SQLite gecached für schnelle Reindexes

---

## Wie OpenClaw dieselben Probleme löst die autonomous-stan lösen will

### 1. Enforcement (Skills + AGENTS.md vs Hooks + Rules)

**OpenClaw:**
- **Tool Policy:** Harte Enforcement via `tools.allow`/`tools.deny` (deny wins), per-agent override möglich
- **Elevated Exec:** Approval-Flow für kritische Commands, Sender-Allowlist, UI-Prompts
- **Sandbox:** Docker-basiert, per-agent konfigurierbar, per-run overridable
- **Hooks (internal):** Event-driven Scripts für Commands (`command:new`, `command:reset`), Agent-Lifecycle (`agent:bootstrap`, `agent:end`), Gateway (`gateway:startup`)
- **Plugin Hooks:** Runtime-Hooks (`before_agent_start`, `tool_result_persist`, `message_received`)
- **Skills:** Markdown-Docs + optional MCP-Wrapper, on-demand geladen (nicht alle im System Prompt)

**autonomous-stan:**
- **Skills:** Python-Module, Registry-basiert, Validation-Layer
- **AGENTS.md:** Regeln in Markdown (PITH-Notation), aber nur prompt-level enforcement
- **Keine Hooks:** Enforcement rein via Prompt + Skills-Validierung

**Ehrlich:**
- OpenClaw hat **härtere Boundaries** (Tool-Deny ist nicht umgehbar, Sandbox erzwingt Isolation)
- autonomous-stan's AGENTS.md ist **prompt-only** — Agent kann Regeln ignorieren (siehe MEMORY.md Learnings!)
- **Gap:** autonomous-stan braucht Runtime-Hooks für echte Enforcement (z.B. "kein Browser nach 22:00", "keine GitHub-Pushes ohne Review")

---

### 2. Memory (Graphiti + memory/*.md vs lokale Learnings)

**OpenClaw:**
- **Zwei Layer:** 
  - `memory/YYYY-MM-DD.md` (daily, append-only, read today + yesterday)
  - `MEMORY.md` (kuratiert, main-session only, long-term)
- **Vector Search:** Hybrid BM25 + Embeddings, Batch-Indexing, Citations optional
- **QMD (experimental):** Local-first Sidecar, BM25 + Vectors + Reranking, auto-downloads GGUF-Models
- **Session Memory (opt-in):** JSONL-Transcripts indexieren, via `memory_search` durchsuchbar
- **Pre-Compaction Flush:** Automatischer Silent-Turn zum Memory-Schreiben vor Compaction
- **Graphiti:** NICHT Teil von Core OpenClaw, sondern MCP-Skill! (Stan nutzt es via `graphiti` Skill)

**autonomous-stan:**
- **Graphiti:** Primäres Langzeitgedächtnis (Entities, Relations, Episodes)
- **memory/*.md:** Tagesnotizen, nicht indexiert
- **Kein Vector Search:** Graphiti übernimmt Semantic Search
- **Kein Pre-Compaction Flush:** Manuelles Memory-Management

**Ehrlich:**
- OpenClaw's Memory-System ist **flexibler** (Markdown + Vector + optional Graphiti via MCP)
- autonomous-stan's **All-in auf Graphiti** ist riskant (siehe MEMORY.md: "Graphiti Root Cause — AI Ranking brauchte OpenAI API → Single Point of Failure", "Graphiti 502 intermittierend")
- **Pre-Compaction Flush ist genial** — autonomous-stan verliert Learnings wenn Context rotated (kein automatischer Memory-Write-Trigger)
- **Gap:** autonomous-stan braucht Fallback-Memory wenn Graphiti down ist (Hybrid-Ansatz wie OpenClaw)

---

### 3. Subagents (sessions_spawn vs Claude Tasks)

**OpenClaw:**
- **`sessions_spawn` Tool:** Spawnt Sub-Agent in eigener Session, announce zurück
- **Isolation:** Keine Session-Tools (kein `sessions_list`, `sessions_send`, `sessions_spawn`), eigener Context
- **Concurrency:** Queue-Lane `subagent`, max 8 parallel (konfigurierbar)
- **Auto-Cleanup:** `cleanup: "delete"` oder auto-archive nach 60 Min
- **Announce:** Template-basiert (Status, Result, Notes, Stats + Transcript Path)
- **Cost-Control:** Default-Model für Sub-Agents konfigurierbar (billiger als Main-Agent)
- **Timeout:** `runTimeoutSeconds` für Abort nach N Sekunden

**autonomous-stan:**
- **Claude Tasks API:** Native Claude Feature (kein eigenes Spawning)
- **Isolation:** ??? (unklar ob Sessions isoliert sind)
- **Announce:** ??? (unklar ob automatisch oder manuell)

**Ehrlich:**
- OpenClaw's `sessions_spawn` ist **production-ready** (12 Agents nutzen es seit Wochen)
- **Learnings aus MEMORY.md:** 
  - "Sub-Agent Transparenz — IMMER Start-Meldung + Ergebnis posten" (musste manuell durchgesetzt werden!)
  - "Sub-Agents können kein kreatives Design — Kopieren Dateien 1:1 statt CSS zu ändern" (Design-Limits!)
  - "Parallele MCP-Agents crashen FalkorDB — 4 Sub-Agents gleichzeitig auf Graphiti → Connection Reset"
  - "Sub-Agent Batching Regel — EINE Start-Nachricht, ALLE Announces NO_REPLY, EINE Zusammenfassung" (Anti-Spam)
- **Gap:** autonomous-stan nutzt Claude Tasks API — keine Kontrolle über Announce-Format, keine Tool-Policy für Sub-Tasks
- **Vorteil Claude Tasks:** Native Integration, weniger eigener Code
- **Vorteil OpenClaw:** Volle Kontrolle, Tool-Policy, Cost-Control

---

### 4. Context Management (Compaction + Pre-Compaction Flush vs Manual /compact)

**OpenClaw:**
- **Auto-Compaction:** Triggert bei Context-Limit, optional retry
- **Pre-Compaction Flush:** Silent Memory-Turn (NO_REPLY) kurz vor Compaction — schreibt Learnings auf Disk
- **Session Pruning:** Alte Tool-Results aus Context entfernt (transient, nicht aus JSONL), cache-ttl aware
- **Manual:** `/compact [instructions]` für User-gesteuerte Compaction
- **Inspection:** `/context list`, `/context detail` für Deep-Dive
- **Bootstrap Truncation:** 20k chars per file, Truncation-Marker

**autonomous-stan:**
- **Manual `/compact`:** User-gesteuert, keine Auto-Compaction
- **Kein Pre-Compaction Flush:** Memory-Management ist Agent-Verantwortung
- **Kein Pruning:** Volle Tool-Results bleiben im Context bis `/compact`

**Ehrlich:**
- **Pre-Compaction Flush ist Game-Changer** — Verhindert Learnings-Verlust bei Auto-Compaction
- **Session Pruning ist cache-aware** — Spart Kosten bei Anthropic (cacheWrite reduziert nach TTL-Expiry)
- **Gap:** autonomous-stan hat **keine Auto-Compaction** — Long-Running Sessions können Context-Limit crashen
- **Gap:** Keine Inspection-Tools — Agent "fliegt blind" bis `/status` kommt
- **Learning aus MEMORY.md:** "verboseDefault = 'off' — Verbose ist für Debugging, nicht Normalbetrieb. Tool-Calls überholen sich in Discord"

---

### 5. Quality Gates (Heartbeats + Cron vs Criteria Checks)

**OpenClaw:**
- **Heartbeats:** Periodic Agent-Runs (konfigurierbar per Session-Type, Channel, Agent)
- **Cron:** Isolated Runs (eigene Session, kein Kontext-Sharing), `cron.jobs[].schedule` via cron-parser
- **Hooks:** Event-driven (z.B. `command:new` → save session context to memory)
- **System Prompt Section:** "Heartbeats" erklärt Ack-Behavior (`NO_HEARTBEAT_ACK` für silent heartbeats)

**autonomous-stan:**
- **Criteria Checks:** Quality-Gates für Deliverables (z.B. "Code muss Tests haben")
- **Keine Heartbeats:** Kein periodisches Self-Check
- **Keine Crons:** Kein automatisches Background-Work

**Ehrlich:**
- **Heartbeats sind ESSENTIELL für Production** — ohne sie keine proaktive Wartung
- **Learnings aus HEARTBEAT.md (Stan's echte Config):**
  - E-Mail Pipeline Self-Check JEDEN Heartbeat (5 Prüfpunkte: Cron läuft?, Mark-Done?, n8n erreichbar?, Execution Status?, Plausibilität >12h keine Mail)
  - Graphiti Health Check bei jedem Heartbeat (GitHub Issue erstellen bei Fehler)
  - Infrastructure Issue Tracker (teste geschlossene Issues, notify wenn broken)
  - Proaktive Checks (Emails, Calendar, Weather) 2-4x/Tag rotierend
  - Memory Maintenance alle paar Tage (`memory/*.md` → `MEMORY.md` destillieren)
- **Crons für echte Production kritisch:** Auto-Labeling (Gmail), Graphiti Duplikat-Merge (Sonntags 10:00)
- **Gap:** autonomous-stan hat **keine Self-Checks** — Infrastruktur-Probleme bleiben unentdeckt
- **Gap:** Keine Background-Jobs — alles ist User-triggered

---

### 6. Task Management (BusinessMap MCP vs .stan/tasks.jsonl)

**OpenClaw:**
- **MCP-Skills:** Wrapper für externe Tools (BusinessMap, Morgen Calendar, Graphiti)
- **BusinessMap:** Kanban-Board, Workflows, Predecessors, Kommentare via MCP
- **Skill-basiert:** `mcporter call 'businessmap.list_cards(board_id: 5)'`

**autonomous-stan:**
- **`.stan/tasks.jsonl`:** Lokale Task-Queue (JSONL-File)
- **Kein MCP:** Native Python-Integration

**Ehrlich:**
- **MCP ist flexibler** — beliebige externe Tools integrierbar (nicht nur Tasks)
- **Learnings aus MEMORY.md:**
  - "KARTE ZUERST — Bevor ich IRGENDWAS anfange: Karte auf Board 5 anlegen"
  - "Committed ≠ In Arbeit — BusinessMap Skill lesen!"
  - "Review = FERTIG — Alle Akzeptanzkriterien erfüllt, keine offenen Fragen"
  - "Forward-Only Flow — Karten NIE zurück bewegen. Bug? Neue Karte, alte blocken"
  - "Silent WIP = Violation — Unsichtbare Arbeit existiert nicht"
  - "BusinessMap MCP hat kein `create_comment` — API kann es, MCP-Package nicht. Workaround: curl direkt"
- **Gap:** autonomous-stan's `.stan/tasks.jsonl` ist **nicht shared** — nur Agent sieht Tasks, User nicht (außer via Agent-Query)
- **Vorteil BusinessMap:** **Visibility für alle** (User + Agent + Team)
- **Vorteil `.stan/tasks.jsonl`:** Einfacher, keine externe Dependency

---

### 7. Multi-Agent (12 echte Agents vs Single-Agent Personas)

**OpenClaw:**
- **12 echte Agents:** Stan, Klaus, Patrick, Tony, Andrew, Dave, Mario, Sven, Jacob, Tobias, Nathanael, Susanna
- **Isolation:** Eigene Workspaces, Sessions, Auth-Profiles, Tool-Policies, Sandboxes
- **Routing:** Bindings per Channel/Account/Peer (deterministisch)
- **Agent-to-Agent:** `sessions_send` (allowlist, timeout 0 = fire-and-forget)
- **Persona-Files:** SOUL.md, AGENTS.md, USER.md, HEARTBEAT.md pro Agent

**autonomous-stan:**
- **Single-Agent:** Nur "Stan"
- **Personas:** Potentiell als Prompt-Swaps (nicht als separate Agents)

**Ehrlich:**
- **Multi-Agent funktioniert in Production** (3 Wochen+ Laufzeit bei Marakanda)
- **Learnings aus MEMORY.md:**
  - "Channels = Themen, Agents = Persönlichkeiten"
  - "Deep Personality Research als Standard für Agent-Personas"
  - "Agent-zu-Agent Kommunikation fix — `sessions_send` Syntax in ALLE 11 AGENTS.md eingefügt"
  - "Nicht raten, recherchieren! — Bolidor hat mich gerügt weil ich 3 falsche Hypothesen als Fakten präsentiert habe"
  - "Antwort-Disziplin ABSOLUTES GESETZ — Text VOR message-Tool-Call = separater Reply in falscher Reihenfolge"
- **Probleme:**
  - "Browser Multi-Tab Problem — 40+ Tabs offen → Memory/CDP-Overhead + Timeouts. Max 5-10 aktive Tabs, Rest schließen"
  - "Parallele MCP-Agents crashen FalkorDB — 4 Sub-Agents gleichzeitig auf Graphiti"
  - "VOR Deployment IMMER Container-Liste checken — Parallele Deployments (Stan + Patrick-SubAgent) → 34 Container statt 8"
- **Gap:** autonomous-stan ist **Single-Agent** — keine Spezialisierung, keine Parallelarbeit
- **Frage:** Braucht autonomous-stan Multi-Agent? Oder reichen Personas als Prompt-Swaps?

---

## Plugin/Hook-System (was könnte autonomous-stan als Plugin nutzen?)

### OpenClaw Plugins (official):
- **Voice Call** (`@openclaw/voice-call`) — Twilio-Integration
- **Matrix** (`@openclaw/matrix`) — Matrix-Channel
- **Nostr** (`@openclaw/nostr`) — Nostr-Channel
- **MS Teams** (`@openclaw/msteams`) — Teams-Channel (plugin-only)
- **Memory (LanceDB)** — Auto-Recall/Capture (bundled, opt-in)
- **Provider Auth** (Google Antigravity, Gemini CLI, Qwen, Copilot Proxy) — OAuth-Flows

### OpenClaw Hooks (bundled):
- **session-memory** — Speichert Session-Context vor `/new` in `memory/YYYY-MM-DD-slug.md` (LLM-generierter Slug)
- **command-logger** — JSONL-Audit-Log für alle Commands (`~/.openclaw/logs/commands.log`)
- **boot-md** — Führt `BOOT.md` beim Gateway-Start aus
- **soul-evil** — Swappt `SOUL.md` mit `SOUL_EVIL.md` (Purge-Window oder Random-Chance)

### Was autonomous-stan übernehmen könnte:
1. **Hook-System für Event-Driven Automation:**
   - `task:created` → Auto-Label via Graphiti-Context
   - `task:completed` → Speichere Learning in Graphiti
   - `skill:validation_failed` → Log to monitoring
   - `agent:bootstrap` → Swap Persona-Files (wie `soul-evil`)

2. **Plugin-System für Channel/Tool-Extensions:**
   - Slack-Plugin (analog zu OpenClaw's Matrix/Nostr)
   - GitHub-Plugin (Issues, PRs, Code-Review)
   - Linear-Plugin (alternative zu Tasks.jsonl)

3. **Memory-Plugins:**
   - QMD-Backend für Hybrid Search (wie OpenClaw)
   - Session-Memory-Indexing (JSONL → Vector DB)

4. **Provider-Auth-Plugins:**
   - OAuth-Flows für APIs (analog zu Google Antigravity)
   - Credential-Management (1Password-Integration wie Stan)

---

## Stärken gegenüber Claude-Code-only Frameworks

### OpenClaw:
1. **Production-Ready Multi-Channel:** WhatsApp, Telegram, Discord, Slack, Signal, iMessage, WebChat (+ Plugins für Matrix, Nostr, Teams)
2. **Multi-Agent Isolation:** 12 Agents, eigene Workspaces, Sessions, Auth
3. **Tool-Enforcement:** Deny-Liste, Elevated-Exec-Approvals, Sandbox
4. **Memory-System:** Markdown + Vector + optional Graphiti (Hybrid!)
5. **Heartbeats + Crons:** Proaktive Self-Checks, Background-Jobs
6. **Session Management:** Secure DM Mode, Reset-Policies, Session Pruning
7. **Context Management:** Auto-Compaction, Pre-Compaction Flush, Bootstrap Injection
8. **MCP-Support:** Skills können MCP-Server wrappen (BusinessMap, Morgen, Graphiti)
9. **Sub-Agents:** `sessions_spawn` mit Tool-Policy, Cost-Control, Auto-Cleanup
10. **Plugin/Hook-System:** Erweiterbar ohne Core-Änderungen
11. **Observability:** `/status`, `/context detail`, `/subagents list`, Command-Logger

### autonomous-stan:
1. **Fokus auf Single-Use-Case:** Persönlicher Agent, nicht Multi-User-Gateway
2. **Python-Ecosystem:** Einfachere Integration mit Data-Science-Tools
3. **Graphiti-First:** Dedizierte Langzeitgedächtnis-Architektur
4. **Simpler:** Weniger Komplexität, schneller zu verstehen

---

## Schwächen/Limitierungen

### OpenClaw:
1. **Komplexität:** 200k+ LOC, steile Lernkurve, viele Config-Optionen
2. **TypeScript/Node.js:** Nicht ideal für Data-Science/ML (Python-Ecosystem fehlt)
3. **Multi-Channel Overhead:** Viele Features die Single-User nicht brauchen
4. **Memory-System fragmentiert:** Markdown + Vector + Graphiti + Session-Memory → zu viele Optionen?
5. **Tool-Result Truncation:** Kann wichtige Details verlieren (siehe Session Pruning)
6. **Enforcement ist Prompt-Level bei Skills:** AGENTS.md Regeln sind nicht hart enforced (nur Tool-Deny ist hart)
7. **Kein natives Python:** MCP-Skills müssen Python-Tools wrappen (zusätzlicher Layer)

### autonomous-stan:
1. **Kein Multi-Channel:** Nur CLI/API (kein WhatsApp, Discord, etc.)
2. **Kein Multi-Agent:** Single-Agent-Architektur
3. **Kein Hook-System:** Keine Event-Driven Automation
4. **Kein Auto-Compaction:** Context-Management ist manuell
5. **Kein Session Management:** Keine DM-Isolation, keine Reset-Policies
6. **Kein Sub-Agent System:** Nur Claude Tasks API (weniger Kontrolle)
7. **Graphiti SPOF:** Single Point of Failure (siehe MEMORY.md Learnings)

---

## Was OpenClaw von autonomous-stan lernen könnte

1. **Python-First Approach:** Besseres Data-Science-Ecosystem
2. **Graphiti-Integration als Core:** Nicht nur als MCP-Skill (autonomous-stan hat dedizierte Graphiti-Architektur)
3. **Skills als Python-Module:** Validierung + Type-Safety (statt Markdown-Docs + MCP-Wrapper)
4. **Simpler Config:** Weniger Optionen, bessere Defaults
5. **Criteria-Checks:** Quality-Gates für Deliverables (analog zu OpenClaw's Hook-System)
6. **Task-Management in Core:** `.stan/tasks.jsonl` ist simpler als BusinessMap-MCP (aber weniger Visibility)

---

## Was autonomous-stan von OpenClaw übernehmen sollte

### High Priority:
1. **Pre-Compaction Memory Flush:** Automatischer Memory-Write-Trigger vor Context-Rotation
2. **Session Pruning:** Cache-aware Tool-Result Trimming (spart Kosten!)
3. **Hook-System:** Event-Driven Automation (`task:created`, `skill:failed`, etc.)
4. **Auto-Compaction:** Verhindert Context-Limit Crashes
5. **Heartbeats:** Proaktive Self-Checks (Graphiti-Health, Infra-Monitoring)
6. **Memory Fallback:** Hybrid Markdown + Vector als Fallback wenn Graphiti down

### Medium Priority:
7. **Sub-Agent Tool-Policy:** Keine Session-Tools für Sub-Tasks (Sicherheit!)
8. **Tool Deny-Liste:** Harte Enforcement (nicht nur Prompt-Level)
9. **Session Isolation:** Secure DM Mode (verhindert Cross-User Context Leakage bei Multi-User)
10. **Context Inspection:** `/context detail` analog (Debugging!)

### Low Priority:
11. **Multi-Channel Support:** Nur wenn autonomous-stan wachsen soll (WhatsApp, Discord, etc.)
12. **Multi-Agent:** Nur wenn Spezialisierung gewünscht (Klaus für FL-Coaching, Patrick für Web-Dev)

---

## Ehrliche Praxis-Analyse: Was funktioniert bei 12 Agents über 3 Wochen WIRKLICH?

### ✅ Was funktioniert:

1. **Multi-Agent Isolation:** 12 Agents laufen parallel, keine Crashes, keine Session-Kollisionen
2. **Agent-to-Agent Kommunikation:** `sessions_send` funktioniert (musste aber Syntax in ALLE AGENTS.md einfügen!)
3. **Heartbeats für Monitoring:** E-Mail Pipeline Self-Check, Graphiti Health Check — hätten Downtime verhindert
4. **Pre-Compaction Memory Flush:** Learnings gehen nicht verloren (kein Manual-Memory-Management nötig)
5. **Session Pruning:** Spart Kosten bei Anthropic (cache-aware)
6. **MCP-Skills:** BusinessMap, Morgen Calendar, Graphiti funktionieren (mit Workarounds)
7. **Sub-Agents:** Parallele Tasks, announce zurück (mit Batching-Rules gegen Spam)
8. **Tool Deny:** Browser nach 22:00 verhinderbar (härtere Enforcement als Prompt-Rules)

### ⚠️ Was funktioniert MIT Workarounds:

1. **AGENTS.md Regeln:** Werden ignoriert ohne Runtime-Enforcement
   - **Beispiel:** "NIE raten bei Fakten" → Agent rät trotzdem → Bolidor rügt (3x in MEMORY.md!)
   - **Workaround:** Explizite Learnings in MEMORY.md schreiben ("Nicht raten, recherchieren!")
   - **Learning:** Prompt-Rules ≠ Enforcement. Braucht Hooks oder Tool-Deny.

2. **Antwort-Disziplin:** Text VOR message-Tool-Call = separater Reply in falscher Reihenfolge
   - **Beispiel:** Agent schreibt Gedanken, dann message-Tool → Gedanken werden als separater Reply gesendet
   - **Workaround:** "ABSOLUTES GESETZ" in alle 12 AGENTS.md: "Wenn message-Tool → NUR Tool-Call + NO_REPLY"
   - **Learning:** Braucht Gateway-Level Enforcement (Feature-Request offen)

3. **Sub-Agent Batching:** Jede Announce einzeln beantwortet = Message-Chaos
   - **Beispiel:** 5 Sub-Agents → 10+ Messages (Start + Announce pro Sub-Agent)
   - **Workaround:** "EINE Start-Nachricht, ALLE Announces NO_REPLY, EINE Zusammenfassung" in AGENTS.md
   - **Learning:** Sub-Agent Announce-Template braucht "silent mode" Option

4. **Browser Multi-Tab:** 40+ Tabs offen → Memory/CDP-Overhead + Timeouts
   - **Beispiel:** Mario hatte 40+ Tabs offen → Browser-Timeouts
   - **Workaround:** "Max 3 Tabs/Agent, nach Nutzung schließen" in alle 12 AGENTS.md
   - **Learning:** Browser-Hygiene braucht Auto-Cleanup oder Tab-Limit-Enforcement

5. **Graphiti MCP:** Keine CRUD-Tools, kein Browse, nur Search
   - **Beispiel:** Duplikat-Merge nicht möglich (bis Skill v2 kam mit create/update/delete)
   - **Workaround:** Skill upgraden (v2 hat 10 neue Tools)
   - **Learning:** MCP-Skills brauchen Feature-Parity mit nativen APIs

6. **BusinessMap MCP:** Kein `create_comment` (API kann es, MCP nicht)
   - **Workaround:** `curl` direkt mit API-Key
   - **Learning:** MCP-Packages sind oft unvollständig

### ❌ Was NICHT funktioniert:

1. **Graphiti als Single Point of Failure:**
   - **Problem:** AI Ranking brauchte OpenAI API → SPOF
   - **Fix:** Ollama lokal mit Llama 3.2
   - **Learning:** JEDES System braucht Fallback (Hybrid Memory wie OpenClaw!)

2. **Gmail OAuth-Tokens sterben ~1%/Monat:**
   - **Problem:** Google revokt aus undokumentierten Security-Heuristiken
   - **Symptom:** n8n meldet "success" mit leeren Responses (kein Error!)
   - **Learning:** "success" ≠ "funktioniert" — IMMER auf Item-Count prüfen!

3. **DNS-Ausfälle = OAuth-Token-Tod:**
   - **Problem:** 27 Error-Executions (DNS, ENETUNREACH) seit 04.02. → Google widerruft Tokens
   - **Learning:** IMMER zuerst Logs prüfen, dann Hypothesen!

4. **Parakeet TDT bei kurzen Clips unzuverlässig:**
   - **Problem:** 2,5s Voice-Messages kommen leer zurück
   - **Workaround:** OpenClaw transkribiert manchmal selbst vor Zustellung (kein OpenAI-Key für Whisper-Fallback)

5. **Parallele MCP-Agents crashen FalkorDB:**
   - **Problem:** 4 Sub-Agents gleichzeitig auf Graphiti → Connection Reset, DB down
   - **Learning:** IMMER sequenziell arbeiten bei Graphiti-Cleanup

6. **Parallele Deployments → 34 Container statt 8:**
   - **Problem:** Stan + Patrick-SubAgent parallel deployt
   - **Learning:** VOR Deployment IMMER Container-Liste checken

7. **CSS-Basics-Krise:**
   - **Problem:** Bolidor komplett frustriert — Logo nicht fixed, Proportionen falsch, clamp() zu niedrig, kein Bootstrap Grid. Zitat: "einfach nur scheisse"
   - **Fix:** Modular Scale (Utopia.fyi), Pre-Flight Checklist, Visual Lint erweitert, 7 Referenzdateien erstellt
   - **Learning:** Sub-Agents können kein kreatives Design — kopieren Dateien 1:1 statt CSS zu ändern

8. **Inbox Queue statt sessions_send:**
   - **Problem:** `sessions_send` hat Timeouts wenn Agent busy
   - **Workaround:** File-basierte Queue (`~/inbox/`), Cron alle 15 Min
   - **Learning:** Fire-and-forget braucht **echte** Queue (nicht Tool-basiert)

---

## Fazit: OpenClaw vs autonomous-stan

### OpenClaw ist:
- **Production-Ready Gateway** für Multi-User, Multi-Channel, 24/7
- **Komplex** aber **vollständig** — alle Probleme sind gelöst (Enforcement, Memory, Sessions, Multi-Agent)
- **TypeScript/Node.js** — gut für Web-Integration, schlecht für Data-Science

### autonomous-stan ist:
- **Single-User Personal Agent** mit Python-Ecosystem
- **Einfacher** aber **lückenhaft** — viele Probleme noch offen (Auto-Compaction, Heartbeats, Enforcement)
- **Python-First** — gut für Data-Science, einfacher zu erweitern

### Was autonomous-stan DRINGEND braucht (aus OpenClaw lernen):
1. **Pre-Compaction Memory Flush** — Verhindert Learnings-Verlust
2. **Auto-Compaction** — Verhindert Context-Limit Crashes
3. **Session Pruning** — Spart Kosten
4. **Hook-System** — Event-Driven Automation
5. **Heartbeats** — Proaktive Self-Checks
6. **Memory Fallback** — Hybrid Markdown + Vector als Graphiti-Fallback
7. **Tool Deny-Liste** — Harte Enforcement
8. **Sub-Agent Tool-Policy** — Sicherheit

### Was autonomous-stan NICHT braucht:
1. Multi-Channel (WhatsApp, Discord) — es sei denn Wachstum geplant
2. Multi-Agent (12 separate Agents) — Personas als Prompt-Swaps reichen vermutlich
3. WebSocket-Gateway — CLI/API reicht für Single-User

---

## Ehrlichkeit über Stan's Praxis (MEMORY.md Learnings):

### Regelbrüche die TROTZ AGENTS.md passieren:
- **"NIE raten bei Fakten"** → 3x geraten, 3x von Bolidor gerügt
- **"Karte zuerst"** → Oft vergessen, musste verschärft werden
- **"Browser-Hygiene"** → 40+ Tabs offen, musste Policy einführen
- **"Antwort-Disziplin"** → Text vor message-Tool → separate Reply (ABSOLUTES GESETZ nötig!)
- **"Sub-Agent Batching"** → 10+ Messages, musste Batching-Regel einführen

### Was daraus folgt:
- **Prompt-Rules alleine reichen NICHT** — braucht Runtime-Enforcement (Hooks, Tool-Deny, Auto-Cleanup)
- **AGENTS.md muss mit Learnings wachsen** — "ABSOLUTES GESETZ", "NICHT ÜBERSPRINGBAR", "🚨" für kritische Regeln
- **Graphiti alleine reicht NICHT** — braucht Markdown-Fallback (MEMORY.md hat 9x "Graphiti down" Entries!)
- **Single Point of Failure vermeiden** — DNS-Ausfall → OAuth-Token-Tod, Graphiti-API → kein Ranking

### Was WIRKLICH funktioniert:
- **Multi-Agent** — 12 Agents über 3 Wochen, keine Session-Kollisionen
- **Agent-to-Agent** — `sessions_send` fire-and-forget funktioniert
- **MCP-Skills** — BusinessMap, Morgen, Graphiti funktionieren (mit Workarounds)
- **Pre-Compaction Flush** — Learnings gehen nicht verloren
- **Heartbeats** — E-Mail Pipeline Monitoring hätte Downtime verhindert
- **Session Pruning** — Spart Kosten bei Anthropic

### Was NICHT funktioniert (und warum):
- **AGENTS.md Enforcement** — nur Prompt, keine Runtime-Checks → Regeln werden ignoriert
- **Graphiti SPOF** — AI Ranking down → kein Search → alles blockiert
- **Gmail OAuth** — stirbt ~1%/Monat, n8n sagt "success" mit leeren Responses
- **Sub-Agents kreativ** — kopieren 1:1, ändern kein CSS
- **Parallele MCP-Zugriffe** — crashen FalkorDB

---

**Letzte Aktualisierung:** 2026-02-16  
**Quelle:** OpenClaw `/app/docs/` + Stan's echte Config (`AGENTS.md`, `MEMORY.md`, `SOUL.md`, `HEARTBEAT.md`)  
**Ehrlichkeit:** Basiert auf **echten Learnings über 3 Wochen** mit 12 Production-Agents, nicht auf Marketing-Material.