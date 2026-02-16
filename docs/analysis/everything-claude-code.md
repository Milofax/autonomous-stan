# Everything Claude Code — Framework-Analyse

> **Analysiert:** 2026-02-16  
> **Methode:** Vollständige Code-Review + Vergleich mit bestehender Analyse + OpenClaw/Graphiti-Kontext  
> **Quelle:** `vendor/everything-claude-code/`

---

## Kern-Idee (1 Satz)

Ein **battle-tested Claude Code Plugin** aus 10+ Monaten Produktivnutzung (Anthropic Hackathon Winner), das durch **modulare Skills, spezialisierte Agents, automatisierte Hooks und Eval-Driven Development** eine produktionsreife Entwicklungsumgebung für AI-gestützte Software-Entwicklung schafft.

---

## Architektur

### Plugin-Struktur (Modular & Installierbar)

```
everything-claude-code/
├── .claude-plugin/          # Plugin-Manifest für Marketplace
│   ├── plugin.json          # Metadaten, Komponenten-Pfade
│   └── marketplace.json     # Marketplace-Katalog
│
├── agents/                  # 9 spezialisierte Sub-Agents
│   ├── planner.md           # Implementierungs-Planung
│   ├── architect.md         # System-Design + ADRs
│   ├── tdd-guide.md         # Test-Driven Development
│   ├── code-reviewer.md     # Quality Review
│   ├── security-reviewer.md # OWASP Top 10, Vulnerability Scanning
│   ├── build-error-resolver.md
│   ├── e2e-runner.md        # Playwright E2E
│   ├── refactor-cleaner.md  # Dead Code Cleanup
│   └── doc-updater.md       # Dokumentations-Sync
│
├── skills/                  # Workflow-Definitionen
│   ├── coding-standards/    # Language Best Practices
│   ├── backend-patterns/    # API, DB, Caching
│   ├── frontend-patterns/   # React, Next.js
│   ├── continuous-learning/ # Auto-Pattern-Extraktion
│   ├── strategic-compact/   # Manuelle Compaction-Vorschläge
│   ├── tdd-workflow/        # TDD Methodik
│   ├── security-review/     # Security Checklist
│   ├── eval-harness/        # Eval-Driven Development
│   └── verification-loop/   # 6-Phase Quality Gates
│
├── commands/                # Slash-Commands
│   ├── /tdd                 # TDD Workflow starten
│   ├── /plan                # Implementierungs-Plan
│   ├── /e2e                 # E2E-Tests generieren
│   ├── /code-review         # Code Review triggern
│   ├── /learn               # Patterns mid-session extrahieren
│   ├── /checkpoint          # Verification State speichern
│   └── /verify              # Verification Loop ausführen
│
├── rules/                   # Always-Follow Guidelines
│   ├── security.md          # Mandatory Security Checks
│   ├── coding-style.md      # Immutability, File Organization
│   ├── testing.md           # TDD, 80% Coverage
│   ├── git-workflow.md      # Commit Format, PR Process
│   ├── agents.md            # Agent-Delegation Rules
│   └── performance.md       # Model Selection, Context Management
│
├── hooks/                   # Event-Driven Automations
│   ├── hooks.json           # Hook-Konfiguration (alle Events)
│   ├── memory-persistence/  # Session Lifecycle (Start/End)
│   └── strategic-compact/   # Tool-Call Counter
│
├── scripts/                 # Cross-Platform Node.js Implementierungen
│   ├── lib/
│   │   ├── utils.js         # Platform-agnostische File/Path/System Utils
│   │   └── package-manager.js # Package Manager Detection (npm/pnpm/yarn/bun)
│   └── hooks/
│       ├── session-start.js  # Context Loader
│       ├── session-end.js    # State Persister
│       ├── pre-compact.js    # State Backup vor Compaction
│       ├── suggest-compact.js # Tool-Call Counter
│       └── evaluate-session.js # Pattern Extraction
│
├── contexts/                # Dynamische System Prompt Injection
│   ├── dev.md               # Development Mode
│   ├── review.md            # Code Review Mode
│   └── research.md          # Research/Exploration Mode
│
├── mcp-configs/             # MCP Server Konfigurationen
│   └── mcp-servers.json     # 15+ vorkonfigurierte MCPs
│
└── examples/                # Beispiel-Konfigurationen
    ├── CLAUDE.md            # Projekt-Level Config
    └── user-CLAUDE.md       # User-Level Config
```

### Architektur-Prinzipien

1. **Modularität:** Jede Komponente ist eigenständig installierbar
2. **Cross-Platform:** Node.js Scripts statt Shell (Windows/macOS/Linux)
3. **Plugin-System:** Installierbar via Marketplace oder manuell
4. **Event-Driven:** Hooks auf PreToolUse, PostToolUse, SessionStart, SessionEnd, Stop, PreCompact
5. **Delegation:** Spezialisierte Agents statt Monolith
6. **Eval-First:** Verification Loops + Eval Harness für Qualität

---

## Einzigartige Stärken (continuous-learning-v2!)

### 1. **Continuous Learning System** (SessionEnd Hook)

**Was es macht:**
- SessionEnd Hook analysiert Session-Transcript auf Patterns
- Extrahiert wiederverwendbare Lösungen automatisch
- Speichert sie in `~/.claude/skills/learned/[pattern].md`

**Kategorien:**
- Error Resolution Patterns
- User Corrections
- Workarounds (Library Quirks)
- Debugging Techniques
- Project-Specific Conventions

**Konfigurierbar:**
```json
{
  "min_session_length": 10,
  "extraction_threshold": "medium",
  "auto_approve": false,
  "patterns_to_detect": [
    "error_resolution", "user_corrections", "workarounds",
    "debugging_techniques", "project_specific"
  ],
  "ignore_patterns": ["simple_typos", "one_time_fixes"]
}
```

**Warum SessionEnd statt UserPromptSubmit?**
- Läuft einmal am Ende (lightweight)
- Kein Latenz-Overhead pro Message
- Vollständiger Session-Kontext verfügbar

**Kritische Bewertung:**
- ✅ **Automatisch:** Nichts wird vergessen
- ✅ **Konsistent:** Immer gleicher Prozess
- ❌ **Qualitätsproblem:** WAS ist ein "Learning"? Algorithmus entscheidet, nicht Mensch
- ❌ **Noise-Gefahr:** Triviale Patterns könnten auch gespeichert werden
- ⚠️ **Kontext-Abhängig:** Funktioniert NUR wenn Session-Transcripts verfügbar

### 2. **Strategic Compaction** (PreToolUse Hook)

**Was es macht:**
- Zählt Tool-Calls pro Session
- Bei 50 Calls: "Erwäge /compact"
- Danach alle 25 Calls erneut
- Counter in Session-spezifischer Temp-Datei

**Philosophie:**
> Manuelle Compaction an logischen Grenzen > Auto-Compaction mitten in Task

**Logische Grenzen:**
- Nach Exploration, vor Execution
- Nach Milestone-Completion
- Vor Major Context Shift

**Kritische Bewertung:**
- ✅ **Bewusstsein:** User wird erinnert
- ❌ **Zu simpel:** Tool-Call-Zählung ≠ Phase-Wechsel
- ⚠️ **Noise:** Bei 75, 100, 125 Calls nervt es
- 💡 **Besser wäre:** Phase-basierte Erkennung (DEFINE → PLAN Wechsel)

### 3. **Verification Loop** (6-Phase Quality Gates)

**Die 6 Phasen:**

```bash
# Phase 1: Build
npm run build

# Phase 2: Types
npx tsc --noEmit

# Phase 3: Lint
npm run lint

# Phase 4: Tests + Coverage
npm test -- --coverage  # Target: 80%+

# Phase 5: Security
grep -r "console.log" src/
grep -r "sk-" .

# Phase 6: Diff Review
git diff --stat
```

**Output: Verification Report**
```
VERIFICATION REPORT
==================
Build:     [PASS/FAIL]
Types:     [PASS/FAIL] (X errors)
Lint:      [PASS/FAIL] (X warnings)
Tests:     [PASS/FAIL] (X/Y passed, Z% coverage)
Security:  [PASS/FAIL] (X issues)
Diff:      [X files changed]
Overall:   [READY/NOT READY] for PR
```

**Kritische Bewertung:**
- ✅ **Systematisch:** Keine Checks werden vergessen
- ✅ **Reproduzierbar:** Immer gleiche Schritte
- ✅ **Pre-Commit:** Verhindert fehlerhafte Commits
- 💡 **Erweiterbar:** Python-Projekte brauchen ruff/pytest/bandit

### 4. **Eval Harness** (Eval-Driven Development)

**Philosophie:** Evals sind die "Unit Tests of AI Development"

**Workflow:**
1. **Define** (vor Code): Capability + Regression Evals schreiben
2. **Implement:** Code schreiben um Evals zu bestehen
3. **Evaluate:** Evals ausführen
4. **Report:** pass@k Metriken

**Eval-Typen:**

| Typ | Zweck | Beispiel |
|-----|-------|----------|
| Capability | Neue Fähigkeiten testen | "Can create user account" |
| Regression | Bestehende Funktionen | "Existing login still works" |

**Grader-Typen:**

| Grader | Determinismus | Verwendung |
|--------|---------------|------------|
| Code-Based | ✅ Deterministisch | grep, tests, build checks |
| Model-Based | ⚠️ Probabilistisch | Code-Qualität, Open-ended |
| Human | 👤 Manual | Security, UX |

**Metriken:**
- **pass@k:** "Mindestens 1 Erfolg in k Versuchen"
  - pass@1: First-Attempt Success Rate
  - pass@3: Success within 3 attempts (Target: >90%)
- **pass^k:** "Alle k Versuche erfolgreich" (Stricter)
  - pass^3: 3 consecutive successes

**Kritische Bewertung:**
- ✅ **Rigorose Qualität:** Evals vor Code zwingt zu klarem Denken
- ✅ **Messbar:** pass@k ist objektive Metrik
- ✅ **Regression-Schutz:** Bestehende Funktionen werden geschützt
- ⚠️ **Overhead:** Eval-Definition kostet Zeit
- 💡 **Best Practice:** Nur für kritische Features (Auth, Payments)

### 5. **Spezialisierte Agents** (9 Agents mit klaren Rollen)

**Besonders wertvoll:**

#### architect.md
- **Rolle:** ADRs (Architecture Decision Records)
- **Output:** Trade-Off-Analyse, System-Design
- **Trigger:** Neue Features, Refactoring, Skalierung
- **Besonderheit:** Dokumentiert WARUM Entscheidungen getroffen wurden

**ADR-Format:**
```markdown
# ADR-001: Use Redis for Vector Storage

## Context
Need fast vector search for embeddings.

## Decision
Redis Stack with vector search.

## Consequences
Positive:
- <10ms latency
- Simple deployment

Negative:
- In-memory (expensive)
- Single point of failure

Alternatives:
- PostgreSQL pgvector (slower)
- Pinecone (expensive)

Status: Accepted
Date: 2025-01-15
```

#### security-reviewer.md
- **Rolle:** OWASP Top 10, Vulnerability Scanning
- **Checks:** SQL Injection, XSS, SSRF, Hardcoded Secrets, Race Conditions
- **Tools:** npm audit, eslint-plugin-security, trufflehog
- **Besonderheit:** Speziell für Fintech (Race Conditions in Balance Checks!)

**Beispiel-Check (Financial):**
```javascript
// ❌ CRITICAL: Race Condition
const balance = await getBalance(userId);
if (balance >= amount) {
  await withdraw(userId, amount); // Another request could withdraw in parallel!
}

// ✅ CORRECT: Atomic Transaction
await db.transaction(async (trx) => {
  const balance = await trx('balances')
    .where({ user_id: userId })
    .forUpdate() // Lock row
    .first();
  if (balance.amount < amount) throw new Error('Insufficient balance');
  await trx('balances').where({ user_id: userId }).decrement('amount', amount);
});
```

#### code-reviewer.md
- **Rolle:** Quality + Security vor Commit
- **Checks:** Code Style, Duplicated Code, Performance, Test Coverage
- **Output:** CRITICAL / HIGH / MEDIUM / LOW Issues
- **Besonderheit:** Blockiert Commits bei CRITICAL/HIGH

### 6. **Memory Persistence Hooks**

**SessionStart:**
- Lädt letzten Session-State
- Zeigt verfügbare Session-Files (letzten 7 Tage)
- Listet Learned Skills
- Erkennt Package Manager

**SessionEnd:**
- Speichert Session-State
- Triggert Continuous Learning

**PreCompact:**
- Sichert State vor Auto-Compaction
- Backup wichtiger Context-Elemente

### 7. **Cross-Platform Node.js Scripts**

**Problem gelöst:**
- Ursprünglich Bash-Scripts (nur macOS/Linux)
- Jetzt Node.js (Windows/macOS/Linux)

**Package Manager Detection (6-Level Chain):**
1. `CLAUDE_PACKAGE_MANAGER` env var
2. `.claude/package-manager.json` (project)
3. `package.json` → `packageManager` field
4. Lock Files (package-lock.json, yarn.lock, pnpm-lock.yaml, bun.lockb)
5. `~/.claude/package-manager.json` (global)
6. Fallback: First available

**Kritische Bewertung:**
- ✅ **Echte Cross-Platform Kompatibilität**
- ✅ **Intelligente Detection**
- ❌ **STAN braucht das nicht** (Python-Projekte)

### 8. **Context-Injection Modes**

**3 Modi:**
- `dev.md`: Development Mode (Priorisiert Tools)
- `review.md`: Code Review Mode (Read-Only, Analysis)
- `research.md`: Exploration Mode (Web Search, Docs)

**Kritische Bewertung:**
- ⚠️ **STAN hat bereits Phasen** (DEFINE/PLAN/CREATE)
- 💡 **Redundant für STAN**

---

## Schwächen/Limitierungen

### 1. **Continuous Learning: Qualitätsproblem**

**Problem:** WAS ist ein "Learning"?
- Algorithmus muss erkennen ob Pattern wiederverwendbar ist
- Risiko: Triviale Patterns werden auch gespeichert
- Noise in `~/.claude/skills/learned/`

**Warum nicht einfach manuelle Speicherung?**
- Graphiti + `!!save_immediately` Rule ist BESSER
- User entscheidet bewusst was wertvoll ist
- Höhere Qualität

**Fazit:** Feature für Umgebungen OHNE Graphiti.

### 2. **Strategic Compact: Zu simpel**

**Problem:** Tool-Call-Zählung ≠ logische Phase
- 50 Calls können mitten in Task passieren
- 100 Calls können alle in einer Phase sein

**Was wirklich zählt:**
- DEFINE → PLAN Wechsel
- Feature Complete
- Themen-Wechsel

**Besser wäre:**
- Phase-basierte Erkennung
- Task-Abschluss-Trigger
- Intelligente Heuristiken

### 3. **MCP Overload Warning fehlt Enforcement**

**Warnung im README:**
> "Don't enable all MCPs at once. 200k context → 70k with too many tools."

**Problem:**
- Nur Warnung, keine Enforcement
- User kann trotzdem 30 MCPs aktivieren

**Besser wäre:**
- Tool-Count-Checker (z.B. max 80 Tools)
- Warning bei SessionStart wenn >80 Tools
- Vorschlag welche MCPs zu disablen

### 4. **Hooks können Session blockieren**

**Beispiel:** PreToolUse Hook auf `git push`
```json
{
  "matcher": "tool == \"Bash\" && tool_input.command matches \"git push\"",
  "hooks": [{
    "type": "command",
    "command": "echo 'Review changes before push...'"
  }]
}
```

**Problem:**
- Wenn Hook `exit 1` macht → Tool blocked
- Keine Möglichkeit User-Override

**Besser wäre:**
- Warnings statt Blocks (default)
- Opt-in Blocking via Config

### 5. **Eval Harness: Overhead für kleine Projekte**

**Problem:**
- Eval-Definition + Execution kostet Zeit
- Für kleine Features overkill

**Wann sinnvoll:**
- Kritische Features (Auth, Payments)
- Komplexe Business Logic
- Regressions-anfällige Bereiche

**Wann nicht:**
- Simple CRUD
- UI-Komponenten
- Prototyping

### 6. **Keine Integration mit CI/CD**

**Problem:**
- Verification Loop läuft nur lokal
- Keine GitHub Actions / GitLab CI Integration

**Besser wäre:**
- `.github/workflows/verify.yml`
- Pre-Commit Hook Installation Script
- CI/CD Templates

### 7. **Agent-Definitionen sind statisch**

**Problem:**
- Agents sind Markdown-Files
- Keine dynamische Konfiguration
- Projekt-spezifische Anpassungen schwierig

**Besser wäre:**
- Template-System
- Variable Substitution
- Project-Context Injection

---

## Key Features

### Top 10 Features nach Wichtigkeit

| # | Feature | Kategorie | Impact |
|---|---------|-----------|--------|
| 1 | **Verification Loop** | Quality | Systematische Pre-Commit Checks |
| 2 | **Security Reviewer** | Security | OWASP Top 10, Vulnerability Scanning |
| 3 | **Architect Agent** | Design | ADRs, Trade-Off Analysis |
| 4 | **Eval Harness** | Quality | Eval-Driven Development, pass@k |
| 5 | **Code Reviewer** | Quality | Automated Quality Gates |
| 6 | **TDD Workflow** | Testing | Test-First Development |
| 7 | **Continuous Learning** | Memory | Auto-Pattern Extraction |
| 8 | **Hooks System** | Automation | Event-Driven Workflows |
| 9 | **Cross-Platform Scripts** | DevEx | Windows/macOS/Linux Support |
| 10 | **MCP Configs** | Integration | 15+ vorkonfigurierte MCPs |

### Innovative Features (nicht in anderen Frameworks)

1. **Eval-Driven Development** (Eval Harness)
   - pass@k Metriken
   - Capability + Regression Evals
   - Code/Model/Human Grader Types

2. **Architecture Decision Records** (Architect Agent)
   - Strukturierte Trade-Off Analyse
   - Alternatives Considered
   - Warum + Wann Dokumentation

3. **Strategic Compaction** (vs. Auto-Compact)
   - Manuelle Kontrolle über Compaction
   - Logische Grenzen statt Overflow

4. **Continuous Learning** (SessionEnd Hook)
   - Auto-Extraktion von Patterns
   - Kategorisierung (Error Resolution, Workarounds, etc.)

5. **6-Phase Verification Loop**
   - Build → Types → Lint → Tests → Security → Diff
   - Comprehensive Pre-Commit Gate

---

## Was die bestehende Analyse richtig erkannt hat

### ✅ Korrekte Erkenntnisse

1. **SessionEnd Hook ist für Umgebungen OHNE Graphiti**
   > Bestätigt: Continuous Learning löst ein Problem das STAN mit Graphiti bereits hat.

2. **Strategic Compact ist zu simpel**
   > Bestätigt: Tool-Call-Counter ist keine intelligente Phase-Erkennung.

3. **Verification Loop ist wertvoll**
   > Bestätigt: Systematische Quality Gates fehlen in STAN.

4. **3 Agents sind wertvoll (architect, code-reviewer, security-reviewer)**
   > Bestätigt: Systematische Reviews fehlen.

5. **Context-Injection redundant zu STAN's Phasen**
   > Bestätigt: DEFINE/PLAN/CREATE ist spezifischer.

6. **PreCompact Hook redundant**
   > Bestätigt: docs/tasks.md + Graphiti reichen.

7. **Stop Hook marginaler Nutzen**
   > Bestätigt: User kann einfach "weiter" sagen.

8. **Package Manager Detection für Python irrelevant**
   > Bestätigt: STAN ist Python-basiert.

### ✅ Richtige Entscheidungs-Matrix

| Feature | Implementieren? |
|---------|-----------------|
| SessionEnd Hook | ❌ NEIN (Graphiti ist besser) |
| Tool-Counter | ❌ NEIN (zu simpel) |
| Agents (3 von 9) | ✅ JA |
| Continuous Learning | ❌ NEIN (Qualitätsproblem) |
| Verification Loop | ✅ JA |
| Context-Modes | ❌ NEIN (Phasen existieren) |
| PreCompact | ❌ NEIN (redundant) |
| Stop Hook | ❌ NEIN (Low ROI) |

---

## Was die bestehende Analyse ÜBERSEHEN hat

### 1. **Eval Harness ist das innovativste Feature**

**Übersehen:**
- Die bestehende Analyse behandelt Verification Loop (6-Phase)
- Aber NICHT das Eval Harness (Eval-Driven Development)

**Warum wichtig:**
- Eval-Driven Development ist ein **Paradigma**, nicht nur ein Tool
- pass@k Metriken sind objektive Qualitätsindikatoren
- Capability + Regression Evals strukturieren Entwicklung

**Was STAN fehlt:**
- Systematische Evals für kritische Features
- pass@k Tracking
- Eval-Before-Code Workflow

**Empfehlung:**
- Eval Harness für STAN adaptieren (Python-Version)
- Speziell für Mathias' AI-Produkte (Zenith, Marakanda AI)

### 2. **Architecture Decision Records (ADRs) sind einzigartig wertvoll**

**Übersehen:**
- Bestehende Analyse nennt "architect.md" als wertvoll
- Aber NICHT die ADR-Struktur explizit

**Warum wichtig:**
- ADRs dokumentieren WARUM Entscheidungen getroffen wurden
- Context, Decision, Consequences, Alternatives
- Langfristig wertvoller als Code-Kommentare

**Was STAN fehlt:**
- Strukturierte Architektur-Dokumentation
- Trade-Off Analyse in `docs/`
- Historical Context für Entscheidungen

**Empfehlung:**
- ADR-Template in `docs/adr/ADR-001-template.md`
- Architect Agent für ADR-Erstellung

### 3. **Security Reviewer geht weit über OWASP hinaus**

**Übersehen:**
- Bestehende Analyse nennt "security-reviewer.md"
- Aber NICHT die Fintech-spezifischen Checks (Race Conditions!)

**Warum wichtig:**
- Fintech braucht mehr als OWASP Top 10
- Race Conditions in Balance Checks sind CRITICAL
- Atomic Transactions sind essentiell

**Was STAN fehlt:**
- Fintech-spezifische Security Checks
- Race Condition Detection
- Transaction Integrity Verification

**Empfehlung:**
- Security Reviewer für STAN adaptieren
- Fintech Checklist für Mathias' Projekte

### 4. **Hooks sind nicht nur Automation, sondern Workflow-Integration**

**Übersehen:**
- Bestehende Analyse listet Hooks
- Aber NICHT die Workflow-Integration-Logik

**Beispiel:**
```json
{
  "matcher": "tool == \"Bash\" && tool_input.command matches \"gh pr create\"",
  "hooks": [{
    "type": "command",
    "command": "node -e \"...[extract PR URL]...\""
  }]
}
```

**Warum wichtig:**
- Hook extrahiert PR URL und gibt `gh pr review` Command
- Das ist nicht nur Automation, sondern NEXT-STEP-GUIDANCE

**Was STAN fehlt:**
- Next-Step Guidance nach Tool-Calls
- Context-Aware Suggestions
- Workflow-Chaining

**Empfehlung:**
- PostToolUse Hooks für Git-Workflow
- PR-URL Extraktion + Review Command

### 5. **Cross-Platform Scripts lösen REALES Problem**

**Übersehen:**
- Bestehende Analyse sagt "STAN braucht das nicht (Python)"
- Aber übersieht: Node.js Scripts sind UNIVERSELLER

**Warum wichtig:**
- Viele Projekte nutzen BEIDE (Python Backend + Node.js Frontend)
- Cross-Platform Scripts funktionieren überall
- `scripts/lib/utils.js` ist wiederverwendbare Bibliothek

**Was STAN fehlt:**
- Wiederverwendbare Script-Bibliothek
- Cross-Platform File-Operationen
- Temp-File Management

**Empfehlung:**
- `scripts/lib/utils.js` nach STAN portieren (Python-Version)
- Für Cross-Project Utilities

### 6. **MCP-Configs sind kuratiertes Wissen**

**Übersehen:**
- Bestehende Analyse erwähnt MCP-Configs nicht

**Warum wichtig:**
- 15+ vorkonfigurierte MCPs mit ENV-Variablen
- Best Practices für MCP-Setup
- Context-Window-Warning

**Was STAN fehlt:**
- Kuratierte MCP-Liste mit Setup-Anleitung
- Context-Window Management Rules

**Empfehlung:**
- MCP-Konfigs nach `docs/mcp-setup.md`
- Tool-Count Monitoring

### 7. **Hooks.json ist vollständiges Hook-System**

**Übersehen:**
- Bestehende Analyse listet einzelne Hooks
- Aber NICHT das vollständige System

**Hook-Events:**
- PreToolUse
- PostToolUse
- SessionStart
- SessionEnd
- Stop
- PreCompact

**Warum wichtig:**
- Vollständige Event-Coverage
- Matchers mit Regex
- Command + Stdin/Stdout Handling

**Was STAN fehlt:**
- Systematische Hook-Organisation
- Event-Coverage Matrix

**Empfehlung:**
- Hook-System dokumentieren
- Event-Katalog erstellen

---

## Was autonomous-stan davon fehlt

### Kategorie 1: CRITICAL (Muss implementiert werden)

#### 1.1 **Verification Loop** (6-Phase Quality Gates)

**Warum CRITICAL:**
- STAN hat keine systematischen Pre-Commit Checks
- Fehlerhafte Commits kosten Zeit (Revert → Fix → Re-Commit)
- CI-Failures sind vermeidbar

**Was fehlt:**
```python
# verification_loop.py
def verify():
    checks = [
        ("Syntax", "python -m py_compile {files}"),
        ("Lint", "ruff check ."),
        ("Tests", "pytest"),
        ("Security", "bandit -r ."),
        ("Git", "git diff --check")
    ]
    for name, cmd in checks:
        if not run(cmd).success:
            return deny(f"[STAN] {name} failed")
    return allow()
```

**Integration:**
- `stan_gate.py` → Automatisch vor jedem Commit
- Blockiert bei CRITICAL/HIGH Issues

#### 1.2 **Security Reviewer Agent**

**Warum CRITICAL:**
- STAN arbeitet an Fintech-Projekten (Mathias' AI-Produkte)
- Race Conditions in Balance Checks sind CRITICAL
- OWASP Top 10 müssen gecheckt werden

**Was fehlt:**
```markdown
# .claude/agents/stan/security-reviewer.md

Fintech Security Checks:
- [ ] Atomic Transactions (no race conditions)
- [ ] Balance Checks vor Withdrawal
- [ ] Rate Limiting auf Financial Endpoints
- [ ] Audit Logging für Money Movements
- [ ] No Hardcoded Secrets
```

**Integration:**
- Automatisch vor `/stan create` Commit
- Blockiert bei CRITICAL Issues

#### 1.3 **Architecture Decision Records (ADRs)**

**Warum CRITICAL:**
- STAN trifft Architektur-Entscheidungen ohne Dokumentation
- 6 Monate später: "Warum haben wir das so gemacht?"
- ADRs sind langfristiges Wissen

**Was fehlt:**
```markdown
# docs/adr/ADR-001-template.md

# ADR-XXX: [Title]

## Context
[Problem/Situation]

## Decision
[What we decided]

## Consequences
Positive:
- ...
Negative:
- ...

Alternatives:
- Option 1: [Pro/Con]
- Option 2: [Pro/Con]

Status: [Proposed/Accepted/Deprecated]
Date: YYYY-MM-DD
```

**Integration:**
- Architect Agent erstellt ADRs
- Triggern bei neuen Features, Refactorings

### Kategorie 2: HIGH (Sollte implementiert werden)

#### 2.1 **Eval Harness** (Eval-Driven Development)

**Warum HIGH:**
- Kritische Features (Auth, Payments) brauchen systematische Evals
- pass@k Metriken sind objektive Qualität
- Regression-Schutz

**Was fehlt:**
```markdown
# .claude/evals