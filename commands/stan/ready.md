# /stan ready

Show all tasks that are ready to work on (no open blockers).

## Arguments

- `--phase <phase>` - Optional filter by phase (define, plan, create)

## Instructions

1. Check if `.stan/tasks.jsonl` exists:
   - If no:
     ```
     [STAN] No task file found.

     The file .stan/tasks.jsonl does not exist.

     Use /stan plan to generate tasks from your plan.
     ```
     STOP

2. Load tasks using `task_schema.py`:
   - Use `load_tasks()` to get all tasks
   - Use `get_ready_tasks(phase)` to filter ready tasks
   - Ready = status `pending` AND all dependencies are `done`

3. Parse `--phase` argument if provided:
   - Valid phases: define, plan, create
   - If invalid phase:
     ```
     [STAN] Invalid phase: {phase}

     Valid phases: define, plan, create
     ```
     STOP

4. Get ready tasks:
   - If `--phase` provided: `get_ready_tasks(phase="{phase}")`
   - Otherwise: `get_ready_tasks()`

5. Display results:

   **If ready tasks exist:**
   ```
   [STAN] Ready Tasks ({count} task(s)):

     {id}  {subject}  [{phase}]
     {id}  {subject}  [{phase}]
     ...

   Use /stan create to start working on these tasks.
   ```

   **If no ready tasks:**
   ```
   [STAN] No Ready Tasks

   All tasks are either:
   - Done (completed)
   - Blocked (waiting on dependencies)
   - In progress

   Use /stan statusupdate to see current project status.
   ```

   **If phase filter returned no results but tasks exist:**
   ```
   [STAN] No Ready Tasks in [{phase}] phase

   Ready tasks in other phases: {other_count}

   Try /stan ready without --phase filter.
   ```

## Output Format

Task list format (aligned columns):
```
  {id}  {subject}  [{phase}]
```

- ID: 6 chars fixed width (e.g., `t-a1b2`)
- Subject: variable width
- Phase: in square brackets

Example:
```
[STAN] Ready Tasks (3 tasks):

  t-a1b2  Setup database schema     [plan]
  t-c3d4  Create API routes         [create]
  t-e5f6  Write integration tests   [create]

Use /stan create to start working on these tasks.
```

## Important

- This skill is read-only, changes nothing
- Ready tasks are shown in order of creation (as stored in JSONL)
- Blocked tasks are NOT shown (use /stan statusupdate for full view)
