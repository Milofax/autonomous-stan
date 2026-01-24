# /stan plan

Start or continue the PLAN phase.

## Instructions

1. Check preconditions:
   - `stan.md` exists?
   - PRD `status: approved`?
   - If no: Notify and STOP

2. Check current phase:
   - If DEFINE: Switch to PLAN (normal)
   - If PLAN: Continue
   - If CREATE: **Push back!**
     ```
     Currently in CREATE phase!

     Going back to PLAN means:
     - Pausing implementation
     - Potentially defining new tasks

     Reason for going back?
     ```

3. If in PLAN phase:
   - Check if plan exists (`docs/plan.md`)
   - If no: Derive plan from PRD
   - If yes: Check plan status

4. Plan creation:
   - Read PRD and identify tasks
   - **Apply Story Size Rule** (see below)
   - Create tasks with:
     - ID (T-001, T-002, ...)
     - Description (2-3 sentences max)
     - Dependencies
     - Affected files (max 5 per task)
     - Acceptance criteria
   - For UI tasks: Add "Verify in browser" to criteria
   - Create dependency graph
   - Identify parallelizable tasks

5. After plan creation:
   - Run criteria checks
   - If all required=true are met: Set at least 1 task to `status: ready`

6. When tasks are ready:
   ```
   Plan ready!

   Tasks: {count}
   Parallelizable: {parallel_count}

   Next step: /stan create
   ```

## Story Size Rule

**Each task must be completable in ONE iteration (one context window).**

### Right-sized tasks:
- Add a database column and migration
- Add a UI component to an existing page
- Update a server action with new logic
- Add a filter dropdown to a list

### Too big (split these):
- "Build the entire dashboard" → Split into: schema, queries, UI components, filters
- "Add authentication" → Split into: schema, middleware, login UI, session handling
- "Refactor the API" → Split into one task per endpoint

**Rule of thumb:** If you cannot describe the change in 2-3 sentences, it is too big.

### Task Ordering

Tasks must be ordered by dependency:
1. Schema/database changes (migrations)
2. Server actions / backend logic
3. UI components that use the backend
4. Dashboard/summary views that aggregate data

## Important

- Tasks should be concrete and actionable
- Dependencies MUST be complete
- Each task must fit in one iteration
- For UI tasks, include "Verify in browser" in criteria
- Parallelization only where SAFE
