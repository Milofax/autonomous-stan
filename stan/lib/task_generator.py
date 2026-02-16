"""Redirect to hooks/autonomous-stan/lib/task_generator."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "hooks" / "autonomous-stan" / "lib"))
from task_generator import *
