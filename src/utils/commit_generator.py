# SPDX-License-Identifier: MIT
# Copyright (C) 2026 Marco Antônio Bueno da Silva <bueno.marco@gmail.com>
#
# This file is part of SwarmCode.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
Conventional Commits for SwarmCode.

Generates standardized commit messages based on code changes.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CommitType(str, Enum):
    """Conventional commit types."""
    FEAT = "feat"       # New feature
    FIX = "fix"         # Bug fix
    DOCS = "docs"       # Documentation changes
    STYLE = "style"     # Code style (formatting, semicolons, etc)
    REFACTOR = "refactor"  # Code refactoring
    PERF = "perf"       # Performance improvement
    TEST = "test"       # Adding or updating tests
    BUILD = "build"     # Build system or external dependencies
    CI = "ci"           # CI configuration
    CHORE = "chore"     # Maintenance (non-source code changes)
    CONFIG = "config"   # Configuration changes


@dataclass
class CommitMessage:
    """Conventional commit message."""
    type: CommitType
    description: str
    scope: Optional[str] = None
    body: Optional[str] = None
    footer: Optional[str] = None
    
    def __str__(self) -> str:
        """Format as conventional commit message."""
        # Header: type(scope): description
        if self.scope:
            header = f"{self.type.value}({self.scope}): {self.description}"
        else:
            header = f"{self.type.value}: {self.description}"
        
        # Body (optional)
        parts = [header]
        if self.body:
            parts.append("\n" + self.body)
        
        # Footer (optional)
        if self.footer:
            parts.append("\n" + self.footer)
        
        return "\n".join(parts)


class CommitGenerator:
    """Generates conventional commit messages from code changes."""
    
    def __init__(self):
        self.type_keywords = {
            CommitType.FEAT: ["add", "create", "implement", "new", "feature"],
            CommitType.FIX: ["fix", "resolve", "patch", "correct", "bug", "error"],
            CommitType.DOCS: ["doc", "readme", "documentation", "comment"],
            CommitType.STYLE: ["format", "style", "lint", "whitespace"],
            CommitType.REFACTOR: ["refactor", "restructure", "rename", "move"],
            CommitType.PERF: ["perf", "optimize", "speed", "performance"],
            CommitType.TEST: ["test", "spec", "coverage"],
            CommitType.BUILD: ["build", "deps", "dependencies", "package"],
            CommitType.CI: ["ci", "github", "gitlab", "jenkins", "workflow"],
            CommitType.CHORE: ["chore", "cleanup", "remove", "delete"],
            CommitType.CONFIG: ["config", "settings", "env", "configuration"],
        }
    
    def generate(self, code: str, task: str, has_tests: bool = False) -> CommitMessage:
        """
        Generate commit message from code and task.
        
        Args:
            code: Generated code
            task: Original task description
            has_tests: Whether tests were generated
        
        Returns:
            CommitMessage object
        """
        # Determine commit type from task
        commit_type = self._detect_type(task)
        
        # Generate description
        description = self._generate_description(task, commit_type)
        
        # Determine scope from code
        scope = self._detect_scope(code)
        
        # Generate body
        body = self._generate_body(code, has_tests)
        
        # Generate footer
        footer = None
        if has_tests:
            footer = "Tests: included"
        
        return CommitMessage(
            type=commit_type,
            description=description,
            scope=scope,
            body=body,
            footer=footer
        )
    
    def _detect_type(self, task: str) -> CommitType:
        """Detect commit type from task description."""
        task_lower = task.lower()
        
        for commit_type, keywords in self.type_keywords.items():
            if any(keyword in task_lower for keyword in keywords):
                return commit_type
        
        # Default to feat for new development
        return CommitType.FEAT
    
    def _generate_description(self, task: str, commit_type: CommitType) -> str:
        """Generate short description for commit."""
        # Clean up task for commit message
        description = task.strip()
        
        # Truncate if too long (max 72 chars per conventional commits)
        if len(description) > 72:
            description = description[:69] + "..."
        
        # Capitalize first letter
        description = description[0].upper() + description[1:] if description else description
        
        return description
    
    def _detect_scope(self, code: str) -> Optional[str]:
        """Detect scope from code (main module/component)."""
        # Look for module/class names
        import re
        
        # Python: look for main class or module
        class_match = re.search(r'class\s+(\w+)', code)
        if class_match:
            return class_match.group(1).lower()[:20]
        
        # Function-based
        func_match = re.search(r'def\s+(\w+)', code)
        if func_match:
            return func_match.group(1).lower()[:20]
        
        return None
    
    def _generate_body(self, code: str, has_tests: bool) -> str:
        """Generate commit body with details."""
        lines = []
        
        # Count lines of code
        code_lines = [l for l in code.split('\n') if l.strip() and not l.strip().startswith('#')]
        lines.append(f"Generated {len(code_lines)} lines of code")
        
        # Mention tests
        if has_tests:
            lines.append("Included unit tests")
        
        # Mention quality
        lines.append("Generated by SwarmCode AI agents")
        
        return "\n".join(lines)
