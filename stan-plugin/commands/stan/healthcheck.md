# /stan healthcheck

Check consistency of the STAN project.

## Instructions

1. Check project structure:
   - [ ] `stan.md` exists
   - [ ] `docs/` directory exists
   - [ ] Templates available

2. Check document consistency:
   - [ ] PRD has valid frontmatter
   - [ ] PRD criteria are resolvable
   - [ ] Plan has valid frontmatter
   - [ ] Plan criteria are resolvable

3. Check template-criteria linking:
   - For each template:
     - Read frontmatter
     - Check if all criteria in `criteria:` list exist
     - Report missing criteria

4. Check open reviews:
   - Pending learnings?
   - Tasks without acceptance criteria?
   - PRD without status?

5. Show result:
   ```
   STAN Health Check
   =================

   Structure: ✓ OK / ✗ Problem
   Documents: ✓ OK / ✗ Problem
   Templates: ✓ OK / ✗ Problem
   Reviews: ✓ OK / ✗ {count} open

   Details:
   {problems}

   Recommendations:
   {recommendations}
   ```

## Important

- Healthcheck is purely informational, changes nothing
- Show concrete solution suggestions for problems
