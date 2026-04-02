"""
Copyright 2026 HDAnzz

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Chat environment for ClawDev framework.

Manages the state and data throughout the software development process.
"""


class ChatEnv:
    """Environment that tracks the state of a software development project."""

    def __init__(self, project_name: str):
        """
        Initialize environment for a project.

        Args:
            project_name: Name of the project
        """
        self.project_name = project_name
        self.task_prompt = ""
        self.modality = ""
        self.language = ""
