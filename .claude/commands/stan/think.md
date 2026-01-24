# /stan think

Invoke a thinking technique by purpose.

## Instructions

### Without Argument: Show all Purposes

When `/stan think` is called without argument:

```
What kind of thinking do you need right now?

1. **Root Cause Analysis** - Why did this happen?
2. **Ideation** - What possibilities are there?
3. **Perspective Shift** - How do others see this?
4. **Structured Problem Solving** - How do I proceed systematically?
5. **Code Review** - Is the code good?
6. **Big Picture** - What is the big picture?
7. **Self Reflection** - What have I learned?
8. **Teamwork** - How do we work together?
9. **Decision Making** - Which option is the best?

Choose a purpose: `/stan think <number or name>`
```

### With Purpose Argument: Show Techniques

When `/stan think root-cause-analysis` or `/stan think 1`:

1. Load the purpose from `techniques/purposes/{id}.yaml`
2. Show:
   - Name and core question
   - When is this purpose relevant? (triggers)
   - Available techniques with short description
   - **Recommendation** with reasoning

```
## Root Cause Analysis

**Core Question:** Why did this happen? What is the root of the problem?

### When Relevant?
- Error occurs repeatedly
- Obvious solution didn't help
- Symptom vs. cause unclear

### Available Techniques
1. **Five Whys** - Get to root cause through repeated questioning
2. **Fishbone Diagram** - Visually categorize causes
3. **After Action Review** - Structured reflection after event
4. **Socratic Questioning** - Uncover assumptions through questions

### My Recommendation: Five Whys
Quick, requires no tools, works solo.

Should I apply the technique? (yes/no or technique name)
```

### With Technique Argument: Show Details and Offer Application

When user says "yes" or names a technique:

1. Load the technique from `techniques/{id}.yaml`
2. Show:
   - Name, description, source
   - **Steps** (numbered)
   - When to use / When NOT to use
   - Tips
   - Example (if available)

3. **User consent before application:**
   ```
   Would you like to apply this technique to your problem now?

   If yes, briefly describe your problem/topic.
   ```

4. On consent: Walk through the technique step by step

### Apply Technique

During application:
- Go through each step individually
- Wait for user input where needed
- Document the results
- At the end: Summary + next steps

**Example Five Whys:**
```
Step 1: Clearly formulate the problem
What is the problem we want to analyze?

[User responds]

Step 2: First Why
Why did this happen?
→ [User answer or work out together]

Step 3: Second Why
Why did THAT happen?
→ ...

[Repeat until root cause found]

---
## Summary

**Problem:** [original problem]
**Root Cause:** [identified cause]
**Next Step:** [recommendation for fix]
```

## File Paths

- Purposes: `techniques/purposes/*.yaml`
- Techniques: `techniques/*.yaml`
- Schema: `techniques/schema.yaml`
- Loader: `.claude/hooks/stan/lib/techniques.py`

## Important

- **User consent** before technique application
- Technique is **recommendation**, user decides
- On wrong technique choice: Suggest alternatives
- Results can be saved as **learning**

## Mapping Purpose → ID

| Number | Name | ID |
|--------|------|-----|
| 1 | Root Cause Analysis | root-cause-analysis |
| 2 | Ideation | ideation |
| 3 | Perspective Shift | perspective-shift |
| 4 | Structured Problem Solving | structured-problem-solving |
| 5 | Code Review | code-review |
| 6 | Big Picture | big-picture |
| 7 | Self Reflection | self-reflection |
| 8 | Teamwork | teamwork |
| 9 | Decision Making | decision-making |
