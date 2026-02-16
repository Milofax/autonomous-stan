# Evaluator Hook Test Results

Experiments to understand Claude Code hook capabilities for STAN Evaluator architecture.

## Test 1: Prompt-Hook Transcript Access

**File:** `evaluator-hook-for-settings.json`

**Finding:** Prompt hooks (type: prompt) CANNOT read transcript content.

- `$TRANSCRIPT_PATH` is substituted as a string path only
- The LLM running the prompt has NO file access
- Cannot read files outside working directory
- Transcript is in `~/.claude/projects/` - unreachable

**Hook Response:**
```
Cannot read transcript file at the provided path. The $TRANSCRIPT_PATH variable
is not expanded to an actual file path... I do not have access to read files
outside the current working directory
```

## Test 2: Command-Hook Transcript Access

**File:** `test-transcript-access.py`

**Finding:** Command hooks (type: command) CAN read transcript and any files.

- Python script receives `transcript_path` via stdin JSON
- Full file system access
- Successfully read 16,628 lines from transcript

**Hook Response:**
```
[TRANSCRIPT ACCESS TEST]
Path: /Users/mathias/.claude/projects/-Volumes-DATEN-Coding-autonomous-stan/0ae28b96-d73d-41a2-996c-e7204d68cd64.jsonl
Status: READ SUCCESS - 16628 total lines
Last lines preview: 5 lines captured
Hook input keys: ['session_id', 'transcript_path', 'cwd', 'permission_mode',
                  'hook_event_name', 'tool_name', 'tool_input', 'tool_response', 'tool_use_id']
```

## stdin JSON Structure for Command Hooks

```json
{
  "session_id": "...",
  "transcript_path": "/Users/.../.claude/projects/.../session.jsonl",
  "cwd": "/current/working/directory",
  "permission_mode": "...",
  "hook_event_name": "PostToolUse",
  "tool_name": "Edit",
  "tool_input": { ... },
  "tool_response": { ... },
  "tool_use_id": "..."
}
```

## Implications for STAN Evaluator

1. **Generic Prompt Hook:** Can only evaluate based on `$TOOL_INPUT.*` variables
   - Good for: Catching superficial checkbox edits, obvious issues
   - Limited: Cannot access external criteria files

2. **Criteria-Aware Command Hook:** Can read any files
   - Read `stan.md` / task criteria
   - Read transcript for context
   - Must call LLM API itself for semantic evaluation
   - More complex but full capability

## Test Files

| File | Type | Purpose |
|------|------|---------|
| `test-transcript-access.py` | Command Hook | Proves transcript file access works |
| `evaluator-hook-for-settings.json` | Config | Working prompt hook example |
| `working-evaluator-hook.json` | Documentation | Documents prompt hook behavior |
| `test-criteria.md` | Test Data | File with checkboxes to test evaluation |

## Test 3: Subagent-Based Evaluation (SUCCESS!)

**File:** `stan-evaluate-subagent.py`

**Finding:** Subagent via Task tool provides independent evaluation WITHOUT API token.

**Architecture:**
```
Hook (PostToolUse - Edit)
│
├─ Detects Edit
├─ Reads criteria from stan.md
├─ Returns systemMessage: "Spawn evaluator subagent"
│
▼
Main Agent spawns:
Task(subagent_type="Explore", model="haiku", prompt="Evaluate...")
│
▼
Subagent (Haiku, separate context) evaluates independently
```

**Test Result:**
- Made superficial edit: Checked "No TODO comments" while TODO exists in code
- Subagent correctly returned FAIL
- Subagent identified: "This appears to be exactly the kind of self-serving bias the evaluation task is designed to catch"

**Why This Works:**
1. Subagent has separate context (not "committed" to the edit)
2. Subagent is skeptical by prompt design
3. No API token needed - uses Claude Code subscription
4. Independent evaluation without self-serving bias

## Architecture Decision

**Recommended approach for STAN Evaluator:**

| Layer | Method | When |
|-------|--------|------|
| Regelbasiert | Command Hook | Automatisierbare Criteria (tests, grep) |
| Semantisch | Subagent via Task | Criteria requiring interpretation |

## Date

2026-01-24/25
