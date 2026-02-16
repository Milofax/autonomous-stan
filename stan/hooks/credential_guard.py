"""Redirect to hooks/autonomous-stan/credential_guard."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "hooks" / "autonomous-stan"))
from credential_guard import *
