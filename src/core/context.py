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

"""Execution context for managing state across iterations."""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass
class CodeBlock:
    """A block of code with filepath."""
    filepath: str
    language: str
    content: str


@dataclass
class Issue:
    """An issue found by QA or Security."""
    type: str  # BUG, SECURITY, IMPROVEMENT
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    filepath: str
    description: str
    suggestion: str
    line: Optional[int] = None


@dataclass
class IterationResult:
    """Result from a single iteration."""
    iteration: int
    architecture: Optional[str]
    code: str
    code_blocks: list[CodeBlock]
    qa_issues: list[Issue]
    security_issues: list[Issue]
    approved: bool
    reviewer_notes: str
    timestamp: datetime = field(default_factory=datetime.now)


class ExecutionContext:
    """Manages execution state across iterations."""

    def __init__(self, task: str, output_dir: Optional[Path] = None):
        self.id = str(uuid.uuid4())[:8]
        self.task = task
        self.output_dir = output_dir or Path("./output")
        self.iterations: list[IterationResult] = []
        self.metadata: dict = {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    @property
    def current_iteration(self) -> int:
        """Get current iteration number."""
        return len(self.iterations) + 1

    @property
    def last_iteration(self) -> Optional[IterationResult]:
        """Get last iteration result."""
        return self.iterations[-1] if self.iterations else None

    @property
    def is_approved(self) -> bool:
        """Check if code is approved."""
        return self.last_iteration.approved if self.last_iteration else False

    @property
    def all_code_blocks(self) -> list[CodeBlock]:
        """Get all code blocks from last iteration."""
        if self.last_iteration:
            return self.last_iteration.code_blocks
        return []

    def add_iteration(self, result: IterationResult) -> None:
        """Add iteration result."""
        self.iterations.append(result)
        self.updated_at = datetime.now()

    def get_feedback_for_next_iteration(self) -> str:
        """Build feedback string for next iteration."""
        if not self.last_iteration:
            return ""

        feedback_parts = []

        if self.last_iteration.qa_issues:
            feedback_parts.append("QA Issues:")
            for issue in self.last_iteration.qa_issues:
                feedback_parts.append(f"- [{issue.severity}] {issue.description}")
                feedback_parts.append(f"  Sugestão: {issue.suggestion}")

        if self.last_iteration.security_issues:
            feedback_parts.append("\nSecurity Issues:")
            for issue in self.last_iteration.security_issues:
                feedback_parts.append(f"- [{issue.severity}] {issue.description}")
                feedback_parts.append(f"  Correção: {issue.suggestion}")

        return "\n".join(feedback_parts)

    def save(self) -> Path:
        """Save context to disk."""
        run_dir = self.output_dir / f"run_{self.id}"
        run_dir.mkdir(parents=True, exist_ok=True)

        # Save metadata
        metadata = {
            "id": self.id,
            "task": self.task,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "iterations": len(self.iterations),
            "approved": self.is_approved,
        }

        with open(run_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        # Save iterations
        for i, iteration in enumerate(self.iterations):
            iter_dir = run_dir / f"iteration_{i+1}"
            iter_dir.mkdir(exist_ok=True)

            # Save code
            if iteration.code_blocks:
                for block in iteration.code_blocks:
                    file_path = iter_dir / block.filepath
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(file_path, "w") as f:
                        f.write(block.content)

            # Save iteration report
            report = {
                "iteration": iteration.iteration,
                "approved": iteration.approved,
                "reviewer_notes": iteration.reviewer_notes,
                "qa_issues_count": len(iteration.qa_issues),
                "security_issues_count": len(iteration.security_issues),
                "timestamp": iteration.timestamp.isoformat(),
            }

            with open(iter_dir / "report.json", "w") as f:
                json.dump(report, f, indent=2)

            # Save issues
            if iteration.qa_issues:
                with open(iter_dir / "qa_issues.json", "w") as f:
                    json.dump([
                        {
                            "type": i.type,
                            "severity": i.severity,
                            "filepath": i.filepath,
                            "description": i.description,
                            "suggestion": i.suggestion,
                        }
                        for i in iteration.qa_issues
                    ], f, indent=2)

            if iteration.security_issues:
                with open(iter_dir / "security_issues.json", "w") as f:
                    json.dump([
                        {
                            "type": i.type,
                            "severity": i.severity,
                            "filepath": i.filepath,
                            "description": i.description,
                            "suggestion": i.suggestion,
                        }
                        for i in iteration.security_issues
                    ], f, indent=2)

        return run_dir

    @classmethod
    def load(cls, run_id: str, base_dir: Optional[Path] = None) -> "ExecutionContext":
        """Load context from disk."""
        base_dir = base_dir or Path("./output")
        run_dir = base_dir / f"run_{run_id}"

        if not run_dir.exists():
            raise FileNotFoundError(f"Run {run_id} not found")

        # Load metadata
        with open(run_dir / "metadata.json") as f:
            metadata = json.load(f)

        ctx = cls(task=metadata["task"], output_dir=base_dir)
        ctx.id = metadata["id"]
        ctx.created_at = datetime.fromisoformat(metadata["created_at"])
        ctx.updated_at = datetime.fromisoformat(metadata["updated_at"])

        # Load iterations
        for i in range(metadata["iterations"]):
            iter_dir = run_dir / f"iteration_{i+1}"
            if not iter_dir.exists():
                continue

            # Load report
            with open(iter_dir / "report.json") as f:
                report = json.load(f)

            # Load code blocks from files
            code_blocks = []
            code_dir = iter_dir
            for py_file in code_dir.rglob("*.py"):
                if py_file.name == "report.json":
                    continue
                with open(py_file) as f:
                    code_blocks.append(CodeBlock(
                        filepath=str(py_file.relative_to(code_dir)),
                        language="python",
                        content=f.read()
                    ))

            iteration = IterationResult(
                iteration=report["iteration"],
                architecture=None,  # Not saved separately
                code="",  # Loaded from files
                code_blocks=code_blocks,
                qa_issues=[],  # Would need to load from qa_issues.json
                security_issues=[],
                approved=report["approved"],
                reviewer_notes=report["reviewer_notes"],
                timestamp=datetime.fromisoformat(report["timestamp"])
            )

            ctx.iterations.append(iteration)

        return ctx
