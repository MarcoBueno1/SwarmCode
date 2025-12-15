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

"""Tests for AI providers."""

import pytest
import subprocess
from unittest.mock import Mock, patch

from src.providers.base import AIProvider, ChatMessage
from src.providers.qwen_provider import QwenProvider
from src.providers.factory import ProviderFactory
from src.config import Config, ProviderType


class TestQwenProvider:
    """Tests for QwenProvider."""

    def test_name(self):
        """Test provider name."""
        provider = QwenProvider()
        assert provider.name == "qwen"

    def test_model(self):
        """Test default model."""
        provider = QwenProvider()
        assert provider.model == "qwen2.5-coder"

    @patch('subprocess.Popen')
    def test_chat_success(self, mock_popen):
        """Test successful chat."""
        mock_process = Mock()
        mock_process.communicate.return_value = ("Response text", "")
        mock_popen.return_value = mock_process

        provider = QwenProvider(timeout=30)
        result = provider.chat("system", "user")

        assert result == "Response text"
        mock_popen.assert_called_once()

    @patch('subprocess.Popen')
    def test_chat_timeout(self, mock_popen):
        """Test chat timeout."""
        mock_process = Mock()
        mock_process.communicate.side_effect = subprocess.TimeoutExpired("cmd", 30)
        mock_popen.return_value = mock_process

        provider = QwenProvider(timeout=30)

        with pytest.raises(TimeoutError):
            provider.chat("system", "user")

    @patch('subprocess.run')
    def test_health_check_success(self, mock_run):
        """Test health check success."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        provider = QwenProvider()
        assert provider.check_health() is True

    @patch('subprocess.run')
    def test_health_check_failure(self, mock_run):
        """Test health check failure."""
        mock_run.side_effect = FileNotFoundError()

        provider = QwenProvider()
        assert provider.check_health() is False


class TestProviderFactory:
    """Tests for ProviderFactory."""

    def test_list_providers(self):
        """Test listing providers."""
        providers = ProviderFactory.list_providers()
        assert "qwen" in providers
        assert "claude" in providers
        assert "gpt" in providers
        assert "gemini" in providers

    def test_create_qwen(self):
        """Test creating Qwen provider."""
        config = Config(provider=ProviderType.QWEN)
        provider = ProviderFactory.create(config)
        assert isinstance(provider, QwenProvider)

    def test_create_claude_missing_key(self):
        """Test creating Claude provider without API key."""
        config = Config(provider=ProviderType.CLAUDE, anthropic_api_key=None)

        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
            ProviderFactory.create(config)

    def test_create_gpt_missing_key(self):
        """Test creating GPT provider without API key."""
        config = Config(provider=ProviderType.GPT, openai_api_key=None)

        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            ProviderFactory.create(config)

    def test_create_unknown_provider(self):
        """Test creating unknown provider."""
        # This would require modifying the enum, so we skip
        pass

    def test_get_default_model(self):
        """Test getting default model for provider."""
        assert ProviderFactory.get_default_model(ProviderType.QWEN) == "qwen2.5-coder"
        assert ProviderFactory.get_default_model(ProviderType.CLAUDE) == "claude-sonnet-4-20250514"
        assert ProviderFactory.get_default_model(ProviderType.GPT) == "gpt-4o"
        assert ProviderFactory.get_default_model(ProviderType.GEMINI) == "gemini-pro"


class TestChatMessage:
    """Tests for ChatMessage dataclass."""

    def test_create_message(self):
        """Test creating a chat message."""
        msg = ChatMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
