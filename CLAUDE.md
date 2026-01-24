# autonomous-stan (Development)

Autonomes Workflow-Framework mit modularen Denkwerkzeugen für Claude Code.

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
