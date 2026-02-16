"""Redirect to hooks/autonomous-stan/loop_breaker."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "hooks" / "autonomous-stan"))
from loop_breaker import *
