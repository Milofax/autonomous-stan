"""Redirect to hooks/autonomous-stan/stan_gate — full module proxy."""
import importlib
import sys
from pathlib import Path

_hooks_path = str(Path(__file__).parent.parent.parent / "hooks" / "autonomous-stan")
if _hooks_path not in sys.path:
    sys.path.insert(0, _hooks_path)

# Import the real module and copy all attributes
_real = importlib.import_module("stan_gate")
for _name in dir(_real):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_real, _name)
