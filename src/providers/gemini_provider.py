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

"""Gemini provider implementation using Google AI API."""

import time
from typing import Optional

from .base import AIProvider


class GeminiProvider(AIProvider):
    """Google Gemini provider."""

    def __init__(self, api_key: str, model: str = "gemini-pro", timeout: int = 120):
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError(
                "google-generativeai package not installed. "
                "Install with: pip install google-generativeai"
            )

        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model)
        self._model_name = model
        self._timeout = timeout

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def model(self) -> str:
        return self._model_name

    def chat(self, system: str, user: str) -> str:
        """Send message to Gemini."""
        start_time = time.time()

        # Gemini doesn't have system messages, so we prepend to user message
        full_prompt = f"{system}\n\n{user}"
        response = self._model.generate_content(
            full_prompt,
            generation_config={"max_output_tokens": 4096}
        )

        latency = (time.time() - start_time) * 1000
        return response.text

    def check_health(self) -> bool:
        """Check if Gemini API is accessible."""
        try:
            self._model.generate_content("Hi", generation_config={"max_output_tokens": 10})
            return True
        except Exception:
            return False
