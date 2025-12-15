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

"""Tests for execution context."""

import json
import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from src.core.context import (
    ExecutionContext,
    IterationResult,
    CodeBlock,
    Issue
)


class TestCodeBlock:
    """Tests for CodeBlock dataclass."""

    def test_create_code_block(self):
        """Test creating a code block."""
        block = CodeBlock(
            filepath="src/main.py",
            language="python",
            content="def main(): pass"
        )
        assert block.filepath == "src/main.py"
        assert block.language == "python"
        assert block.content == "def main(): pass"


class TestIssue:
    """Tests for Issue dataclass."""

    def test_create_issue(self):
        """Test creating an issue."""
        issue = Issue(
            type="BUG",
            severity="HIGH",
            filepath="main.py",
            description="Null pointer",
            suggestion="Add null check",
            line=10
        )
        assert issue.type == "BUG"
        assert issue.severity == "HIGH"
        assert issue.line == 10


class TestIterationResult:
    """Tests for IterationResult dataclass."""

    def test_create_iteration_result(self):
        """Test creating an iteration result."""
        result = IterationResult(
            iteration=1,
            architecture="Some architecture",
            code="Some code",
            code_blocks=[],
            qa_issues=[],
            security_issues=[],
            approved=True,
            reviewer_notes="APPROVED"
        )
        assert result.iteration == 1
        assert result.approved is True


class TestExecutionContext:
    """Tests for ExecutionContext."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_create_context(self):
        """Test creating execution context."""
        ctx = ExecutionContext(task="Build a REST API")
        assert ctx.task == "Build a REST API"
        assert ctx.current_iteration == 1
        assert ctx.is_approved is False

    def test_add_iteration(self):
        """Test adding iteration to context."""
        ctx = ExecutionContext(task="Test task")
        
        result = IterationResult(
            iteration=1,
            architecture=None,
            code="code",
            code_blocks=[],
            qa_issues=[],
            security_issues=[],
            approved=False,
            reviewer_notes="REPROVADO: bugs"
        )
        
        ctx.add_iteration(result)
        
        assert len(ctx.iterations) == 1
        assert ctx.current_iteration == 2
        assert ctx.last_iteration == result

    def test_is_approved(self):
        """Test approval status."""
        ctx = ExecutionContext(task="Test")
        
        # Not approved initially
        assert ctx.is_approved is False
        
        # Add approved iteration
        result = IterationResult(
            iteration=1,
            architecture=None,
            code="code",
            code_blocks=[],
            qa_issues=[],
            security_issues=[],
            approved=True,
            reviewer_notes="APROVADO"
        )
        ctx.add_iteration(result)
        
        assert ctx.is_approved is True

    def test_get_feedback(self):
        """Test getting feedback for next iteration."""
        ctx = ExecutionContext(task="Test")
        
        # Add iteration with issues
        result = IterationResult(
            iteration=1,
            architecture=None,
            code="code",
            code_blocks=[],
            qa_issues=[
                Issue("BUG", "HIGH", "main.py", "Bug 1", "Fix it")
            ],
            security_issues=[],
            approved=False,
            reviewer_notes="REPROVADO"
        )
        ctx.add_iteration(result)
        
        feedback = ctx.get_feedback_for_next_iteration()
        
        assert "QA Issues" in feedback
        assert "Bug 1" in feedback

    def test_save_context(self, temp_dir):
        """Test saving context to disk."""
        ctx = ExecutionContext(task="Test", output_dir=temp_dir)
        
        result = IterationResult(
            iteration=1,
            architecture=None,
            code="code",
            code_blocks=[
                CodeBlock("main.py", "python", "def main(): pass")
            ],
            qa_issues=[],
            security_issues=[],
            approved=True,
            reviewer_notes="APROVADO"
        )
        ctx.add_iteration(result)
        
        saved_path = ctx.save()
        
        assert saved_path.exists()
        assert (saved_path / "metadata.json").exists()
        assert (saved_path / "iteration_1").exists()

    def test_load_context(self, temp_dir):
        """Test loading context from disk."""
        # Create and save context
        ctx1 = ExecutionContext(task="Test task", output_dir=temp_dir)
        result = IterationResult(
            iteration=1,
            architecture=None,
            code="code",
            code_blocks=[
                CodeBlock("src/main.py", "python", "def main(): pass")
            ],
            qa_issues=[],
            security_issues=[],
            approved=True,
            reviewer_notes="APROVADO"
        )
        ctx1.add_iteration(result)
        saved_path = ctx1.save()
        
        # Load context
        ctx2 = ExecutionContext.load(ctx1.id, temp_dir)
        
        assert ctx2.task == ctx1.task
        assert len(ctx2.iterations) == len(ctx1.iterations)
        assert ctx2.is_approved == ctx1.is_approved
