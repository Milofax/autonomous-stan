"""Redirect to hooks/autonomous-stan/lib/acceptance."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "hooks" / "autonomous-stan" / "lib"))
from acceptance import *
