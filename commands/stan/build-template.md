# /stan build-template

Build a new template interactively.

## Step 0: Check Existing Templates (MANDATORY)

**Before creating anything, check what already exists!**

1. List all existing templates:
   ```bash
   ls templates/*.template
   ```

2. Ask user: "What should the new template be used for?"

3. Search for similar templates:
   - Same purpose? (PRD, plan, spec, etc.)
   - Similar structure?

4. If similar exists, offer options:
   ```
   Found similar: prd.md.template

   Options:
   A) Create variant → prd-lightweight.md.template
   B) Extend existing → add sections to prd.md.template
   C) Create separate → new template (explain why different)
   ```

5. Only proceed with new template if:
   - No similar exists, OR
   - User explicitly wants separate with good reason

## Variant Pattern

**Base + Variant architecture:**

```
prd.md.template                    ← Standard (full PRD)
  └── prd-lightweight.md.template  ← Variant (small features)
  └── prd-enterprise.md.template   ← Variant (large projects)

plan.md.template                   ← Standard (implementation plan)
  └── plan-spike.md.template       ← Variant (research/exploration)
  └── plan-migration.md.template   ← Variant (data migrations)
```

**When to create variant vs. new template:**

| Situation | Action |
|-----------|--------|
| Same purpose, different scope | Variant: `{base}-{scope}.md.template` |
| Same purpose, different audience | Variant: `{base}-{audience}.md.template` |
| Completely different purpose | New template |
| Subset of existing sections | Variant: `{base}-lightweight.md.template` |

**Variant naming:** `{base-name}-{variant-name}.md.template`
- `prd-lightweight.md.template` (less sections than prd)
- `plan-spike.md.template` (research-focused plan)

## Instructions

1. **Check existing templates** (Step 0 above - MANDATORY!)

2. Collect template information:
   - **Name:** What should it be called?
   - **Is this a variant?** If yes, of which base?
   - **Type:** manifest, prd, plan, custom
   - **Description:** What is it for?

3. Build template content interactively:
   - Ask for desired sections
   - For each section:
     - Heading
     - Description of what goes in it
     - Example structure

4. At the END: Link criteria
   - List available criteria from `criteria/`
   - Show: Name + Description
   - MultiSelect: Which criteria apply?
   - Note: Variants typically use same criteria as base (maybe fewer)

5. Create template file:
   ```yaml
   ---
   type: {type}
   status: draft
   created: {{date}}
   updated: {{date}}
   criteria:
     - {selected_criteria_1}
     - {selected_criteria_2}
   ---

   # {Name}

   {Sections}
   ```

6. Save to `templates/{name}.md.template`

7. Confirm:
   ```
   Template created: templates/{name}.md.template

   Type: {Base | Variant of {base}}
   Sections: {count}

   Linked criteria:
   - {criteria_1}
   - {criteria_2}
   ```

## Examples

| Need | Existing | Action | Result |
|------|----------|--------|--------|
| Quick PRD for small feature | `prd.md.template` | Variant | `prd-lightweight.md.template` |
| Research task plan | `plan.md.template` | Variant | `plan-spike.md.template` |
| API specification | (none) | New | `api-spec.md.template` |
| Style guide | (none) | New | `style-guide.md.template` |

## Important

- **Check existing FIRST** - avoid duplicates
- **Prefer variants** - over creating similar new templates
- Template MUST have frontmatter with `type` and `criteria`
- Criteria linking at the END, not at the beginning
- Descriptions in sections, not prompts
- Variants inherit criteria sensibly (same or subset)
