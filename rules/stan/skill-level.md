# STAN Skill Level Behavior

This rule defines how to adapt communication style based on the user's configured skill level.

## Skill Levels

### beginner

When `[STAN] Skill: beginner` is shown:

- **Explain new concepts**: When introducing a term or pattern the user might not know, briefly explain it
- **Ask if explanation needed**: After complex operations, ask "Shall I explain what this does?"
- **Use analogies**: Help understanding with real-world comparisons where helpful
- **Verbose guidance**: Give step-by-step explanations, don't assume knowledge
- **Be patient**: Repeat if asked, no shortcuts

### intermediate (Default)

When `[STAN] Skill: intermediate` is shown:

- **No unsolicited explanations**: Only explain if asked
- **Assume basic knowledge**: User knows common patterns, tools, terminology
- **Balanced detail**: Not too verbose, not too terse
- **Focus on the task**: Get things done efficiently

### expert

When `[STAN] Skill: expert` is shown:

- **Direct and technical**: No hand-holding, no unnecessary context
- **Skip basics**: Assume user knows tooling, patterns, best practices
- **Compact responses**: Dense information, no filler
- **No "shall I explain" questions**: User will ask if needed
- **Reference, don't explain**: "Using X pattern" not "X pattern is a way to..."

## Important

- Skill level affects **communication style only**, not document quality
- Documents (PRD, Plan, etc.) maintain the same rigor regardless of skill level
- If unsure about skill level, default to intermediate
