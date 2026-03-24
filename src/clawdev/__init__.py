"""
ClawDev - A multi-agent software development framework based on OpenClaw ACP.

This package provides a structured approach to software development using AI agents,
following a waterfall model with phases for demand analysis, coding, testing, and documentation.
"""

from .chain.chain import ChatChain
from .adapter.agent_adapter import AgentAdapter
from .env.env import ChatEnv
from .phases.base import Phase
from .phases.simple_phase import SimplePhase
from .phases.composed_phase import ComposedPhase

__all__ = [
    "ChatChain",
    "AgentAdapter",
    "ChatEnv",
    "Phase",
    "SimplePhase",
    "ComposedPhase",
]
