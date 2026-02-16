"""Redirect to hooks/autonomous-stan/ hook modules."""
import sys
from pathlib import Path
_hooks_path = str(Path(__file__).parent.parent.parent / "hooks" / "autonomous-stan")
if _hooks_path not in sys.path:
    sys.path.insert(0, _hooks_path)
