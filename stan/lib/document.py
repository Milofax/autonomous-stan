"""Redirect to hooks/autonomous-stan/lib/document."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "hooks" / "autonomous-stan" / "lib"))
from document import *
