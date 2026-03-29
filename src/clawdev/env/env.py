"""
Chat environment for ClawDev framework.

Manages the state and data throughout the software development process.
"""

from typing import Dict
import os
import json


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
        self.modality = ""  # Application, Website, Document, etc.
        self.language = ""  # Python, JavaScript, etc.
        self.ideas = ""
        self.codes: Dict[str, str] = {}  # filename -> code content
        self.requirements = ""
        self.manuals = ""
        self.review_comments = ""
        self.error_summary = ""
        self.test_reports = ""
        self.images: Dict[str, str] = {}  # filename -> description
        self.unimplemented_file = ""
        self.description = ""
        self.gui = ""  # GUI-related information

    def update_codes(self, filename: str, content: str) -> None:
        """
        Update code content for a file.

        Args:
            filename: Name of the file to update
            content: New content for the file
        """
        self.codes[filename] = content

    def get_codes(self) -> str:
        """
        Get all code content formatted for prompts.

        Returns:
            String representation of all code files
        """
        code_lines = []
        for filename, content in self.codes.items():
            code_lines.append(f"{filename}\n```{self.language.lower()}\n{content}\n```")
        return "\n".join(code_lines)

    def exist_employee(self, role: str) -> bool:
        """
        Check if a role exists in the environment.

        Args:
            role: Role name to check

        Returns:
            True if role exists, False otherwise
        """
        # This would check against registered roles
        # For now, return True to avoid breaking existing logic
        return True
