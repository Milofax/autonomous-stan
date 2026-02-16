"""Redirect to hooks/autonomous-stan/stan_context."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "hooks" / "autonomous-stan"))
from stan_context import *
