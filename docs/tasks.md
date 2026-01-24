# STAN Framework - Tasks

Abgeleitet aus [plan.md](plan.md). Format: Task-ID, Beschreibung, Dependencies, Acceptance Criteria.

---

## Status Legend

| Symbol | Status | Meaning |
|--------|--------|---------|
| `·` | pending | **REQUIRED** - must be implemented |
| `►` | in_progress | Currently being worked on |
| `✓` | done | Completed |
| `~` | parked | Deliberately deferred (optional) |
| `§` | completed | Deliberately not implementing (archived) |

**IMPORTANT:** Only `~` (parked) and `§` (completed/archived) are optional. All other tasks are required.

---

## Phase 1: Foundation ✓

### T-001: Templates erstellen ✓

**Beschreibung:** Basis-Templates für stan.md, prd.md, plan.md erstellen.

**Dependencies:** Keine

**Dateien:**
- `templates/stan.md.template`
- `templates/prd.md.template` (erweitert mit BMAD+PRP Best Practices)
- `templates/plan.md.template`

**PRD Template enthält (aus BMAD+PRP):**
- Key Hypothesis ("Wir glauben... wenn wir... weil...")
- Jobs to Be Done (JTBD)
- Evidenz-Sektion
- Success Metrics mit Baseline + Ziel
- MoSCoW Priorisierung
- Implementation Phases
- Feasibility Rating
- Decisions Log
- Traceability (Stories → Metrics)

**Acceptance Criteria:**
- [x] Templates haben Frontmatter mit `type:` und `criteria:` Liste
- [x] Templates enthalten beschreibende Abschnitte (keine Prompts)
- [x] Markdown-Format, gut lesbar
- [x] PRD Template integriert Best Practices aus BMAD + PRP

---

### T-002: Criteria Pack Struktur ✓

**Beschreibung:** Verzeichnisstruktur für Criteria anlegen + erste Packs.

**Dependencies:** Keine

**Dateien (Basis):**
- `criteria/code/tests.yaml`
- `criteria/code/typecheck.yaml`
- `criteria/code/lint.yaml`
- `criteria/text/spelling.yaml`
- `criteria/strategy/goal-quality.yaml`

**Dateien (PRD Best Practices - erweitert):**
- `criteria/strategy/hypothesis-quality.yaml` ✓
- `criteria/strategy/evidence-quality.yaml` ✓
- `criteria/strategy/success-metrics-quality.yaml` ✓
- `criteria/strategy/scope-quality.yaml` ✓
- `criteria/strategy/traceability-quality.yaml` ✓
- `criteria/strategy/requirements-quality.yaml` ✓
- `criteria/text/information-density.yaml` ✓
- `criteria/strategy/business-value-quality.yaml` (erweitert) ✓

**Acceptance Criteria:**
- [x] YAML-Format: name, description, checks[]
- [x] Jeder Check hat: id, question, required (bool)
- [x] Auto-Checks haben `command` Feld
- [x] PRD-Criteria decken BMAD+PRP Best Practices ab

---

### T-003: Lokales Learnings-System ✓

**Beschreibung:** Tiered Storage für Learnings in `~/.stan/learnings/`.

**Dependencies:** Keine

**Dateien:**
- `.claude/hooks/stan/lib/learnings.py`

**Acceptance Criteria:**
- [x] `~/.stan/learnings/recent.json` - Rolling ~50, FIFO
- [x] `~/.stan/learnings/hot.json` - Oft genutzte
- [x] `~/.stan/learnings/archive.json` - Permanent
- [x] Funktionen: save_learning(), load_learnings(), promote_to_hot()

---

## Phase 2: Core Hooks ✓

### T-004: stan-context Hook (UserPromptSubmit) ✓

**Beschreibung:** Kontext in jede Nachricht injizieren.

**Dependencies:** T-001, T-003

**Dateien:**
- `.claude/hooks/stan/user-prompt-submit/stan_context.py`

**Acceptance Criteria:**
- [x] Liest stan.md Manifest (wenn vorhanden)
- [x] Lädt lokale Learnings (hot + recent)
- [x] Injiziert: Phase, Current Task, Learnings Count
- [x] Graceful Fallback wenn kein stan.md

---

### T-005: stan-track Hook (PostToolUse - Bash) ✓

**Beschreibung:** Test-Ergebnisse tracken, Learnings automatisch erkennen.

**Dependencies:** T-003

**Dateien:**
- `.claude/hooks/stan/post-tool-use/stan_track.py`

**Acceptance Criteria:**
- [x] Erkennt Test-Commands (npm test, pytest, etc.)
- [x] Speichert Exit-Code in Session State
- [x] Erkennt ROT→GRÜN Wechsel
- [x] Erstellt pending_learning bei Wechsel
- [x] Injiziert Reminder: "Learning erkannt! Vor Commit speichern."

---

### T-006: stan-gate Hook (PreToolUse) ✓

**Beschreibung:** Phase-Enforcement, Quality Gates, Learnings-Enforcement, Worktree-Enforcement.

**Dependencies:** T-003, T-005

**Dateien:**
- `.claude/hooks/stan/pre-tool-use/stan_gate.py`

**Acceptance Criteria:**
- [x] BLOCKIERT Commit wenn pending_learnings existieren
- [x] BLOCKIERT Feature-Arbeit auf main (Worktree-Enforcement)
- [x] BLOCKIERT nach 3-Strikes (gleiche Fehler)
- [x] WARNT wenn Tests rot vor Commit

---

## Phase 3: Skill ✓

### T-007: /stan Skill - Core Commands ✓

**Beschreibung:** Basis-Skill mit init, define, plan, create, statusupdate.

**Dependencies:** T-001, T-004, T-006

**Dateien:**
- `.claude/commands/stan/init.md`
- `.claude/commands/stan/define.md`
- `.claude/commands/stan/plan.md`
- `.claude/commands/stan/create.md`
- `.claude/commands/stan/statusupdate.md`

**Acceptance Criteria:**
- [x] `/stan init` - Erstellt stan.md, fragt nach Projekt-Info
- [x] `/stan define` - Startet/fortsetzt DEFINE Phase
- [x] `/stan plan` - Startet/fortsetzt PLAN Phase
- [x] `/stan create` - Startet CREATE Phase (autonom)
- [x] `/stan statusupdate` - Zeigt Status, erlaubt manuelle Änderung
- [x] Widerworte bei bedeutsamem Phase-Wechsel (in Commands beschrieben)

---

### T-008: /stan Skill - Builder Commands ✓

**Beschreibung:** Template und Criteria Builder.

**Dependencies:** T-001, T-002

**Dateien:**
- `.claude/commands/stan/build-template.md`
- `.claude/commands/stan/build-criteria.md`
- `.claude/commands/stan/healthcheck.md`

**Acceptance Criteria:**
- [x] `/stan build-template` - Interaktiv Template bauen + Criteria verknüpfen
- [x] `/stan build-criteria` - Interaktiv Criteria bauen + Templates identifizieren
- [x] `/stan healthcheck` - Konsistenz prüfen

---

## Phase 4: Testing & Validation

### T-009: Unit Tests ✓

**Beschreibung:** pytest Tests für alle Komponenten.

**Dependencies:** T-001 bis T-006

**Dateien:**
- `tests/test_criteria.py`
- `tests/test_hooks.py`
- `tests/test_learnings.py`
- `tests/test_session_state.py`

**Acceptance Criteria:**
- [x] 81 Tests grün
- [x] Criteria Schema Tests
- [x] Hook Behavior Tests
- [x] Worktree Enforcement Tests

---

### T-010: Interaktive Criteria-Tests (LLM-as-Judge) ✓

**Beschreibung:** Evaluator-Markdown-Dateien die Claude als Prompt nutzt um Criteria zu testen.

**Dependencies:** T-002

**Dateien:**
- `tests/criteria-eval/evaluators/*.md` (11 Evaluatoren)
- `tests/criteria-eval/golden/*.md` (22 Golden Examples)
- `criteria/meta/*.yaml` (3 Meta-Criteria)

**Acceptance Criteria:**
- [x] Evaluator-Template mit Grading Rubric (1-5)
- [x] JSON Output Format für strukturierte Ergebnisse
- [x] Golden Examples für alle PRD-Criteria
- [x] Meta-Criteria für Wissenstransfer (criteria-quality, template-quality, evaluator-quality)

**Evaluatoren (11 total):**

| Criteria | Evaluator | Golden | Status |
|----------|-----------|--------|--------|
| goal-quality | ✓ | ✓ | Done |
| hypothesis-quality | ✓ | ✓ | Done |
| evidence-quality | ✓ | ✓ | Done |
| success-metrics-quality | ✓ | ✓ | Done |
| scope-quality | ✓ | ✓ | Done |
| traceability-quality | ✓ | ✓ | Done |
| requirements-quality | ✓ | ✓ | Done |
| information-density | ✓ | ✓ | Done |
| business-value-quality | ✓ | ✓ | Done |
| user-stories-quality | ✓ | ✓ | Done |
| text-quality | ✓ | ✓ | Done |

**Meta-Criteria (für /stan build-*):**

| Meta-Criteria | Zweck |
|---------------|-------|
| criteria-quality | Was macht gutes Criteria-YAML aus? |
| template-quality | Was macht gutes Template aus? |
| evaluator-quality | Was macht guten LLM-as-Judge Evaluator aus? |

**Hinweis:** Auto-Checks (`spelling`, `tests`, `typecheck`, `lint`) brauchen keinen LLM-Evaluator - sie haben Commands.

---

## Phase 5: Denktechniken-Bibliothek ✓

### T-016: Technik-Datenstruktur ✓

**Beschreibung:** Atomare Techniken aus BMAD extrahieren und in eigene Struktur überführen.

**Dependencies:** Keine

**Dateien:**
- `techniques/` - Verzeichnis für Techniken
- `techniques/schema.yaml` - Schema-Definition
- `techniques/*.yaml` - 20 Techniken (atomar)

**Techniken (20 total):**

| Technik | Zwecke |
|---------|--------|
| five-whys | ursachenanalyse, selbstreflexion, code-review |
| fishbone-diagram | ursachenanalyse, big-picture, teamarbeit |
| six-thinking-hats | perspektivwechsel, entscheidungsfindung, teamarbeit |
| first-principles | strukturierte-problemloesung, ideenfindung, big-picture |
| scamper | ideenfindung, perspektivwechsel, strukturierte-problemloesung |
| rubber-duck-debugging | code-review, ursachenanalyse, selbstreflexion |
| pre-mortem | entscheidungsfindung, perspektivwechsel, teamarbeit |
| decision-matrix | entscheidungsfindung, strukturierte-problemloesung, teamarbeit |
| retrospective | selbstreflexion, teamarbeit, ursachenanalyse |
| mind-mapping | ideenfindung, big-picture, strukturierte-problemloesung |
| reverse-thinking | perspektivwechsel, ideenfindung, ursachenanalyse |
| brainstorming | ideenfindung, teamarbeit, big-picture |
| stakeholder-mapping | perspektivwechsel, big-picture, teamarbeit |
| dot-voting | entscheidungsfindung, teamarbeit |
| tree-of-thoughts | strukturierte-problemloesung, entscheidungsfindung, code-review |
| after-action-review | selbstreflexion, ursachenanalyse, teamarbeit |
| code-walkthrough | code-review, teamarbeit, selbstreflexion |
| divide-and-conquer | strukturierte-problemloesung, big-picture |
| socratic-questioning | perspektivwechsel, ursachenanalyse, selbstreflexion |
| round-robin | teamarbeit, perspektivwechsel |
| pros-cons | entscheidungsfindung, perspektivwechsel |

**Acceptance Criteria:**
- [x] Schema definiert: name, description, steps[], examples[], source
- [x] Min. 20 Techniken aus BMAD extrahiert
- [x] PRP-implizite Techniken explizit gemacht (Five Whys, Hypothesis Generation, etc.)
- [x] Jede Technik in eigener YAML-Datei

---

### T-017: Zweck-Mapping ✓

**Beschreibung:** 9 Zwecke mit Techniken verknüpfen (n:m Beziehung).

**Dependencies:** T-016

**Dateien:**
- `techniques/purposes/` - Zweck-Definitionen
- `techniques/purposes/ursachenanalyse.yaml`
- `techniques/purposes/ideenfindung.yaml`
- `techniques/purposes/perspektivwechsel.yaml`
- `techniques/purposes/strukturierte-problemloesung.yaml`
- `techniques/purposes/code-review.yaml`
- `techniques/purposes/big-picture.yaml`
- `techniques/purposes/selbstreflexion.yaml`
- `techniques/purposes/teamarbeit.yaml`
- `techniques/purposes/entscheidungsfindung.yaml`

**Acceptance Criteria:**
- [x] Alle 9 Zwecke als YAML-Dateien
- [x] Jeder Zweck hat: name, question, techniques[] (Referenzen)
- [x] n:m Beziehung funktioniert (Technik in mehreren Zwecken)
- [x] Loader-Funktion: get_techniques_for_purpose(purpose_name)

---

### T-018: /stan think Skill ✓

**Beschreibung:** Skill zum Aufrufen von Denktechniken nach Zweck.

**Dependencies:** T-016, T-017

**Dateien:**
- `.claude/commands/stan/think.md`
- `.claude/hooks/stan/lib/techniques.py`

**Acceptance Criteria:**
- [x] `/stan think` zeigt alle 9 Zwecke
- [x] `/stan think ursachenanalyse` zeigt passende Techniken
- [x] Empfehlung mit Begründung
- [x] User-Consent vor Anwendung
- [x] Technik-Anleitung wird angezeigt (steps, examples)

---

### T-019: Tests für Denktechniken-System ✓

**Beschreibung:** pytest Tests für Techniken-Loader und Zweck-Mapping.

**Dependencies:** T-016, T-017, T-018

**Dateien:**
- `tests/test_techniques.py`

**Acceptance Criteria:**
- [x] Schema-Validierung für alle Techniken (29 Tests)
- [x] Schema-Validierung für alle Zwecke
- [x] Loader gibt korrekte Techniken für Zweck zurück
- [x] n:m Beziehung korrekt aufgelöst
- [x] Bidirektionale Konsistenz (Technik↔Zweck) validiert

---

## Phase 6: Dokument-Versionierung ✓

### T-020: Frontmatter Status-Schema ✓

**Beschreibung:** Templates mit `status` Feld erweitern, Validierung einbauen.

**Dependencies:** T-001

**Dateien:**
- `templates/*.template` - Status-Feld hinzufügen
- `.claude/hooks/stan/lib/document.py` - Status-Validierung

**Acceptance Criteria:**
- [x] Alle Templates haben `status: draft` im Frontmatter
- [x] Gültige Status: draft, approved, in-progress, done, archived
- [x] Validierungsfunktion: `validate_document_status()`
- [x] `updated` Feld wird bei Status-Änderung aktualisiert

---

### T-021: Automatische Status-Übergänge ✓

**Beschreibung:** stan-gate erweitern für automatische Dokument-Status-Updates.

**Dependencies:** T-006, T-020

**Dateien:**
- `.claude/hooks/stan/pre-tool-use/stan_gate.py` - Status-Logik

**Acceptance Criteria:**
- [x] approved → in-progress: Automatisch wenn CREATE Phase startet
- [x] in-progress → done: Automatisch wenn alle Tasks abgeschlossen
- [x] draft → approved: Bleibt manuell (User-Bestätigung)
- [x] done → archived: Bleibt manuell (User räumt auf)
- [x] Status-Änderung wird in Frontmatter geschrieben

---

### T-022: Tests für Dokument-Lifecycle ✓

**Beschreibung:** pytest Tests für Status-Validierung und automatische Übergänge.

**Dependencies:** T-020, T-021

**Dateien:**
- `tests/test_document_lifecycle.py`

**Acceptance Criteria:**
- [x] Validierung erkennt ungültige Status (34 Tests)
- [x] Übergänge nur in erlaubter Reihenfolge (draft → approved, nicht draft → done)
- [x] Automatische Übergänge triggern korrekt
- [x] Frontmatter wird korrekt aktualisiert

---

## Phase 7: Tiered Storage ✓

### T-011: Learnings Promotion ✓

**Beschreibung:** Automatische Promotion von recent → hot bei Mehrfachnutzung.

**Dependencies:** T-003, T-004

**Dateien:**
- `.claude/hooks/stan/lib/learnings.py` - Erweitert

**Implementiert:**
- [x] Heat-Score Berechnung (use_count + recency)
- [x] Automatische Promotion bei PROMOTE_THRESHOLD (3 Nutzungen)
- [x] `get_hot_ranked()` - Hot Learnings nach Score sortiert
- [x] `get_learning_with_score()` - Learning mit Score abrufen

---

### T-012: Learnings Rotation ✓

**Beschreibung:** Automatische Rotation recent → archive bei Overflow + Heat Decay.

**Dependencies:** T-003

**Dateien:**
- `.claude/hooks/stan/lib/learnings.py` - Erweitert
- `.claude/hooks/stan/user-prompt-submit/stan_context.py` - Rotation integriert

**Implementiert:**
- [x] `is_stale()` - Erkennt ungenutzte Learnings (DECAY_DAYS = 14)
- [x] `demote_from_hot()` - Demote stale hot → recent
- [x] `rotate_learnings()` - Periodische Rotation (stale hot → demote/archive, overflow → archive)
- [x] MAX_HOT = 20 Kapazitätslimit
- [x] Integration in stan_context (max 1x täglich)

**Tests:** 19 neue Tests in test_learnings.py (36 total)

---

### T-014: Weitere Criteria Packs ✓

**Beschreibung:** Responsive, A11y, Brand-Consistency Criteria.

**Dependencies:** T-002

**Dateien:**
- `criteria/design/responsive.yaml` - Mobile-First, Breakpoints, Touch-Targets (9 Checks)
- `criteria/design/a11y.yaml` - WCAG 2.1 AA, Semantic HTML, Keyboard Nav (12 Checks)
- `criteria/design/brand-consistency.yaml` - Colors, Typography, Design Tokens (10 Checks)

**Acceptance Criteria:**
- [x] Responsive Criteria mit Mobile-First Fokus
- [x] Accessibility Criteria nach WCAG 2.1 AA
- [x] Brand Consistency Criteria für Design Systems
- [x] Tests für design/ Verzeichnis

---

## Phase 9: Polish ✓

### T-015: E2E Integration Test ✓

**Beschreibung:** Validierung dass alle Komponenten korrekt zusammenarbeiten.

**Dependencies:** T-001 bis T-014

**Dateien:**
- `tests/test_e2e_integration.py` - 26 Integration Tests

**Validiert:**
- [x] Alle 3 Hooks existieren und geben valides JSON zurück
- [x] Alle 9 Skills existieren
- [x] Alle 3 Templates existieren mit status Feld
- [x] Alle 5 Criteria-Kategorien haben Criteria
- [x] Techniken-System funktioniert (20 Techniken, 9 Purposes)
- [x] Alle Lib-Module sind importierbar
- [x] Document Lifecycle ist konfiguriert
- [x] Tiered Storage ist konfiguriert
- [x] Framework-Statistiken: 24+ Criteria, 20 Techniken, 9 Skills

---

## Dependency Graph

```
Phase 1-3 (✓ erledigt):
T-001 (Templates) ──────┐
                        ├──> T-004 (stan-context) ──┐
T-002 (Criteria) ───────┤                           │
                        │                           ├──> T-007 (Skill Core) ──┐
T-003 (Learnings) ──────┼──> T-005 (stan-track) ────┤                         │
                        │           │               │                         │
                        │           ▼               │                         │
                        └──> T-006 (stan-gate) ─────┘                         │
                                                                              │
Phase 4 (✓ erledigt):                                                         │
T-001..T-006 ───────────────────────────────> T-009 (Unit Tests) ✓            │
T-002 ──────────────────────────────────────> T-010 (Criteria-Tests) ✓ ◄──────┘

Phase 5 (✓ erledigt):
T-016 (Technik-Daten) ──┬──> T-017 (Zweck-Mapping) ──┬──> T-018 (/stan think) ✓
                        │                            │
                        └────────────────────────────┴──> T-019 (Tests) ✓

Phase 6 (Dokument-Versionierung):
T-001 (Templates) ──> T-020 (Status-Schema) ──┬──> T-021 (Auto-Übergänge)
                                              │
T-006 (stan-gate) ────────────────────────────┤
                                              │
                                              └──> T-022 (Tests)
```

## Phase 10: Internationalisierung (i18n) ✓

### T-023: Config-System für Sprachen ✓

**Beschreibung:** Konfigurationssystem für User-Präferenzen und Spracheinstellungen.

**Dateien:**
- `.claude/hooks/stan/lib/config.py`
- `.stan/config.yaml` (pro Projekt)

**Acceptance Criteria:**
- [x] User-Config: name, skill_level (beginner/intermediate/expert)
- [x] Language-Config: communication, documents
- [x] Skill-Level-Behavior mit angepasstem Verhalten
- [x] Tests für Config-System (28 Tests)

---

### T-024: Techniques auf Englisch ✓

**Beschreibung:** Alle 21 Technique-YAML-Dateien auf Englisch übersetzen.

**Dateien:**
- `techniques/*.yaml` (21 Dateien)

**Acceptance Criteria:**
- [x] Alle Techniques auf Englisch (name, description, steps, etc.)
- [x] Schema bleibt kompatibel
- [x] Tests grün (217 Tests)

---

### T-025: Purposes auf Englisch ✓

**Beschreibung:** Alle 9 Purpose-YAML-Dateien auf Englisch übersetzen und umbenennen.

**Dateien:**
- `techniques/purposes/*.yaml` (9 Dateien, umbenannt)
- `techniques/schema.yaml` (aktualisiert)

**Umbenennungen:**
- ursachenanalyse.yaml → root-cause-analysis.yaml
- ideenfindung.yaml → ideation.yaml
- perspektivwechsel.yaml → perspective-shift.yaml
- strukturierte-problemloesung.yaml → structured-problem-solving.yaml
- selbstreflexion.yaml → self-reflection.yaml
- teamarbeit.yaml → teamwork.yaml
- entscheidungsfindung.yaml → decision-making.yaml

**Acceptance Criteria:**
- [x] Alle Purposes auf Englisch
- [x] Dateinamen auf Englisch
- [x] Schema aktualisiert
- [x] Tests angepasst und grün

---

### T-026: Commands auf Englisch ✓

**Beschreibung:** Alle /stan Commands auf Englisch übersetzen.

**Dateien:**
- `.claude/commands/stan/*.md` (8 Dateien)

**Acceptance Criteria:**
- [x] `/stan init` - Englisch + Config-Setup erweitert
- [x] `/stan define` - Englisch
- [x] `/stan plan` - Englisch
- [x] `/stan create` - Englisch
- [x] `/stan statusupdate` - Englisch
- [x] `/stan build-template` - Englisch
- [x] `/stan build-criteria` - Englisch
- [x] `/stan healthcheck` - Englisch
- [x] `/stan think` - Englisch + Purpose-IDs aktualisiert

---

## Phase 11: Pre-Launch Review ✓

### T-027: Ralph Best Practices Review ✓

**Beschreibung:** Ralph-Framework analysieren und Best Practices identifizieren, die wir noch nicht haben.

**Quellen:**
- https://github.com/coleam00/ralph-loop-quickstart
- https://github.com/JeredBlu/guides/blob/main/Ralph_Wiggum_Guide.md
- `vendor/ralph/` (lokale Kopie)

**Acceptance Criteria:**
- [x] Ralph Loop Quickstart analysiert
- [x] Ralph Wiggum Guide analysiert
- [x] Fehlende Best Practices identifiziert
- [x] Gap-Liste erstellt → `docs/gap-analysis-ralph-bmad.md`

---

### T-028: BMAD Best Practices Review ✓

**Beschreibung:** BMAD-Framework durchgehen und sicherstellen, dass alle relevanten Best Practices integriert sind.

**Quellen:**
- `vendor/BMAD-METHOD/`
- `vendor/BMAD-METHOD/docs/`

**Acceptance Criteria:**
- [x] BMAD Four-Phases vs. STAN Three-Phases verglichen
- [x] BMAD Scale-Adaptive Levels analysiert
- [x] Fehlende Patterns identifiziert
- [x] Gap-Liste erstellt → `docs/gap-analysis-ralph-bmad.md`

---

### T-029: Template-Criteria Verknüpfung validieren ✓

**Beschreibung:** Prüfen ob alle Templates die richtigen Criteria haben und ob die Verknüpfungen sinnvoll sind.

**Dateien:**
- `templates/*.template`
- `criteria/**/*.yaml`

**Validation Report:**
- prd.md.template: 11 criteria ✓
- plan.md.template: 3 criteria ✓
- stan.md.template: 0 criteria (manifest, keine Qualitätsprüfung nötig) ✓

**Acceptance Criteria:**
- [x] Jedes Template hat passende Criteria
- [x] Keine Criteria verwaist (10 nicht-Template-Criteria für implementation/meta)
- [x] Criteria-Checks sind sinnvoll für Template-Typ
- [x] Alle 217 Tests bestehen

---

### T-030: Gaps schließen ✓

**Beschreibung:** Identifizierte Lücken aus T-027 und T-028 schließen.

**Dependencies:** T-027, T-028, T-029

**Neue Dateien:**
- `criteria/code/visual-verification.yaml` - UI-Verification Criteria
- `criteria/strategy/story-size.yaml` - Story-Size Criteria

**Aktualisierte Dateien:**
- `.claude/commands/stan/create.md` - Activity Log, Visual Verification, Completion Signal
- `.claude/commands/stan/plan.md` - Story Size Rule, Task Ordering

**Acceptance Criteria:**
- [x] Visual Verification Criteria erstellt (HIGH Priority)
- [x] Story Size Criteria erstellt (HIGH Priority)
- [x] CREATE Command mit Activity Log Pattern aktualisiert
- [x] CREATE Command mit Completion Signal aktualisiert
- [x] PLAN Command mit Story Size Rule aktualisiert
- [x] Tests aktualisiert und grün (217 Tests)
- [x] Dokumentation aktualisiert

---

## Phase 12: Enforcement Completion ✓

### T-031: Acceptance Criteria Completion Check ✓

**Beschreibung:** Ralph-Style Loop implementieren: Hook blockiert Commit wenn nicht alle Acceptance Criteria abgehakt sind.

**Dependencies:** T-006

**Dateien:**
- `src/stan/lib/acceptance.py` - Checkbox-Parser
- `src/stan/lib/session_state.py` - Iteration Counter
- `src/stan/hooks/stan_gate.py` - check_acceptance_criteria()
- `.claude/hooks/stan/lib/acceptance.py` - Kopie für Test-Kompatibilität
- `.claude/hooks/stan/lib/session_state.py` - Iteration Functions
- `tests/test_acceptance_criteria.py` - 17 Tests
- `tests/test_gate_acceptance.py` - 14 Tests

**Acceptance Criteria:**
- [x] Hook blockiert Commit wenn Checkboxen nicht abgehakt
- [x] Iteration Counter (reset bei Task-Wechsel)
- [x] Max Iterations Check (10 wie Ralph)
- [x] Eskalations-Message bei Max erreicht
- [x] Block-Message zeigt offene Criteria
- [x] 357 Tests grün

---

### T-032: STAN Plugin erstellen ✓

**Beschreibung:** Claude Code Plugin erstellen statt separatem Test-Projekt. Plugin kann mit `cc --plugin-dir` installiert werden.

**Dependencies:** T-031

**Dateien:**
- `stan-plugin/.claude-plugin/plugin.json` - Plugin-Manifest
- `stan-plugin/commands/stan/*.md` - 10 Commands
- `stan-plugin/hooks/hooks.json` - Hook-Konfiguration
- `stan-plugin/rules/stan/*.md` - Rules
- `stan-plugin/assets/` - Templates, Criteria, Techniques
- `tests/test_stan_plugin.py` - 31 Tests

**Acceptance Criteria:**
- [x] Plugin-Verzeichnis mit .claude-plugin/plugin.json
- [x] Alle 10 /stan Commands kopiert
- [x] hooks.json mit PreToolUse, PostToolUse, UserPromptSubmit
- [x] Rules (skill-level.md, task-priority.md)
- [x] Assets (templates, criteria, techniques)
- [x] Keine absolute Pfade im Plugin
- [x] Tests (31 passed)

---

## Phase 13: Hybrid-Architektur + Gap-Analysis Items

### T-033: STAN Skill erstellen (Hybrid-Ansatz) ✓

**Beschreibung:** Skill erstellen der automatisch Phasen und Denktechniken erkennt. Commands bleiben für explizite Kontrolle.

**Dependencies:** Keine

**Dateien:**
- `stan-plugin/skills/stan/SKILL.md` - Hauptlogik mit Trigger-Phrases
- `tests/test_stan_skill.py` - 13 Tests

**Acceptance Criteria:**
- [x] SKILL.md mit Trigger-Phrases (DE + EN)
- [x] Phasen-Erkennung: kein stan.md → DEFINE, PRD approved → PLAN, Tasks ready → CREATE
- [x] Think-Erkennung: "ich stecke fest", "warum passiert das" → Techniken vorschlagen
- [x] Commands bleiben für explizite Kontrolle (`/stan init`, `/stan think`, etc.)
- [x] Widerworte bei Phase-Skip dokumentiert
- [x] Tests (13 passed)

---

### T-034: Project Complexity Levels (0-4) ✓

**Beschreibung:** BMAD-Style Planungstiefe pro Projekt mit transparenter Einschätzung und Anpassungsmöglichkeit.

**Dependencies:** Keine

**Dateien:**
- `.claude/hooks/stan/lib/config.py` - COMPLEXITY_LEVELS + get/set functions
- `.claude/commands/stan/init.md` - Complexity-Auswahl erweitert
- `tests/test_complexity_levels.py` - 14 Tests

**Acceptance Criteria:**
- [x] 5 Levels: 0 (trivial), 1 (minimal), 2 (standard), 3 (detailed), 4 (comprehensive)
- [x] Level beeinflusst Planungstiefe, nicht Kommunikationsstil
- [x] **Transparenz:** /stan init zeigt Einschätzung mit Begründung
- [x] **User Override:** User kann Komplexität korrigieren
- [x] Komplexität wird in .stan/config.yaml gespeichert
- [x] Tests für alle Levels

---

### T-035: Feature Completion (explizit durch User) ✓

**Beschreibung:** Completion passiert erst wenn User explizit sagt "fertig" / "passt". Nicht automatisch nach CREATE. Verschiebt PRD, Plan UND Tasks zusammen als Package nach `.stan/completed/`.

**Dependencies:** Keine

**Dateien:**
- `.claude/commands/stan/complete.md` - Expliziter Command mit Trigger-Wörtern
- `tests/test_feature_completion.py` - 9 Tests

**Trigger:**
- User sagt: "Das ist jetzt wirklich fertig" / "Passt alles" / "Abgeschlossen"
- Oder explizit: `/stan complete`

**Completion Package:**
```
docs/prd.md   → .stan/completed/prd-{feature}.md
docs/plan.md  → .stan/completed/plan-{feature}.md
docs/tasks.md → .stan/completed/tasks-{feature}.md
```

Then fresh files are created from templates for the next feature.
This keeps `docs/` clean (only current feature).

**Acceptance Criteria:**
- [x] Trigger-Wörter dokumentiert: "fertig", "passt", "abgeschlossen", "finished", "done"
- [x] Nachfrage vor Completion: "Are you sure?"
- [x] Dateiname = **Feature-Name** (NICHT Datum!): `prd-dark-mode.md`
- [x] Datum nur als Metadatum im Frontmatter (`completed_at`)
- [x] Verschiebt **alle 3 Dokumente** als Package
- [x] Setzt status: completed im Frontmatter
- [x] Erstellt neue leere Dateien aus Templates
- [x] Optional: Learnings nach Graphiti promoten
- [x] Tests (9 passed)

---

### T-036: Max Iterations konfigurierbar ✓

**Beschreibung:** Default 10 (wie Ralph), optional in stan.md überschreibbar.

**Dependencies:** Keine

**Referenz:** Ralph löst es genauso - Default 10, via Argument überschreibbar.

**Dateien:**
- `templates/stan.md.template` - `max_iterations` Feld (optional)
- `.claude/hooks/stan/pre-tool-use/stan_gate.py` - aus Manifest lesen, Fallback 10
- `tests/test_max_iterations.py` - 12 Tests

**stan.md Beispiel:**
```yaml
---
phase: create
max_iterations: 15  # Optional, default 10
---
```

**Acceptance Criteria:**
- [x] Default 10 im Hook (hardcoded Fallback)
- [x] Optional überschreibbar in stan.md
- [x] Hook liest `max_iterations` aus Manifest, nutzt 10 wenn nicht vorhanden
- [x] Tests (12 passed)

---

## Status Übersicht

| Phase | Status | Tasks |
|-------|--------|-------|
| 1: Foundation | ✓ | T-001, T-002, T-003 |
| 2: Core Hooks | ✓ | T-004, T-005, T-006 |
| 3: Skill | ✓ | T-007, T-008 |
| 4: Testing | ✓ | T-009 ✓, T-010 ✓ |
| 5: Denktechniken | ✓ | T-016 ✓, T-017 ✓, T-018 ✓, T-019 ✓ |
| 6: Dokument-Versionierung | ✓ | T-020 ✓, T-021 ✓, T-022 ✓ |
| 7: Tiered Storage | ✓ | T-011 ✓, T-012 ✓ |
| 8: Criteria Packs | ✓ | T-014 ✓ |
| 9: Polish | ✓ | T-015 ✓ |
| 10: i18n | ✓ | T-023 ✓, T-024 ✓, T-025 ✓, T-026 ✓ |
| 11: Pre-Launch Review | ✓ | T-027 ✓, T-028 ✓, T-029 ✓, T-030 ✓ |
| 12: Enforcement Completion | ✓ | T-031 ✓, T-032 ✓ |
| 13: Hybrid + Gap-Analysis | ✓ | T-033 ✓, T-034 ✓, T-035 ✓, T-036 ✓ |
| 14: Claude Tasks Integration | · | T-037 ·, T-038 ·, T-039 ·, T-040 · |
| 15: Version-Tracking | ✓ | T-041 ✓ |
| 16: Autonomie-Features | ✓ | T-042 ✓, T-043 ✓, T-044 ✓, T-045 ✓ |
| 17: Terminology Cleanup | ✓ | T-046 ✓ |

---

## Phase 14: Claude Tasks Integration

### T-037: Claude Tasks Adapter in /stan create

**Beschreibung:** Bei `/stan create` werden STAN Tasks (docs/tasks.md) zu Claude Tasks konvertiert für Runtime-Koordination.

**Dependencies:** T-031

**Dateien:**
- `.claude/commands/stan/create.md` - Erweitern mit Claude Tasks Setup
- `.claude/hooks/stan/lib/task_adapter.py` - Konvertierungslogik

**Acceptance Criteria:**
- [ ] Beim Start von `/stan create` werden pending STAN Tasks zu Claude Tasks
- [ ] Task-ID Mapping: T-XXX → Claude Task #Y (für Rückverfolgung)
- [ ] Dependencies werden übernommen (blockedBy)
- [ ] Acceptance Criteria bleiben in STAN Task (Source of Truth)

---

### T-038: Bidirektionale Synchronisation

**Beschreibung:** Wenn Claude Task completed wird, wird entsprechender STAN Task in docs/tasks.md als ✓ markiert.

**Dependencies:** T-037

**Dateien:**
- `.claude/hooks/stan/post-tool-use/stan_track.py` - Sync-Logik

**Acceptance Criteria:**
- [ ] Claude Task #Y completed → STAN Task T-XXX wird aktualisiert
- [ ] Checkboxen in docs/tasks.md werden automatisch angehakt
- [ ] Fehlerfall: Warnung wenn Mapping nicht gefunden

---

### T-039: Multi-Agent Owner-Zuweisung

**Beschreibung:** Bei Parallelisierung wird Claude Task einem Subagent zugewiesen (owner-Feld).

**Dependencies:** T-037

**Dateien:**
- `.claude/commands/stan/create.md` - Parallelisierungs-Logik

**Acceptance Criteria:**
- [ ] Tasks ohne Konflikte werden parallel geplant
- [ ] Jeder Subagent bekommt eigenen Claude Task mit owner
- [ ] Hauptagent überwacht Completion

---

### T-040: Session-Resume Synchronisation

**Beschreibung:** Bei Session-Start werden Claude Tasks und STAN Tasks abgeglichen.

**Dependencies:** T-038

**Dateien:**
- `.claude/hooks/stan/user-prompt-submit/stan_context.py` - Sync bei Start

**Acceptance Criteria:**
- [ ] Bei Session-Start: Claude Tasks Status mit STAN Tasks vergleichen
- [ ] Diskrepanzen werden aufgelöst (STAN Tasks = Source of Truth)
- [ ] Warnung bei unerwartetem State

---

## Phase 15: Version-Tracking & Auto-Updates

### T-041: Version-Tracking in CLAUDE.md ✓

**Beschreibung:** Claude Code Version-Tracking in CLAUDE.md für automatische Update-Erkennung.

**Dependencies:** Keine

**Dateien:**
- `CLAUDE.md` - Version-Tracking Sektion

**Acceptance Criteria:**
- [x] `Zuletzt geprüft` Feld mit Version und Datum
- [x] Automatische Prüfung Anleitung
- [x] Bekannte Features dokumentiert
- [x] Changelog-Quelle angegeben

---

## Phase 16: Autonomie-Features

### T-042: Loop-Logik in /stan create ✓

**Beschreibung:** Autonome Execution-Loop in `/stan create` implementieren.

**Dependencies:** T-031, T-036

**Dateien:**
- `.claude/commands/stan/create.md` - Loop-Instruktionen erweitert
- `tests/test_create_loop.py` - 13 Tests

**Acceptance Criteria:**
- [x] Loop: Task holen → Ausführen → Acceptance Criteria prüfen → Nächster Task
- [x] Bei Fehlschlag: Iteration Counter erhöhen
- [x] Bei Max Iterations: STOP + Perspective Shift Empfehlung (/stan think)
- [x] Bei Erfolg: Nächsten ready Task holen
- [x] Completion Signal wenn alle Tasks done

---

### T-043: Persistent Session State ✓

**Beschreibung:** Session State von `/tmp/` nach `.stan/session.json` verschieben für Session-Überlebende Persistenz.

**Dependencies:** T-003

**Dateien:**
- `.claude/hooks/stan/lib/session_state.py` - Pfad geändert
- `.gitignore` - `.stan/` hinzugefügt
- `tests/test_persistent_session.py` - 9 Tests

**Acceptance Criteria:**
- [x] Session State in `.stan/session.json`
- [x] Migration-Logik: Alte `/tmp/` Session → neue Location
- [x] Bei Session-Resume: State wiederherstellen
- [x] `.stan/` in `.gitignore`
- [x] Tests aktualisiert (9 Tests)

---

### T-044: Model Auto-Selection ✓

**Beschreibung:** Automatische Modellwahl für Subagenten basierend auf Task-Komplexität.

**Dependencies:** T-034

**Dateien:**
- `.claude/hooks/stan/lib/model_selection.py` - Selection + Escalation
- `tests/test_model_selection.py` - 19 Tests

**Acceptance Criteria:**
- [x] AVAILABLE_MODELS: haiku, sonnet, opus
- [x] Auto-Logik: complexity < 3 → sonnet, complexity ≥ 3 → opus
- [x] Model Escalation bei Fehlschlägen (haiku → sonnet → opus → None)
- [x] can_escalate() und escalate_model() Funktionen
- [x] get_model_info() mit description und use_case
- [x] Tests (19 passed)

---

### T-045: Task Priority Default Rule ✓

**Description:** Safeguard against Claude labeling required tasks as "optional" or "enhancement".

**Dependencies:** None

**Files:**
- `.claude/rules/stan/task-priority.md` - Rule file (English)
- `.claude/commands/stan/create.md` - Add explicit rule section
- `docs/tasks.md` - Add status legend header

**Acceptance Criteria:**
- [x] Rule file `.claude/rules/stan/task-priority.md` created
- [x] Status legend in tasks.md header explains: · = required, ~ = optional, § = archived
- [x] /stan create command includes explicit "all pending = required" rule
- [x] Tests verify rule file exists and has correct content (12 tests)

---

## Phase 17: Terminology Cleanup ✓

### T-046: Rename "archived" to "completed" ✓

**Description:** Rename terminal status from "archived" to "completed" for clarity. Also move completed files to `.stan/completed/` instead of `docs/archive/`.

**Dependencies:** T-035

**Files:**
- `.claude/hooks/stan/lib/document.py` - Change VALID_STATUSES and transitions
- `tests/test_document_lifecycle.py` - Update tests
- `tests/test_completed_status.py` - New TDD tests
- `.claude/rules/stan/task-priority.md` - Update § symbol meaning if needed
- `docs/tasks.md` - Update status legend

**Rationale:**
- "completed" is clearer and more positive than "archived"
- `.stan/completed/` keeps `docs/` clean (only current feature)
- Matches T-035 (Feature Completion) terminology

**Acceptance Criteria:**
- [x] VALID_STATUSES uses "completed" instead of "archived"
- [x] ALLOWED_TRANSITIONS updated for "completed"
- [x] MANUAL_TRANSITIONS updated for "completed"
- [x] Tests updated and passing (34 document lifecycle + 10 completed status tests)
- [x] Status legend in tasks.md updated (§ = completed, not archived)
- [x] T-035 uses consistent terminology
