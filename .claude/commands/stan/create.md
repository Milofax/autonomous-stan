# /stan create

Start the CREATE phase (autonomous execution).

## Instructions

1. Check preconditions:
   - `stan.md` exists?
   - `.stan/tasks.jsonl` exists?
   - At least 1 ready task (use `get_ready_tasks()`)?
   - If no: Notify and STOP

2. Check current phase:
   - If PLAN: Switch to CREATE (normal)
   - If CREATE: Continue with next task
   - If DEFINE: **BLOCKED**
     ```
     Still in DEFINE!

     CREATE requires:
     1. Approved PRD
     2. At least 1 ready task

     First use /stan define and /stan plan
     ```

3. CREATE is AUTONOMOUS:
   - Work through tasks from JSONL
   - Use `get_ready_tasks()` to find next task
   - Respect dependencies (handled by ready check)
   - Run tests after each change
   - Commit after each completed task
   - Maintain activity log (see below)

4. Per task (JSONL-based):
   ```python
   from task_schema import get_ready_tasks, update_task
   from task_generator import regenerate_tasks_md

   # Get next ready task
   ready = get_ready_tasks()
   if not ready:
       # All done!
       break
   task = ready[0]

   # Mark as in progress
   update_task(task.id, status="in_progress")
   regenerate_tasks_md()

   # ... implement task ...

   # Mark as done
   update_task(task.id, status="done")
   regenerate_tasks_md()
   ```
   - **For UI stories:** Verify in browser (see Visual Verification)
   - Run relevant tests
   - If GREEN: Set task to `status: done`
   - Append to activity log
   - Commit with reference to task ID (t-xxxx)

5. On problems:
   - Observe 3-strikes rule
   - On fundamental problems: Reconciliation to DEFINE
   - Save pending learnings before commit

6. After all tasks:
   ```
   <promise>COMPLETE</promise>

   CREATE phase completed!

   Completed tasks: {done_count}
   Commits: {commit_count}
   Learnings: {learning_count}

   Recommendation: Review learnings with /stan learnings
   ```

## Activity Log

Maintain `docs/activity.md` during CREATE phase:

```markdown
## [Date] - [Task ID]
- What was implemented
- Files changed
- **Learnings:**
  - Patterns discovered
  - Gotchas encountered
  - Useful context
---
```

**Rules:**
- APPEND only (never replace previous entries)
- Log AFTER each completed task
- Include learnings for future iterations

## Visual Verification (UI Stories)

For any task that changes UI, you MUST:

1. Verify the change works in a browser
2. Check the browser console for errors
3. (Optional) Take a screenshot as evidence

A frontend task is NOT complete until browser verification passes.

**Acceptance criteria pattern for UI stories:**
```
- [ ] ...specific criteria...
- [ ] Typecheck passes
- [ ] Verify in browser
```

## Story Size Guidance

Each task should be completable in ONE iteration. If a task is too large:

**Signs it's too big:**
- Cannot describe in 2-3 sentences
- Touches more than 5 files
- Mixes database + backend + UI changes

**Split large tasks:**
1. Database/schema changes first
2. Backend logic second
3. UI components last

## Completion Signal

When ALL tasks are complete, output:
```
<promise>COMPLETE</promise>
```

This signals to autonomous loops that the work is done.

## Execution Loop

CREATE phase follows this execution loop:

```
LOOP:
  1. Get next ready task (pending + no blockers)
  2. If no task: COMPLETE → Exit loop
  3. Reset iteration counter for this task
  4. INNER LOOP:
     a. Attempt task implementation
     b. Run tests
     c. If SUCCESS: Mark done, commit, go to step 1
     d. If FAIL: Increment iteration counter
     e. If iterations >= max_iterations: STOP + perspective shift
     f. Else: Retry with different approach
```

### Max Iterations Reached

When you hit max_iterations (default 10), you MUST:

1. **STOP** - Do not retry the same approach
2. **Reflect** - What pattern is repeating?
3. **Perspective Shift** - Use `/stan think` to try a different approach:
   - `root-cause-analysis` - Why is this failing?
   - `perspective-shift` - How would someone else solve this?
   - `structured-problem-solving` - Break it down differently
4. **Ask for help** - If stuck after perspective shift, ask the user

**Never** brute-force past max iterations. The limit exists to prevent spinning.

## Task Priority Rule

**IMPORTANT:** All pending tasks (`·`) are REQUIRED unless explicitly marked as:
- `~` (parked) - Deliberately deferred
- `§` (archived) - Not implementing

Never skip, deprioritize, or label required tasks as "optional" or "enhancement".
Execute them in dependency order.

## Important

- CREATE is AUTONOMOUS - minimal user interaction
- Tests MUST be green before commit
- Learnings MUST be saved before commit
- UI tasks MUST be visually verified
- On max iterations: STOP and use perspective shift techniques
- On 3-strikes: STOP and reflect
- Output `<promise>COMPLETE</promise>` when done
