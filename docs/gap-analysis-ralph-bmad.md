# Gap Analysis: STAN vs. Ralph & BMAD

**Date:** 2026-01-22
**Status:** T-027 (Ralph) + T-028 (BMAD) Complete

---

## Executive Summary

STAN Framework has strong foundations but lacks some tactical patterns from Ralph and BMAD that would improve autonomous execution reliability.

**Priority Gaps:**
1. Visual verification for UI stories (HIGH)
2. Story size guidance/enforcement (HIGH)
3. Activity/session logging (MEDIUM)
4. Completion signal pattern (MEDIUM)

---

## Ralph Best Practices Analysis

### Source Documents
- `vendor/ralph/CLAUDE.md` - Claude Code instructions
- `vendor/ralph/prompt.md` - AMP instructions
- `vendor/ralph/skills/ralph/SKILL.md` - PRD converter
- https://github.com/coleam00/ralph-loop-quickstart
- https://github.com/JeredBlu/guides/blob/main/Ralph_Wiggum_Guide.md

### Key Patterns from Ralph

| Pattern | Description | STAN Status |
|---------|-------------|-------------|
| **Fresh Context Per Iteration** | Each iteration runs in fresh context window | ⚠️ Not enforced - STAN relies on context compaction |
| **Progress.txt Codebase Patterns** | Consolidate learnings at TOP of file | ✓ STAN has tiered learnings (recent/hot/archive) |
| **JSON passes: true/false** | Simple task completion tracking | ✓ STAN has Acceptance Criteria checkboxes |
| **Story Size Rule** | "Must be completable in ONE iteration" | ⚠️ Missing - no size enforcement |
| **Story Ordering** | Database → Backend → UI | ✓ STAN has dependencies |
| **Verifiable Acceptance Criteria** | No vague criteria like "works correctly" | ✓ STAN has criteria-quality checks |
| **Visual Verification** | "Verify in browser" for UI stories | ❌ Missing - critical gap |
| **activity.md Session Log** | Records what was accomplished | ❌ Missing - only learnings |
| **Screenshots Folder** | Visual verification evidence | ❌ Missing |
| **Archive Previous Runs** | Archive old PRD before new feature | ⚠️ Missing - no explicit archiving |
| **Sandboxing** | Isolated environment for long runs | ✓ Worktree enforcement exists |
| **Max Iterations** | Prevent runaway costs | ⚠️ Only 3-strikes for errors |
| **`<promise>COMPLETE</promise>`** | Clear completion signal | ❌ Missing |

### Ralph's Story Size Rule (Critical)

> **Each story must be completable in ONE iteration (one context window).**

Ralph splits large stories:
- ❌ "Build the entire dashboard"
- ✓ Split into: schema, queries, UI components, filters

**Rule of thumb:** If you cannot describe the change in 2-3 sentences, it's too big.

### Ralph's Visual Verification Pattern

For **every** UI story, Ralph requires:
```
**Acceptance Criteria:**
- [ ] ...specific criteria...
- [ ] Typecheck passes
- [ ] Verify in browser using dev-browser skill
```

---

## BMAD Best Practices Analysis

### Source Documents
- `vendor/BMAD-METHOD/README.md`
- `vendor/BMAD-METHOD/docs/explanation/architecture/four-phases.md`
- `vendor/BMAD-METHOD/docs/how-to/workflows/`

### Key Patterns from BMAD

| Pattern | Description | STAN Status |
|---------|-------------|-------------|
| **Four Phases** | Analysis → Planning → Solutioning → Implementation | ✓ STAN: DEFINE → PLAN → CREATE |
| **Scale-Adaptive Levels (0-4)** | Adjusts planning depth to complexity | ⚠️ STAN: skill_level only (user, not project) |
| **Specialized Agents** | 12+ domain experts | ⚠️ STAN: single agent with techniques |
| **Tracks (Quick/BMad/Enterprise)** | 5 min / 15 min / 30 min workflows | ⚠️ Missing - no workflow scaling |
| **ADRs (Architecture Decision Records)** | Explicit technical decisions | ⚠️ PRD has Decisions Log, not full ADRs |
| **Implementation Readiness Gate** | Gate check before implementation | ⚠️ stan-gate checks quality, not readiness |
| **Story-Centric Workflow** | One story at a time | ✓ STAN: one task at a time |
| **Retrospective Workflow** | Continuous improvement | ✓ STAN: /stan think retrospective |
| **Brainstorming Techniques** | Creative problem solving | ✓ STAN: 21 techniques library |

### BMAD's Scale-Adaptive System

| Level | Planning Depth | When to Use |
|-------|----------------|-------------|
| 0 | None | Trivial fix |
| 1 | Minimal | Simple bug fix |
| 2 | Standard | Feature addition |
| 3 | Detailed | Complex feature |
| 4 | Comprehensive | Enterprise/compliance |

STAN has `skill_level` (beginner/intermediate/expert) but this adjusts **communication style**, not **planning depth** per project.

### BMAD's Three Tracks

| Track | Time to Story | Use Case |
|-------|---------------|----------|
| Quick Flow | ~5 min | Bug fixes, small features |
| BMad Method | ~15 min | Products, platforms |
| Enterprise | ~30 min | Compliance-heavy systems |

STAN currently has one workflow regardless of project complexity.

---

## What STAN Does Well

### Already Implemented ✓

1. **Tiered Learnings Storage** - recent/hot/archive with promotion/demotion
2. **PRD Template** - Hypothesis, Evidence, JTBD, MoSCoW, Feasibility
3. **LLM-as-Judge Criteria** - 11 evaluators with golden examples
4. **21 Thinking Techniques** - Organized by 9 purposes
5. **Quality Gates** - stan-gate hook enforcement
6. **Worktree Enforcement** - Git branch isolation
7. **3-Strikes Rule** - Error pattern detection
8. **Document Lifecycle** - draft → approved → in-progress → done → archived
9. **Config System** - User preferences, skill level, language settings

### STAN Unique Advantages

- **Criteria Packs** - Modular, reusable quality checks
- **Template-Criteria Linking** - Templates reference applicable criteria
- **Meta-Criteria** - Quality checks for criteria/templates themselves
- **Tiered Learnings with Heat Scoring** - Automatic promotion based on usage

---

## Gap Priority Assessment

### HIGH Priority (Do Now)

| Gap | Impact | Effort | Action |
|-----|--------|--------|--------|
| Visual Verification for UI Stories | Prevents UI bugs shipping | Low | Add criteria check + guidance |
| Story Size Enforcement | Prevents context overflow | Low | Add criteria check + guidance |

### MEDIUM Priority (Next Iteration)

| Gap | Impact | Effort | Action |
|-----|--------|--------|--------|
| Activity/Session Log | Better debugging, auditability | Medium | Add activity.md pattern |
| Completion Signal | Cleaner autonomous loops | Low | Document `<promise>COMPLETE</promise>` pattern |
| Project Complexity Levels | Better planning calibration | Medium | Add Level 0-4 alongside skill_level |

### LOW Priority (Nice to Have)

| Gap | Impact | Effort | Action |
|-----|--------|--------|--------|
| Screenshots Folder | Visual evidence | Low | Document pattern |
| Archive Mechanism | Cleaner project history | Medium | Add `/stan archive` command |
| Max Iterations Setting | Cost control | Low | Document in CREATE phase |
| Quick/Standard/Enterprise Tracks | Workflow scaling | High | Major framework change |

---

## Recommended Actions for T-030

### 1. Add Visual Verification Criteria (HIGH)

Create `criteria/code/visual-verification.yaml`:
```yaml
name: Visual Verification
description: Ensures UI changes are visually verified

checks:
  - id: browser-verification
    question: "Has the UI change been verified in a browser?"
    required: true  # For UI stories only

  - id: screenshot-taken
    question: "Is there a screenshot documenting the change?"
    required: false
```

Update `templates/prd.md.template` user stories section with guidance.

### 2. Add Story Size Criteria (HIGH)

Create `criteria/strategy/story-size.yaml`:
```yaml
name: Story Size
description: Ensures stories are right-sized for autonomous execution

checks:
  - id: one-iteration
    question: "Can this story be completed in one iteration/context window?"
    required: true

  - id: two-sentence-rule
    question: "Can the change be described in 2-3 sentences?"
    required: true

  - id: file-count
    question: "Does the story touch 5 or fewer files?"
    required: false
```

### 3. Document Activity Log Pattern (MEDIUM)

Add to `/stan create` instructions:
- Maintain `docs/activity.md` during CREATE phase
- Format: Date, Task, Changes, Learnings
- Append-only (never replace)

### 4. Document Completion Signal (MEDIUM)

Add to `/stan create` instructions:
- When ALL tasks have acceptance criteria met
- Output: `<promise>COMPLETE</promise>`
- This signals autonomous loop completion

---

## Metrics Comparison

| Framework | Templates | Criteria | Techniques | Phases |
|-----------|-----------|----------|------------|--------|
| **STAN** | 3 | 24+ | 21 | 3 (DEFINE/PLAN/CREATE) |
| **Ralph** | 1 (prd.json) | 0 (implicit) | 0 | 1 (loop) |
| **BMAD** | 50+ | N/A (workflows) | 12+ | 4 |

STAN sits between Ralph (minimal) and BMAD (comprehensive).

---

## Conclusion

STAN Framework is well-positioned but needs two immediate improvements:

1. **Visual Verification** - Prevent UI bugs from shipping
2. **Story Size Guidance** - Prevent context overflow in autonomous execution

These gaps can be closed with minimal effort (new criteria files + documentation updates) and will significantly improve autonomous execution reliability.
