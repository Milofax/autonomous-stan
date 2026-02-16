# /stan init

Initialize a STAN project in the current directory.

## Instructions

### 1. Create .stan/ Directory Structure

First, create the `.stan/` directory structure:

1. Create `.stan/` directory
2. Create empty `.stan/tasks.jsonl` file
3. Create `.stan/completed/` directory for archived features
4. Verify `.gitignore` contains `.stan/session.json` (session state should not be committed)

**Note:** The `.stan/` directory should already be in `.gitignore` for the entire framework. Only `session.json` specifically needs to be gitignored within a project.

Display message:
```
[STAN] Initialized .stan/ directory structure:
  - .stan/tasks.jsonl (task storage)
  - .stan/completed/ (for completed features)
```

### 2. Check for Existing Project

Check if a `stan.md` already exists:
- If yes: Ask if it should be overwritten
- If no: Continue

### 3. Check for Existing Config

Check if `.stan/config.yaml` exists:
- If yes: Load existing config, offer to update
- If no: Run config setup (Step 4)

### 4. Config Setup (Interactive)

Use AskUserQuestion to collect user preferences:

**User Name (optional):**
- Question: "What's your name? (optional, for personalized greetings)"
- Options: Text input (allow empty)

**Skill Level:**
- Question: "What's your experience level?"
- Options:
  - `beginner` - Detailed explanations, step-by-step guidance
  - `intermediate` (default) - Balanced guidance
  - `expert` - Direct, technical, skip basics

**Communication Language:**
- Question: "Which language should I use for conversation?"
- Options: `en` (default), `de`, or custom ISO code

**Document Language:**
- Question: "Which language for generated documents?"
- Options: `en` (default), `de`, or custom ISO code

Save config to `.stan/config.yaml` using the config module.

### 5. Collect Project Information (Interactive)

- **Project Name:** What is the project called?
- **Description:** Brief description in 1-2 sentences
- **Goal:** What should be achieved?
- **Complexity Level:** Assess the project complexity (0-4)

**Complexity Levels:**
- `0 - Trivial` - No planning (typo fix, config change)
- `1 - Minimal` - Bug fix, small change
- `2 - Standard` (default) - Feature implementation
- `3 - Detailed` - Complex feature, architecture decisions
- `4 - Comprehensive` - Enterprise scope, multi-system

Show your initial assessment with reasoning, then ask if the user agrees or wants to adjust.

### 6. Create Project Files

1. Create `stan.md` based on template:
   - Use template from `templates/stan.md.template`
   - Replace placeholders with collected info
   - Set phase to `DEFINE`
   - Replace template date with current date

2. Create `docs/` directory if it doesn't exist

### 7. Confirm Initialization

```
STAN initialized!

Project: {name}
Phase: DEFINE

Structure created:
  - .stan/              (STAN data directory)
  - .stan/tasks.jsonl   (task storage)
  - .stan/completed/    (completed features archive)
  - .stan/config.yaml   (user preferences)
  - stan.md             (project manifest)
  - docs/               (documentation)

Next step: /stan define
```

## Important

- NEVER overwrite an existing stan.md without confirmation
- Replace the date in the template with the current date
- After init, the phase is always DEFINE
- Config is stored in `.stan/config.yaml` (persists across sessions)
- Use the communication language from config for all messages

## Config Location

The config file is stored at `.stan/config.yaml` with this structure:

```yaml
user:
  name: ""                # How STAN addresses you
  skill_level: intermediate  # beginner | intermediate | expert

language:
  communication: en       # Language for conversation
  documents: en           # Language for generated documents

project:
  name: ""
  output_folder: ".stan"
  complexity: 2           # 0-4, project complexity level
```
