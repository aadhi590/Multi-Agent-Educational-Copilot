"""
Backward-compatible orchestrator import.
The canonical orchestrator is now in orchestration/orchestrator.py
"""
from orchestration.orchestrator import app

__all__ = ["app"]
