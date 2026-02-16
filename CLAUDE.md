# autonomous-stan (Development)

Autonomes Workflow-Framework mit modularen Denkwerkzeugen für Claude Code.

## Language Rules

- **Conversation:** German with the user
- **All files:** English (documentation, config, code, comments, commit messages)
- **Plugin name:** Always "autonomous-stan" (not "stan" alone)

## Verpflichtend

1. **Plan lesen:** [docs/plan.md](docs/plan.md)
2. **Tasks nutzen und Status aktuell halten:** [docs/tasks.md](docs/tasks.md)
3. **Parallelisierung wo möglich:** Tasks ohne Datei-Überschneidung parallel ausführen

## KRITISCH: Keine STAN Hooks in diesem Projekt!

**NIEMALS** STAN Hooks in `autonomous-stan` aktivieren oder installieren!

- Dieses Projekt **entwickelt** das autonomous-stan Framework
- Die Hooks gehören in das **autonomous-stan Plugin** (separates Repo für Installation)
- Das Plugin wird dann in **andere Projekte** installiert
- Hier: Entwicklung, Testing, kein Selbst-Enforcement

**Wenn du STAN Hooks hier siehst → DEAKTIVIEREN, nicht nutzen.**

Die Features werden hier über `/stan` Skills getestet, NICHT über Hooks.

## Arbeitsweise

- **Techniques nutzen:** Bei Problemen → `/stan think` oder Purpose wählen
- **Criteria-Check:** "Würde das meine eigenen Criteria bestehen?"
- **Parallelisierung:** Unabhängige Tasks parallel, Subagents nutzen

## WICHTIG: Single Source of Truth

**IGNORIERE** alle Pläne in `~/.claude/plans/` oder anderen Claude-internen Verzeichnissen.

Die einzige gültige Quelle für Planung und Tasks ist:
- `docs/plan.md` - Der Plan
- `docs/tasks.md` - Die Task-Liste

Diese Projekt-Dateien sind IMMER aktueller als Claude-interne Pläne.

## Claude Code Version-Tracking

**Zuletzt geprüft:** v2.1.19 (2026-01-24)

### Automatische Prüfung

Bei Session-Start in diesem Projekt:
1. Prüfe aktuelle Claude Code Version (`claude --version`)
2. Wenn neuer als `Zuletzt geprüft` → Changelog auf GitHub lesen
3. Analysiere Impact auf STAN Framework
4. Informiere User über relevante Änderungen
5. Aktualisiere `Zuletzt geprüft` auf neue Version + Datum

### Bekannte Features (Stand v2.1.19)

- **Claude Tasks (v2.1.16+):** Task-Management mit Dependencies, Status-Workflow, Multi-Agent Support
  - STAN nutzt hybrides Modell: Claude Tasks = Runtime-Layer, docs/tasks.md = Planning-Layer
- **CLAUDE_CODE_ENABLE_TASKS:** Env-Var zum Deaktivieren (default: enabled)

### Changelog-Quelle

GitHub: `gh api repos/anthropics/claude-code/contents/CHANGELOG.md`

## Hook-Architektur (Validiert 2026-01-25)

### Erkenntnisse

| Hook-Typ | Datei-Zugriff | Subagent spawnen |
|----------|---------------|------------------|
| `type: prompt` | ❌ Nein ($TRANSCRIPT_PATH ist nur String) | ❌ Nein |
| `type: command` | ✅ Ja (via stdin JSON) | ❌ Nein (kann nur systemMessage) |

### Lösung: Command-Hook + Subagent via Task Tool

```
Hook (PostToolUse) → Liest Criteria → systemMessage
                                           ↓
Hauptagent → Task(model="haiku", prompt="Evaluiere...") → Subagent
                                                              ↓
                                                     PASS / FAIL / WARN
```

**Vorteile:**
- Kein API-Token nötig (nutzt Subscription)
- Subagent hat separaten Kontext (nicht "committed" zum Edit)
- Unabhängige Evaluation erkennt Self-Serving Bias

### Dateistruktur (analog taming-stan)

```
scripts/
├── prompts/*.md          # Evaluator-Prompts als Markdown
├── lib/                  # Shared Code
└── *.py                  # Hook-Scripts

hooks/
└── hooks.json            # Config mit ${CLAUDE_PLUGIN_ROOT}
```
