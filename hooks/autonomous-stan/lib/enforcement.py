#!/usr/bin/env python3
"""Enforcement logic for STAN hooks."""

from pathlib import Path
from typing import Optional
from dataclasses import dataclass

from frontmatter import (
    parse_frontmatter,
    get_document_type,
    get_document_criteria,
    get_techniques_applied,
    is_archived,
)
from criteria import (
    get_template_criteria,
    get_template_for_type,
    check_criteria_not_removed,
    load_criteria,
)


@dataclass
class EnforcementResult:
    """Result of an enforcement check."""
    allowed: bool
    message: str
    details: Optional[dict] = None


def allow(message: str = "OK") -> EnforcementResult:
    """Create an allow result."""
    return EnforcementResult(allowed=True, message=message)


def deny(message: str, details: Optional[dict] = None) -> EnforcementResult:
    """Create a deny result."""
    return EnforcementResult(allowed=False, message=message, details=details)


# Phase-specific required purposes
PHASE_PURPOSES = {
    "define": ["big-picture", "ideation"],
    "plan": ["structured-problem-solving", "decision-making"],
    "create": ["code-review"],  # root-cause-analysis added on 3-strikes
}


def check_document_criteria(doc_path: str | Path) -> EnforcementResult:
    """
    Check that document has all required criteria from template.

    Args:
        doc_path: Path to the document

    Returns:
        EnforcementResult indicating if check passed
    """
    path = Path(doc_path)
    if not path.exists():
        return deny(f"Document not found: {doc_path}")

    # Skip archived documents
    if is_archived(doc_path):
        return allow("Archived document - skipped")

    # Get document type and criteria
    doc_type = get_document_type(doc_path)
    if not doc_type:
        return deny(f"Document has no 'type' in frontmatter: {doc_path}")

    doc_criteria = get_document_criteria(doc_path)

    # Find template for this type
    template_name = get_template_for_type(doc_type)
    if not template_name:
        return deny(f"No template found for type '{doc_type}'")

    # Get template criteria (minimum required)
    template_criteria = get_template_criteria(template_name)

    # Check no criteria were removed
    is_valid, missing = check_criteria_not_removed(doc_criteria, template_criteria)
    if not is_valid:
        return deny(
            f"Criteria removed from document (not allowed): {missing}",
            details={"missing": missing, "template": template_name}
        )

    return allow(f"Document criteria valid ({len(doc_criteria)} criteria)")


def check_techniques_for_phase(
    doc_path: str | Path,
    phase: str
) -> EnforcementResult:
    """
    Check that document has techniques covering required purposes for phase.

    Args:
        doc_path: Path to the document
        phase: Current phase (define, plan, create)

    Returns:
        EnforcementResult indicating if check passed
    """
    if is_archived(doc_path):
        return allow("Archived document - skipped")

    techniques_applied = get_techniques_applied(doc_path)
    if not techniques_applied:
        required = PHASE_PURPOSES.get(phase, [])
        return deny(
            f"No techniques_applied in frontmatter. Required purposes for {phase}: {required}",
            details={"required_purposes": required}
        )

    # Get purposes covered by applied techniques
    covered_purposes = get_purposes_for_techniques(techniques_applied)

    # Check if at least one required purpose is covered
    required_purposes = PHASE_PURPOSES.get(phase, [])
    covered_required = [p for p in required_purposes if p in covered_purposes]

    if not covered_required:
        return deny(
            f"No required purpose covered. Required: {required_purposes}, Covered: {list(covered_purposes)}",
            details={
                "required": required_purposes,
                "covered": list(covered_purposes),
                "techniques": techniques_applied
            }
        )

    return allow(f"Purposes covered: {covered_required}")


def get_purposes_for_techniques(techniques: list[str]) -> set[str]:
    """
    Get all purposes that are covered by given techniques.

    Args:
        techniques: List of technique IDs

    Returns:
        Set of purpose IDs covered by these techniques
    """
    from .techniques import get_technique

    purposes = set()
    for tech_id in techniques:
        tech = get_technique(tech_id)
        if tech and "purposes" in tech:
            purposes.update(tech["purposes"])
    return purposes


def check_all_required_criteria_checks(doc_path: str | Path) -> EnforcementResult:
    """
    Check that all required criteria checks pass for a document.

    This is a simplified version that checks structure, not content.
    Auto-checks would need to be run separately.

    Args:
        doc_path: Path to the document

    Returns:
        EnforcementResult indicating if check passed
    """
    if is_archived(doc_path):
        return allow("Archived document - skipped")

    doc_criteria = get_document_criteria(doc_path)
    failed_checks = []

    for criteria_name in doc_criteria:
        criteria = load_criteria(criteria_name)
        if not criteria:
            failed_checks.append({
                "criteria": criteria_name,
                "error": "Criteria file not found"
            })
            continue

        # For auto checks, we'd need to run commands
        # For now, just validate structure
        for check in criteria.get("checks", []):
            if check.get("required") and check.get("auto"):
                # Auto checks need external execution
                # This is handled by the hook, not this library
                pass

    if failed_checks:
        return deny(
            f"Some criteria checks failed",
            details={"failed": failed_checks}
        )

    return allow("All criteria checks passed (structure only)")


def check_phase_transition(
    from_phase: str,
    to_phase: str,
    doc_path: Optional[str | Path] = None
) -> EnforcementResult:
    """
    Check if a phase transition is allowed.

    Args:
        from_phase: Current phase
        to_phase: Target phase
        doc_path: Optional document to check

    Returns:
        EnforcementResult indicating if transition is allowed
    """
    valid_transitions = {
        "define": ["plan"],
        "plan": ["create", "define"],  # Can go back to define for reconciliation
        "create": ["define"],  # Reconciliation
    }

    allowed_targets = valid_transitions.get(from_phase, [])
    if to_phase not in allowed_targets:
        return deny(
            f"Invalid phase transition: {from_phase} -> {to_phase}",
            details={"allowed": allowed_targets}
        )

    # If document provided, check it meets criteria
    if doc_path:
        result = check_document_criteria(doc_path)
        if not result.allowed:
            return result

        result = check_techniques_for_phase(doc_path, from_phase)
        if not result.allowed:
            return result

    return allow(f"Phase transition {from_phase} -> {to_phase} allowed")
