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

"""File manager for saving and loading code artifacts."""

import shutil
from pathlib import Path
from typing import Optional

from .output_parser import CodeBlock


class FileManager:
    """Manages file operations for generated code."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_code_blocks(
        self,
        code_blocks: list[CodeBlock],
        iteration: int,
        sub_dir: Optional[str] = None
    ) -> list[Path]:
        """
        Save code blocks to files.

        Args:
            code_blocks: List of code blocks to save
            iteration: Iteration number (for directory naming)
            sub_dir: Optional subdirectory name

        Returns:
            List of saved file paths
        """
        saved_files = []

        # Create directory for this iteration
        if sub_dir:
            base_dir = self.output_dir / sub_dir / f"iteration_{iteration}"
        else:
            base_dir = self.output_dir / f"iteration_{iteration}"

        base_dir.mkdir(parents=True, exist_ok=True)

        for block in code_blocks:
            file_path = base_dir / block.filepath
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(block.content)

            saved_files.append(file_path)

        return saved_files

    def copy_iteration(
        self,
        from_iteration: int,
        to_iteration: int,
        sub_dir: Optional[str] = None
    ) -> None:
        """Copy all files from one iteration to another."""
        if sub_dir:
            from_dir = self.output_dir / sub_dir / f"iteration_{from_iteration}"
            to_dir = self.output_dir / sub_dir / f"iteration_{to_iteration}"
        else:
            from_dir = self.output_dir / f"iteration_{from_iteration}"
            to_dir = self.output_dir / f"iteration_{to_iteration}"

        if from_dir.exists():
            if to_dir.exists():
                shutil.rmtree(to_dir)
            shutil.copytree(from_dir, to_dir)

    def get_latest_files(self, sub_dir: Optional[str] = None) -> list[Path]:
        """Get all files from the latest iteration."""
        if sub_dir:
            base_dir = self.output_dir / sub_dir
        else:
            base_dir = self.output_dir

        if not base_dir.exists():
            return []

        # Find highest iteration number
        iterations = sorted([
            int(d.name.replace("iteration_", ""))
            for d in base_dir.iterdir()
            if d.is_dir() and d.name.startswith("iteration_")
        ])

        if not iterations:
            return []

        latest_dir = base_dir / f"iteration_{iterations[-1]}"
        return list(latest_dir.rglob("*"))

    def clear(self) -> None:
        """Clear all output files."""
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_run_directory(self, run_id: str) -> Path:
        """Get directory for a specific run."""
        run_dir = self.output_dir / f"run_{run_id}"
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir
