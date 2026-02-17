# autonomous-stan (Development)

Autonomous workflow framework with modular thinking tools for Claude Code.

## Language Rules

- **Conversation:** German with the user
- **All files:** English (documentation, config, code, comments, commit messages)
- **Plugin name:** Always "autonomous-stan" (not "stan" alone)

## Mandatory

1. **Read the plan:** [docs/plan.md](docs/plan.md)
2. **Use tasks and keep status current:** [docs/tasks.md](docs/tasks.md)
3. **Parallelize where possible:** Tasks without file overlap can run in parallel

## CRITICAL: No STAN Hooks in This Project!

**NEVER** activate or install STAN hooks inside `autonomous-stan`!

- This project **develops** the autonomous-stan framework
- The hooks belong in the **autonomous-stan plugin** (installed into other projects)
- Here: development and testing only, no self-enforcement

**If you see STAN hooks active here → DEACTIVATE, don't use.**

Features are tested here via `/stan` slash commands, NOT via hooks.

## Repository Structure

```
autonomous-stan/
├── hooks/
│   ├── hooks.json                # Hook config (uses ${CLAUDE_PLUGIN_ROOT})
│   ├── autonomous-stan/          # Hook scripts (installed as plugin)
│   │   ├── stan_context.py       # UserPromptSubmit: phase/learnings/criteria injection
│   │   ├── stan_gate.py          # PreToolUse(Bash): phase enforcement
│   │   ├── git_guard.py          # PreToolUse(Bash): conventional commits + branch protection
│   │   ├── credential_guard.py   # PreToolUse(Bash): 905 secret patterns, 3-strikes
│   │   ├── research_guard.py     # PreToolUse(*): blocks decisions without prior research
│   │   ├── stan_track.py         # PostToolUse(Bash): test tracking, red→green detection
│   │   └── loop_breaker.py       # PostToolUse(Bash+Edit): edit→test loop detection
│   └── lib/                      # Shared hook utilities
├── stan/                         # Python package (importable library)
│   ├── hooks/                    # Hook implementations (mirrored)
│   └── lib/                      # Core library: config, criteria, session_state, etc.
├── commands/stan/                # Slash commands (/stan init, /stan plan, etc.)
│   ├── init.md, define.md, plan.md, create.md
│   ├── think.md, complete.md, ready.md
│   ├── healthcheck.md, statusupdate.md
│   └── build-criteria.md, build-template.md
├── criteria/                     # 23 YAML criteria files (quality checklists)
├── techniques/                   # 22 YAML thinking techniques
├── docs/                         # Plan, tasks, analysis docs
├── tests/                        # 583+ tests (pytest)
└── .claude-plugin/plugin.json    # Plugin manifest
```

## 8 Active Hooks

| # | Hook | Event | What it does |
|---|------|-------|-------------|
| 1 | **stan_context** | UserPromptSubmit | Injects current phase, learnings, active criteria |
| 2 | **stan_gate** | PreToolUse(Bash) | Phase enforcement: no build without plan |
| 3 | **git_guard** | PreToolUse(Bash) | Conventional Commits, branch protection |
| 4 | **credential_guard** | PreToolUse(Bash) | 905 secret patterns, 3-strikes escalation |
| 5 | **research_guard** | PreToolUse(*) | Blocks architecture decisions without research |
| 6 | **stan_track** | PostToolUse(Bash) | Test tracking, red→green detection |
| 7 | **loop_breaker** | PostToolUse(Bash+Edit) | Edit→test loop detection → escalation |
| 8 | **Evaluator** | PostToolUse(Edit) | Prompt-hook: independent quality check |
| 9 | **Final Gate** | Stop | Prompt-hook: completion verification |

## Hook Output Formats (CRITICAL)

Different hook events require different output formats. Mixing them causes **silent failure** — Claude Code ignores wrong formats without error.

```python
# PreToolUse → permissionDecision
{"hookSpecificOutput": {"permissionDecision": "allow"}}  # or "deny" or "ask"

# PostToolUse → continue
{"continue": True, "systemMessage": "..."}

# UserPromptSubmit → continue
{"continue": True, "systemMessage": "..."}
```

**Never use `continue` in PreToolUse or `permissionDecision` in PostToolUse.**

## Working Principles

- **Research first, build second** — research_guard enforces this
- **Techniques for problems** — use `/stan think` or pick a purpose
- **Criteria self-check** — "Would this pass my own criteria?"
- **Parallelize** — independent tasks in parallel, use subagents

## Single Source of Truth

**IGNORE** all plans in `~/.claude/plans/` or other Claude-internal directories.

The only valid sources for planning and tasks:
- `docs/plan.md` — The plan
- `docs/tasks.md` — The task list

These project files are ALWAYS more current than Claude-internal plans.

## Installation

```bash
claude plugin install github:Milofax/autonomous-stan
```

## Testing

```bash
cd /path/to/autonomous-stan
python3 -m pytest tests/ -v
```

All tests must pass. Currently 583+ tests, zero dependencies beyond Python stdlib.
