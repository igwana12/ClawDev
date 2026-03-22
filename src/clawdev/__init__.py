"""
ClawDev - A multi-agent software development framework based on OpenClaw ACP.

This package provides a structured approach to software development using AI agents,
following a waterfall model with phases for demand analysis, coding, testing, and documentation.
"""

# Import main components for easy access
from .chain.chain import ChatChain
from .adapter.agent_adapter import AgentAdapter
from .env.env import ChatEnv
from .phases.base import Phase
from .phases.demand_analysis import DemandAnalysisPhase
from .phases.language_choose import LanguageChoosePhase
from .phases.coding import CodingPhase
from .phases.code_review import CodeReviewCommentPhase, CodeReviewModificationPhase
from .phases.testing import TestErrorSummaryPhase, TestModificationPhase
from .phases.environment_doc import EnvironmentDocPhase
from .phases.manual import ManualPhase
from .phases.composed_phase import ComposedPhase

__all__ = [
    "ChatChain",
    "AgentAdapter", 
    "ChatEnv",
    "Phase",
    "DemandAnalysisPhase",
    "LanguageChoosePhase", 
    "CodingPhase",
    "CodeReviewCommentPhase",
    "CodeReviewModificationPhase",
    "TestErrorSummaryPhase",
    "TestModificationPhase", 
    "EnvironmentDocPhase",
    "ManualPhase",
    "ComposedPhase",
]