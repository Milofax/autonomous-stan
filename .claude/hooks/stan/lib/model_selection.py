#!/usr/bin/env python3
"""
STAN Model Auto-Selection

Automatic model selection based on task complexity.
Escalation logic when tasks fail repeatedly.
"""

from typing import Optional


# Available models in Claude Code
AVAILABLE_MODELS = ["haiku", "sonnet", "opus"]

# Default model for most tasks
DEFAULT_MODEL = "sonnet"

# Escalation order (lowest to highest capability)
ESCALATION_ORDER = ["haiku", "sonnet", "opus"]

# Model information
MODEL_INFO = {
    "haiku": {
        "description": "Fast, lightweight model for simple tasks",
        "use_case": "Quick fixes, simple formatting, trivial changes",
        "complexity_range": (0, 1),
    },
    "sonnet": {
        "description": "Balanced model for most development tasks",
        "use_case": "Standard features, bug fixes, moderate complexity",
        "complexity_range": (1, 3),
    },
    "opus": {
        "description": "Most capable model for complex reasoning",
        "use_case": "Architecture decisions, complex features, debugging hard problems",
        "complexity_range": (3, 4),
    },
}


def select_model_for_task(
    complexity: int = 2,
    model: str = "auto"
) -> str:
    """
    Select appropriate model based on task complexity.

    Args:
        complexity: Project complexity level (0-4)
        model: Explicit model or "auto" for automatic selection

    Returns:
        Model name (haiku, sonnet, or opus)
    """
    # Explicit model overrides auto-selection
    if model != "auto" and model in AVAILABLE_MODELS:
        return model

    # Auto-selection based on complexity
    # complexity < 3 → sonnet (standard)
    # complexity >= 3 → opus (complex)
    if complexity < 3:
        return "sonnet"
    else:
        return "opus"


def escalate_model(current_model: str) -> Optional[str]:
    """
    Get the next model in escalation order.

    Args:
        current_model: Current model being used

    Returns:
        Next model or None if already at maximum
    """
    if current_model not in ESCALATION_ORDER:
        return None

    current_index = ESCALATION_ORDER.index(current_model)

    # Check if we can escalate
    if current_index >= len(ESCALATION_ORDER) - 1:
        return None  # Already at max (opus)

    return ESCALATION_ORDER[current_index + 1]


def can_escalate(current_model: str) -> bool:
    """
    Check if escalation is possible from current model.

    Args:
        current_model: Current model being used

    Returns:
        True if escalation is possible
    """
    return escalate_model(current_model) is not None


def get_model_info(model: str) -> dict:
    """
    Get information about a model.

    Args:
        model: Model name

    Returns:
        Dict with description, use_case, complexity_range
    """
    return MODEL_INFO.get(model, {
        "description": "Unknown model",
        "use_case": "N/A",
        "complexity_range": (0, 4),
    })


def get_escalation_message(
    current_model: str,
    failure_count: int
) -> str:
    """
    Generate message for model escalation notification.

    Args:
        current_model: Current model
        failure_count: Number of failures

    Returns:
        User notification message
    """
    next_model = escalate_model(current_model)

    if next_model is None:
        return (
            f"[STAN] Task failed {failure_count}x with {current_model} (max model). "
            "Consider /stan think for perspective shift."
        )

    return (
        f"[STAN] Task failed {failure_count}x with {current_model}. "
        f"Escalating to {next_model} for more capability."
    )


# CLI for testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: model_selection.py [select <complexity>|escalate <model>|info <model>]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "select" and len(sys.argv) >= 3:
        complexity = int(sys.argv[2])
        model = select_model_for_task(complexity)
        print(f"Complexity {complexity} → {model}")

    elif cmd == "escalate" and len(sys.argv) >= 3:
        current = sys.argv[2]
        next_model = escalate_model(current)
        print(f"{current} → {next_model or 'MAX'}")

    elif cmd == "info" and len(sys.argv) >= 3:
        model = sys.argv[2]
        info = get_model_info(model)
        print(f"{model}: {info['description']}")
        print(f"Use case: {info['use_case']}")

    else:
        print("Unknown command")
        sys.exit(1)
