# taming-stan + Claude Agent SDK — Framework-Analyse

**Datum:** 16.02.2026  
**Analyst:** Stan (Subagent)  
**Kontext:** Vergleich zweier Ansätze zur Agent-Steuerung + Erkenntnisse für autonomous-stan

---

## taming-stan

### Kern-Idee (1 Satz)
**Hook-basierte Quality Gates für Claude Code:** Python-Guards blockieren gefährliche/ineffiziente Tool-Calls präventiv, während PITH-formatierte Rules das Verhalten dokumentieren.

### Architektur (Hook-Pipeline, Guard-System, State Management)

**3-Schichten-Architektur:**

```
┌─────────────────────────────────────────────────────────────┐
│  RULES (Markdown)                                            │
│  - graphiti.md, stanflux.md, pith.md                        │
│  - MCP-configs (context7, firecrawl, playwright, etc.)      │
│  → Dokumentation + Claude-Instruktionen                     │
└─────────────────────────────────────────────────────────────┘
                         ↓ (passive Lesepflicht)
┌─────────────────────────────────────────────────────────────┐
│  HOOKS (Python Scripts)                                      │
│  - SessionStart: graphiti-context-loader, reset-flags       │
│  - UserPromptSubmit: session-reminder, knowledge-reminder   │
│  - PreToolUse: graphiti-guard, graphiti-first-guard, etc.   │
│  - PostToolUse: graphiti-retry-guard (3-Strikes)            │
│  → Aktive Durchsetzung + Blockierung                        │
└─────────────────────────────────────────────────────────────┘
                         ↓ (State-basierte Verkettung)
┌─────────────────────────────────────────────────────────────┐
│  SESSION STATE (/tmp/claude-session-{hash}.json)            │
│  - graphiti_searched, firecrawl_attempted                   │
│  - context7_attempted_for, error_counts                     │
│  - active_group_ids                                         │
│  → Ermöglicht Verkettung + Deduplizierung                   │
└─────────────────────────────────────────────────────────────┘
```

**Hook-Verkettung (Beispiel: Web-Recherche):**
1. User: "Was kostet React?"
2. **graphiti-first-guard:** WebSearch → `graphiti_searched?` → NEIN → BLOCK
3. User: search_nodes("React Kosten")
4. **graphiti-context-loader** setzt: `graphiti_searched: true`
5. **graphiti-first-guard:** WebSearch → `graphiti_searched?` → JA → ALLOW
6. **firecrawl-guard:** WebSearch → `firecrawl_attempted?` → NEIN → BLOCK ("Erst Firecrawl!")
7. User: firecrawl.search("React Kosten")
8. **firecrawl-guard** setzt: `firecrawl_attempted: true`
9. **graphiti-first-guard:** WebSearch → JA → ALLOW
10. WebSearch geht durch

**State Management:**
- **Atomic File-Locks:** `session_state.py` nutzt `fcntl.flock()` (POSIX-konform)
- **CWD-basierter Hash:** Session-State pro Working-Directory isoliert
- **Deduplizierung:** `run_once(hook_name, ttl)` verhindert Mehrfach-Ausführung bei globalen + lokalen Hooks

### Einzigartige Stärken (welche Guards sind wirklich wertvoll?)

| Guard | Wert | Warum |
|-------|------|-------|
| **graphiti-guard.py** | ⭐⭐⭐⭐⭐ | **Credential-Schutz:** 903 Regex-Patterns für API-Keys, Tokens, Passwörter. 3-Strikes-System bei Violation. Verhindert Secrets im Wissensgraph. |
| **graphiti-first-guard.py** | ⭐⭐⭐⭐ | **Research-Hierarchie:** Erzwingt "eigenes Wissen VOR externem Web". Verhindert Duplikat-Recherche + spart API-Credits. |
| **graphiti-retry-guard.py** | ⭐⭐⭐⭐ | **3-Strikes-Pattern:** Nach 3 identischen Fehlern → BLOCK + "Suche erst im Graphiti nach Learnings". Durchbricht Fehler-Loops. |
| **git-workflow-guard.py** | ⭐⭐⭐ | **Conventional Commits:** Blockiert non-conformant Commits. Force-Push-Schutz. Ermöglicht automatische Changelogs. |
| **file-context-tracker.py** | ⭐⭐⭐ | **Kontext-Awareness:** Trackt alle File-Operations → liefert `active_group_ids` für Graphiti. Ermöglicht intelligentes Routing. |
| context7-guard.py | ⭐⭐ | Gute Idee (aktuelle Docs statt Training-Wissen), ABER: Nur Tracking, kein echtes Blocking. |
| firecrawl-guard.py | ⭐⭐ | Nützlich wenn Firecrawl-Account vorhanden, sonst SKIP (optional). |
| playwright-guard.py | ⭐ | Sehr spezifisch (MCP > CLI). Nur relevant wenn beide Optionen existieren. |

**Top-3-Takeaways:**
1. **Credential-Schutz ist KRITISCH** – 903 Patterns + 3-Strikes funktioniert
2. **Research-Hierarchie spart Geld** – Eigenes Wissen VOR teuren API-Calls
3. **3-Strikes-Pattern bricht Loops** – Nach 3 Fehlern: Graph durchsuchen statt Retry

### Schwächen/Limitierungen

| Problem | Detail |
|---------|--------|
| **Installer-Overhead** | 700 Zeilen Node.js nur für Datei-Kopieren + settings.json mergen. Bei Plugin-Migration obsolet. |
| **Keine LLM-Intelligenz** | Hooks sind Regex/Python-Logik. Kann NICHT semantisch verstehen: "Ist das ein Learning?" → Plan.md zeigt: type:prompt Hooks können nicht blocken, nur warnen. |
| **Falsche Positives** | Citation-Check hat Regex-basierte Buch-Erkennung → False Positives bei Wörtern wie "cookbook". |
| **Keine Cross-Session-Memory** | Session-State stirbt mit Session. Learnings aus Hooks müssen manuell in Graphiti gespeichert werden. |
| **Tight Coupling mit Claude Code** | Hooks sind 100% Claude-Code-spezifisch. Nicht übertragbar auf andere Runtimes. |
| **Plan.md zeigt toten Traum** | Intelligente LLM-basierte Hooks bräuchten eigenen API-Key → nicht für alle nutzbar. |

**Kritische Erkenntnis aus plan.md (Experiment 5):**
- `type:prompt` Hooks **können NICHT blocken** (nur warnen)
- `type:command` mit LLM-Call **bräuchte API-Key** (User-Abhängigkeit)
- → "Der tote Traum": Intelligente Hooks für alle nutzbar existieren nicht

### Key Features

| Feature | Beschreibung |
|---------|--------------|
| **Session-State-Verkettung** | `/tmp/claude-session-{hash}.json` ermöglicht Hook-Kommunikation |
| **Deduplizierung** | `run_once(hook_name, ttl)` verhindert Mehrfach-Ausführung |
| **Hierarchie-Support** | HOME + Project hooks mergen automatisch |
| **PITH-Notation** | Kompakte, maschinenlesbare Rules (`!!` = kritisch, `\|` = or, `→` = then) |
| **Entity-Type-System** | 18 Types (Person, Organization, Learning, Decision, etc.) für strukturiertes Wissen |
| **group_id-Logik** | 6-Stufen-Fallback (.graphiti-group → CLAUDE.md → GitHub-Remote → Git+Owner → Git-Only → "main") |
| **Citation-Templates** | Dokumenttyp-spezifische Validierung (Book, Article, Website, RFC, etc.) |
| **3-Strikes-System** | Bei Credentials: 3 Violations → Session BLOCKIERT |
| **Commands** | `/graphiti:check`, `/graphiti:learn`, `/stanflux:challenge`, `/stanflux:retro` |

### Was hat sich in der Praxis bewährt? (Vergleich mit OpenClaw Stans MEMORY.md)

**Bewährt in MEMORY.md (= funktioniert in der Praxis):**

| Learning aus MEMORY.md | Entspricht taming-stan | Status |
|------------------------|------------------------|--------|
| "NIE raten bei Fakten – IMMER recherchieren" | graphiti-first-guard | ✅ Durchgesetzt |
| "Nicht voreilig handeln – erst verstehen" | stanflux.md (Brownfield-Regeln) | ✅ Dokumentiert |
| "It depends ist Violation – Position beziehen" | stanflux.md (Grundsätze) | ✅ Dokumentiert |
| "Graphiti Root Cause (10.02.): AI Ranking brauchte OpenAI API" | **FEHLT** | ❌ Nicht als Learning erfasst |
| "Browser Multi-Tab Problem: Max 5-10 aktive Tabs" | **FEHLT** | ❌ Kein Browser-Guard dafür |
| "Antwort-Disziplin: KEIN Text vor message-Tool" | **FEHLT** | ❌ Kein Hook dafür möglich |
| "KARTE ZUERST – Bevor ich anfange: Karte anlegen" | **FEHLT** | ❌ Projekt-spezifisch (BusinessMap) |

**NICHT bewährt (aus plan.md Experimenten):**

| Ansatz | Problem | Lesson Learned |
|--------|---------|----------------|
| type:prompt für Blocking | Hook feuert, erkennt Fehler, BLOCKT ABER NICHT | "beratend, nicht durchsetzend" |
| systemMessage-Anweisungen | Claude ignoriert sie | "Claude spawnt Subagents nur wenn User fragt, nicht wenn Hook es verlangt" |
| Guess-Detection via Stop-Hook | Claude argumentiert gegen dumme Blocks | "Bei 'Was kostet die Welt?' argumentiert Claude statt zu gehorchen" |

**Zentrale Erkenntnis:**
- **Was in MEMORY.md steht, hat Mathias MANUELL gelernt** (durch Frustration/Fehler)
- **taming-stan kann nur MECHANISCHE Checks durchsetzen** (Regex, Credentials, Formatting)
- **SEMANTISCHE Learnings (Browser-Hygiene, Karte zuerst, Antwort-Disziplin) brauchen BEWUSSTES BEFOLGEN der Rules**

---

## Claude Agent SDK

### Kern-Idee (1 Satz)
**Programmatischer Zugriff auf Claude Code:** Python-API für bidirektionale Konversationen, Custom Tools (in-process MCP), Hooks als Python-Funktionen, und AgentDefinitions für spezialisierte Sub-Agents.

### Wie funktionieren programmatische Subagents?

**2 Ansätze:**

#### 1. AgentDefinition (Inline-Config)

```python
from claude_agent_sdk import ClaudeAgentOptions, AgentDefinition, query

options = ClaudeAgentOptions(
    agents={
        "code-reviewer": AgentDefinition(
            description="Reviews code for best practices",
            prompt="You are a code reviewer. Analyze for bugs, security, performance.",
            tools=["Read", "Grep"],
            model="sonnet",
        ),
    },
)

async for message in query(
    prompt="Use the code-reviewer agent to review src/types.py",
    options=options
):
    print(message)
```

**Eigenschaften:**
- Agent läuft in **derselben Session** (kein separater Prozess)
- Prompt/Tools/Model werden **temporär überschrieben**
- **Kein eigener State** (teilt Session-History)
- **Kein Fork** (gleicher Kontext)

#### 2. Filesystem-Based Agents (.claude/agents/)

```python
options = ClaudeAgentOptions(
    setting_sources=["project"],  # lädt .claude/agents/*.md
    cwd="/path/to/repo"
)

async with ClaudeSDKClient(options=options) as client:
    await client.query("Use test-agent to say hello")
```

**Eigenschaften:**
- Agent-Definitionen in `.claude/agents/test-agent.md`
- Wiederverwendbar über Projekte
- Geladen via `setting_sources`

**Kritischer Unterschied zu OpenClaw `sessions_spawn`:**

| Eigenschaft | SDK AgentDefinition | OpenClaw sessions_spawn |
|-------------|---------------------|-------------------------|
| **Prozess** | Gleicher Prozess | Separater Agent-Prozess |
| **State** | Geteilt (Session-History) | Isoliert |
| **Context** | Gleicher Kontext | Eigener AGENTS.md/MEMORY.md |
| **Kommunikation** | Synchron (Funktionsaufruf) | Asynchron (sessions_send) |
| **Lifetime** | Nur während query() | Persistent bis terminated |
| **Use-Case** | Spezialisierung innerhalb Task | Parallele, autonome Tasks |

### Vergleich mit OpenClaw sessions_spawn

**OpenClaw sessions_spawn (aus AGENTS.md / multi-agent Skill):**

```python
# Stan spawnt einen Sub-Agent
spawn_result = sessions_spawn(
    sessionKey="agent:main:subagent:123",
    label="analyze-code",
    initialPrompt="Analysiere taming-stan",
    channel="discord",
    requesterChannel="discord"
)

# Sub-Agent arbeitet AUTONOM
# → Eigene AGENTS.md, MEMORY.md, Skills
# → Separater Prozess
# → Kommuniziert via sessions_send()

# Stan wartet auf Fertigstellung
sessions_history(sessionKey="agent:main:subagent:123", limit=1)
```

**Claude SDK "Agent" (AgentDefinition):**

```python
# "Agent" ist nur eine Prompt/Tool-Überschreibung
async for msg in query(
    prompt="Use code-reviewer to analyze taming-stan",
    options=ClaudeAgentOptions(
        agents={"code-reviewer": AgentDefinition(...)}
    )
):
    # Läuft SYNCHRON im selben Prozess
    # Keine Isolation, kein eigener State
```

**Fazit:**
- **SDK "Agents" sind KEINE echten Agents** (nur Prompt-Presets)
- **OpenClaw Subagents sind ECHTE parallele Workers**
- **SDK ist gut für: Spezialisierung, Fokus-Shift**
- **OpenClaw ist gut für: Parallele Arbeit, Isolation, Autonomie**

### Konkrete Einsatzmöglichkeiten für autonomous-stan

| Use-Case | SDK-Ansatz | Nutzen für autonomous-stan |
|----------|-----------|----------------------------|
| **Custom Tools (in-process MCP)** | @tool Decorator + create_sdk_mcp_server() | Skills als Python-Funktionen statt MCP-Subprocess → schneller, einfacher debuggbar |
| **Python-basierte Hooks** | HookMatcher + Python-Funktion | Hooks als Code statt CLI-Script → bessere Integration, Typsicherheit |
| **Spezialisierte Agents** | AgentDefinition für Reviewer/Tester/Analyzer | Prompt-Fokussierung für spezifische Tasks (ohne eigene Sessions) |
| **Bidirektionale Konversation** | ClaudeSDKClient.query() + receive_response() | Interaktive Dialoge (z.B. für Sparring-Mode) |
| **Permission Callbacks** | ToolPermissionCallback | Dynamische Tool-Freigaben basierend auf Context |
| **Streaming Mode** | AsyncIterator[Message] | Reaktive UIs, Progress-Updates |

**NICHT geeignet für:**
- Parallele, autonome Tasks → OpenClaw `sessions_spawn` besser
- Cross-Agent Koordination → OpenClaw `sessions_send` besser
- Langlebige Background-Workers → OpenClaw Agents besser

---

## Vergleich: taming-stan Guards vs OpenClaw Skills-System

| Dimension | taming-stan Guards | OpenClaw Skills |
|-----------|-------------------|-----------------|
| **Trigger** | Event-basiert (PreToolUse, PostToolUse) | Manual (User nennt Skill) oder Metadata-Match |
| **Durchsetzung** | HARD (kann blocken) | SOFT (Claude muss befolgen wollen) |
| **Intelligenz** | Regex/Python-Logik | Natürliche Sprache + Instruktionen |
| **Format** | Python-Scripts | Markdown mit Metadata |
| **Kontext-Verbrauch** | 0 (läuft außerhalb Claude) | ~100 Wörter Metadata immer, Body bei Aktivierung |
| **Wartung** | Code-Changes | Text-Edits |
| **Cross-Runtime** | Claude Code only | Platform-agnostisch |
| **Erweiterbarkeit** | Pull-Request ins Repo | User kann selbst erstellen |
| **Testbarkeit** | Unit-Tests (Python) | Schwer (manuelle Validierung) |
| **Verkettung** | Via Session-State | Via Instruktionen |

**Hybrides Best-of-Both:**

```
┌─────────────────────────────────────────────────────────┐
│  SKILL (OpenClaw)                                        │
│  - Instruktionen: "Nutze Graphiti BEVOR Web-Recherche" │
│  - Wann: Immer im Kontext (Metadata)                   │
│  - Wie: Claude entscheidet                             │
└─────────────────────────────────────────────────────────┘
                         ↓ (falls ignoriert)
┌─────────────────────────────────────────────────────────┐
│  GUARD (taming-stan Style)                              │
│  - Hook: graphiti-first-guard.py                        │
│  - Wann: PreToolUse WebSearch                          │
│  - Wie: BLOCK wenn graphiti_searched=false             │
└─────────────────────────────────────────────────────────┘
```

**Kombination:**
1. Skill gibt Instruktionen → Claude befolgt (meistens)
2. Guard als Sicherheitsnetz → blockt wenn Claude Regel ignoriert
3. Best of Both: Eleganz (Skill) + Garantie (Guard)

---

## Was autonomous-stan davon fehlt

### Fehlende Guards (mechanische Durchsetzung)

| Guard | Warum wichtig | Priorität |
|-------|---------------|-----------|
| **Credential-Schutz** | 903 Patterns + 3-Strikes verhindert API-Key-Leaks | ⭐⭐⭐⭐⭐ |
| **3-Strikes-Retry** | Durchbricht Fehler-Loops | ⭐⭐⭐⭐ |
| **Research-Hierarchie** | Spart API-Credits | ⭐⭐⭐ |
| **Git Conventional Commits** | Saubere History | ⭐⭐ |

### Fehlende Rules (Verhaltens-Dokumentation)

| Rule | Warum wichtig | Priorität |
|------|---------------|-----------|
| **stanflux.md** | Gründlichkeit, Empathie, Fehler-Handling, 3-Strikes-Pattern | ⭐⭐⭐⭐⭐ |
| **PITH-Notation** | Kompakte, maschinenlesbare Regeln | ⭐⭐⭐ |
| **Entity-Type-Guidelines** | 18 Types für strukturiertes Wissen | ⭐⭐⭐ |
| **Citation-Templates** | Vollständige Quellenangaben | ⭐⭐ |

### Fehlende Infrastruktur

| Feature | Warum wichtig | Priorität |
|---------|---------------|-----------|
| **Session-State-System** | Verkettung von Guards, Deduplizierung | ⭐⭐⭐⭐ |
| **group_id-Logik** | Intelligentes Routing (main vs project-*) | ⭐⭐⭐ |
| **Commands** | `/graphiti:check`, `/stanflux:challenge` | ⭐⭐ |

---

## Was autonomous-stan schon hat

### OpenClaw-exklusive Stärken

| Feature | Detail | taming-stan Equivalent |
|---------|--------|------------------------|
| **Echte Subagents** | sessions_spawn → parallele Workers | ❌ FEHLT (SDK hat nur Prompt-Presets) |
| **Agent-zu-Agent Comm** | sessions_send() | ❌ FEHLT |
| **Multi-Channel** | Discord, WhatsApp, Telegram | ❌ FEHLT (CLI only) |
| **Skills-System** | Metadata-basiert, Progressive Disclosure | ✅ Ähnlich wie Rules, aber eleganter |
| **Graphiti-Integration** | MCP-basiert | ✅ Gleich |
| **MEMORY.md** | Kuratierte Learnings über Sessions | ⚠️ Plan.md zeigt Experimente, aber kein MEMORY.md |

### Bereits implementierte taming-stan Konzepte

| Konzept | In autonomous-stan | Wo |
|---------|-------------------|-----|
| **Graphiti-First** | ✅ JA | skills/graphiti/SKILL.md (!!graphiti_gate) |
| **PITH-Notation** | ✅ JA | skills/pith/SKILL.md |
| **Entity-Types** | ✅ JA | skills/graphiti/SKILL.md |
| **stanflux-Regeln** | ⚠️ TEILWEISE | skills/stanflux/SKILL.md (aber nicht vollständig wie standalone) |
| **Credential-Schutz** | ❌ NEIN | Kein Guard vorhanden |
| **3-Strikes-Pattern** | ❌ NEIN | Kein Guard vorhanden |

---

## Konkrete Übernahme-Empfehlungen

### 1. SOFORT (High Impact, Low Effort)

#### A) Credential-Schutz Guard (critical)
```python
# autonomous-stan/.claude/hooks/pre-tool-use/credential-guard.py
# DIREKT von taming-stan/hooks/lib/secret_patterns.py übernehmen
# + taming-stan/hooks/pre-tool-use/graphiti-guard.py (Credential-Check-Logik)

from secret_patterns import detect_secret, has_keyword_with_value

def check_credentials(input_data):
    tool_name = input_data.get("tool_name")
    if tool_name.startswith("graphiti") or tool_name.startswith("mcp__graphiti"):
        args = input_data.get("tool_input", {})
        episode_body = args.get("episode_body", "")
        
        found, secret_type, _ = detect_secret(episode_body)
        if found:
            return {
                "hookSpecificOutput": {
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"❌ CREDENTIALS DETECTED: {secret_type}. Use 1Password!"
                }
            }
    return {"continue": True}
```

**Warum:** 903 Patterns schützen vor API-Key-Leaks. 3-Strikes-System bei Violation.

#### B) stanflux.md vollständig übernehmen
```bash
cp taming-stan/rules/stanflux.md autonomous-stan/docs/philosophy/stanflux.md
```

**Anpassungen:**
- Ersetze "Claude Code" → "autonomous-stan"
- Ergänze OpenClaw-spezifische Regeln (sessions_spawn, Browser-Hygiene)
- Referenziere in AGENTS.md: "Lies docs/philosophy/stanflux.md bei JEDER Session"

**Warum:** Bewährte Verhaltensregeln (Gründlichkeit, Empathie, 3-Strikes, Brownfield). Mathias MEMORY.md zeigt: funktioniert in der Praxis.

#### C) Session-State-System portieren
```python
# autonomous-stan/.openclaw/lib/session_state.py
# DIREKT von taming-stan/hooks/lib/session_state.py übernehmen

# Anpassung: State-Pfad von /tmp → ~/.openclaw/session-state/
# Grund: OpenClaw-Umgebung, Persistenz über Neustarts
```

**Warum:** Ermöglicht Guard-Verkettung. Kritisch für research-hierarchy.

### 2. BALD (High Impact, Medium Effort)

#### D) 3-Strikes-Retry Guard
```python
# autonomous-stan/.claude/hooks/post-tool-use/retry-guard.py
# Logik von taming-stan/hooks/post-tool-use/graphiti-retry-guard.py

# Anpassung: Bei 3 Fehlern → suche SOWOHL Graphiti ALS AUCH autonomous-stan/docs/troubleshooting/
```

**Warum:** Durchbricht Fehler-Loops. MEMORY.md zeigt: Learnings in Graphiti helfen.

#### E) Research-Hierarchy Guard
```python
# autonomous-stan/.claude/hooks/pre-tool-use/research-hierarchy.py
# Logik von taming-stan/hooks/pre-tool-use/graphiti-first-guard.py

# Erweiterung:
# 1. Graphiti
# 2. autonomous-stan/docs/ (Firecrawl)
# 3. Web (Web-Search)
```

**Warum:** Spart API-Credits. Nutzt eigenes Wissen zuerst.

#### F) Citation-Templates als Skill
```markdown
# autonomous-stan/skills/citation-templates/SKILL.md
---
name: citation-templates
description: Vollständige Quellenangaben für Graphiti
trigger: add_memory mit source_description
---

## Templates
- Book: Author, Title, Year, Publisher, ISBN?
- Article: Author, Title, Journal, Year, DOI
- Website: Author/Org, Title, URL, Accessed Date
- RFC: Author, Title, Number, Year, Org
- Learning: "Eigene Erfahrung [Datum]"
```

**Warum:** Strukturierte Quellenangaben. taming-stan zeigt: funktioniert.

### 3. SPÄTER (Medium Impact, High Effort)

#### G) Commands für Workflows
```markdown
# autonomous-stan/commands/graphiti/check.md
# autonomous-stan/commands/stanflux/challenge.md
# autonomous-stan/commands/stanflux/retro.md

# DIREKT von taming-stan/commands/ übernehmen
```

**Warum:** User-freundliche Workflows. Nützlich, aber nicht kritisch.

#### H) Agent SDK für Custom Tools
```python
# Beispiel: Graphiti-Tools als in-process MCP

from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("graphiti_health_check", "Check Graphiti availability")
async def graphiti_health(args):
    # Ruft Graphiti-API direkt auf
    # Schneller als MCP-Subprocess
    ...

server = create_sdk_mcp_server(
    name="graphiti-tools",
    tools=[graphiti_health, ...]
)
```

**Warum:** Schneller als MCP-Subprocess. Aber: Nur relevant wenn Performance-Problem.

### 4. NICHT übernehmen

| Feature | Warum nicht |
|---------|-------------|
| **Installer** | OpenClaw hat Plugin-System (kein manual install nötig) |
| **group_id-Logik** | Mathias Direktive 15.02.: NUR "main" nutzen |
| **playwright-guard** | Zu spezifisch für taming-stan Setup |
| **agent-browser-guard** | Nicht relevant (OpenClaw nutzt Browser anders) |

---

## Priorisierte Roadmap

```
┌──────────────────────────────────────────────────────────┐
│  PHASE 1: KRITISCHER SCHUTZ (1-2 Tage)                   │
├──────────────────────────────────────────────────────────┤
│  1. Credential-Schutz Guard (secret_patterns.py)         │
│  2. Session-State-System (~/.openclaw/session-state/)    │
│  3. stanflux.md vollständig übernehmen + anpassen        │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│  PHASE 2: QUALITÄTSSICHERUNG (3-5 Tage)                 │
├──────────────────────────────────────────────────────────┤
│  4. 3-Strikes-Retry Guard                                │
│  5. Research-Hierarchy Guard                             │
│  6. Citation-Templates Skill                             │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│  PHASE 3: UX & WORKFLOWS (1-2 Wochen)                    │
├──────────────────────────────────────────────────────────┤
│  7. Commands (/graphiti:check, /stanflux:challenge)      │
│  8. PITH-Notation in alle Docs integrieren              │
└──────────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────────┐
│  PHASE 4: OPTIMIERUNG (später)                           │
├──────────────────────────────────────────────────────────┤
│  9. Agent SDK für Custom Tools (in-process MCP)          │
│  10. Agent SDK für Python-basierte Hooks                 │
└──────────────────────────────────────────────────────────┘