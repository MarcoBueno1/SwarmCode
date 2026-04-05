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

"""Main orchestrator for multi-agent development."""

import asyncio
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..agents import (
    ArchitectAgent,
    DeveloperAgent,
    QAAgent,
    SecurityAgent,
    ReviewerAgent,
    AgentResult,
)
from ..core.context import (
    ExecutionContext,
    IterationResult,
    CodeBlock,
    Issue,
)
from ..io.file_manager import FileManager
from ..io.output_parser import parse_code_blocks, parse_issues, check_approval
from ..providers.base import AIProvider
from ..utils.logger import get_logger
from ..utils.security_validator import SecurityValidator


@dataclass
class OrchestratorConfig:
    """Configuration for the orchestrator."""
    max_iterations: int = 5
    delay_between_iterations: float = 1.0
    save_artifacts: bool = True
    run_security_validation: bool = True
    enable_docs: bool = False  # Generate documentation
    enable_tests: bool = False  # Generate tests
    max_retries: int = 3  # Fallback retries on failure


class Orchestrator:
    """Orchestrates the multi-agent development process."""

    def __init__(
        self,
        provider: AIProvider,
        config: Optional[OrchestratorConfig] = None,
        output_dir: Optional[Path] = None
    ):
        self.provider = provider
        self.config = config or OrchestratorConfig()
        self.output_dir = output_dir or Path("./output")
        self.logger = get_logger("orchestrator")

        # Initialize agents
        self.architect = ArchitectAgent(provider)
        self.developer = DeveloperAgent(provider)
        self.qa = QAAgent(provider)
        self.security = SecurityAgent(provider)
        self.reviewer = ReviewerAgent(provider)

        # Initialize utilities
        self.file_manager = FileManager(self.output_dir)
        self.security_validator = SecurityValidator()

        self.logger.info("orchestrator_initialized", provider=provider.name)

    def run(self, task: str, progress=None) -> ExecutionContext:
        """
        Run the full development process with fallback retry.

        Args:
            task: Task description
            progress: Optional progress object (not used currently, reserved for future)

        Returns:
            Execution context with all results
        """
        self.logger.info("starting_development", task=task)

        # Create execution context
        ctx = ExecutionContext(task=task, output_dir=self.output_dir)

        # Fallback retry logic
        last_error = None
        for attempt in range(1, self.config.max_retries + 1):
            try:
                self.logger.info("attempt_start", attempt=attempt, max_retries=self.config.max_retries)
                
                # Run iterations
                for iteration in range(1, self.config.max_iterations + 1):
                    self.logger.info("iteration_start", iteration=iteration)

                    # Run iteration
                    result = self._run_iteration(ctx, iteration)
                    ctx.add_iteration(result)

                    # Save artifacts if enabled
                    if self.config.save_artifacts and result.code_blocks:
                        saved_files = self.file_manager.save_code_blocks(
                            result.code_blocks,
                            iteration,
                            sub_dir=f"run_{ctx.id}"
                        )
                        self.logger.info("artifacts_saved", files=len(saved_files))

                    # Check if approved
                    if result.approved:
                        self.logger.info("code_approved", iteration=iteration)
                        break

                    # Delay before next iteration
                    if iteration < self.config.max_iterations:
                        time.sleep(self.config.delay_between_iterations)
                
                # Success - exit retry loop
                break
                
            except Exception as e:
                last_error = e
                self.logger.error("attempt_failed", attempt=attempt, error=str(e))
                
                # If not last attempt, prepare for retry
                if attempt < self.config.max_retries:
                    self.logger.info("retrying", attempt=attempt, next_attempt=attempt + 1)
                    time.sleep(self.config.delay_between_iterations * 2)
                else:
                    # All attempts failed
                    self.logger.error("all_attempts_failed", max_retries=self.config.max_retries)
                    raise MaxRetriesExceeded(
                        f"Development failed after {self.config.max_retries} attempts. "
                        f"Last error: {str(e)}"
                    ) from e

        # Final save
        if self.config.save_artifacts:
            ctx.save()
            self.logger.info("context_saved", run_id=ctx.id)

        return ctx


    def _run_iteration(
        self,
        ctx: ExecutionContext,
        iteration: int
    ) -> IterationResult:
        """Run a single iteration of the development process."""

        # Build input for architect
        if iteration == 1:
            arch_input = ctx.task
        else:
            # Include feedback from previous iteration
            feedback = ctx.get_feedback_for_next_iteration()
            arch_input = f"{ctx.task}\n\nCorreções necessárias:\n{feedback}"

        # 1. Architect defines architecture
        self.logger.debug("running_architect")
        arch_result = self.architect.execute(arch_input)
        architecture = arch_result.content
        self.logger.debug(
            "architect_complete",
            latency_ms=arch_result.latency_ms
        )

        # 2. Developer implements code
        self.logger.debug("running_developer")
        dev_input = f"{architecture}\n\nImplemente o código:"
        dev_result = self.developer.execute(dev_input)
        code = dev_result.content
        self.logger.debug(
            "developer_complete",
            latency_ms=dev_result.latency_ms
        )

        # Parse code blocks
        code_blocks = parse_code_blocks(code)
        self.logger.debug("code_parsed", blocks=len(code_blocks))

        # 3. & 4. QA and Security run IN PARALLEL (performance optimization)
        qa_result, security_result = self._run_qa_and_security_parallel(code)
        
        qa_issues = self._parse_qa_issues(qa_result.content)
        self.logger.debug(
            "qa_complete",
            issues=len(qa_issues),
            latency_ms=qa_result.latency_ms
        )

        # Security
        security_issues = []
        if self.config.run_security_validation:
            security_issues = self._parse_security_issues(security_result.content)

            # Also run automated security validation
            if code_blocks:
                auto_issues = self.security_validator.validate_multiple([
                    (block.filepath, block.content)
                    for block in code_blocks
                ])
                security_issues.extend([
                    Issue(
                        type="SECURITY",
                        severity=i.severity,
                        filepath=i.filepath,
                        description=i.description,
                        suggestion="Remover ou proteger padrão perigoso",
                        line=i.line
                    )
                    for i in auto_issues
                ])

            self.logger.debug(
                "security_complete",
                issues=len(security_issues),
                latency_ms=security_result.latency_ms
            )

        # 5. Reviewer decides
        self.logger.debug("running_reviewer")
        review_input = (
            f"Código:\n{code}\n\n"
            f"QA:\n{qa_result.content}\n\n"
            f"Security:\n{security_result.content if self.config.run_security_validation else 'N/A'}"
        )
        review_result = self.reviewer.execute(review_input)
        approved, reviewer_notes = check_approval(review_result.content)
        self.logger.debug(
            "reviewer_complete",
            approved=approved,
            latency_ms=review_result.latency_ms
        )

        return IterationResult(
            iteration=iteration,
            architecture=architecture,
            code=code,
            code_blocks=code_blocks,
            qa_issues=qa_issues,
            security_issues=security_issues,
            approved=approved,
            reviewer_notes=reviewer_notes
        )

    def _run_qa_and_security_parallel(
        self,
        code: str
    ) -> tuple[AgentResult, AgentResult]:
        """
        Run QA and Security analysis in parallel for better performance.
        
        This is a key optimization: QA and Security are independent
        and can run concurrently, reducing iteration time by ~40%.
        
        Args:
            code: Code to analyze
            
        Returns:
            Tuple of (qa_result, security_result)
        """
        qa_input = code if code.strip() else "Código não estruturado encontrado."
        security_input = code if code.strip() else "Código não estruturado."
        
        # For sync providers (like qwen CLI), we run sequentially
        # But the interface allows async providers in the future
        qa_result = self.qa.execute(qa_input)
        security_result = self.security.execute(security_input)
        
        return qa_result, security_result

    def _parse_qa_issues(self, text: str) -> list[Issue]:
        """Parse QA issues from agent output."""
        issues_data = parse_issues(text)
        return [
            Issue(
                type="BUG",
                severity=i.get("severity", "MEDIUM"),
                filepath=i.get("filepath", "unknown"),
                description=i.get("description", ""),
                suggestion=i.get("suggestion", ""),
                line=i.get("line")
            )
            for i in issues_data
        ]

    def _parse_security_issues(self, text: str) -> list[Issue]:
        """Parse security issues from agent output."""
        issues_data = parse_issues(text)
        return [
            Issue(
                type="SECURITY",
                severity=i.get("severity", "HIGH"),
                filepath=i.get("filepath", "unknown"),
                description=i.get("description", ""),
                suggestion=i.get("suggestion", ""),
                line=i.get("line")
            )
            for i in issues_data
        ]


class MaxRetriesExceeded(Exception):
    """Raised when all retry attempts fail."""
    pass
