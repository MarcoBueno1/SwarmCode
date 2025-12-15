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

"""Parser for structured code output."""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class CodeBlock:
    """A parsed code block."""
    filepath: str
    language: str
    content: str


def parse_code_blocks(text: str) -> list[CodeBlock]:
    """
    Parse code blocks from text.

    Expects format:
    ```language filepath=path
    code content
    ```

    Or:
    ```language path
    code content
    ```
    """
    code_blocks = []

    # Pattern 1: ```language filepath=path
    pattern1 = r'```(\w+)\s+filepath=(.+?)\n(.*?)```'

    # Pattern 2: ```language path (no spaces in path)
    pattern2 = r'```(\w+)\s+([^\s`]+?\.[^\s`]+)\n(.*?)```'

    # Try pattern 1 first (explicit filepath=)
    matches = re.findall(pattern1, text, re.DOTALL)
    for match in matches:
        language, filepath, content = match
        code_blocks.append(CodeBlock(
            filepath=filepath.strip(),
            language=language.strip(),
            content=content.strip()
        ))

    # If no matches with pattern 1, try pattern 2
    if not code_blocks:
        matches = re.findall(pattern2, text, re.DOTALL)
        for match in matches:
            language, filepath, content = match
            # Filter out common non-file matches
            if filepath not in ['filepath', 'path', 'file']:
                code_blocks.append(CodeBlock(
                    filepath=filepath.strip(),
                    language=language.strip(),
                    content=content.strip()
                ))

    return code_blocks


def extract_architecture(text: str) -> Optional[str]:
    """Extract architecture section from text."""
    # Look for common architecture section headers
    patterns = [
        r'(?:##?\s*)?(?:arquitetura|architecture|visão\s+geral|overview).+?(?=(?:##?\s*|$))',
        r'(?:1\.?\s*)?(?:visão\s+geral|overview).+?(?=(?:2\.|$))',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(0).strip()

    return None


def parse_issues(text: str) -> list[dict]:
    """Parse issues from QA or Security output."""
    issues = []

    # Pattern for [TYPE] or [SEVERITY] issues
    pattern = r'\[(\w+)\]\s*\n?(?:Arquivo|File)?[:\s]*(.+?)?\n?(?:Linha|Line)?[:\s]*(\d+)?\n?(?:Descrição|Description)?[:\s]*(.+?)\n?(?:Sugestão|Correção|Impacto|Suggestion|Correction|Impact)?[:\s]*(.+?)(?=\n\n|\n\[|$)'

    matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
    for match in matches:
        severity, filepath, line, description, suggestion = match
        issues.append({
            "severity": severity.upper(),
            "filepath": filepath.strip() if filepath else "",
            "line": int(line) if line and line.isdigit() else None,
            "description": description.strip(),
            "suggestion": suggestion.strip() if suggestion else ""
        })

    return issues


def check_approval(text: str) -> tuple[bool, str]:
    """
    Check if code is approved.

    Returns:
        (approved, notes)
    """
    text_upper = text.upper().strip()

    # Check for APROVADO
    if text_upper.startswith("APROVADO") or text_upper == "APROVADO":
        return True, "Aprovado"

    # Check for REPROVADO
    if text_upper.startswith("REPROVADO"):
        # Extract reason
        reason = text_upper.replace("REPROVADO", "").strip(": \n")
        return False, reason if reason else "Reprovado"

    # Check for APPROVED (English)
    if text_upper.startswith("APPROVED") or text_upper == "APPROVED":
        return True, "Approved"

    # Check for REJECTED (English)
    if text_upper.startswith("REJECTED"):
        reason = text_upper.replace("REJECTED", "").strip(": \n")
        return False, reason if reason else "Rejected"

    # Default: not approved
    return False, "No clear approval decision found"
