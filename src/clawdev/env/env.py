"""
Chat environment for ClawDev framework.

Manages the state and data throughout the software development process.
"""

from typing import Dict, List, Any, Optional
import os
import json


class ChatEnv:
    """Environment that tracks the state of a software development project."""

    def __init__(self, directory: str):
        """
        Initialize environment with project directory.

        Args:
            directory: Project directory path
        """
        self.directory = directory
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

        # Create project directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)

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

    def write_meta(self) -> None:
        """Write metadata file for the project."""
        meta_path = os.path.join(self.directory, "meta.txt")
        meta_data = {
            "task": self.task_prompt,
            "modality": self.modality,
            "language": self.language,
            "requirements": self.requirements,
        }

        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta_data, f, indent=2, ensure_ascii=False)

    def write_codes(self) -> None:
        """Write all code files to the project directory."""
        for filename, content in self.codes.items():
            file_path = os.path.join(self.directory, filename)
            # Create subdirectories if needed
            os.makedirs(
                os.path.dirname(file_path)
                if os.path.dirname(filename)
                else self.directory,
                exist_ok=True,
            )

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

    def write_manual(self) -> None:
        """Write user manual to the project directory."""
        if self.manuals:
            manual_path = os.path.join(self.directory, "manual.md")
            with open(manual_path, "w", encoding="utf-8") as f:
                f.write(self.manuals)

    def write_requirements(self) -> None:
        """Write requirements file to the project directory."""
        if self.requirements:
            req_path = os.path.join(self.directory, "requirements.txt")
            with open(req_path, "w", encoding="utf-8") as f:
                f.write(self.requirements)
