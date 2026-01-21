# STAN Framework

Leichtgewichtiges Framework für autonome, qualitativ hochwertige Implementierung mit wenig Korrektur.

**Kernprinzip:** Hooks enforced Rules. Der User muss sich nichts merken.

## Aktueller Plan

**IMMER lesen:** [docs/plan.md](docs/plan.md)

Der Plan ist die Single Source of Truth für:
- Architektur-Entscheidungen
- Implementierungs-Reihenfolge
- Offene Tasks

## Meine Verpflichtungen

### Git Workflow
- **Worktree-Pflicht:** Feature-Arbeit NIEMALS direkt auf main
- Bei Feature-Arbeit: `git worktree add ../autonomous-stan-feature feature-name`
- stan_gate.py enforced das automatisch

### Plan-Pflege
- Plan IMMER im Projekt halten (`docs/plan.md`)
- Bei Änderungen: Plan aktualisieren VOR Implementierung
- Status in Plan aktuell halten

### Testing
- Alle Tests grün halten: `python -m pytest tests/ -v`
- Neue Features = neue Tests
- 81 Tests aktuell (Stand: 2026-01-21)

### Learnings
- Bei ROT→GRÜN: Learning speichern (lokal + ggf. Graphiti)
- stan_track.py erkennt das automatisch
- stan_gate.py blockiert Commit wenn pending_learnings existieren

## Projektstruktur

```
autonomous-stan/
├── .claude/hooks/stan/       # STAN Hooks (3 Stück)
├── criteria/                 # Criteria Packs (YAML)
├── templates/                # Document Templates
├── src/stan/                 # Core Library
├── tests/                    # pytest Tests
├── docs/plan.md              # Aktueller Plan
└── vendor/                   # Referenz-Frameworks
```

## Quick Commands

```bash
# Tests
source .venv/bin/activate && python -m pytest tests/ -v

# Worktree erstellen
git branch feature-name
git worktree add ../autonomous-stan-feature feature-name

# Nach Feature-Arbeit
git checkout main && git merge feature-name
git worktree remove ../autonomous-stan-feature
git branch -d feature-name
```

## Aktueller Status

**Phase:** Implementation (Phase 4: Testing & Enforcement)

**Erledigt:**
- Phase 1-3: Foundation, Core Hooks, Skill
- Worktree-Enforcement implementiert
- 81 Unit Tests

**Offen:**
- Interaktive Criteria-Tests (LLM-as-Judge)
- Tiered Learnings Storage (Recent→Hot Promotion)
- Weitere Criteria Packs
