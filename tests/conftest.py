"""Pytest configuration for autonomous-stan tests."""

import sys
from pathlib import Path

# Add hooks lib to Python path for all tests
# New location after plugin structure migration
hooks_lib_path = Path(__file__).parent.parent / "hooks" / "autonomous-stan" / "lib"
sys.path.insert(0, str(hooks_lib_path))
