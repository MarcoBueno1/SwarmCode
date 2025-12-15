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

"""Base agent class for Qwen-Agentes."""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..providers.base import AIProvider


@dataclass
class AgentResult:
    """Result from an agent execution."""
    content: str
    latency_ms: float
    tokens_used: Optional[int] = None


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(
        self,
        provider: AIProvider,
        prompt_file: Optional[Path] = None,
        temperature: float = 0.2
    ):
        self._provider = provider
        self._temperature = temperature
        self._system_prompt = self._load_prompt(prompt_file) if prompt_file else self.default_prompt

    @property
    @abstractmethod
    def name(self) -> str:
        """Return agent name."""
        pass

    @property
    def default_prompt(self) -> str:
        """Return default system prompt for this agent."""
        return ""

    def _load_prompt(self, prompt_file: Path) -> str:
        """Load system prompt from file."""
        with open(prompt_file, "r") as f:
            return f.read().strip()

    @abstractmethod
    def execute(self, input_data: str) -> AgentResult:
        """
        Execute the agent's task.

        Args:
            input_data: Input data for the agent

        Returns:
            AgentResult with the agent's response
        """
        pass

    def _call_provider(self, system: str, user: str) -> AgentResult:
        """Call the AI provider and measure latency."""
        start_time = time.time()
        response = self._provider.chat(system, user)
        latency = (time.time() - start_time) * 1000
        return AgentResult(content=response, latency_ms=latency)
