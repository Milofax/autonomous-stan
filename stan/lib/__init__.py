"""Compatibility — imports from hooks/autonomous-stan/lib/."""
import sys
from pathlib import Path
_lib_path = str(Path(__file__).parent.parent.parent / "hooks" / "autonomous-stan" / "lib")
if _lib_path not in sys.path:
    sys.path.insert(0, _lib_path)
