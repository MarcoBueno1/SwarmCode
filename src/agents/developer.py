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

"""Developer agent for implementing code."""

from pathlib import Path
from typing import TYPE_CHECKING

from .base import BaseAgent, AgentResult

if TYPE_CHECKING:
    from ..providers.base import AIProvider


class DeveloperAgent(BaseAgent):
    """Agent responsible for implementing code."""

    @property
    def name(self) -> str:
        return "developer"

    @property
    def default_prompt(self) -> str:
        return """
You are a Senior Software Engineer with 10+ years of experience writing clean, efficient, and production-ready code.

Your task is to implement the complete system based on the provided architecture.

CODING STANDARDS:
1. Clean Code - SOLID, DRY, KISS principles
2. Documentation - Docstrings, type hints, comments for complex logic
3. Best Practices - Input validation, security, performance, testability
4. Structure - Follow architecture exactly, proper imports and modules

RESPONSE FORMAT:
For EACH file, use this exact format:

```language filepath=path/to/file.ext
# Complete file content here
```

REQUIREMENTS:
1. Implement ALL files from the architecture
2. Include comprehensive error handling
3. Add logging where appropriate
4. Include configuration options
5. Write a complete README.md

DELIVERABLES:
- All source code files
- Requirements/dependencies file
- README.md with installation and usage instructions
- Configuration files

IMPORTANT: Write production-ready code. Assume this will be used by real users.
""".strip()

    def execute(self, input_data: str) -> AgentResult:
        """
        Implement code based on architecture.

        Args:
            input_data: Architecture definition and requirements

        Returns:
            Complete code implementation
        """
        return self._call_provider(self._system_prompt, input_data)
