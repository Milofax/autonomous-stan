# Everything Claude Code - Kritische Analyse für STAN

> **Analysiert:** 2026-01-24
> **Methode:** Five Whys + Six Perspectives für jedes Feature
> **Quelle:** vendor/everything-claude-code

---

## Vorwort: Was diese Analyse NICHT ist

Diese Analyse ist **keine Feature-Liste zum Kopieren**. Sie ist eine kritische Reflexion:

- Was löst welches KONKRETE Problem?
- Braucht STAN das wirklich?
- Was haben wir BEREITS?
- Was ist die ALTERNATIVE?

---

## Feature 1: SessionEnd Hook

### Was es tut
Speichert Session-Kontext in `~/.claude/sessions/{date}.md` wenn Claude beendet wird.

### Five Whys

| # | Warum? | Antwort |
|---|--------|---------|
| 1 | Warum SessionEnd? | Um Learnings zwischen Sessions zu persistieren |
| 2 | Warum persistieren? | Damit nächste Session davon profitiert |
| 3 | Warum profitiert sie nicht schon? | Weil... **MOMENT** |
| 4 | **STOP** | STAN hat Graphiti! |

### Was STAN bereits hat

```
Graphiti MCP:
- add_memory() → Speichert sofort
- search_nodes() → Abruf bei Session-Start
- !!save_immediately Regel → Learnings werden SOFORT gespeichert
- UserPromptSubmit Hook → Lädt Graphiti-Kontext automatisch
```

### Warum everything-claude-code SessionEnd braucht

**Sie haben KEIN Graphiti.** Ihr einziger Persistenz-Mechanismus sind lokale Dateien.

### Braucht STAN das?

**NEIN.** Graphiti löst das Problem bereits besser:
- Semantische Suche statt Datei-Suche
- Strukturierte Entities statt Freitext
- Projekt-übergreifend nutzbar

### Fazit

| Aspekt | Bewertung |
|--------|-----------|
| Problem existiert? | Ja, aber bereits gelöst |
| STAN-Lösung | Graphiti |
| Implementieren? | **NEIN** |

---

## Feature 2: Strategic Compact (Tool-Call-Counter)

### Was es tut
Zählt Tool-Calls pro Session. Bei 50 Calls: "Erwäge /compact". Danach alle 25 Calls erneut.

### Five Whys

| # | Warum? | Antwort |
|---|--------|---------|
| 1 | Warum Counter? | Um zu wissen wann /compact sinnvoll ist |
| 2 | Warum /compact? | Um Context-Overflow zu vermeiden |
| 3 | Warum Overflow vermeiden? | Weil sonst Auto-Compact passiert |
| 4 | Warum ist Auto-Compact schlecht? | Weil... ist es das? |
| 5 | **STOP** | Was ist der ECHTE Unterschied? |

### Die echte Frage

**Manuelles Compact vs. Automatisches Compact - was ist besser?**

| Aspekt | Manuell (/compact) | Automatisch |
|--------|-------------------|-------------|
| Kontrolle | User entscheidet WAS zusammengefasst wird | Claude entscheidet |
| Timing | User wählt den Moment | Passiert bei Overflow |
| Risiko | User vergisst es | Passiert garantiert |
| Qualität | Theoretisch besser | Praktisch ausreichend |

### Eigene Erfahrung (diese Session)

- ~100+ Tool-Calls in dieser Session
- Kein manuelles /compact nötig gewesen
- Auto-Compact hat funktioniert

### Wann wäre Strategic Compact WIRKLICH nützlich?

1. **Phasenwechsel:** DEFINE → PLAN → CREATE
2. **Themenwechsel:** Neues Feature beginnen
3. **Vor komplexer Aufgabe:** Fokus schaffen

**Aber:** Das erfordert INTELLIGENZ, nicht Tool-Call-Zählung.

Ein Counter sagt: "50 Calls erreicht"
Was wir bräuchten: "Du wechselst gerade die Phase, /compact könnte helfen"

### Braucht STAN das?

**NEIN in dieser Form.** Ein dummer Counter ist Noise.

**VIELLEICHT:** Intelligente Compact-Vorschläge basierend auf:
- Phase-Wechsel (DEFINE → PLAN)
- Task-Abschluss
- Themen-Wechsel

Aber das ist ein ANDERES Feature.

### Fazit

| Aspekt | Bewertung |
|--------|-----------|
| Problem existiert? | Marginal |
| Lösung sinnvoll? | Nein, zu simpel |
| Implementieren? | **NEIN** |
| Alternative? | Intelligente Phase-basierte Vorschläge |

---

## Feature 3: Agent-Definitionen (9 Agents)

### Was es tut
9 spezialisierte Agent-Definitionen mit YAML-Frontmatter:
- planner, architect, tdd-guide, code-reviewer
- security-reviewer, build-error-resolver, e2e-runner
- refactor-cleaner, doc-updater

### Five Whys

| # | Warum? | Antwort |
|---|--------|---------|
| 1 | Warum Agent-Definitionen? | Um spezialisierte Tasks zu delegieren |
| 2 | Warum delegieren? | Fokussierter Kontext = bessere Ergebnisse |
| 3 | Warum bessere Ergebnisse? | Spezifische Anweisungen statt generisch |
| 4 | Warum haben wir das nicht? | STAN nutzt eingebaute Agents |
| 5 | Warum reichen die nicht? | **Reichen sie?** |

### Was STAN bereits hat

```
Eingebaute Claude Code Agents:
- Explore Agent: Codebase durchsuchen
- Plan Agent: Implementierung planen
- Bash Agent: Commands ausführen
- general-purpose: Alles andere

STAN-spezifisch:
- Phase-System (DEFINE/PLAN/CREATE)
- Criteria-System für Qualitätsprüfung
- Techniques für Problemlösung
```

### Gap-Analyse: Was fehlt wirklich?

| Agent | Brauchen wir das? | Warum? |
|-------|-------------------|--------|
| planner | **NEIN** | Plan Agent existiert |
| architect | **JA** | Architektur-Entscheidungen dokumentieren (ADRs) |
| tdd-guide | **VIELLEICHT** | STAN hat Criteria-System für Tests |
| code-reviewer | **JA** | Systematische Review vor Commit fehlt |
| security-reviewer | **JA** | Sicherheits-Check fehlt in STAN |
| build-error-resolver | **NEIN** | Das mache ich sowieso |
| e2e-runner | **NEIN** | Playwright MCP existiert |
| refactor-cleaner | **VIELLEICHT** | Dead-Code-Cleanup ist selten nötig |
| doc-updater | **NEIN** | Docs sind Teil des normalen Workflows |

### Würde ich diese Agents NUTZEN?

**Ehrliche Antwort:** Nur wenn sie in den Workflow integriert sind.

Beispiel:
```
/stan create (vor Commit):
→ Ruft automatisch code-reviewer Agent
→ Ruft automatisch security-reviewer Agent
→ Blockiert bei Problemen
```

Ohne Integration: Ich vergesse sie zu nutzen.

### Braucht STAN das?

**TEILWEISE.** Drei Agents haben echten Wert:

1. **architect.md** - ADRs für Architektur-Entscheidungen
2. **code-reviewer.md** - Systematische Review
3. **security-reviewer.md** - Sicherheits-Check

**Aber:** Nur sinnvoll wenn in `/stan create` integriert.

### Fazit

| Aspekt | Bewertung |
|--------|-----------|
| Problem existiert? | Ja, systematische Reviews fehlen |
| Lösung sinnvoll? | Ja, aber nur 3 von 9 Agents |
| Implementieren? | **JA, aber integriert** |
| Welche? | architect, code-reviewer, security-reviewer |

---

## Feature 4: Continuous Learning System

### Was es tut
Am Session-Ende: Transcript analysieren → Patterns extrahieren → In Skills speichern.

### Five Whys

| # | Warum? | Antwort |
|---|--------|---------|
| 1 | Warum Continuous Learning? | Patterns automatisch extrahieren |
| 2 | Warum automatisch? | Manuelles Speichern wird vergessen |
| 3 | Warum vergessen? | Fokus auf Aufgabe |
| 4 | Warum ist das ein Problem? | Wissen geht verloren |
| 5 | **STOP** | Haben wir nicht !!save_immediately? |

### Was STAN bereits hat

```
Graphiti + STAN.FLUX Regeln:
- !!save_immediately: Bei neuem Learning → SOFORT add_memory()
- PostToolUse Hook: Bei 3-Strikes → Graphiti durchsuchen
- graphiti.md Rule: Detaillierte Anweisungen wann/was speichern
```

### Der Unterschied

| Aspekt | STAN (manuell) | Continuous Learning (automatisch) |
|--------|---------------|-----------------------------------|
| Trigger | Ich erkenne Learning | Session-Ende |
| Qualität | Ich entscheide was wertvoll ist | Algorithmus entscheidet |
| Vollständigkeit | Kann vergessen werden | Nichts wird vergessen |
| Noise | Wenig | Potenziell viel |

### Die echte Frage

**Ist automatische Extraktion BESSER als manuelle?**

Pro Automatisch:
- Nichts wird vergessen
- Konsistent

Contra Automatisch:
- Was ist ein "Learning"? Wie erkennt man das?
- Qualitätsproblem: Triviales wird auch gespeichert
- Graphiti-Kontamination mit Low-Value Content

### Braucht STAN das?

**NEIN in dieser Form.**

Die !!save_immediately Regel ist BESSER:
- Ich erkenne aktiv was wertvoll ist
- Qualitätskontrolle durch Bewusstsein
- Keine Kontamination

**Was wir STATTDESSEN verbessern könnten:**
- Reminder am Session-Ende: "Gab es Learnings die du speichern solltest?"
- Aber: Kein automatisches Extrahieren

### Fazit

| Aspekt | Bewertung |
|--------|-----------|
| Problem existiert? | Marginal (!!save_immediately hilft) |
| Lösung sinnvoll? | Nein, Qualitätsproblem |
| Implementieren? | **NEIN** |
| Alternative? | Session-Ende Reminder |

---

## Feature 5: Verification Loop (6-Phase)

### Was es tut
Vor jedem Commit: Build → Types → Lint → Tests → Security → Diff

### Five Whys

| # | Warum? | Antwort |
|---|--------|---------|
| 1 | Warum Verification Loop? | Qualität vor Commit sichern |
| 2 | Warum vor Commit? | Fehlerhafte Commits kosten Zeit |
| 3 | Warum kosten sie Zeit? | Revert, Fix, erneuter Commit |
| 4 | Warum passiert das? | Tests/Lint laufen nicht konsistent |
| 5 | Warum nicht konsistent? | Kein systematischer Check |

### Was STAN bereits hat

```
stan_track.py:
- Trackt Test-Ergebnisse
- 3-Strikes Rule bei wiederholten Fehlern
- Erkennt ROT → GRÜN Transition

stan_gate.py:
- Blockiert Commit wenn pending_learnings
- Quality Gates (nur in CREATE Phase)
```

### Gap-Analyse

| Check | STAN macht das? | Automatisch? |
|-------|----------------|--------------|
| Build (compile) | Nein | - |
| Types (mypy/pyright) | Nein | - |
| Lint (ruff) | Nein | - |
| Tests (pytest) | **Ja** (stan_track) | Tracking, nicht Enforcement |
| Security (bandit) | Nein | - |
| Git diff | Nein | - |

**Problem:** STAN trackt Tests, aber ENFORCED nicht alle Checks.

### Die echte Frage

**Würde ein Verification Loop STAN verbessern?**

Szenario OHNE Loop:
1. Ich schreibe Code
2. Ich committe
3. CI schlägt fehl (ruff-Fehler)
4. Ich fixe
5. Ich committe erneut

Szenario MIT Loop:
1. Ich schreibe Code
2. `/stan verify` läuft automatisch vor Commit
3. ruff-Fehler wird erkannt
4. Ich fixe
5. Ich committe (erfolgreich)

**Ersparnis:** Ein Commit-Zyklus.

### Braucht STAN das?

**JA.** Das ist echte Qualitätsverbesserung.

**Konkret für Python-Projekte:**
```
/stan verify:
1. python -m py_compile *.py  → Syntax-Check
2. ruff check .               → Lint
3. pytest                     → Tests
4. bandit -r .               → Security (optional)
5. git diff --check          → Whitespace
```

### Integration in STAN

**Option A:** Neuer Command `/stan verify`
- Manuell aufrufen vor Commit

**Option B:** In stan_gate.py integrieren
- Automatisch vor jedem `git commit`

**Empfehlung:** Option B - Automatisch ist besser.

### Fazit

| Aspekt | Bewertung |
|--------|-----------|
| Problem existiert? | Ja, keine systematische Prüfung |
| Lösung sinnvoll? | Ja |
| Implementieren? | **JA** |
| Wie? | In stan_gate.py vor Commit |

---

## Feature 6: Context-Injection Modes

### Was es tut
3 vordefinierte Kontexte: dev.md, review.md, research.md
Jeder Kontext priorisiert andere Tools und Verhaltensweisen.

### Five Whys

| # | Warum? | Antwort |
|---|--------|---------|
| 1 | Warum Context-Modes? | Verhalten je nach Phase anpassen |
| 2 | Warum anpassen? | DEFINE ist anders als CREATE |
| 3 | Warum brauchen wir Modes? | Um Tools zu priorisieren |
| 4 | Warum priorisieren? | **STOP** |
| 5 | **Hat STAN nicht schon Phasen?** | JA! |

### Was STAN bereits hat

```
Phase-System:
- DEFINE: Interview, PRD erstellen
- PLAN: Tasks ableiten
- CREATE: Implementieren

stan-context Hook:
- Injiziert [STAN] Phase: {phase} | Task: {task}

Rules pro Phase:
- Unterschiedliches Verhalten je Phase
```

### Vergleich

| Aspekt | everything-claude-code | STAN |
|--------|------------------------|------|
| Modi | dev/review/research | DEFINE/PLAN/CREATE |
| Injection | Via Context-Files | Via Hook |
| Tool-Priorisierung | Explizit | Implizit in Rules |

### Braucht STAN das?

**NEIN.** STAN hat bereits ein äquivalentes System.

Die Phase-basierte Injektion ist SPEZIFISCHER als generische Modi:
- DEFINE = Interview + PRD (nicht nur "research")
- PLAN = Tasks + Dependencies (nicht nur "planning")
- CREATE = Implementierung + Tests (nicht nur "dev")

### Fazit

| Aspekt | Bewertung |
|--------|-----------|
| Problem existiert? | Nein, Phase-System existiert |
| Lösung sinnvoll? | Redundant |
| Implementieren? | **NEIN** |

---

## Feature 7: PreCompact Hook

### Was es tut
Sichert State bevor Claude automatisch kompaktiert.

### Five Whys

| # | Warum? | Antwort |
|---|--------|---------|
| 1 | Warum PreCompact? | State vor Kompaktierung sichern |
| 2 | Warum sichern? | Wichtige Info geht sonst verloren |
| 3 | Warum verloren? | Kompaktierung fasst zusammen |
| 4 | Was genau geht verloren? | **Gute Frage** |
| 5 | **STOP** | Was würden wir speichern? |

### Was würde PreCompact konkret tun?

```python
def on_pre_compact():
    # Was speichern?
    # 1. Task-Status → Aber das ist in docs/tasks.md!
    # 2. Learnings → Aber das ist in Graphiti!
    # 3. Session-State → Aber das ist in session_state.py!
    pass  # Was bleibt übrig?
```

### Braucht STAN das?

**NEIN.** STAN persistiert bereits alles Wichtige:
- Tasks → docs/tasks.md (Git-tracked)
- Learnings → Graphiti (persistent)
- State → session_state.py (Session-local)

### Fazit

| Aspekt | Bewertung |
|--------|-----------|
| Problem existiert? | Nein, bereits gelöst |
| Lösung sinnvoll? | Redundant |
| Implementieren? | **NEIN** |

---

## Feature 8: Stop Hook

### Was es tut
Prüft ob alle Tasks erledigt sind bevor Claude aufhört.

### Five Whys

| # | Warum? | Antwort |
|---|--------|---------|
| 1 | Warum Stop Hook? | Finale Prüfung vor Session-Ende |
| 2 | Warum finale Prüfung? | Sicherstellen dass alles erledigt ist |
| 3 | Warum könnte was fehlen? | Ich höre zu früh auf |
| 4 | Warum zu früh? | Keine Prüfung |
| 5 | Wie oft passiert das? | **Selten** |

### Ehrliche Reflexion

**Wann höre ich zu früh auf?**
- Wenn ich denke, ich bin fertig
- User kann "weiter" sagen
- Kein großes Problem

**Was würde Stop Hook prüfen?**
```python
def on_stop():
    # 1. Alle Tasks done? → docs/tasks.md prüfen
    # 2. Tests grün? → stan_track.py weiß das
    # 3. Uncommitted changes? → git status

    # Aber: Wenn ich stoppe, ist das oft BEWUSST
    # User will Pause machen
```

### Braucht STAN das?

**MARGINAL.** Der Nutzen ist gering:
- User kann einfach "weiter" sagen
- Blockieren wäre nervig wenn User Pause will
- Die Prüfungen passieren eh im Workflow

### Fazit

| Aspekt | Bewertung |
|--------|-----------|
| Problem existiert? | Minimal |
| Lösung sinnvoll? | Marginal |
| Implementieren? | **NEIN** (Low ROI) |

---

## Feature 9: Package Manager Detection

### Was es tut
6-Level Detection Chain: ENV → Project Config → package.json → Lock File → Global Config → Fallback

### Braucht STAN das?

**NEIN.** STAN ist Python-basiert, nicht Node.js.

Für Python-Projekte ist Package-Management einfacher:
- pip/uv/poetry wird durch Lock-Files erkannt
- Kein komplexes Detection nötig

### Fazit

| Implementieren? | **NEIN** |

---

## Zusammenfassung: Was STAN wirklich braucht

### JA - Implementieren

| Feature | Warum | Wie |
|---------|-------|-----|
| **Verification Loop** | Keine systematische Prüfung vor Commit | In stan_gate.py integrieren |
| **3 Agent-Definitionen** | Systematische Reviews fehlen | architect, code-reviewer, security-reviewer |

### NEIN - Nicht implementieren

| Feature | Warum nicht |
|---------|-------------|
| SessionEnd Hook | Graphiti löst das besser |
| Strategic Compact | Tool-Counter ist zu simpel |
| Continuous Learning | Qualitätsproblem, !!save_immediately ist besser |
| Context-Injection | Phase-System existiert bereits |
| PreCompact Hook | docs/tasks.md + Graphiti reichen |
| Stop Hook | Marginaler Nutzen |
| Package Manager | Python braucht das nicht |

### VIELLEICHT - Später evaluieren

| Feature | Bedingung |
|---------|-----------|
| Intelligente Compact-Vorschläge | Wenn Phase-basiert statt Counter-basiert |
| Session-Ende Reminder | "Gab es Learnings?" ohne Auto-Extraktion |

---

## Entscheidungs-Matrix

| Feature | Problem real? | Lösung existiert? | Lösung besser? | Implementieren? |
|---------|--------------|-------------------|----------------|-----------------|
| SessionEnd | Ja | Ja (Graphiti) | Nein | **NEIN** |
| Tool-Counter | Marginal | - | - | **NEIN** |
| Agents | Ja | Teilweise | Ja (3 von 9) | **JA** |
| Cont. Learning | Marginal | Ja (!!save_immediately) | Nein | **NEIN** |
| Verification | Ja | Nein | - | **JA** |
| Context-Modes | Nein | Ja (Phasen) | Nein | **NEIN** |
| PreCompact | Nein | Ja (docs/tasks.md) | Nein | **NEIN** |
| Stop Hook | Marginal | - | - | **NEIN** |

---

## Konkrete nächste Schritte

### 1. Verification Loop in stan_gate.py

```python
# Vor git commit:
def verify_before_commit():
    checks = [
        ("Syntax", "python -m py_compile {files}"),
        ("Lint", "ruff check ."),
        ("Tests", "pytest"),
    ]
    for name, cmd in checks:
        if not run(cmd).success:
            return deny(f"[STAN] {name} fehlgeschlagen")
    return allow()
```

### 2. Drei Agent-Definitionen

```
.claude/agents/stan/
├── architect.md      # ADRs, System-Design
├── code-reviewer.md  # Quality Review vor Commit
└── security-reviewer.md  # OWASP Checks
```

**Integration:** Automatisch aufrufen in `/stan create` vor Commit.

---

## Learnings aus dieser Analyse

1. **Feature-Listen sind gefährlich** - Ich habe oberflächlich kopiert statt analysiert
2. **"Warum" ist wichtiger als "Was"** - Five Whys hätte mich früher gestoppt
3. **Bestehende Lösungen prüfen** - Graphiti macht SessionEnd obsolet
4. **Kontext ist König** - everything-claude-code hat KEIN Graphiti, STAN hat es
5. **Weniger ist mehr** - 2 Features implementieren statt 12 oberflächlich listen
