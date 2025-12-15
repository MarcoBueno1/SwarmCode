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

"""Tests for security validator."""

import pytest

from src.utils.security_validator import SecurityValidator, SecurityIssue


class TestSecurityValidator:
    """Tests for SecurityValidator."""

    def setup_method(self):
        """Setup test fixtures."""
        self.validator = SecurityValidator()

    def test_detect_os_system(self):
        """Test detection of os.system()."""
        code = """
import os
os.system("ls -la")
"""
        issues = self.validator.validate("test.py", code)
        assert len(issues) > 0
        assert any(i.issue_type == "os_system" for i in issues)

    def test_detect_subprocess_shell(self):
        """Test detection of subprocess with shell=True."""
        code = """
import subprocess
subprocess.call("ls", shell=True)
"""
        issues = self.validator.validate("test.py", code)
        assert any(i.issue_type == "subprocess_shell" for i in issues)

    def test_detect_eval(self):
        """Test detection of eval()."""
        code = """
result = eval(user_input)
"""
        issues = self.validator.validate("test.py", code)
        assert any(i.issue_type == "eval" for i in issues)

    def test_detect_exec(self):
        """Test detection of exec()."""
        code = """
exec(code_string)
"""
        issues = self.validator.validate("test.py", code)
        assert any(i.issue_type == "exec" for i in issues)

    def test_detect_hardcoded_secret(self):
        """Test detection of hardcoded secrets."""
        code = """
password = "supersecret123"
"""
        issues = self.validator.validate("test.py", code)
        assert any(i.issue_type == "hardcoded_secret" for i in issues)

    def test_safe_code(self):
        """Test that safe code passes validation."""
        code = """
def add(a, b):
    return a + b
"""
        issues = self.validator.validate("test.py", code)
        assert len(issues) == 0

    def test_validate_multiple_files(self):
        """Test validating multiple files."""
        files = [
            ("file1.py", "os.system('ls')"),
            ("file2.py", "def safe(): pass"),
        ]
        issues = self.validator.validate_multiple(files)
        assert len(issues) == 1
        assert issues[0].filepath == "file1.py"

    def test_get_summary(self):
        """Test getting issue summary."""
        issues = [
            SecurityIssue("CRITICAL", "eval", "a.py", "desc"),
            SecurityIssue("HIGH", "exec", "b.py", "desc"),
            SecurityIssue("CRITICAL", "system", "c.py", "desc"),
        ]
        summary = self.validator.get_summary(issues)
        assert summary["CRITICAL"] == 2
        assert summary["HIGH"] == 1
        assert summary["MEDIUM"] == 0
        assert summary["LOW"] == 0
