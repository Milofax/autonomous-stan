# Evaluator Hook Experiment - Findings

**Date:** 2026-01-24
**Status:** Research Complete, Manual Test Required

## Research Summary

### Key Discovery: Prompt Hooks ARE the Solution

Claude Code supports `type: prompt` hooks that use an LLM for evaluation. This is EXACTLY what we need for independent evaluation.

### Hook Types and Output Formats

| Hook Event | Output Format | Key Field |
|------------|---------------|-----------|
| PostToolUse | `{continue, systemMessage}` | `systemMessage` for feedback |
| Stop | `{decision, reason, systemMessage}` | `decision: block` prevents completion |
| PreToolUse | `{hookSpecificOutput, systemMessage}` | `permissionDecision: deny` blocks tool |

### Configuration Format

**IMPORTANT:** `.claude/settings.json` uses DIFFERENT format than plugin `hooks.json`:

```json
// settings.json - NO "hooks" wrapper
{
  "PostToolUse": [...],
  "Stop": [...]
}

// hooks.json - HAS "hooks" wrapper
{
  "description": "...",
  "hooks": {
    "PostToolUse": [...],
    "Stop": [...]
  }
}
```

## Architecture for STAN Evaluator

```
┌─────────────────────────────────────────────────────────┐
│                    Main Agent                            │
│  (Does the work: edits files, checks checkboxes)        │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│               PostToolUse Hook (Edit)                    │
│  type: prompt                                            │
│  "Evaluate if this edit properly meets criteria..."     │
│                                                          │
│  Output: {continue: true, systemMessage: "[EVALUATOR]   │
│           Criteria X not actually met because..."}      │
└──────────────────────────┬──────────────────────────────┘
                           │ systemMessage
                           ▼
┌─────────────────────────────────────────────────────────┐
│                Main Agent (continues)                    │
│  Receives feedback, can iterate                         │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼ (tries to stop)
┌─────────────────────────────────────────────────────────┐
│                    Stop Hook                             │
│  type: prompt                                            │
│  "Review transcript at $TRANSCRIPT_PATH. Are ALL        │
│   criteria genuinely met?"                              │
│                                                          │
│  Output: {decision: "block", reason: "...",             │
│           systemMessage: "[EVALUATOR] Fix these..."}    │
└─────────────────────────────────────────────────────────┘
```

## Configuration Files in This Directory

| File | Format | Purpose |
|------|--------|---------|
| `hooks.json` | Plugin format (has wrapper) | For plugin `hooks/hooks.json` |
| `settings.json.example` | Settings format (no wrapper) | For `.claude/settings.json` |

**IMPORTANT:** The format differs between these two locations!

## Test Setup

A complete test project is available at `/tmp/evaluator-hook-test/` with:
- `.claude/settings.json` - Correct format (no wrapper)
- `acceptance-criteria.md` - Test document with checkboxes
- `CLAUDE.md` - Project instructions
- `README.md` - Full test instructions

### Manual Test Instructions

```bash
# Navigate to test project
cd /tmp/evaluator-hook-test

# Start Claude Code session
claude

# Test 1: Superficial Checking
# Say: "Check off all criteria in acceptance-criteria.md"
# Expected: PostToolUse warns, Stop blocks

# Test 2: Legitimate Work
# Say: "Implement the add function properly with tests, then check criteria"
# Expected: Stop approves
```

## Open Questions (Require Manual Testing)

1. **Does the prompt hook actually get called?**
   - Theory: Yes, for any Edit tool call
   - Needs verification in real session

2. **Is the systemMessage visible to main agent?**
   - Theory: Yes, as system message in transcript
   - Needs verification

3. **Can Stop hook actually block completion?**
   - Theory: Yes, with `decision: "block"`
   - Needs verification

4. **What's in $TRANSCRIPT_PATH?**
   - Theory: JSONL file with full conversation
   - Needs verification of format

## Next Step

**MANUAL TEST REQUIRED:**

```bash
cd /tmp/evaluator-hook-test
claude
# Then: "Check off all criteria in acceptance-criteria.md without implementing anything"
# Observe: Does evaluator detect superficial checking?
```

## Implications for STAN Framework

If hooks work as documented:

1. **No Subagent needed** - Prompt hooks ARE the evaluator subagent
2. **Built-in mechanism** - Claude Code already supports this
3. **Integration point** - stan-gate.py could be converted to prompt hook
4. **Simpler architecture** - No need for Task tool spawning

### Proposed STAN Integration

```json
{
  "PostToolUse": [
    {
      "matcher": "Edit",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "STAN EVALUATOR: Check if acceptance criteria are genuinely met..."
        }
      ]
    }
  ],
  "Stop": [
    {
      "matcher": "*",
      "hooks": [
        {
          "type": "prompt",
          "prompt": "STAN GATE: Review $TRANSCRIPT_PATH. Block if criteria incomplete..."
        }
      ]
    }
  ]
}
```

This would replace/augment the current Python-based hooks with LLM-based evaluation.
