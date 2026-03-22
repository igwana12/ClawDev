"""
Phases package for ClawDev framework.

Contains all development phases organized by function.
"""

# Import all phase classes for easy access
from .base import Phase
from .demand_analysis import DemandAnalysisPhase
from .language_choose import LanguageChoosePhase
from .coding import CodingPhase, CodeCompletePhase
from .code_review import CodeReviewCommentPhase, CodeReviewModificationPhase
from .testing import TestErrorSummaryPhase, TestModificationPhase
from .environment_doc import EnvironmentDocPhase, ManualPhase
from .composed_phase import ComposedPhase

__all__ = [
    "Phase",
    "DemandAnalysisPhase",
    "LanguageChoosePhase",
    "CodingPhase",
    "CodeCompletePhase",
    "CodeReviewCommentPhase",
    "CodeReviewModificationPhase",
    "TestErrorSummaryPhase",
    "TestModificationPhase",
    "EnvironmentDocPhase",
    "ManualPhase",
    "ComposedPhase",
]
