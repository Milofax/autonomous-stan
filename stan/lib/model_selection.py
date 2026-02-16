"""Redirect to hooks/autonomous-stan/lib/model_selection."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "hooks" / "autonomous-stan" / "lib"))
from model_selection import *
