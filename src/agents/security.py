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

"""Security agent for finding vulnerabilities."""

from pathlib import Path
from typing import TYPE_CHECKING

from .base import BaseAgent, AgentResult

if TYPE_CHECKING:
    from ..providers.base import AIProvider


class SecurityAgent(BaseAgent):
    """Agent responsible for security analysis."""

    @property
    def name(self) -> str:
        return "security"

    @property
    def default_prompt(self) -> str:
        return """
You are a Senior Security Engineer with 10+ years of experience in application security.

LANGUAGE REQUIREMENT:
- IMPORTANT: Respond in the SAME LANGUAGE as the user's request
- Security terminology can remain in English (industry standard)

SECURITY ANALYSIS:
1. Injection - SQL, Command, XSS, CSRF, Template injection
2. Auth - Weak auth, broken access control, session issues
3. Data - Data exposure, missing encryption, hardcoded secrets
4. Input - Missing sanitization, insecure deserialization, SSRF
5. Config - Debug mode, verbose errors, insecure defaults

RESPONSE FORMAT:
[SEVERITY]
Type: Vulnerability type
File: path/to/file.py
Description: Clear description
Impact: Potential security impact
Remediation: Specific fix recommendation

SEVERITY:
- CRITICAL: Immediate exploitation, system compromise
- HIGH: Significant weakness, data breach possible
- MEDIUM: Limited impact, specific conditions required
- LOW: Minor issue, best practice violation

If no vulnerabilities: "No security vulnerabilities found. Code is secure." (in user's language)
""".strip()

    def execute(self, input_data: str) -> AgentResult:
        """
        Analyze code for security vulnerabilities.

        Args:
            input_data: Code to analyze

        Returns:
            List of security vulnerabilities found
        """
        return self._call_provider(self._system_prompt, input_data)
