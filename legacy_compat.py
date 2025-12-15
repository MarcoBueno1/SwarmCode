#!/usr/bin/env python3
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
Legacy compatibility mode for SwarmCode.

This script maintains 100% compatibility with the original SwarmCode
implementation, using the same prompts from agents/ directory and the
same execution flow.

Usage:
    python legacy_compat.py
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.providers.qwen_provider import QwenProvider
from src.agents.base import BaseAgent, AgentResult
from src.providers.base import AIProvider


class LegacyAgent(BaseAgent):
    """Agent that loads prompts from agents/ directory (legacy mode)."""

    def __init__(self, provider: AIProvider, name: str, agents_dir: Path):
        self._name = name
        prompt_file = agents_dir / f"{name}.txt"
        super().__init__(provider, prompt_file)

    @property
    def name(self) -> str:
        return self._name

    def execute(self, input_data: str) -> AgentResult:
        """Execute agent task."""
        return self._call_provider(self._system_prompt, input_data)


def main():
    """Run in legacy compatibility mode."""
    print("=" * 60)
    print("Qwen-Agentes - Legacy Compatibility Mode")
    print("=" * 60)

    # Check if qwen is available
    provider = QwenProvider()
    if not provider.check_health():
        print("\n[ERROR] qwen command not found!")
        print("Please install qwen CLI or use a different provider.")
        sys.exit(1)

    print("\n[OK] qwen CLI is available\n")

    # Load agents from agents/ directory
    agents_dir = Path(__file__).parent / "orchestrator" / "agents"

    if not agents_dir.exists():
        print(f"[ERROR] Agents directory not found: {agents_dir}")
        sys.exit(1)

    print(f"Loading agents from: {agents_dir}\n")

    architect = LegacyAgent(provider, "architect", agents_dir)
    developer = LegacyAgent(provider, "developer", agents_dir)
    qa = LegacyAgent(provider, "qa", agents_dir)
    security = LegacyAgent(provider, "security", agents_dir)
    reviewer = LegacyAgent(provider, "reviewer", agents_dir)

    # Get task from user
    task = input("O que deseja construir?\n")

    context = {"task": task}
    max_iter = 5

    for i in range(max_iter):
        print(f"\n{'=' * 60}")
        print(f"ITERACAO {i+1}/{max_iter}")
        print(f"{'=' * 60}")

        # Architect
        print("\n[ARCHITECT] Thinking...")
        arch = architect.execute(context["task"])
        print(f"\n{arch.content}")

        # Developer
        print("\n[DEVELOPER] Coding...")
        code = developer.execute(arch.content)
        print(f"\n{code}")

        # QA
        print("\n[QA] Reviewing...")
        qa_out = qa.execute(code)
        print(f"\n{qa_out}")

        # Security
        print("\n[SECURITY] Auditing...")
        sec_out = security.execute(code)
        print(f"\n{sec_out}")

        # Reviewer
        print("\n[REVIEWER] Deciding...")
        review_input = f"Codigo:\n{code}\n\nQA:\n{qa_out}\n\nSecurity:\n{sec_out}"
        decision = reviewer.execute(review_input)
        print(f"\n{decision}")

        if "APROVADO" in decision.upper():
            print("\n" + "=" * 60)
            print("FINALIZADO - Código APROVADO!")
            print("=" * 60)
            return

        # Prepare for next iteration
        context["task"] += f"\n\nCorrigir:\n{qa_out}\n{sec_out}"

    print("\n" + "=" * 60)
    print("Limite de iteracoes atingido")
    print("=" * 60)


if __name__ == "__main__":
    main()
