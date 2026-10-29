"""QuorumCraft: deterministic Raft consensus and fault-injection laboratory."""
from .raft import Cluster
from .invariants import SafetyViolation, check_safety

__all__ = ["Cluster", "SafetyViolation", "check_safety"]
__version__ = "0.1.0"
