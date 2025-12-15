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
Test script to validate the entire SwarmCode structure.

This script tests:
1. Configuration loading
2. Provider factory
3. Agent creation
4. Code parsing
5. Security validation
6. Context management
7. File management
"""

import sys
import tempfile
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config, ProviderType, get_config
from src.providers.factory import ProviderFactory
from src.providers.qwen_provider import QwenProvider
from src.agents import ArchitectAgent, DeveloperAgent, QAAgent, SecurityAgent, ReviewerAgent
from src.io.output_parser import parse_code_blocks, check_approval
from src.utils.security_validator import SecurityValidator
from src.core.context import ExecutionContext, IterationResult, CodeBlock, Issue
from src.io.file_manager import FileManager


def test_config():
    """Test configuration loading."""
    print("Testing configuration...")
    
    # Test default config
    config = Config()
    assert config.provider == ProviderType.QWEN
    assert config.max_iterations == 5
    assert config.timeout == 120
    
    # Test custom config
    config = Config(provider=ProviderType.CLAUDE, max_iterations=10)
    assert config.provider == ProviderType.CLAUDE
    assert config.max_iterations == 10
    
    print("  ✓ Configuration tests passed")


def test_providers():
    """Test provider creation."""
    print("Testing providers...")
    
    # Test Qwen provider
    provider = QwenProvider(timeout=30)
    assert provider.name == "qwen"
    assert provider.model == "qwen2.5-coder"
    
    # Test factory
    config = Config(provider=ProviderType.QWEN)
    provider = ProviderFactory.create(config)
    assert isinstance(provider, QwenProvider)
    
    # Test provider list
    providers = ProviderFactory.list_providers()
    assert "qwen" in providers
    assert "claude" in providers
    
    print("  ✓ Provider tests passed")


def test_agents():
    """Test agent creation."""
    print("Testing agents...")
    
    provider = QwenProvider()
    
    # Test all agents can be created
    architect = ArchitectAgent(provider)
    assert architect.name == "architect"
    
    developer = DeveloperAgent(provider)
    assert developer.name == "developer"
    
    qa = QAAgent(provider)
    assert qa.name == "qa"
    
    security = SecurityAgent(provider)
    assert security.name == "security"
    
    reviewer = ReviewerAgent(provider)
    assert reviewer.name == "reviewer"
    
    print("  ✓ Agent tests passed")


def test_parser():
    """Test code parsing."""
    print("Testing parser...")
    
    # Test code block parsing
    text = """
```python filepath=main.py
def hello():
    print("Hello, World!")
```

```python filepath=utils.py
def helper():
    return 42
```
"""
    blocks = parse_code_blocks(text)
    assert len(blocks) == 2
    assert blocks[0].filepath == "main.py"
    assert blocks[1].filepath == "utils.py"
    
    # Test approval parsing
    approved, notes = check_approval("APROVADO")
    assert approved is True
    
    approved, notes = check_approval("REPROVADO: Bug crítico")
    assert approved is False
    assert "BUG" in notes.upper()
    
    print("  ✓ Parser tests passed")


def test_security_validator():
    """Test security validation."""
    print("Testing security validator...")
    
    validator = SecurityValidator()
    
    # Test safe code
    safe_code = "def add(a, b): return a + b"
    issues = validator.validate("test.py", safe_code)
    assert len(issues) == 0
    
    # Test dangerous code
    dangerous_code = "import os; os.system('ls')"
    issues = validator.validate("test.py", dangerous_code)
    assert len(issues) > 0
    assert any(i.issue_type == "os_system" for i in issues)
    
    print("  ✓ Security validator tests passed")


def test_context():
    """Test execution context."""
    print("Testing execution context...")
    
    ctx = ExecutionContext(task="Test task")
    assert ctx.task == "Test task"
    assert ctx.current_iteration == 1
    
    # Add iteration
    result = IterationResult(
        iteration=1,
        architecture=None,
        code="test",
        code_blocks=[CodeBlock("main.py", "python", "print('hi')")],
        qa_issues=[],
        security_issues=[],
        approved=True,
        reviewer_notes="APROVADO"
    )
    ctx.add_iteration(result)
    
    assert len(ctx.iterations) == 1
    assert ctx.is_approved is True
    assert ctx.current_iteration == 2
    
    print("  ✓ Context tests passed")


def test_file_manager():
    """Test file management."""
    print("Testing file manager...")
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        fm = FileManager(output_dir)
        
        # Save code blocks
        blocks = [
            CodeBlock("src/main.py", "python", "def main(): pass"),
            CodeBlock("src/utils.py", "python", "def helper(): pass"),
        ]
        
        saved = fm.save_code_blocks(blocks, iteration=1)
        assert len(saved) == 2
        assert all(p.exists() for p in saved)

        # Get latest files (filter only files, not directories)
        files = [f for f in fm.get_latest_files() if f.is_file()]
        assert len(files) >= 2

        # Clear
        fm.clear()
        files = [f for f in fm.get_latest_files() if f.is_file()]
        assert len(files) == 0
    
    print("  ✓ File manager tests passed")


def test_integration():
    """Test basic integration."""
    print("Testing integration...")
    
    # Create provider
    provider = QwenProvider()
    
    # Create agent
    architect = ArchitectAgent(provider)
    assert architect._provider == provider
    
    # Verify prompt is loaded
    assert len(architect._system_prompt) > 0
    assert "Principal Engineer" in architect._system_prompt
    
    print("  ✓ Integration tests passed")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Qwen-Agentes Structure Validation Tests")
    print("=" * 60)
    print()
    
    tests = [
        test_config,
        test_providers,
        test_agents,
        test_parser,
        test_security_validator,
        test_context,
        test_file_manager,
        test_integration,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  ✗ {test.__name__} failed: {e}")
            failed += 1
    
    print()
    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
