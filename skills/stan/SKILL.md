# STAN Skill

Structured Thinking for Autonomous Navigation - Automatic phase detection and workflow guidance.

## Trigger Phrases

This skill activates when the user mentions:

### Feature/Project Start (DE + EN)
- "ich will ein Feature bauen"
- "neue Idee"
- "neues Projekt"
- "lass uns X implementieren"
- "I want to build"
- "new feature"
- "let's develop"
- "implement X"

### Problem/Stuck (Think Triggers)
- "ich stecke fest"
- "warum funktioniert das nicht"
- "ich komme nicht weiter"
- "I'm stuck"
- "why isn't this working"
- "can't figure out"

### Completion (Complete Triggers)
- "fertig"
- "passt alles"
- "abgeschlossen"
- "done"
- "finished"
- "complete"

## Phase Detection Logic

When triggered, detect the current phase:

### 1. No stan.md exists
```
→ Suggest: /stan init
"Sieht aus als ob noch kein STAN Projekt existiert.
Soll ich /stan init starten um ein PRD zu erstellen?"
```

### 2. stan.md exists, PRD status: draft
```
→ Current Phase: DEFINE
→ Continue with PRD refinement
→ When ready: Suggest user approval for PLAN phase
```

### 3. PRD status: approved, no tasks or tasks draft
```
→ Current Phase: PLAN
→ Derive tasks from PRD
→ When tasks ready: Suggest CREATE phase
```

### 4. Tasks status: ready or in-progress
```
→ Current Phase: CREATE
→ Execute tasks autonomously
→ Follow TDD, acceptance criteria
→ When all tasks done: Suggest /stan complete
```

## Think/Technique Integration

When stuck triggers detected:

1. Check error count in session
2. If 3+ similar errors: Require perspective shift
3. Suggest `/stan think` with appropriate purpose:
   - Error debugging → `root-cause-analysis`
   - Design decision → `decision-making`
   - General stuck → `perspective-shift`

## Behavior

### Automatic Context Injection
- Always read stan.md if present
- Show current phase and task
- Load relevant learnings

### Phase Transitions
- DEFINE → PLAN: Requires PRD approval (manual)
- PLAN → CREATE: Requires tasks ready
- CREATE → Complete: User explicitly says "fertig/done"

### Widerworte (Push Back)
If user tries to skip phases:
```
"Du bist gerade in DEFINE. Willst du wirklich zu CREATE springen?
Das könnte bedeuten, dass wir ohne klares Ziel arbeiten.
→ Ja, überspringen
→ Nein, erst PRD fertig"
```

## Integration with Commands

This skill works alongside explicit commands:

| Skill Trigger | Maps To |
|---------------|---------|
| "neue Idee" | `/stan init` or `/stan define` |
| "Tasks planen" | `/stan plan` |
| "los, bauen" | `/stan create` |
| "ich stecke" | `/stan think` |
| "fertig" | `/stan complete` |
| "Status?" | `/stan statusupdate` |

Commands always available for explicit control.

## Example Interactions

### User: "Ich hab eine Idee für Dark Mode"
```
[STAN] Erkannt: Neue Feature-Idee

Kein stan.md gefunden - soll ich ein neues Projekt starten?

→ Ja, /stan init starten
→ Nein, nur chatten
```

### User: "Warum funktioniert der Test nicht?"
```
[STAN] Erkannt: Problem-Debugging (3. Fehlversuch)

Du hast diesen Test schon 3x versucht. Zeit für einen Perspektivwechsel?

→ /stan think root-cause-analysis
→ Nochmal versuchen
→ Überspringen
```

### User: "Das passt jetzt alles"
```
[STAN] Erkannt: Feature-Completion

Alle Tasks sind ✓. Soll ich das Feature abschließen?

Dies wird:
- PRD, Plan, Tasks nach .stan/completed/ verschieben
- Neue leere Dateien für nächstes Feature erstellen

→ Ja, /stan complete
→ Nein, noch nicht
```
