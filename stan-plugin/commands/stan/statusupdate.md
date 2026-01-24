# /stan statusupdate

Show current STAN status and allow manual changes.

## Instructions

1. Check if `stan.md` exists
   - If no: Point to `/stan init`

2. Show current status:
   ```
   STAN Status
   ===========

   Project: {name}
   Phase: {phase}
   Current Task: {task}
   Last Updated: {date}

   Documents:
   - PRD: {prd_status}
   - Plan: {plan_status}

   Learnings:
   - Hot: {hot_count}
   - Recent: {recent_count}
   - Pending: {pending_count}

   Session:
   - Test History: {test_count} runs
   - Last Test: {last_test_status}
   ```

3. Ask for desired action:
   - `[1]` Change phase manually
   - `[2]` Set current task
   - `[3]` Show pending learnings
   - `[4]` No changes

4. On phase change:
   - Show warnings if significant (e.g., CREATE → DEFINE)
   - Confirmation required
   - Update stan.md

5. On task change:
   - List available tasks from plan.md
   - Update current task in stan.md

## Important

- Status is informative AND interactive
- Phase changes have consequences - communicate transparently
