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

"""Provider factory for creating AI providers."""

from typing import Optional

from ..config import Config, ProviderType
from .base import AIProvider
from .qwen_provider import QwenProvider
from .claude_provider import ClaudeProvider
from .gpt_provider import GPTProvider
from .gemini_provider import GeminiProvider


class ProviderFactory:
    """Factory for creating AI providers."""

    @staticmethod
    def create(config: Optional[Config] = None) -> AIProvider:
        """
        Create an AI provider based on configuration.

        Args:
            config: Application configuration. If None, loads default config.

        Returns:
            Configured AI provider instance

        Raises:
            ValueError: If provider type is not supported
            ImportError: If required package is not installed
        """
        if config is None:
            from ..config import get_config
            config = get_config()

        provider_type = config.provider

        if provider_type == ProviderType.QWEN:
            return QwenProvider(timeout=config.timeout)

        elif provider_type == ProviderType.CLAUDE:
            if not config.anthropic_api_key:
                raise ValueError(
                    "ANTHROPIC_API_KEY not set. "
                    "Please set it in .env file or environment variable."
                )
            model = config.model or "claude-sonnet-4-20250514"
            return ClaudeProvider(
                api_key=config.anthropic_api_key,
                model=model,
                timeout=config.timeout
            )

        elif provider_type == ProviderType.GPT:
            if not config.openai_api_key:
                raise ValueError(
                    "OPENAI_API_KEY not set. "
                    "Please set it in .env file or environment variable."
                )
            model = config.model or "gpt-4o"
            return GPTProvider(
                api_key=config.openai_api_key,
                model=model,
                timeout=config.timeout
            )

        elif provider_type == ProviderType.GEMINI:
            if not config.gemini_api_key:
                raise ValueError(
                    "GEMINI_API_KEY not set. "
                    "Please set it in .env file or environment variable."
                )
            model = config.model or "gemini-pro"
            return GeminiProvider(
                api_key=config.gemini_api_key,
                model=model,
                timeout=config.timeout
            )

        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")

    @staticmethod
    def list_providers() -> list[str]:
        """List all available provider types."""
        return [p.value for p in ProviderType]

    @staticmethod
    def get_default_model(provider_type: ProviderType) -> str:
        """Get default model name for a provider type."""
        defaults = {
            ProviderType.QWEN: "qwen2.5-coder",
            ProviderType.CLAUDE: "claude-sonnet-4-20250514",
            ProviderType.GPT: "gpt-4o",
            ProviderType.GEMINI: "gemini-pro",
        }
        return defaults.get(provider_type, "unknown")
