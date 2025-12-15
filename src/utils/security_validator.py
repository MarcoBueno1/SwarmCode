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

"""Security validators for generated code."""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class SecurityIssue:
    """A security issue found in code."""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    issue_type: str
    filepath: str
    description: str
    line: Optional[int] = None
    pattern: Optional[str] = None


class SecurityValidator:
    """Validates code for security issues."""

    # Dangerous patterns to check
    DANGEROUS_PATTERNS = {
        "os_system": {
            "pattern": r"os\.system\s*\([^)]*\)",
            "severity": "CRITICAL",
            "description": "Use of os.system() can lead to command injection"
        },
        "subprocess_shell": {
            "pattern": r"subprocess\.(call|run|Popen)\s*\([^)]*shell\s*=\s*True",
            "severity": "CRITICAL",
            "description": "Using subprocess with shell=True can lead to command injection"
        },
        "eval": {
            "pattern": r"\beval\s*\(",
            "severity": "CRITICAL",
            "description": "Use of eval() can execute arbitrary code"
        },
        "exec": {
            "pattern": r"\bexec\s*\(",
            "severity": "CRITICAL",
            "description": "Use of exec() can execute arbitrary code"
        },
        "pickle": {
            "pattern": r"pickle\.load\s*\(",
            "severity": "HIGH",
            "description": "Unpickling untrusted data can execute arbitrary code"
        },
        "sql_injection": {
            "pattern": r"(execute|cursor\.execute)\s*\(\s*[\"'].*%.*[\"'].*%",
            "severity": "CRITICAL",
            "description": "Possible SQL injection vulnerability"
        },
        "hardcoded_secret": {
            "pattern": r"(password|secret|api_key|token)\s*=\s*[\"'][^\"']{8,}[\"']",
            "severity": "HIGH",
            "description": "Possible hardcoded secret"
        },
        "input_injection": {
            "pattern": r"input\s*\(\s*\)",
            "severity": "MEDIUM",
            "description": "User input without validation"
        },
    }

    def __init__(self):
        self.compiled_patterns = {
            name: re.compile(info["pattern"], re.MULTILINE)
            for name, info in self.DANGEROUS_PATTERNS.items()
        }

    def validate(self, filepath: str, code: str) -> list[SecurityIssue]:
        """
        Validate code for security issues.

        Args:
            filepath: Path to the file (for reporting)
            code: Code content to validate

        Returns:
            List of security issues found
        """
        issues = []

        for name, pattern in self.compiled_patterns.items():
            matches = pattern.finditer(code)
            for match in matches:
                # Calculate line number
                line_number = code[:match.start()].count('\n') + 1

                info = self.DANGEROUS_PATTERNS[name]
                issues.append(SecurityIssue(
                    severity=info["severity"],
                    issue_type=name,
                    filepath=filepath,
                    description=info["description"],
                    line=line_number,
                    pattern=match.group(0)
                ))

        return issues

    def validate_multiple(
        self,
        files: list[tuple[str, str]]
    ) -> list[SecurityIssue]:
        """
        Validate multiple files.

        Args:
            files: List of (filepath, code) tuples

        Returns:
            List of all security issues found
        """
        all_issues = []
        for filepath, code in files:
            issues = self.validate(filepath, code)
            all_issues.extend(issues)
        return all_issues

    def get_summary(self, issues: list[SecurityIssue]) -> dict:
        """Get summary of issues by severity."""
        summary = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0
        }

        for issue in issues:
            if issue.severity in summary:
                summary[issue.severity] += 1

        return summary
