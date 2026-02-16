"""Redirect to hooks/autonomous-stan/git_guard."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "hooks" / "autonomous-stan"))
from git_guard import *
