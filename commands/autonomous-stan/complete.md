# /stan complete

Complete a feature and archive all related documents as a package.

**"Land the Plane" Pattern:** This skill enforces mandatory completion steps including git push.

## Instructions

### 0. Pre-Completion Verification (MANDATORY)

Before anything else, verify all requirements are met:

1. **Load tasks from JSONL:**
   ```python
   from task_schema import load_tasks, get_tasks_by_status
   tasks = load_tasks()  # From .stan/tasks.jsonl
   ```

2. **Check all tasks are done:**
   ```python
   pending = get_tasks_by_status("pending")
   in_progress = get_tasks_by_status("in_progress")
   if pending or in_progress:
       # BLOCK completion
   ```

3. **If incomplete tasks exist:**
   ```
   [STAN] Cannot complete - incomplete tasks remain!

   In Progress: {count}
   Pending: {count}

   All tasks must be done before completing.
   Use /stan statusupdate to see remaining work.
   ```
   **STOP - Do not proceed.**

4. **Run quality checks:**
   - Tests must pass: `npm test` or `pytest`
   - Typecheck must pass (if configured)
   - Lint must pass (if configured)

5. **If quality checks fail:**
   ```
   [STAN] Cannot complete - quality checks failed!

   Failed: {check_name}
   Error: {error_message}

   Fix issues before completing.
   ```
   **STOP - Do not proceed.**

### 1. Confirm Completion

After verification passes, ask for confirmation:

```
You want to complete this feature?

Feature: {feature_name}
Status: All tasks done

This will:
1. Move PRD, Plan, and Tasks to .stan/completed/
2. Update status to "completed" in frontmatter
3. Create fresh files from templates for the next feature

Are you sure? (yes/no)
```

**Wait for explicit confirmation before proceeding.**

### 2. Create Completed Package

Move all 3 documents as a package:

```
docs/prd.md   → .stan/completed/prd-{feature-slug}.md
docs/plan.md  → .stan/completed/plan-{feature-slug}.md
docs/tasks.md → .stan/completed/tasks-{feature-slug}.md
```

**Feature slug:** Use feature name, lowercase, hyphens for spaces.
Example: "Dark Mode" → `prd-dark-mode.md`

**IMPORTANT:** Use feature name, NOT date! Date is only a metadata field.

### 3. Update Frontmatter

Add completion metadata to each moved document:

```yaml
---
type: prd
status: completed
completed_at: "2026-01-24"  # Current date
original_path: "docs/prd.md"
---
```

### 4. Create Fresh Files

Create new empty files from templates:

1. Copy `templates/prd.md.template` → `docs/prd.md`
2. Copy `templates/plan.md.template` → `docs/plan.md`
3. Create fresh `docs/tasks.md` with just the header

Replace template placeholders with current date.

### 5. Optional: Learnings Promotion

After completion, optionally promote learnings to Graphiti:

```
Feature completed!

You had {learning_count} learnings during this feature.

Options:
1. Promote all to Graphiti (group: main)
2. Promote project-specific to Graphiti (group: {project})
3. Skip - keep only in local storage
```

This is optional. Local learnings remain in `~/.stan/learnings/` either way.

### 6. Git Commit & Push (MANDATORY - "Land the Plane")

**This step is NOT optional.** Every completed feature must be pushed.

1. **Stage completion changes:**
   ```bash
   git add .stan/completed/
   git add docs/prd.md docs/plan.md docs/tasks.md
   git add .stan/tasks.jsonl
   ```

2. **Create completion commit:**
   ```bash
   git commit -m "feat: complete {feature-name}

   - All tasks done
   - Documents archived to .stan/completed/
   - Fresh files ready for next feature

   Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
   ```

3. **Push to remote (MANDATORY):**
   ```bash
   git push
   ```

4. **If push fails:**
   - Pull and merge/rebase first
   - Resolve conflicts if any
   - Push again
   - **Do NOT skip the push**

### 7. Final Completion Message

Only show this AFTER successful git push:

```
[STAN] Feature Complete!

Feature: {feature_name}
Status: All tasks done, pushed to remote

Archived to: .stan/completed/
- prd-{feature-slug}.md
- plan-{feature-slug}.md
- tasks-{feature-slug}.md

Git: Committed and pushed to {branch}

Fresh files created in docs/ for next feature.

Ready for: /stan define (new feature)
```

**If git push was not possible (e.g., no remote configured):**
```
[STAN] Feature Complete (local only)

Feature: {feature_name}
Status: All tasks done

WARNING: No remote configured - changes not pushed!
Remember to push manually when remote is set up.

Archived to: .stan/completed/
...
```

## Trigger Words

This command can be triggered by user saying:
- "fertig" / "das ist fertig"
- "passt" / "passt alles"
- "abgeschlossen"
- "finished" / "done" / "complete"

When these words are detected after CREATE phase is done, suggest running `/stan complete`.

## Important

**Pre-Completion (MANDATORY):**
- All tasks in `.stan/tasks.jsonl` MUST be status `done`
- Quality checks (tests, typecheck, lint) MUST pass
- **NEVER** skip pre-completion verification

**Confirmation:**
- **NEVER** complete without explicit user confirmation
- Feature name in filename, NOT date (date is only in frontmatter)
- All 3 documents move together as a package

**Git ("Land the Plane"):**
- Git push is **MANDATORY**, not optional
- If push fails, resolve and retry - do NOT skip
- Only show final completion message AFTER successful push
- Exception: No remote configured → warn user, complete locally

**Optional:**
- Learnings promotion to Graphiti is OPTIONAL
- Fresh files are created from templates for next feature
- This keeps `docs/` clean - only current feature visible

## Directory Structure

After completion:
```
.stan/
  completed/
    prd-dark-mode.md      # Completed feature
    plan-dark-mode.md
    tasks-dark-mode.md
  config.yaml             # Config (persists)
  session.json            # Session state

docs/
  prd.md                  # Fresh for next feature
  plan.md
  tasks.md
```
