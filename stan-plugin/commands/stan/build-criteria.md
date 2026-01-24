# /stan build-criteria

Build a new criteria interactively.

## Step 0: Check Existing Criteria (MANDATORY)

**Before creating anything, check what already exists!**

1. List all existing criteria:
   ```bash
   ls criteria/*.yaml
   ```

2. Ask user: "What should the new criteria check?"

3. Search for similar criteria:
   - Same prefix? (code-*, ui-*, text-*, etc.)
   - Similar topic? (testing, accessibility, formatting, etc.)

4. If similar exists, offer options:
   ```
   Found similar: code-quality.yaml

   Options:
   A) Extend existing → create code-quality-{extension}.yaml
   B) Add checks to existing → edit code-quality.yaml
   C) Create separate → new criteria (explain why different)
   ```

5. Only proceed with new criteria if:
   - No similar exists, OR
   - User explicitly wants separate criteria with good reason

## Extension Pattern

**Base + Extension architecture:**

```
code-quality.yaml              ← Base (language-agnostic)
  └── code-quality-python.yaml ← Extension (Python-specific)
  └── code-quality-rust.yaml   ← Extension (Rust-specific)

ui-is-accessible.yaml          ← Base (general a11y)
  └── ui-is-accessible-wcag-aaa.yaml ← Extension (stricter)
```

**When to create extension vs. new criteria:**

| Situation | Action |
|-----------|--------|
| Adds checks to existing topic | Extension: `{base}-{specific}.yaml` |
| Completely different topic | New criteria |
| Language/framework specific | Extension of language-agnostic base |
| Stricter version of existing | Extension: `{base}-strict.yaml` |

**Extension naming:** `{base-name}-{extension-name}.yaml`
- `code-quality-python.yaml` (extends code-quality)
- `ui-is-accessible-wcag-aaa.yaml` (extends ui-is-accessible)

## Naming Convention

**Flat structure, self-explanatory names.**

| Prefix | When to use |
|--------|-------------|
| (none) | Name alone is clear: `goal-is-smart`, `hypothesis-is-testable` |
| `code-` | Technical code quality: `code-quality`, `code-quality-python` |
| `ui-` | Visual interface: `ui-is-responsive`, `ui-verified-in-browser` |
| `ux-` | User experience: `ux-flow-is-intuitive` |
| `text-` | Text quality: `text-quality` |
| `meta-` | STAN framework itself: `meta-criteria-valid` |
| `task-` | Workflow/tasks: `task-fits-iteration` |

**Filename pattern:** `{prefix-if-needed}{what-is-checked}.yaml`

## Instructions

1. **Check existing criteria** (Step 0 above - MANDATORY!)

2. Collect criteria information:
   - **What does it check?**
   - **Is this an extension?** If yes, which base?
   - **Description:** One sentence

3. Build checks interactively:
   - For each check ask:
     - **ID:** Short identifier
     - **Question:** Yes/no answerable
     - **Required:** Must be met?
     - **Auto:** Automatically checkable? If yes: command?

4. Repeat until user says "done"

5. At the END: Identify templates
   - List existing templates
   - Ask: Which templates could benefit?
   - If selected: Offer to update

6. Create criteria file:
   ```yaml
   name: {Name}
   description: {Description}. Use WITH {base} for full coverage.  # if extension

   checks:
     - id: {id}
       question: "{Question}"
       required: {true/false}
       auto: {true/false}
       command: "{command}"  # only when auto=true
   ```

7. Save to `criteria/{filename}.yaml`

8. Confirm:
   ```
   Criteria created: criteria/{filename}.yaml

   Type: {Base | Extension of {base}}
   Checks: {count}
   Auto-checks: {auto_count}

   Linked templates:
   - {template_1}
   ```

## Examples

| Need | Existing | Action | Result |
|------|----------|--------|--------|
| Python linting | `code-quality.yaml` | Extend | `code-quality-python.yaml` |
| WCAG AAA | `ui-is-accessible.yaml` | Extend | `ui-is-accessible-wcag-aaa.yaml` |
| German text rules | `text-quality.yaml` | Extend | `text-quality-german.yaml` |
| API security | (none) | New | `api-is-secure.yaml` |

## Important

- **Check existing FIRST** - avoid duplicates
- **Prefer extensions** - over creating similar new criteria
- **Flat structure** - no subfolders
- **Self-explanatory names** - reader understands without opening
- Questions must be yes/no answerable
- Auto commands must return exit 0 on success
