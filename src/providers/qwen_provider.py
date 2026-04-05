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

import json
import fcntl
import os
import select
import subprocess
import time
from pathlib import Path
from typing import Optional

from .base import AIProvider, ChatResponse


class QwenProvider(AIProvider):
    """Qwen AI provider using CLI command.

    Features:
    - Configures YOLO mode for the target project directory
    - Streams all Qwen output to the terminal (like normal Qwen CLI)
    - Auto-answers questions from Qwen with full access
    """

    def __init__(
        self,
        timeout: int = 120,
        command: str = "qwen",
        agents_dir: Optional[Path] = None,
        project_dir: Optional[Path] = None,
        show_output: bool = True
    ):
        self._timeout = timeout
        self._command = command
        self._agents_dir = agents_dir
        self._project_dir = project_dir
        self._show_output = show_output
        self._prompts_cache = {}

        # Configure YOLO mode for the target project
        self._configure_yolo_mode()

    @property
    def name(self) -> str:
        return "qwen"

    @property
    def model(self) -> str:
        return "qwen2.5-coder"

    def _configure_yolo_mode(self):
        """Configure Qwen to use YOLO mode for the target project directory."""
        target_dir = self._project_dir
        if target_dir is None:
            # Default to SwarmCode project
            target_dir = Path(__file__).parent.parent.parent

        # Create/update .qwen/settings.json with yolo mode
        settings_dir = target_dir / ".qwen"
        settings_dir.mkdir(parents=True, exist_ok=True)
        settings_file = settings_dir / "settings.json"

        settings = {}
        if settings_file.exists():
            try:
                with open(settings_file, "r") as f:
                    settings = json.load(f)
            except (json.JSONDecodeError, IOError):
                settings = {}

        # Always force yolo mode
        settings["approvalMode"] = "yolo"

        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=2)

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
        Send message to Qwen via CLI with smart timeout that resets on output.

        The timeout only triggers when Qwen is silent for more than `timeout`
        seconds. Every time new output arrives, the countdown resets. This
        prevents timeouts on long-running tasks where Qwen is actively
        producing output (e.g. streaming tokens, writing many files).

        All output from Qwen is shown to the terminal in real-time.
        Questions from Qwen are auto-answered with full access (YOLO mode).

        Args:
            system: System prompt (agent role)
            user: User prompt (task/input)

        Returns:
            Qwen response

        Raises:
            TimeoutError: If Qwen is silent for more than timeout seconds
            RuntimeError: If qwen command not found
        """
        # Format prompt exactly like the original implementation
        prompt = f"{system}\n\nTAREFA:\n{user}"

        # Build command with yolo mode and auth type for non-interactive usage
        # --auth-type qwen-oauth is required because when Qwen is called via stdin pipe
        # (non-interactive), it can't access the browser-based OAuth session from the
        # interactive terminal. This flag tells it to use the cached OAuth token.
        cmd = [self._command, "--yolo", "--auth-type", "qwen-oauth"]

        start_time = time.time()
        output_buffer: list[str] = []

        try:
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Merge stderr into stdout
                text=False,  # Binary mode for unbuffered reads
                bufsize=0,  # Unbuffered for real-time reads
                cwd=self._project_dir  # Run from project directory
            )

            # Send prompt and close stdin to signal EOF
            process.stdin.write(prompt.encode("utf-8"))
            process.stdin.close()

            # Make stdout non-blocking so we can poll with select
            fd = process.stdout.fileno()
            flags = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

            last_output_time = time.time()
            chunk_size = 4096
            output_buffer: list[bytes] = []

            while True:
                # Check if process has exited
                if process.poll() is not None:
                    # Read any remaining data
                    try:
                        remaining = os.read(fd, chunk_size)
                        while remaining:
                            output_buffer.append(remaining)
                            if self._show_output:
                                print(remaining.decode("utf-8", errors="replace"), end="", flush=True)
                            remaining = os.read(fd, chunk_size)
                    except (IOError, OSError):
                        pass
                    break

                # Wait for data with short poll interval
                ready, _, _ = select.select([process.stdout], [], [], 0.1)
                if ready:
                    try:
                        data = os.read(fd, chunk_size)
                        if data:
                            output_buffer.append(data)
                            # Reset the idle timer on every new chunk
                            last_output_time = time.time()
                            if self._show_output:
                                print(data.decode("utf-8", errors="replace"), end="", flush=True)
                    except (IOError, OSError):
                        # Process exited or pipe closed
                        break

                # Check idle timeout — only fires when Qwen is silent
                elapsed_idle = time.time() - last_output_time
                if elapsed_idle > self._timeout:
                    process.kill()
                    total = time.time() - start_time
                    raise TimeoutError(
                        f"Qwen was silent for {self._timeout}s "
                        f"(total elapsed: {total:.0f}s)"
                    )

            # Wait for clean exit (already exited or just finished)
            process.wait()

            total_elapsed = (time.time() - start_time) * 1000
            stdout_data = b"".join(output_buffer).decode("utf-8", errors="replace")
            return stdout_data.strip() if stdout_data else ""

        except TimeoutError:
            raise  # Re-raise our own timeouts
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
