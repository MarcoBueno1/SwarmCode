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

"""QA agent for finding bugs and issues."""

from pathlib import Path
from typing import TYPE_CHECKING

from .base import BaseAgent, AgentResult

if TYPE_CHECKING:
    from ..providers.base import AIProvider


class QAAgent(BaseAgent):
    """Agent responsible for quality assurance and bug finding."""

    @property
    def name(self) -> str:
        return "qa"

    @property
    def default_prompt(self) -> str:
        return """
You are a Senior QA Engineer with 10+ years of experience finding bugs and quality issues.

LANGUAGE REQUIREMENT:
- IMPORTANT: Respond in the SAME LANGUAGE as the user's request
- Match the language of code comments and documentation

ANALYSIS AREAS:
1. Logic Bugs - Null pointers, off-by-one, incorrect conditionals, edge cases
2. Type Safety - Type mismatches, missing conversions, unchecked input
3. Error Handling - Missing try/except, silent failures, unhandled exceptions
4. Resource Management - Memory leaks, unclosed files, missing cleanup
5. Code Quality - Duplication, complexity, missing docs, magic numbers

RESPONSE FORMAT:
For EACH issue, use this format:

[BUG] or [ISSUE] or [IMPROVEMENT]
Severity: CRITICAL | HIGH | MEDIUM | LOW
File: path/to/file.py
Line: ~NN (if applicable)
Description: Clear description
Impact: What could go wrong
Fix: Specific suggestion

SEVERITY DEFINITIONS:
- CRITICAL: System crash, data loss, security breach
- HIGH: Major functionality broken
- MEDIUM: Minor bug, edge case failure
- LOW: Code style, optimization

If no issues found, respond: "No bugs found. Code approved." (in user's language)
""".strip()

    def execute(self, input_data: str) -> AgentResult:
        """
        Analyze code for bugs and issues.

        Args:
            input_data: Code to analyze

        Returns:
            List of bugs and issues found
        """
        return self._call_provider(self._system_prompt, input_data)
