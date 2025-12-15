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
Comprehensive test suite for Qwen-Agentes.

Tests:
1. Configuration system
2. Provider factory and implementations
3. Agent creation and prompts
4. Code parser
5. Security validator
6. Context management
7. File management
8. Integration tests
9. Language detection (prompt verification)
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import Config, ProviderType, get_config
from src.providers.factory import ProviderFactory
from src.providers.qwen_provider import QwenProvider
from src.agents import (
    ArchitectAgent,
    DeveloperAgent,
    QAAgent,
    SecurityAgent,
    ReviewerAgent
)
from src.io.output_parser import parse_code_blocks, check_approval
from src.utils.security_validator import SecurityValidator
from src.core.context import ExecutionContext, IterationResult, CodeBlock, Issue
from src.io.file_manager import FileManager


def print_header(text):
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def test_config():
    """Test configuration system."""
    print_header("Testing Configuration System")
    
    # Test default config
    config = Config()
    assert config.provider == ProviderType.QWEN, "Default provider should be QWEN"
    assert config.max_iterations == 5, "Default max_iterations should be 5"
    assert config.timeout == 120, "Default timeout should be 120"
    print("  ✓ Default configuration correct")
    
    # Test custom config
    config = Config(provider=ProviderType.CLAUDE, max_iterations=10, timeout=60)
    assert config.provider == ProviderType.CLAUDE
    assert config.max_iterations == 10
    assert config.timeout == 60
    print("  ✓ Custom configuration correct")
    
    # Test config file loading
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("provider: gpt\nmax_iterations: 3\n")
        f.flush()
        config = Config.load(Path(f.name))
        assert config.provider == ProviderType.GPT
        assert config.max_iterations == 3
    print("  ✓ YAML config loading correct")
    
    print("\n✅ Configuration tests PASSED")


def test_providers():
    """Test provider implementations."""
    print_header("Testing Providers")
    
    # Test Qwen provider
    provider = QwenProvider(timeout=30)
    assert provider.name == "qwen"
    assert provider.model == "qwen2.5-coder"
    print("  ✓ QwenProvider initialized")
    
    # Test health check
    health = provider.check_health()
    print(f"  ✓ Qwen health check: {'OK' if health else 'Not available'}")
    
    # Test factory
    config = Config(provider=ProviderType.QWEN)
    provider = ProviderFactory.create(config)
    assert isinstance(provider, QwenProvider)
    print("  ✓ ProviderFactory creates QwenProvider")
    
    # Test provider list
    providers = ProviderFactory.list_providers()
    assert len(providers) == 4
    assert "qwen" in providers
    assert "claude" in providers
    print(f"  ✓ Provider list: {providers}")
    
    print("\n✅ Provider tests PASSED")


def test_agents():
    """Test agent implementations."""
    print_header("Testing Agents")
    
    provider = QwenProvider()
    
    # Test all agents can be created
    agents = {
        "Architect": ArchitectAgent(provider),
        "Developer": DeveloperAgent(provider),
        "QA": QAAgent(provider),
        "Security": SecurityAgent(provider),
        "Reviewer": ReviewerAgent(provider),
    }
    
    for name, agent in agents.items():
        assert agent.name == name.lower()
        assert len(agent._system_prompt) > 0
        assert "LANGUAGE" in agent._system_prompt or "language" in agent._system_prompt.lower()
        print(f"  ✓ {name} agent created with language requirement")
    
    print("\n✅ Agent tests PASSED")


def test_language_requirement_in_prompts():
    """Test that all prompts include language requirement."""
    print_header("Testing Language Requirement in Prompts")
    
    agents_dir = Path(__file__).parent / "orchestrator" / "agents"
    agent_files = ["architect.txt", "developer.txt", "qa.txt", "security.txt", "reviewer.txt"]
    
    for agent_file in agent_files:
        prompt_file = agents_dir / agent_file
        if prompt_file.exists():
            with open(prompt_file) as f:
                content = f.read()
                assert "LANGUAGE" in content.upper() or "language" in content.lower()
                assert "SAME LANGUAGE" in content.upper() or "user's language" in content.lower()
                print(f"  ✓ {agent_file} has language requirement")
        else:
            print(f"  ⚠ {agent_file} not found")
    
    print("\n✅ Language requirement tests PASSED")


def test_parser():
    """Test code parser."""
    print_header("Testing Code Parser")
    
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
    print("  ✓ Code block parsing correct")
    
    # Test approval parsing
    approved, notes = check_approval("APPROVED")
    assert approved is True
    print("  ✓ APPROVED detection correct")
    
    approved, notes = check_approval("REJECTED: Bug found")
    assert approved is False
    print("  ✓ REJECTED detection correct")
    
    print("\n✅ Parser tests PASSED")


def test_security_validator():
    """Test security validator."""
    print_header("Testing Security Validator")
    
    validator = SecurityValidator()
    
    # Test safe code
    safe_code = "def add(a, b): return a + b"
    issues = validator.validate("test.py", safe_code)
    assert len(issues) == 0
    print("  ✓ Safe code passes validation")
    
    # Test dangerous code
    dangerous_code = "import os; os.system('ls')"
    issues = validator.validate("test.py", dangerous_code)
    assert len(issues) > 0
    assert any(i.issue_type == "os_system" for i in issues)
    print("  ✓ Dangerous code detected")
    
    # Test multiple files
    files = [
        ("file1.py", "eval(user_input)"),
        ("file2.py", "def safe(): pass"),
    ]
    issues = validator.validate_multiple(files)
    assert len(issues) == 1
    print("  ✓ Multiple file validation correct")
    
    print("\n✅ Security validator tests PASSED")


def test_context():
    """Test execution context."""
    print_header("Testing Execution Context")
    
    ctx = ExecutionContext(task="Test task")
    assert ctx.task == "Test task"
    assert ctx.current_iteration == 1
    assert ctx.is_approved is False
    print("  ✓ Context initialization correct")
    
    # Add iteration
    result = IterationResult(
        iteration=1,
        architecture=None,
        code="test",
        code_blocks=[CodeBlock("main.py", "python", "print('hi')")],
        qa_issues=[],
        security_issues=[],
        approved=True,
        reviewer_notes="APPROVED"
    )
    ctx.add_iteration(result)
    
    assert len(ctx.iterations) == 1
    assert ctx.is_approved is True
    assert ctx.current_iteration == 2
    print("  ✓ Iteration management correct")
    
    # Test save
    with tempfile.TemporaryDirectory() as tmpdir:
        ctx.output_dir = Path(tmpdir)
        saved_path = ctx.save()
        assert saved_path.exists()
        assert (saved_path / "metadata.json").exists()
        print("  ✓ Context save correct")
    
    print("\n✅ Context tests PASSED")


def test_file_manager():
    """Test file management."""
    print_header("Testing File Manager")
    
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
        print("  ✓ Code blocks saved")
        
        # Get latest files
        files = [f for f in fm.get_latest_files() if f.is_file()]
        assert len(files) >= 2
        print("  ✓ Get latest files correct")
        
        # Clear
        fm.clear()
        files = [f for f in fm.get_latest_files() if f.is_file()]
        assert len(files) == 0
        print("  ✓ Clear correct")
    
    print("\n✅ File manager tests PASSED")


def test_integration():
    """Test basic integration."""
    print_header("Testing Integration")
    
    # Create provider
    provider = QwenProvider()
    
    # Create all agents
    architect = ArchitectAgent(provider)
    developer = DeveloperAgent(provider)
    
    # Verify prompts are loaded
    assert len(architect._system_prompt) > 100
    assert len(developer._system_prompt) > 100
    print("  ✓ Agent prompts loaded correctly")
    
    # Verify language requirement in prompts
    assert "LANGUAGE" in architect._system_prompt.upper()
    assert "LANGUAGE" in developer._system_prompt.upper()
    print("  ✓ Language requirement in all prompts")
    
    print("\n✅ Integration tests PASSED")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("  QWEN-AGENTES COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Configuration", test_config),
        ("Providers", test_providers),
        ("Agents", test_agents),
        ("Language Requirement", test_language_requirement_in_prompts),
        ("Parser", test_parser),
        ("Security Validator", test_security_validator),
        ("Context", test_context),
        ("File Manager", test_file_manager),
        ("Integration", test_integration),
    ]
    
    passed = 0
    failed = 0
    skipped = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ {name} FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)
    print(f"  Passed:  {passed}/{len(tests)}")
    print(f"  Failed:  {failed}/{len(tests)}")
    print("=" * 60)
    
    if failed == 0:
        print("\n✅ ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n❌ {failed} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
