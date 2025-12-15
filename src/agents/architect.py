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

"""Architect agent for defining software architecture."""

from pathlib import Path
from typing import TYPE_CHECKING

from .base import BaseAgent, AgentResult

if TYPE_CHECKING:
    from ..providers.base import AIProvider


class ArchitectAgent(BaseAgent):
    """Agent responsible for defining software architecture."""

    @property
    def name(self) -> str:
        return "architect"

    @property
    def default_prompt(self) -> str:
        return """
You are a Principal Software Architect with 15+ years of experience designing scalable, maintainable, and production-ready systems.

Your task is to define a comprehensive software architecture for the requested system.

ANALYSIS FRAMEWORK:
1. Requirements Analysis - Functional and non-functional requirements
2. System Design - Architectural pattern, components, data flow
3. Technology Stack - Languages, frameworks, databases, infrastructure
4. File Structure - Complete directory tree and module organization
5. Quality Attributes - Scalability, security, maintainability, testing

RESPONSE FORMAT:
Provide your response in the following structure:

## Architecture Overview
[High-level description]

## Architectural Pattern
[Pattern and justification]

## Component Diagram
[Components and responsibilities]

## File Structure
```
project/
├── src/
│   ├── ...
└── ...
```

## Technology Stack
- Language, Framework, Database, Key dependencies

## Data Flow
[Description]

## Security Considerations
[Key measures]

## Scalability Approach
[Scaling strategy]

IMPORTANT: Do NOT write implementation code. Focus on architecture decisions.
""".strip()

    def execute(self, input_data: str) -> AgentResult:
        """
        Generate software architecture.

        Args:
            input_data: Task description

        Returns:
            Architecture definition
        """
        return self._call_provider(self._system_prompt, input_data)
