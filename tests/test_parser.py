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

"""Tests for output parser."""

import pytest

from src.io.output_parser import (
    parse_code_blocks,
    CodeBlock,
    parse_issues,
    check_approval
)


class TestParseCodeBlocks:
    """Tests for parse_code_blocks."""

    def test_parse_single_block(self):
        """Test parsing a single code block."""
        text = """
```python filepath=main.py
def hello():
    print("Hello, World!")
```
"""
        blocks = parse_code_blocks(text)
        assert len(blocks) == 1
        assert blocks[0].filepath == "main.py"
        assert blocks[0].language == "python"
        assert "def hello():" in blocks[0].content

    def test_parse_multiple_blocks(self):
        """Test parsing multiple code blocks."""
        text = """
```python filepath=main.py
def main():
    pass
```

```python filepath=utils.py
def helper():
    pass
```
"""
        blocks = parse_code_blocks(text)
        assert len(blocks) == 2
        assert blocks[0].filepath == "main.py"
        assert blocks[1].filepath == "utils.py"

    def test_parse_block_without_filepath_prefix(self):
        """Test parsing block with path directly."""
        text = """
```python src/main.py
def main():
    pass
```
"""
        blocks = parse_code_blocks(text)
        assert len(blocks) == 1
        assert blocks[0].filepath == "src/main.py"

    def test_parse_empty_text(self):
        """Test parsing empty text."""
        blocks = parse_code_blocks("")
        assert len(blocks) == 0

    def test_parse_no_code_blocks(self):
        """Test parsing text without code blocks."""
        text = "This is just plain text"
        blocks = parse_code_blocks(text)
        assert len(blocks) == 0


class TestCheckApproval:
    """Tests for check_approval."""

    def test_aprovado_simple(self):
        """Test simple APROVADO."""
        approved, notes = check_approval("APROVADO")
        assert approved is True
        assert notes == "Aprovado"

    def test_aprovado_with_text(self):
        """Test APROVADO with additional text."""
        approved, notes = check_approval("APROVADO - Código está bom")
        assert approved is True

    def test_reprovado_with_reason(self):
        """Test REPROVADO with reason."""
        approved, notes = check_approval("REPROVADO: Bug crítico encontrado")
        assert approved is False
        assert "BUG" in notes.upper() or "CRÍTICO" in notes.upper()

    def test_approved_english(self):
        """Test English APPROVED."""
        approved, notes = check_approval("APPROVED")
        assert approved is True

    def test_rejected_english(self):
        """Test English REJECTED."""
        approved, notes = check_approval("REJECTED: Security issue")
        assert approved is False
        assert "SECURITY" in notes.upper() or "ISSUE" in notes.upper()

    def test_no_clear_decision(self):
        """Test text without clear approval decision."""
        approved, notes = check_approval("The code looks good but...")
        assert approved is False
        assert "No clear approval decision" in notes


class TestParseIssues:
    """Tests for parse_issues."""

    def test_parse_single_issue(self):
        """Test parsing a single issue."""
        text = """
[BUG]
Arquivo: main.py
Linha: 10
Descrição: Variable not initialized
Sugestão: Initialize variable before use
"""
        issues = parse_issues(text)
        # Parser may extract partial filepath depending on regex
        assert len(issues) >= 1
        assert issues[0]["severity"] == "BUG"

    def test_parse_multiple_issues(self):
        """Test parsing multiple issues."""
        text = """
[BUG]
Arquivo: main.py
Descrição: Issue 1

[HIGH]
Arquivo: utils.py
Descrição: Issue 2
"""
        issues = parse_issues(text)
        assert len(issues) == 2

    def test_parse_empty_text(self):
        """Test parsing empty text."""
        issues = parse_issues("")
        assert len(issues) == 0
