# STAN Framework

Leichtgewichtiges Framework für autonome, qualitativ hochwertige Implementierung mit wenig Korrektur.

**Status:** 🚧 Initial Development (0.x.x)

## Konzept

STAN kombiniert bewährte Frameworks zu einem einheitlichen Workflow:

- **BMAD** - Kreativität und Struktur
- **Ralph** - Leichtgewichtige Ausführung
- **PRP** - PRD-Struktur
- **STAN.FLUX** - Verhaltensregeln

### Kernprinzip

> Hooks enforce Rules. Der User muss sich nichts merken.

## Phasen-Modell

```
[DEFINE] ──────> [PLAN] ──────> [CREATE]
Interaktiv      Interaktiv      Autonom
PRD erstellen   Tasks planen    Ausführen
```

## Installation

```bash
# Repository klonen
git clone https://github.com/Milofax/autonomous-stan.git
cd autonomous-stan

# Submodules initialisieren
git submodule update --init --recursive
```

## Struktur

```
autonomous-stan/
├── .claude/
│   ├── hooks/          # Enforcement Hooks
│   ├── skills/         # /stan Skills
│   └── rules/          # Verhaltensregeln
├── criteria/           # Qualitätskriterien (YAML)
├── templates/          # Dokument-Templates (Markdown)
├── docs/
│   └── plan.md         # Implementierungsplan
└── vendor/             # Referenz-Frameworks (Submodules)
```

## Skills

| Skill | Beschreibung |
|-------|--------------|
| `/stan init` | Projekt starten |
| `/stan define` | DEFINE Phase |
| `/stan plan` | PLAN Phase |
| `/stan create` | CREATE Phase (autonom) |
| `/stan statusupdate` | Status anzeigen/ändern |
| `/stan healthcheck` | Konsistenz prüfen |
| `/stan build-template` | Template interaktiv bauen |
| `/stan build-criteria` | Criteria interaktiv bauen |

## Dokumentation

- [Implementierungsplan](docs/plan.md)

## Lizenz

MIT License - siehe [LICENSE](LICENSE)

## Mitwirken

Siehe [CONTRIBUTING.md](CONTRIBUTING.md)
