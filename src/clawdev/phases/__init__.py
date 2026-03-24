"""
Phases package for ClawDev framework.

Contains all development phases organized by function.
Phase hierarchy:
- Phase: Abstract base class defining the interface
- SimplePhase: Single dialog phase execution
- ComposedPhase: Loop execution of multiple sub-phases
"""

from .base import Phase
from .simple_phase import SimplePhase
from .composed_phase import ComposedPhase

__all__ = [
    "Phase",
    "SimplePhase",
    "ComposedPhase",
]
