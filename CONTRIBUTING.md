# Contributing to STAN Framework

## Workflow

Wir nutzen **GitHub Flow**:

1. Branch von `main` erstellen: `feature/`, `fix/`, `docs/`, `chore/`
2. Änderungen committen (Conventional Commits)
3. Pull Request erstellen
4. Review + CI muss grün sein
5. Squash & Merge

## Conventional Commits

Format: `type(scope): description`

**Types:**
- `feat` - Neue Features (→ MINOR Version)
- `fix` - Bugfixes (→ PATCH Version)
- `docs` - Dokumentation
- `style` - Formatierung (kein Code-Change)
- `refactor` - Code-Umbau ohne Feature-Änderung
- `perf` - Performance-Verbesserungen
- `test` - Tests hinzufügen/ändern
- `build` - Build-System
- `ci` - CI/CD Konfiguration
- `chore` - Sonstiges

**Beispiele:**
```
feat(hooks): add stan-gate pre-tool-use hook
fix(skills): handle missing stan.md gracefully
docs: update README with installation steps
```

**Breaking Changes:** `feat!:` oder `BREAKING CHANGE:` im Footer (→ MAJOR Version)

## Commit Messages

- Subject: Max 50 Zeichen, Imperativ ("Add feature", nicht "Added feature")
- Body: Erkläre WARUM, nicht WAS
- Footer: Issue-Referenzen, Breaking Changes

## Pull Requests

- Ideal: < 200 LOC
- Beschreibung: Was, Warum, Wie testen
- Self-Review vor Request
- CI muss grün sein

## Versioning

Wir nutzen [Semantic Versioning](https://semver.org/):

- `0.x.x` - Initial Development (aktuell)
- `1.0.0` - Erste stabile Version

## Entwicklung

```bash
# Repository klonen
git clone https://github.com/Milofax/autonomous-stan.git
cd autonomous-stan

# Submodules initialisieren
git submodule update --init --recursive

# Feature-Branch erstellen
git checkout -b feature/my-feature

# Nach Änderungen
git add .
git commit -m "feat(scope): description"
git push -u origin feature/my-feature
```
