"""
Backward-compatible state import.
The canonical state definition is now in state/agent_state.py
"""
from state.agent_state import AgentState, MasteryData

__all__ = ["AgentState", "MasteryData"]
