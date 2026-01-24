# Plan: Internationalization (i18n) & User Preferences

**Ziel:** Framework-Dokumente auf Englisch, Kommunikations- und Dokumentsprache konfigurierbar, User-Personalisierung.

**Inspiriert von:** BMAD-METHOD (persona config, language settings)

---

## 1. Config-Schema

### `.stan/config.yaml`

```yaml
# STAN Framework Configuration
# Created by: /stan init

# --- User Preferences ---
user:
  name: "Mathias"              # How STAN addresses you
  skill_level: intermediate    # beginner | intermediate | expert
                               # - beginner: detailed explanations
                               # - intermediate: balanced (default)
                               # - expert: direct, technical, no hand-holding

# --- Language Settings ---
language:
  communication: de            # Language for conversation (de | en | fr | es | ...)
  documents: en                # Language for generated docs (PRD, Plan, etc.)
  # Note: Framework internals (templates, criteria) are always English

# --- Project Settings ---
project:
  name: "My Project"           # Project display name
  output_folder: ".stan"       # Where STAN stores state
```

### Warum kein "auto"?

| Problem mit "auto" | Unsere Lösung |
|--------------------|---------------|
| Unzuverlässig - Claude fällt zurück | Explizite Sprachwahl bei `/stan init` |
| Inkonsistent während Session | Sprache wird bei jeder Nachricht injiziert |
| Nicht reproduzierbar | Config ist persistent und eindeutig |

### Skill-Level Auswirkungen

| Level | Kommunikationsstil |
|-------|-------------------|
| **beginner** | Ausführliche Erklärungen, Analogien, Schritt-für-Schritt |
| **intermediate** | Balance zwischen Detail und Geschwindigkeit (Default) |
| **expert** | Direkt, technisch, keine Wiederholungen, nur Essenz |

---

## 2. Betroffene Komponenten

### 2.1 Framework-Dokumente → Englisch

Diese Dateien müssen auf Englisch übersetzt werden:

| Datei | Status |
|-------|--------|
| `templates/stan.md.template` | Übersetzen |
| `templates/prd.md.template` | Übersetzen |
| `templates/plan.md.template` | Übersetzen |
| `criteria/**/*.yaml` | Übersetzen (name, description, questions) |
| `techniques/**/*.yaml` | Übersetzen |
| `techniques/purposes/**/*.yaml` | Übersetzen |
| `.claude/commands/stan/*.md` | Englisch (Skills bleiben Englisch) |

### 2.2 Hooks anpassen

**stan_context.py (UserPromptSubmit):**
```python
def inject_language_context():
    config = load_config()

    messages = []

    # Language reminder
    messages.append(f"[STAN] Communication: {config.language.communication}")
    messages.append(f"[STAN] Documents: {config.language.documents}")

    # User greeting style
    if config.user.name:
        messages.append(f"[STAN] Address user as: {config.user.name}")

    # Skill level adaptation
    if config.user.skill_level == "beginner":
        messages.append("[STAN] Explain thoroughly, use analogies")
    elif config.user.skill_level == "expert":
        messages.append("[STAN] Be direct and technical, skip basics")

    return "\n".join(messages)
```

### 2.3 Neue Library: config.py

```python
# .claude/hooks/stan/lib/config.py

from pathlib import Path
import yaml
from dataclasses import dataclass
from typing import Optional

CONFIG_FILE = Path(".stan/config.yaml")

@dataclass
class UserConfig:
    name: str = ""
    skill_level: str = "intermediate"  # beginner | intermediate | expert

@dataclass
class LanguageConfig:
    communication: str = "en"
    documents: str = "en"

@dataclass
class ProjectConfig:
    name: str = ""
    output_folder: str = ".stan"

@dataclass
class StanConfig:
    user: UserConfig
    language: LanguageConfig
    project: ProjectConfig

def load_config() -> Optional[StanConfig]:
    """Load config from .stan/config.yaml"""
    if not CONFIG_FILE.exists():
        return None
    # ... implementation

def save_config(config: StanConfig) -> None:
    """Save config to .stan/config.yaml"""
    # ... implementation

def ensure_config() -> StanConfig:
    """Load config or return defaults"""
    config = load_config()
    if config is None:
        return StanConfig(
            user=UserConfig(),
            language=LanguageConfig(),
            project=ProjectConfig()
        )
    return config
```

### 2.4 /stan init erweitern

Der Init-Skill muss nach User-Präferenzen fragen:

```markdown
## Initialization Flow

1. **Project Name**
   > What's your project name?

2. **User Preferences**
   > How should I address you?
   > Your experience level? (beginner / intermediate / expert)

3. **Language Settings**
   > Communication language? (de / en / fr / ...)
   > Document language? (de / en / fr / ...)

4. **Create Config**
   → Write .stan/config.yaml
   → Create stan.md manifest
```

---

## 3. Implementation Tasks

### Phase A: Foundation

| Task | Beschreibung | Dateien |
|------|--------------|---------|
| A-001 | Config Library erstellen | `.claude/hooks/stan/lib/config.py` |
| A-002 | Config Schema validieren | `tests/test_config.py` |

### Phase B: Framework auf Englisch

| Task | Beschreibung | Dateien |
|------|--------------|---------|
| B-001 | Templates übersetzen | `templates/*.template` |
| B-002 | Criteria übersetzen | `criteria/**/*.yaml` |
| B-003 | Techniques übersetzen | `techniques/**/*.yaml` |
| B-004 | Purposes übersetzen | `techniques/purposes/*.yaml` |

### Phase C: Hook Integration

| Task | Beschreibung | Dateien |
|------|--------------|---------|
| C-001 | stan_context für Language-Injection | `stan_context.py` |
| C-002 | Skill-Level Adaptation | `stan_context.py` |

### Phase D: Skill Updates

| Task | Beschreibung | Dateien |
|------|--------------|---------|
| D-001 | /stan init für Config-Setup | `init.md` |
| D-002 | /stan statusupdate Config anzeigen | `statusupdate.md` |

### Phase E: Testing

| Task | Beschreibung | Dateien |
|------|--------------|---------|
| E-001 | Config Load/Save Tests | `tests/test_config.py` |
| E-002 | Language Injection Tests | `tests/test_stan_context.py` |
| E-003 | E2E Test mit Config | `tests/test_e2e_integration.py` |

---

## 4. Migration

Bestehende Projekte ohne `.stan/config.yaml`:

1. **stan_context** erkennt fehlende Config
2. Injiziert Hinweis: "No config found. Run /stan init for personalization."
3. Framework funktioniert weiter mit Defaults (Englisch, keine Anrede)

---

## 5. Entscheidungen

| Entscheidung | Begründung |
|--------------|------------|
| Kein "auto" für Sprache | Unzuverlässig, Claude fällt zurück |
| YAML statt JSON für Config | Lesbar, kommentierbar, BMAD-konsistent |
| Skill-Level von BMAD übernommen | Sinnvolle Abstufung für Erklärungstiefe |
| Framework-Dateien Englisch | Internationale Nutzbarkeit, Konsistenz |
| User-Name optional | Nicht jeder will persönlich angesprochen werden |

---

## 6. Beispiel-Interaktion

**Mit Config:**
```yaml
user:
  name: "Mathias"
  skill_level: expert
language:
  communication: de
  documents: en
```

**Claude's Verhalten:**
```
Hallo Mathias, das PRD ist fertig.
[Direkt, ohne lange Erklärungen]

Generated: docs/prd.md (English)
```

**Ohne Config (Defaults):**
```
The PRD is ready.
[Standard English, no personalization]

Generated: docs/prd.md (English)
```
