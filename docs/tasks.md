# STAN Framework - Tasks

Abgeleitet aus [plan.md](plan.md). Format: Task-ID, Beschreibung, Dependencies, Acceptance Criteria.

---

## Phase 1: Foundation

### T-001: Templates erstellen

**Beschreibung:** Basis-Templates für stan.md, prd.md, plan.md erstellen.

**Dependencies:** Keine

**Dateien:**
- `templates/stan.md.template`
- `templates/prd.md.template`
- `templates/plan.md.template`

**Acceptance Criteria:**
- [ ] Templates haben Frontmatter mit `type:` und `criteria:` Liste
- [ ] Templates enthalten beschreibende Abschnitte (keine Prompts)
- [ ] Markdown-Format, gut lesbar

---

### T-002: Criteria Pack Struktur

**Beschreibung:** Verzeichnisstruktur für Criteria anlegen + erste Packs.

**Dependencies:** Keine

**Dateien:**
- `criteria/code/tests.yaml`
- `criteria/code/typecheck.yaml`
- `criteria/code/lint.yaml`
- `criteria/text/spelling.yaml`
- `criteria/strategy/goal-quality.yaml`

**Acceptance Criteria:**
- [ ] YAML-Format: name, description, checks[]
- [ ] Jeder Check hat: id, question, required (bool)
- [ ] Auto-Checks haben `command` Feld

---

### T-003: Lokales Learnings-System

**Beschreibung:** Tiered Storage für Learnings in `~/.stan/learnings/`.

**Dependencies:** Keine

**Dateien:**
- `.claude/hooks/stan/lib/learnings.py`

**Acceptance Criteria:**
- [ ] `~/.stan/learnings/recent.json` - Rolling ~50, FIFO
- [ ] `~/.stan/learnings/hot.json` - Oft genutzte
- [ ] `~/.stan/learnings/archive.json` - Permanent
- [ ] Funktionen: save_learning(), load_learnings(), promote_to_hot()

---

## Phase 2: Core Hooks

### T-004: stan-context Hook (UserPromptSubmit)

**Beschreibung:** Kontext in jede Nachricht injizieren.

**Dependencies:** T-001, T-003

**Dateien:**
- `.claude/hooks/stan/user-prompt-submit/stan-context.py`

**Acceptance Criteria:**
- [ ] Liest stan.md Manifest (wenn vorhanden)
- [ ] Lädt lokale Learnings (hot + recent)
- [ ] Injiziert: Phase, Current Task, Learnings Count
- [ ] Graceful Fallback wenn kein stan.md

---

### T-005: stan-track Hook (PostToolUse - Bash)

**Beschreibung:** Test-Ergebnisse tracken, Learnings automatisch erkennen.

**Dependencies:** T-003

**Dateien:**
- `.claude/hooks/stan/post-tool-use/stan-track.py`

**Acceptance Criteria:**
- [ ] Erkennt Test-Commands (npm test, pytest, etc.)
- [ ] Speichert Exit-Code in Session State
- [ ] Erkennt ROT→GRÜN Wechsel
- [ ] Erstellt pending_learning bei Wechsel
- [ ] Injiziert Reminder: "Learning erkannt! Vor Commit speichern."

---

### T-006: stan-gate Hook (PreToolUse)

**Beschreibung:** Phase-Enforcement, Quality Gates, Learnings-Enforcement.

**Dependencies:** T-003, T-005

**Dateien:**
- `.claude/hooks/stan/pre-tool-use/stan-gate.py`

**Acceptance Criteria:**
- [ ] BLOCKIERT Commit wenn pending_learnings existieren
- [ ] BLOCKIERT Phase-Wechsel wenn Bedingungen nicht erfüllt
- [ ] BLOCKIERT nach 3-Strikes (gleiche Fehler)
- [ ] Quality Gates: Tests grün vor Commit (in CREATE)

---

## Phase 3: Skill

### T-007: /stan Skill - Core Commands

**Beschreibung:** Basis-Skill mit init, define, plan, create, statusupdate.

**Dependencies:** T-001, T-004, T-006

**Dateien:**
- `.claude/skills/stan/SKILL.md`

**Acceptance Criteria:**
- [ ] `/stan init` - Erstellt stan.md, fragt nach Projekt-Info
- [ ] `/stan define` - Startet/fortsetzt DEFINE Phase
- [ ] `/stan plan` - Startet/fortsetzt PLAN Phase
- [ ] `/stan create` - Startet CREATE Phase (autonom)
- [ ] `/stan statusupdate` - Zeigt Status, erlaubt manuelle Änderung
- [ ] Widerworte bei bedeutsamem Phase-Wechsel

---

### T-008: /stan Skill - Builder Commands

**Beschreibung:** Template und Criteria Builder.

**Dependencies:** T-001, T-002

**Dateien:**
- `.claude/skills/stan/SKILL.md` (erweitern)

**Acceptance Criteria:**
- [ ] `/stan build-template` - Interaktiv Template bauen + Criteria verknüpfen
- [ ] `/stan build-criteria` - Interaktiv Criteria bauen + Templates identifizieren
- [ ] `/stan healthcheck` - Konsistenz prüfen

---

## Phase 4: Tiered Storage (Future)

### T-009: Learnings Promotion

**Beschreibung:** Automatische Promotion von recent → hot bei Mehrfachnutzung.

**Dependencies:** T-003, T-004

**Status:** Future

---

### T-010: Learnings Rotation

**Beschreibung:** Automatische Rotation recent → archive bei Overflow.

**Dependencies:** T-003

**Status:** Future

---

## Phase 5: Polish (Future)

### T-011: Weitere Criteria Packs

**Beschreibung:** Responsive, A11y, Brand-Consistency Criteria.

**Dependencies:** T-002

**Status:** Future

---

### T-012: E2E Test

**Beschreibung:** Ein echtes Mini-Feature komplett durch alle Phasen führen.

**Dependencies:** T-001 bis T-008

**Status:** Future

---

## Dependency Graph

```
T-001 (Templates) ──────┐
                        ├──> T-004 (stan-context) ──┐
T-002 (Criteria) ───────┤                           │
                        │                           ├──> T-007 (Skill Core)
T-003 (Learnings) ──────┼──> T-005 (stan-track) ────┤
                        │           │               │
                        │           ▼               │
                        └──> T-006 (stan-gate) ─────┘
                                    │
                                    ▼
                             T-008 (Skill Builder)
```

## Parallelisierung möglich

- **Parallel:** T-001, T-002, T-003 (keine gemeinsamen Dateien)
- **Sequentiell:** T-004, T-005, T-006 (bauen aufeinander auf)
- **Sequentiell:** T-007, T-008 (Skill erweitern)
