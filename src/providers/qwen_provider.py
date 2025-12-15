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

"""Qwen provider implementation using subprocess."""

import subprocess
import time
from pathlib import Path
from typing import Optional

from .base import AIProvider, ChatResponse


class QwenProvider(AIProvider):
    """Qwen AI provider using CLI command.
    
    Maintains 100% compatibility with the original SwarmCode implementation.
    Uses the same prompt format: "{system}\n\nTAREFA:\n{user}"
    """

    def __init__(
        self,
        timeout: int = 120,
        command: str = "qwen",
        agents_dir: Optional[Path] = None
    ):
        self._timeout = timeout
        self._command = command
        self._agents_dir = agents_dir
        self._prompts_cache = {}

    @property
    def name(self) -> str:
        return "qwen"

    @property
    def model(self) -> str:
        return "qwen2.5-coder"

    def _load_prompt_from_file(self, agent_name: str) -> str:
        """Load agent prompt from agents directory (legacy compatibility)."""
        if agent_name in self._prompts_cache:
            return self._prompts_cache[agent_name]

        if self._agents_dir is None:
            raise ValueError("agents_dir not set")

        prompt_file = self._agents_dir / f"{agent_name}.txt"
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

        with open(prompt_file, "r") as f:
            prompt = f.read().strip()

        self._prompts_cache[agent_name] = prompt
        return prompt

    def chat(self, system: str, user: str) -> str:
        """
        Send message to Qwen via CLI.
        
        Uses the exact same prompt format as the original implementation:
        "{system_prompt}\n\nTAREFA:\n{user_prompt}"
        
        Args:
            system: System prompt (agent role)
            user: User prompt (task/input)
            
        Returns:
            Qwen response
            
        Raises:
            TimeoutError: If request exceeds timeout
            RuntimeError: If qwen command not found
        """
        # Format prompt exactly like the original implementation
        prompt = f"{system}\n\nTAREFA:\n{user}"

        start_time = time.time()
        process = subprocess.Popen(
            [self._command],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        try:
            output, _ = process.communicate(prompt, timeout=self._timeout)
            latency = (time.time() - start_time) * 1000
            return output.strip()
        except subprocess.TimeoutExpired:
            process.kill()
            raise TimeoutError(f"Qwen request timed out after {self._timeout}s")
        except FileNotFoundError:
            raise RuntimeError(
                f"Qwen command '{self._command}' not found. "
                "Please install qwen CLI or configure a different provider."
            )

    def check_health(self) -> bool:
        """Check if Qwen CLI is available."""
        try:
            result = subprocess.run(
                [self._command, "--help"],
                capture_output=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
