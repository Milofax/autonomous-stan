# STAN Framework - Tasks

Abgeleitet aus [plan.md](plan.md). Format: Task-ID, Beschreibung, Dependencies, Acceptance Criteria.

---

## Phase 1: Foundation ✓

### T-001: Templates erstellen ✓

**Beschreibung:** Basis-Templates für stan.md, prd.md, plan.md erstellen.

**Dependencies:** Keine

**Dateien:**
- `templates/stan.md.template`
- `templates/prd.md.template`
- `templates/plan.md.template`

**Acceptance Criteria:**
- [x] Templates haben Frontmatter mit `type:` und `criteria:` Liste
- [x] Templates enthalten beschreibende Abschnitte (keine Prompts)
- [x] Markdown-Format, gut lesbar

---

### T-002: Criteria Pack Struktur ✓

**Beschreibung:** Verzeichnisstruktur für Criteria anlegen + erste Packs.

**Dependencies:** Keine

**Dateien:**
- `criteria/code/tests.yaml`
- `criteria/code/typecheck.yaml`
- `criteria/code/lint.yaml`
- `criteria/text/spelling.yaml`
- `criteria/strategy/goal-quality.yaml`

**Acceptance Criteria:**
- [x] YAML-Format: name, description, checks[]
- [x] Jeder Check hat: id, question, required (bool)
- [x] Auto-Checks haben `command` Feld

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
- [ ] Widerworte bei bedeutsamem Phase-Wechsel

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

### T-010: Interaktive Criteria-Tests (LLM-as-Judge)

**Beschreibung:** Evaluator-Markdown-Dateien die Claude als Prompt nutzt um Criteria zu testen.

**Dependencies:** T-002

**Dateien:**
- `tests/criteria-eval/evaluators/*.md`
- `tests/criteria-eval/golden/*.md`
- `tests/criteria-eval/runner.py`

**Acceptance Criteria:**
- [ ] Evaluator-Template mit Grading Rubric (1-5)
- [ ] Golden Examples (gut/schlecht) für jedes Criteria
- [ ] JSON Output Format für strukturierte Ergebnisse
- [ ] Integration in `/stan healthcheck --eval-criteria`

**Status:** In Progress - Prototyping nötig

---

## Phase 5: Tiered Storage (Future)

### T-011: Learnings Promotion

**Beschreibung:** Automatische Promotion von recent → hot bei Mehrfachnutzung.

**Dependencies:** T-003, T-004

**Status:** Future

---

### T-012: Learnings Rotation

**Beschreibung:** Automatische Rotation recent → archive bei Overflow.

**Dependencies:** T-003

**Status:** Future

---

## Phase 6: Document Lifecycle (Future)

### T-013: Dokument-Versionierung

**Beschreibung:** System für Versionierung und Lifecycle von Dokumenten (PRD, Plan, etc.).

**Dependencies:** T-007

**Fragen zu klären:**
- Wie erkennen wir dass ein Dokument "abgeschlossen" ist?
- Wann brauchen wir einen neuen Plan für ein neues Feature?
- Was können wir von PRP und BMAD übernehmen?

**Recherche nötig:**
- [ ] PRP Dokument-Lifecycle analysieren
- [ ] BMAD Versionierung analysieren
- [ ] Best Practices identifizieren

**Acceptance Criteria:**
- [ ] Dokument-Status-Modell (draft → review → approved → archived)
- [ ] Automatische Erkennung von "Dokument veraltet"
- [ ] Neues Feature = Neuer Plan Workflow

**Status:** Needs Analysis

---

### T-014: Weitere Criteria Packs

**Beschreibung:** Responsive, A11y, Brand-Consistency Criteria.

**Dependencies:** T-002

**Status:** Future

---

## Phase 7: Polish (Future)

### T-015: E2E Test

**Beschreibung:** Ein echtes Mini-Feature komplett durch alle Phasen führen.

**Dependencies:** T-001 bis T-008

**Status:** Future

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
Phase 4 (aktuell):                                                            │
T-001..T-006 ───────────────────────────────> T-009 (Unit Tests) ✓            │
T-002 ──────────────────────────────────────> T-010 (Criteria-Tests) ◄────────┘
```

## Status Übersicht

| Phase | Status | Tasks |
|-------|--------|-------|
| 1: Foundation | ✓ | T-001, T-002, T-003 |
| 2: Core Hooks | ✓ | T-004, T-005, T-006 |
| 3: Skill | ✓ | T-007, T-008 |
| 4: Testing | ► | T-009 ✓, T-010 in progress |
| 5: Tiered Storage | Future | T-011, T-012 |
| 6: Document Lifecycle | Needs Analysis | T-013 |
| 6: Criteria Packs | Future | T-014 |
| 7: Polish | Future | T-015 |
