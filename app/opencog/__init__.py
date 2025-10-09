"""
OpenCog integration module for OpenManus framework.

This module provides OpenCog systems optimized for the OpenManus agent framework,
including AtomSpace for knowledge representation, reasoning engines, and
cognitive agent implementations.
"""

from app.opencog.atomspace import AtomSpaceManager
from app.opencog.reasoning import ReasoningEngine
from app.opencog.pattern_matcher import PatternMatcher

# Import CognitiveAgent separately to avoid circular imports
try:
    from app.opencog.cognitive_agent import CognitiveAgent
    _cognitive_agent_available = True
except ImportError:
    _cognitive_agent_available = False

__all__ = [
    "AtomSpaceManager",
    "ReasoningEngine", 
    "PatternMatcher"
]

if _cognitive_agent_available:
    __all__.append("CognitiveAgent")