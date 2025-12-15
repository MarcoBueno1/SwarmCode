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

"""Base provider interface for AI models."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ChatMessage:
    """A chat message."""
    role: str
    content: str


@dataclass
class ChatResponse:
    """Response from AI provider."""
    content: str
    model: str
    usage: Optional[dict] = None
    latency_ms: Optional[float] = None


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return provider name."""
        pass

    @property
    @abstractmethod
    def model(self) -> str:
        """Return default model name."""
        pass

    @abstractmethod
    def chat(self, system: str, user: str) -> str:
        """
        Send a chat message and get response.

        Args:
            system: System prompt
            user: User prompt

        Returns:
            AI response content
        """
        pass

    @abstractmethod
    def check_health(self) -> bool:
        """Check if provider is available."""
        pass

    def format_messages(self, system: str, user: str) -> list[ChatMessage]:
        """Format messages for the provider."""
        return [
            ChatMessage(role="system", content=system),
            ChatMessage(role="user", content=user)
        ]
