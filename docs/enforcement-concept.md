# STAN Enforcement Konzept

**Ziel:** Claude zur Einhaltung von Criteria, Purposes und Techniques zwingen - nicht durch Regeln (die ignoriert werden), sondern durch BLOCKIEREN.

---

## Architektur-Übersicht

```
┌─────────────────────────────────────────────────────────────┐
│                        STAN Framework                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   TEMPLATES (Source of Truth für Minimum-Criteria)          │
│   ┌──────────────────────────────────────────────────┐      │
│   │ templates/prd.md.template                        │      │
│   │   criteria:                                      │      │
│   │     - goal-is-smart        ← PFLICHT             │      │
│   │     - hypothesis-is-testable                     │      │
│   │     - text-quality                               │      │
│   └──────────────────────────────────────────────────┘      │
│                          ↓                                   │
│   DOKUMENTE (Erstellt aus Templates)                        │
│   ┌──────────────────────────────────────────────────┐      │
│   │ docs/prd.md                                      │      │
│   │   type: prd                                      │      │
│   │   criteria:                                      │      │
│   │     - goal-is-smart        ← Von Template        │      │
│   │     - hypothesis-is-testable                     │      │
│   │     - text-quality                               │      │
│   │     - custom-security      ← Hinzugefügt (OK)    │      │
│   │   techniques_applied:                            │      │
│   │     - mind-mapping         ← Verwendet           │      │
│   └──────────────────────────────────────────────────┘      │
│                          ↓                                   │
│   CRITERIA (Checks pro Criteria)                            │
│   ┌──────────────────────────────────────────────────┐      │
│   │ criteria/goal-is-smart.yaml                      │      │
│   │   checks:                                        │      │
│   │     - id: specific                               │      │
│   │       question: "Ist das Ziel spezifisch?"       │      │
│   │       required: true                             │      │
│   │     - id: measurable                             │      │
│   │       question: "Ist es messbar?"                │      │
│   │       required: true                             │      │
│   └──────────────────────────────────────────────────┘      │
│                          ↓                                   │
│   HOOKS (Enforcement)                                       │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│   │stan-context │  │ stan-track  │  │  stan-gate  │        │
│   │Injiziert    │  │ Trackt      │  │ BLOCKIERT   │        │
│   └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Criteria-System

### Template definiert Minimum

```yaml
# templates/prd.md.template
---
type: prd
criteria:
  - goal-is-smart
  - hypothesis-is-testable
  - evidence-exists
  - text-quality
---
```

Diese Criteria sind PFLICHT. Sie können nicht entfernt werden.

### Dokument kann erweitern

```yaml
# docs/prd.md
---
type: prd
criteria:
  - goal-is-smart           # Pflicht (vom Template)
  - hypothesis-is-testable  # Pflicht
  - evidence-exists         # Pflicht
  - text-quality            # Pflicht
  - security-considered     # Zusätzlich (erlaubt)
---
```

### Hook-Enforcement

```python
def check_criteria_integrity(doc_path):
    doc = parse_frontmatter(doc_path)
    doc_type = doc.get("type")
    doc_criteria = set(doc.get("criteria", []))

    # Template = Minimum
    template = parse_frontmatter(f"templates/{doc_type}.md.template")
    template_criteria = set(template.get("criteria", []))

    # Entfernt? → BLOCKIERT
    removed = template_criteria - doc_criteria
    if removed:
        return deny(f"Criteria entfernt: {removed}")

    return allow()
```

### Todos werden GENERIERT

Keine manuelle Todo-Liste. Bei jeder Prüfung:

1. Lese `criteria:` aus Dokument-Frontmatter
2. Für jedes Criteria: Lade `criteria/{name}.yaml`
3. Für jeden `required: true` Check: Generiere Todo
4. Prüfe ob erfüllt

```python
def get_pending_checks(doc_path):
    doc = parse_frontmatter(doc_path)
    criteria_names = doc.get("criteria", [])

    pending = []
    for name in criteria_names:
        criteria = load_yaml(f"criteria/{name}.yaml")
        for check in criteria["checks"]:
            if check["required"]:
                if not is_check_fulfilled(doc_path, check):
                    pending.append({
                        "criteria": name,
                        "check": check["id"],
                        "question": check["question"]
                    })

    return pending
```

---

## 2. Techniques-System

### Techniques bleiben PLAIN

```yaml
# techniques/five-whys.yaml
id: five-whys
name: "Five Whys"
description: |
  Repeated "why" questioning to find root cause.

steps:
  - Ask "Why?" to the problem
  - Ask "Why?" to that answer
  - Repeat 5 times or until root cause found
```

**Keine Checks in Techniques. Keine Pattern. Kein Overhead.**

### Purposes gruppieren Techniques

```yaml
# techniques/purposes/root-cause-analysis.yaml
id: root-cause-analysis
name: "Root Cause Analysis"
question: "Why did this happen?"

techniques:
  - five-whys
  - fishbone-diagram
  - after-action-review

recommended_start: five-whys
```

### Anwendung im Dokument

Techniques werden im Kopf angewendet, Essenz ins Dokument geschrieben.

**Im Frontmatter tracken:**
```yaml
---
techniques_applied:
  - mind-mapping
  - five-whys
---
```

**Im Fließtext erwähnen (erlaubt):**
```markdown
Die Five Whys haben ergeben, dass das Kernproblem bei X liegt.
```

**NICHT erlaubt:** Aufgeblähte `[TECHNIQUE: ...]` Blöcke.

---

## 3. Purpose-Enforcement pro Phase

### Jede Phase hat Pflicht-Purposes

| Phase | Pflicht-Purposes | Frage |
|-------|------------------|-------|
| DEFINE | big-picture, ideation | Was bauen wir und warum? |
| PLAN | structured-problem-solving, decision-making | Wie teilen wir das auf? |
| CREATE | code-review, root-cause-analysis (bei Fehler) | Ist der Code gut? Warum geht das nicht? |

### Hook-Enforcement

```python
def check_purposes_covered(doc_path, required_purposes):
    doc = parse_frontmatter(doc_path)
    techniques_applied = doc.get("techniques_applied", [])

    # Welche Purposes sind durch die Techniques abgedeckt?
    covered_purposes = set()
    for technique in techniques_applied:
        purposes = get_purposes_for_technique(technique)
        covered_purposes.update(purposes)

    # Mindestens einer der required Purposes abgedeckt?
    if not any(p in covered_purposes for p in required_purposes):
        return deny(f"""
Pflicht-Purposes: {required_purposes}
Abgedeckt: {covered_purposes}
Wende eine Technique aus einem Pflicht-Purpose an.
""")

    return allow()
```

---

## 4. Session State

### Struktur

```json
{
  "claude_session_id": "abc123",
  "phase": "define",
  "current_document": "docs/prd.md",

  "required_purposes": ["big-picture", "ideation"],

  "error_count": 0,
  "technique_required": false,

  "test_results": []
}
```

### Verwendung

- **stan-context:** Liest State, injiziert Kontext
- **stan-track:** Updated State (Fehler, Tests)
- **stan-gate:** Liest State, BLOCKIERT bei Verstoß

---

## 5. Die Gates (Wann wird BLOCKIERT?)

### Gate 1: Phase-Start

```
/stan define
    ↓
[STAN] Phase DEFINE gestartet.
Pflicht-Purposes: big-picture, ideation
Du MUSST mindestens eine Technique daraus anwenden.
```

### Gate 2: Dokument-Save

```
Edit docs/prd.md
    ↓
Hook prüft:
- Criteria entfernt? → BLOCKIERT
- Technique aus Pflicht-Purpose? → BLOCKIERT wenn keine
```

### Gate 3: Phase-Übergang

```
/stan plan (DEFINE → PLAN)
    ↓
Hook prüft:
- Alle required Criteria-Checks erfüllt? → BLOCKIERT wenn nicht
- Mindestens ein Pflicht-Purpose abgedeckt? → BLOCKIERT wenn nicht
```

### Gate 4: Commit

```
git commit
    ↓
Hook prüft:
- Tests grün?
- Pending Learnings gespeichert?
- Bei 3-Strikes: Recovery-Technique angewendet?
```

### Gate 5: 3-Strikes (Zusätzlich)

```
3x gleicher Fehler
    ↓
state["technique_required"] = true
    ↓
Commit → BLOCKIERT bis Technique im Frontmatter
```

---

## 6. Zusammenfassung

| Was | Wo definiert | Wie enforced |
|-----|--------------|--------------|
| **Minimum-Criteria** | Template-Frontmatter | Hook vergleicht mit Dokument |
| **Zusätzliche Criteria** | Dokument-Frontmatter | Hook prüft alle |
| **Criteria-Checks** | criteria/*.yaml | Generiert zu Todos, geprüft bei Gate |
| **Pflicht-Purposes** | Phase-Definition (Hook) | Hook prüft techniques_applied |
| **Techniques angewendet** | Dokument-Frontmatter | Hook liest Liste |
| **3-Strikes Recovery** | Session State | Hook blockiert Commit |

---

## 7. Änderungs-Handling

### Template geändert

```python
def check_document_against_template(doc_path):
    doc = parse_frontmatter(doc_path)
    doc_type = doc.get("type")
    doc_criteria = set(doc.get("criteria", []))
    status = doc.get("status", "")

    # Archivierte Dokumente ignorieren
    if status == "archived":
        return allow()

    # Template JETZT lesen (immer aktuell)
    template = parse_frontmatter(f"templates/{doc_type}.md.template")
    template_criteria = set(template.get("criteria", []))

    # Vergleich: Dokument >= Template?
    missing = template_criteria - doc_criteria
    if missing:
        return deny(f"Criteria fehlt (Template geändert?): {missing}")

    return allow()
```

**Kein Sync-Mechanismus.** Hook liest Template bei JEDER Prüfung neu.

### Criteria YAML geändert

Checks werden bei jeder Prüfung aus YAML geladen:

```python
def check_all_criteria(doc_path):
    doc = parse_frontmatter(doc_path)

    if doc.get("status") == "archived":
        return allow()

    for criteria_name in doc.get("criteria", []):
        # YAML JETZT lesen (immer aktuell)
        criteria = load_yaml(f"criteria/{criteria_name}.yaml")

        for check in criteria["checks"]:
            if check["required"]:
                if not verify_check(doc_path, check):
                    return deny(f"Check '{check['id']}' nicht erfüllt")

    return allow()
```

**Keine gecachten Checks.** YAML wird bei jeder Prüfung neu geladen.

### Bestehende Dokumente nachziehen

Wenn Template/Criteria geändert:

1. Nächstes Gate für das Dokument → Hook prüft
2. BLOCKIERT wenn nicht mehr konform
3. Ich muss Dokument anpassen
4. Dann weiter

**Kein automatisches Update.** Ich muss bewusst nachziehen.

### Archivierte Dokumente ignorieren

```yaml
# docs/old-prd.md
---
status: archived  # ← Wird von Hooks ignoriert
---
```

```python
def should_enforce(doc_path):
    fm = parse_frontmatter(doc_path)
    return fm.get("status") != "archived"
```

---

## 8. Was Hooks KÖNNEN und NICHT KÖNNEN

### Können

- Schritte erzwingen (du MUSST X aufrufen)
- Output erzwingen (du MUSST Y im Frontmatter haben)
- Reihenfolge erzwingen (erst Criteria erfüllt, dann Phase-Wechsel)
- Manipulation verhindern (Template-Criteria können nicht entfernt werden)

### Nicht können

- Prüfen ob ich WIRKLICH nachgedacht habe
- Qualität des Denkens messen
- Garantieren dass ich nicht schummle

### Mitigation

- Viele Gates = viel Friction für schlechtes Verhalten
- Audit-Trail = Transparenz was gemacht wurde
- Template als Minimum = keine Manipulation möglich
