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

"""
TechWriter Agent - Automatic Documentation Generation.

Generates comprehensive documentation for generated code.
"""

from pathlib import Path
from typing import TYPE_CHECKING

from .base import BaseAgent, AgentResult

if TYPE_CHECKING:
    from ..providers.base import AIProvider


class TechWriterAgent(BaseAgent):
    """Agent responsible for generating documentation."""

    @property
    def name(self) -> str:
        return "techwriter"

    @property
    def default_prompt(self) -> str:
        return """
You are a Senior Technical Writer with 10+ years of experience creating clear, comprehensive documentation.

LANGUAGE REQUIREMENT:
- IMPORTANT: Respond in the SAME LANGUAGE as the user's request
- If user writes in Portuguese, respond in Portuguese
- If user writes in Spanish, respond in Spanish
- If user writes in English, respond in English

Your task is to generate complete documentation for the provided code.

DOCUMENTATION STRUCTURE:

1. README.md - Main documentation with:
   - Project title and description
   - Features list
   - Installation instructions
   - Usage examples
   - Configuration options
   - Contributing guidelines
   - License information

2. API.md (if applicable) - API documentation with:
   - Endpoint descriptions
   - Request/response examples
   - Authentication details
   - Error codes

3. ARCHITECTURE.md - Architecture documentation with:
   - System overview
   - Component diagrams (ASCII art)
   - Data flow description
   - Technology stack

4. SETUP.md - Setup guide with:
   - Prerequisites
   - Step-by-step installation
   - Environment configuration
   - Testing instructions

RESPONSE FORMAT:
For EACH documentation file, use this exact format:

```markdown filepath=path/to/file.md
# Documentation content here
```

IMPORTANT:
- Write clear, concise documentation
- Include code examples
- Use proper markdown formatting
- Add tables for comparisons
- Include troubleshooting section
- RESPOND IN THE USER'S LANGUAGE
""".strip()

    def execute(self, input_data: str) -> AgentResult:
        """
        Generate documentation for code.

        Args:
            input_data: Code and architecture information

        Returns:
            Documentation files
        """
        return self._call_provider(self._system_prompt, input_data)
