# /stan define

Start or continue the DEFINE phase.

## Instructions

1. Check if `stan.md` exists
   - If no: Point to `/stan init`
   - If yes: Continue

2. Check current phase in `stan.md`
   - If already DEFINE: Continue
   - If PLAN or CREATE: **Push back!**
     ```
     Currently in phase: {phase}

     Going back to DEFINE means:
     - Fundamental change to scope
     - Previous planning/work may become obsolete

     Are you sure? (yes/no)
     ```

3. If in DEFINE phase:
   - Check if PRD exists (`docs/prd.md`)
   - If no: Create PRD interactively with template
   - If yes: Check PRD status and continue if needed

4. PRD Workflow:
   - Recognize maturity of user input:
     - Vague idea → Interview mode (ask questions)
     - Clear concept → Structure PRD
     - Complete PRD → Validate against criteria

5. After PRD creation:
   - Run criteria checks (`prd.md` has criteria in frontmatter)
   - Show check results
   - If all required=true are met: Set PRD to `status: approved`

6. When PRD is approved:
   ```
   PRD approved!

   Next step: /stan plan
   ```

## Important

- DEFINE is interactive, not autonomous
- User input is king - structure it, don't invent it
- When unclear: ASK, don't assume
