"""
Copyright 2024 ClawDev Contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

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
