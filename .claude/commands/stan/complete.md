# /stan complete

Complete a feature and archive all related documents as a package.

## Instructions

### 1. Confirm Completion

Before completing, ask for confirmation:

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

### 6. Completion Message

```
Feature completed!

Archived to: .stan/completed/
- prd-{feature-slug}.md
- plan-{feature-slug}.md
- tasks-{feature-slug}.md

Fresh files created in docs/ for next feature.

Ready for: /stan define (new feature)
```

## Trigger Words

This command can be triggered by user saying:
- "fertig" / "das ist fertig"
- "passt" / "passt alles"
- "abgeschlossen"
- "finished" / "done" / "complete"

When these words are detected after CREATE phase is done, suggest running `/stan complete`.

## Important

- **NEVER** complete without explicit confirmation
- Feature name in filename, NOT date (date is only in frontmatter)
- All 3 documents move together as a package
- Fresh files are created from templates for next feature
- This keeps `docs/` clean - only current feature visible
- Learnings promotion to Graphiti is OPTIONAL

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
