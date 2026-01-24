#PITH:1.2
#RULE:task-priority|stand:2026-01

# Task Priority Default Rule

This rule prevents Claude from labeling required tasks as "optional" or "enhancement".

## Status Definitions

| Symbol | Status | Meaning |
|--------|--------|---------|
| `·` | pending | **REQUIRED** - must be implemented |
| `►` | in_progress | Currently being worked on |
| `✓` | done | Completed |
| `~` | parked | Deliberately deferred (optional) |
| `§` | archived | Deliberately not implementing |

## Critical Rules

!!default_required:All pending tasks (·) are REQUIRED by default
  |violation:Calling a · task "optional"|"enhancement"|"nice-to-have"=Trust breach
  |exception:Only ~ (parked) or § (archived) are optional
  |warning_sign:Thought "this isn't that important" for a · task=STOP

!!never_deprioritize:NEVER downgrade the importance of a pending task
  |violation:Presenting · tasks as "enhancements" or "future work"=User loses trust
  |correct_behavior:All · tasks must be done|Only ~ or § can be deferred
  |action:If task should be optional→change status to ~ FIRST→then communicate

!communication:When discussing tasks
  |required:Pending (·) tasks are "tasks to implement" or "next steps"
  |forbidden:"Optional"|"Enhancement"|"Nice-to-have"|"Could do later"|"Low priority"
  |exception:Only for ~ or § tasks

## When to Use Each Status

pending(·):Task needs to be done|No discussion about priority|Just do it
parked(~):User explicitly said "not now"|Blocked by external factors|Consciously deferred
archived(§):User explicitly said "won't do"|Superseded by other approach|Consciously rejected

## Escalation

If unsure whether a task is required:
1. Assume it IS required (· status)
2. Ask user: "Should I implement this now or park it (~) for later?"
3. NEVER decide on your own to call something optional
