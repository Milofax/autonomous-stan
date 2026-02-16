# autonomous-stan

**Autonomes Workflow-Framework mit modularen Denkwerkzeugen für Claude Code.**

Templates, Criteria, Techniques — zusammen ein stringenter Workflow, einzeln nutzbare Denkwerkzeuge. Nicht nur für Code — für Dokumente, Recherche, Konzepte, Entscheidungen.

## Installation

```bash
claude plugin install github:Milofax/autonomous-stan
```

## Was es macht

autonomous-stan macht Claude zu einem echten **Denk- und Arbeitspartner**:

1. **Dialog erst** — Versteht was gebraucht wird (`/stan define`)
2. **Plan dann** — Strukturierter Plan basierend auf Recherche (`/stan plan`)
3. **Autonom umsetzen** — Zuverlässig mit echtem TDD (`/stan create`)
4. **Selbstkritisch prüfen** — Unabhängiger Evaluator gegen Self-Serving Bias

## Die 8 Hooks

| Hook | Event | Was es macht |
|------|-------|-------------|
| **stan_context** | UserPromptSubmit | Injiziert Phase, Learnings, aktive Criteria |
| **stan_gate** | PreToolUse(Bash) | Phase-Enforcement: kein Build ohne Plan |
| **git_guard** | PreToolUse(Bash) | Conventional Commits, Branch Protection |
| **credential_guard** | PreToolUse(Bash) | 905 Secret-Patterns, 3-Strikes |
| **stan_track** | PostToolUse(Bash) | Test-Tracking, ROT→GRÜN Erkennung |
| **loop_breaker** | PostToolUse(Bash+Edit) | Edit→Test Loop Detection → Eskalation |
| **Evaluator** | PostToolUse(Edit) | Unabhängiger Quality-Check (Prompt-Hook) |
| **Final Gate** | Stop | Completion-Verification (Prompt-Hook) |

## Slash-Commands

```
/stan init       → Projekt initialisieren
/stan define     → PRD erstellen (Dialog)
/stan plan       → Tasks ableiten
/stan create     → Autonom umsetzen
/stan think      → Thinking-Technique anwenden
/stan complete   → Task abschließen
/stan ready      → Nächsten Task starten
/stan healthcheck → Selbstdiagnose
```

## Modulare Denkwerkzeuge

### 23 Criteria (YAML)
Qualitätschecklisten: `goal-is-smart`, `code-quality`, `text-quality`, `ui-is-responsive`, ...

### 22 Techniques (YAML)
Denkwerkzeuge: Five Whys, Six Thinking Hats, First Principles, Pre-Mortem, Systematic Debugging, ...

### 9 Purposes
Einstiegspunkte: Root Cause Analysis, Decision Making, Ideation, Perspective Shift, ...

Purpose → empfiehlt Technique → Steps + Escalation.

## Loop Detection (NEU in v2)

Kein Framework hatte bisher echte Denk-Loop-Erkennung. autonomous-stan trackt Edit→Test-Paare:

- 3x gleiche Datei editiert + Test immer noch rot → **Denk-Loop erkannt**
- Automatische Eskalation: "STOP. Question your approach. Apply Systematic Debugging Phase 1."

Inspiriert von Superpowers' "3+ fixes failed = question architecture", aber mechanisch erzwungen.

## Credential Guard

905 Regex-Patterns aus [secrets-patterns-db](https://github.com/mazen160/secrets-patterns-db). Blockiert `git add`/`git commit` wenn API-Keys, Tokens oder Private Keys in staged Files.

## Evaluator (Anti Self-Serving Bias)

Prompt-Hooks bei jedem Edit und vor Completion. Ein unabhängiger Evaluator prüft:
- Sind Checkboxen ECHT erfüllt oder nur abgehakt?
- Ist der Code FERTIG oder stehen noch TODOs drin?
- Ist das Dokument KONKRET oder nur Wunschdenken?

## Architektur-Entscheidungen

**Was drin ist (und warum):**
- Evaluator-Hooks (Superpowers) — bekämpft Self-Serving Bias mechanisch
- Credential Guard (taming-stan) — 905 Patterns, bewährt
- Loop Breaker (NEU) — einziges Framework mit Denk-Loop-Erkennung
- Git Guard (taming-stan) — Conventional Commits erzwingen
- Systematic Debugging (Superpowers) — 4-Phasen-Prozess mit Anti-Rationalization

**Was NICHT drin ist (und warum):**
- Multi-Agent Personas — ein LLM das Rollen spielt ≠ echte Perspektiven
- Session-End Hook — gibt es in Claude Code nicht
- TUI Visualisierung — 15h Aufwand, Markdown Tasks reichen
- 7 Review-Agents — Overkill, Two-Stage Review deckt 90% ab
- Eval-Driven Development — pass@k elegant, aber Criteria reicht im Alltag

## Synthese aus 10 Frameworks

Analysiert und die besten Ideen integriert:
- [claude-superpowers](https://github.com/mbenhamd/claude-superpowers) — Systematic Debugging, Verification
- [taming-stan](https://github.com/Milofax/taming-stan) — Credential Guard, Git Guard
- [Ralph](https://github.com/ralphthe/ralph) — Fresh Context, Completion Signal
- [GSD](https://github.com/wonderwhy-er/gsd-claude-code) — Context Rot Prevention
- [BMAD Method](https://github.com/bmad-method/bmad-method) — Scale-Adaptive Levels
- [Everything Claude Code](https://github.com/pashpashpash/everything-claude-code) — Verification Loop
- [PRPs](https://github.com/aarontravass/prps-agentic-eng) — Structured Reviews
- [Beads](https://github.com/beads-ai/beads) — JSONL Task Schema
- OpenClaw Architecture — Multi-Agent Learnings, Memory Patterns

## Lizenz

MIT
