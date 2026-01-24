#!/usr/bin/env python3
"""
STAN Config - Persistent configuration for user preferences and language settings.

Storage: .stan/config.yaml (project root)
Persists across sessions.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional

# Try to import yaml, graceful fallback if not available
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


# --- Config Location ---

def get_project_root() -> Path:
    """Find project root (where .stan/ should be)."""
    return Path(os.getcwd())


def get_config_dir() -> Path:
    """Get .stan/ directory path."""
    return get_project_root() / ".stan"


def get_config_file() -> Path:
    """Get config file path."""
    return get_config_dir() / "config.yaml"


# --- Data Classes ---

@dataclass
class UserConfig:
    """User preferences."""
    name: str = ""
    skill_level: str = "intermediate"  # beginner | intermediate | expert

    def __post_init__(self):
        if self.skill_level not in ("beginner", "intermediate", "expert"):
            self.skill_level = "intermediate"


@dataclass
class LanguageConfig:
    """Language settings."""
    communication: str = "en"  # Language for conversation
    documents: str = "en"      # Language for generated documents


@dataclass
class ProjectConfig:
    """Project settings."""
    name: str = ""
    output_folder: str = ".stan"


@dataclass
class StanConfig:
    """Complete STAN configuration."""
    user: UserConfig = field(default_factory=UserConfig)
    language: LanguageConfig = field(default_factory=LanguageConfig)
    project: ProjectConfig = field(default_factory=ProjectConfig)


# --- Load / Save ---

def load_config() -> Optional[StanConfig]:
    """
    Load config from .stan/config.yaml.
    Returns None if file doesn't exist or can't be parsed.
    """
    config_file = get_config_file()

    if not config_file.exists():
        return None

    if not YAML_AVAILABLE:
        return None

    try:
        with open(config_file, "r") as f:
            data = yaml.safe_load(f)

        if not data:
            return None

        # Parse nested structures
        user_data = data.get("user", {})
        language_data = data.get("language", {})
        project_data = data.get("project", {})

        return StanConfig(
            user=UserConfig(
                name=user_data.get("name", ""),
                skill_level=user_data.get("skill_level", "intermediate")
            ),
            language=LanguageConfig(
                communication=language_data.get("communication", "en"),
                documents=language_data.get("documents", "en")
            ),
            project=ProjectConfig(
                name=project_data.get("name", ""),
                output_folder=project_data.get("output_folder", ".stan")
            )
        )
    except Exception:
        return None


def save_config(config: StanConfig) -> bool:
    """
    Save config to .stan/config.yaml.
    Creates .stan/ directory if needed.
    Returns True on success.
    """
    if not YAML_AVAILABLE:
        return False

    config_dir = get_config_dir()
    config_file = get_config_file()

    try:
        # Ensure directory exists
        config_dir.mkdir(parents=True, exist_ok=True)

        # Convert to dict
        data = {
            "user": {
                "name": config.user.name,
                "skill_level": config.user.skill_level
            },
            "language": {
                "communication": config.language.communication,
                "documents": config.language.documents
            },
            "project": {
                "name": config.project.name,
                "output_folder": config.project.output_folder
            }
        }

        # Write with comments
        content = """# STAN Framework Configuration
# Created by: /stan init

# --- User Preferences ---
user:
  name: "{name}"              # How STAN addresses you (empty = no greeting)
  skill_level: {skill_level}    # beginner | intermediate | expert

# --- Language Settings ---
language:
  communication: {communication}   # Language for conversation
  documents: {documents}           # Language for generated documents

# --- Project Settings ---
project:
  name: "{project_name}"
  output_folder: "{output_folder}"
""".format(
            name=config.user.name,
            skill_level=config.user.skill_level,
            communication=config.language.communication,
            documents=config.language.documents,
            project_name=config.project.name,
            output_folder=config.project.output_folder
        )

        with open(config_file, "w") as f:
            f.write(content)

        return True
    except Exception:
        return False


def ensure_config() -> StanConfig:
    """
    Load config or return defaults.
    Always returns a valid StanConfig.
    """
    config = load_config()
    if config is None:
        return StanConfig()
    return config


def config_exists() -> bool:
    """Check if config file exists."""
    return get_config_file().exists()


# --- Convenience Getters ---

def get_user_name() -> str:
    """Get configured user name (empty string if not set)."""
    config = load_config()
    if config and config.user.name:
        return config.user.name
    return ""


def get_skill_level() -> str:
    """Get configured skill level (default: intermediate)."""
    config = load_config()
    if config:
        return config.user.skill_level
    return "intermediate"


def get_communication_language() -> str:
    """Get configured communication language (default: en)."""
    config = load_config()
    if config:
        return config.language.communication
    return "en"


def get_document_language() -> str:
    """Get configured document language (default: en)."""
    config = load_config()
    if config:
        return config.language.documents
    return "en"


# --- Skill Level Behavior ---

SKILL_LEVEL_BEHAVIOR = {
    "beginner": {
        "explain_new_concepts": True,
        "ask_if_explanation_needed": True,
        "use_analogies": True,
        "verbose_guidance": True
    },
    "intermediate": {
        "explain_new_concepts": False,
        "ask_if_explanation_needed": False,
        "use_analogies": False,
        "verbose_guidance": False
    },
    "expert": {
        "explain_new_concepts": False,
        "ask_if_explanation_needed": False,
        "use_analogies": False,
        "verbose_guidance": False,
        "direct_and_technical": True,
        "skip_basics": True
    }
}


def get_skill_behavior() -> dict:
    """Get behavior flags for current skill level."""
    level = get_skill_level()
    return SKILL_LEVEL_BEHAVIOR.get(level, SKILL_LEVEL_BEHAVIOR["intermediate"])


# --- Project Complexity Levels ---

COMPLEXITY_LEVELS = {
    0: {
        "name": "trivial",
        "description": "No planning needed. Single file change, obvious fix.",
        "planning_depth": "none",
        "examples": ["typo fix", "config change", "simple rename"]
    },
    1: {
        "name": "minimal",
        "description": "Bug fix or small change. Limited scope, clear solution.",
        "planning_depth": "lightweight",
        "examples": ["bug fix", "add simple validation", "update dependency"]
    },
    2: {
        "name": "standard",
        "description": "Feature implementation. Multiple files, defined scope.",
        "planning_depth": "standard",
        "examples": ["new feature", "API endpoint", "component"]
    },
    3: {
        "name": "detailed",
        "description": "Complex feature. Cross-cutting concerns, architecture decisions.",
        "planning_depth": "comprehensive",
        "examples": ["auth system", "state management", "major refactor"]
    },
    4: {
        "name": "comprehensive",
        "description": "Enterprise scope. Multiple systems, long-term planning.",
        "planning_depth": "extensive",
        "examples": ["new product", "platform migration", "microservices"]
    }
}

DEFAULT_COMPLEXITY = 2  # standard


def get_project_complexity() -> int:
    """
    Get project complexity level from config.
    Returns DEFAULT_COMPLEXITY (2) if not set.
    """
    config = load_config()
    if config is None:
        return DEFAULT_COMPLEXITY

    # Check if project has complexity set
    # We'll store it in project.complexity but fallback to default
    project_data = getattr(config, 'project', None)
    if project_data and hasattr(project_data, 'complexity'):
        return project_data.complexity

    # Try loading from config file directly
    config_file = get_config_file()
    if config_file.exists() and YAML_AVAILABLE:
        try:
            with open(config_file, "r") as f:
                data = yaml.safe_load(f)
            if data and "project" in data:
                complexity = data["project"].get("complexity")
                if complexity is not None and complexity in COMPLEXITY_LEVELS:
                    return complexity
        except Exception:
            pass

    return DEFAULT_COMPLEXITY


def set_project_complexity(level: int) -> bool:
    """
    Set project complexity level in config.
    Level must be 0-4. Returns True on success.
    """
    if level not in COMPLEXITY_LEVELS:
        return False

    config_file = get_config_file()
    config_dir = get_config_dir()

    if not YAML_AVAILABLE:
        return False

    try:
        # Ensure directory exists
        config_dir.mkdir(parents=True, exist_ok=True)

        # Load existing config or create new
        data = {}
        if config_file.exists():
            with open(config_file, "r") as f:
                data = yaml.safe_load(f) or {}

        # Set complexity in project section
        if "project" not in data:
            data["project"] = {}
        data["project"]["complexity"] = level

        # Write back
        with open(config_file, "w") as f:
            yaml.dump(data, f, default_flow_style=False)

        return True
    except Exception:
        return False


def get_complexity_info(level: int = None) -> dict:
    """
    Get info for a complexity level.
    If level is None, returns info for current project complexity.
    """
    if level is None:
        level = get_project_complexity()

    return COMPLEXITY_LEVELS.get(level, COMPLEXITY_LEVELS[DEFAULT_COMPLEXITY])
