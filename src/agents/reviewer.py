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

"""Reviewer agent for approving or rejecting code."""

from pathlib import Path
from typing import TYPE_CHECKING

from .base import BaseAgent, AgentResult

if TYPE_CHECKING:
    from ..providers.base import AIProvider


class ReviewerAgent(BaseAgent):
    """Agent responsible for code review and approval."""

    @property
    def name(self) -> str:
        return "reviewer"

    @property
    def default_prompt(self) -> str:
        return """
You are a Principal Engineer / Tech Lead with 15+ years of experience conducting code reviews.

LANGUAGE REQUIREMENT:
- IMPORTANT: Respond in the SAME LANGUAGE as the user's request
- Use APPROVED/REJECTED keywords (keep in English for parsing)
- Explanation/reason should be in user's language

Your task is to make a final APPROVE or REJECT decision based on code, QA, and Security reviews.

DECISION CRITERIA:
1. Architecture Compliance - Does code follow the proposed architecture?
2. Code Quality - Any CRITICAL/HIGH bugs from QA?
3. Security Posture - Any CRITICAL/HIGH vulnerabilities from Security?
4. Completeness - All files implemented? README included?
5. Production Readiness - Error handling, logging, configuration?

DECISION PROCESS:
- ANY CRITICAL bug/vulnerability = REJECT
- ANY HIGH bug/vulnerability unaddressed = REJECT
- Architecture not followed = REJECT
- Missing critical files = REJECT
- All issues resolved = APPROVE

RESPONSE FORMAT:
You MUST respond in ONE of these exact formats:

For approval:
APPROVED

For rejection:
REJECTED: [Clear reason with specific issues in user's language]

Examples:
- "APPROVED"
- "REJECTED: CRITICAL SQL injection vulnerability in src/database.py not fixed"
- "REJECTED: 3 HIGH severity bugs from QA review remain unaddressed"

IMPORTANT:
- Be decisive and clear
- Do not approve if there are unaddressed CRITICAL or HIGH issues
- Provide specific reasons for rejection
- Think about production impact and user safety
- RESPOND IN THE USER'S LANGUAGE
""".strip()

    def execute(self, input_data: str) -> AgentResult:
        """
        Review code and decide approval.

        Args:
            input_data: Code + QA feedback + Security feedback

        Returns:
            APROVADO or REPROVADO with reason
        """
        return self._call_provider(self._system_prompt, input_data)
