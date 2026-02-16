"""Redirect to hooks/autonomous-stan/lib/frontmatter."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "hooks" / "autonomous-stan" / "lib"))
from frontmatter import *
