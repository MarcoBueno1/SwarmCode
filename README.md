# SwarmCode

Multi-agent software development system powered by AI. Automates the entire development lifecycle using specialized AI agents for architecture, development, QA, security, and code review.

## Features

- 🤖 **Multi-Agent System**: 5 specialized AI agents working together
  - **Architect**: Defines software architecture
  - **Developer**: Implements code
  - **QA**: Finds bugs and issues
  - **Security**: Identifies vulnerabilities
  - **Reviewer**: Approves or rejects code

- 🔌 **Multiple AI Providers**: Support for various AI models
  - Qwen (local, default)
  - Anthropic Claude
  - OpenAI GPT
  - Google Gemini

- 📁 **Structured Output**: Parses and saves generated code with proper file structure

- 🔒 **Security Validation**: Automated security pattern detection

- 💾 **Persistence**: Saves execution context and artifacts for resuming

- 📊 **Structured Logging**: JSON logging for observability

## Installation

```bash
# Clone the repository
git clone https://github.com/MarcoBueno1/SwarmCode.git
cd SwarmCode

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -e ".[dev]"
```

## Quick Start

```bash
# Initialize configuration
SwarmCode init

# Edit .env and add your API keys (if using Claude/GPT/Gemini)
# Or use local Qwen (no key needed)

# Run a development task
SwarmCode run "crie um servidor REST com FastAPI"

# Use a different provider
SwarmCode run "crie um jogo da velha" -p claude -i 10
```

## CLI Commands

### run

Execute the multi-agent development process.

```bash
SwarmCode run "task description" [options]

Options:
  -p, --provider TEXT     AI provider: qwen, claude, gpt, gemini
  -m, --model TEXT        Model name (optional)
  -i, --max-iter INTEGER  Maximum iterations (default: 5)
  -o, --output PATH       Output directory (default: ./output)
  -c, --config PATH       Config file path
  -v, --verbose           Verbose output
```

### list-providers

List all available AI providers.

```bash
SwarmCode list-providers
```

### health

Check health of configured providers.

```bash
SwarmCode health
```

### init

Initialize configuration files.

```bash
SwarmCode init
```

## Configuration

### config.yaml

```yaml
# Provider selection: qwen, claude, gpt, gemini
provider: qwen

# Model name (optional)
model: null

# Timeout for AI requests (seconds)
timeout: 120

# Maximum iterations per task
max_iterations: 5

# Output directory
output_dir: ./output

# Feature flags
features:
  save_artifacts: true
  run_tests: false
  security_validation: true
  structured_output: true

# Agent-specific settings
agents:
  architect:
    temperature: 0.3
  developer:
    temperature: 0.2
```

### .env

```bash
# API Keys (only required for cloud providers)
ANTHROPIC_API_KEY=sk-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR                             │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐    ┌─────────────────┐    ┌──────────────┐
│  ARCHITECT    │───▶│   DEVELOPER     │───▶│     QA       │
└───────────────┘    └─────────────────┘    └──────────────┘
                             │
                    ┌────────▼────────┐
                    │    SECURITY     │
                    └────────┬────────┘
                             ▼
                    ┌─────────────────┐
                    │    REVIEWER     │
                    └─────────────────┘
```

## Development

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=src

# Run specific test file
pytest tests/test_providers.py -v
```

### Code Quality

```bash
# Lint
ruff check src/ tests/

# Type check
mypy src/

# Format
black src/ tests/
```

## Project Structure

```
SwarmCode/
├── src/
│   ├── __init__.py
│   ├── main.py              # CLI entry point
│   ├── config.py            # Configuration system
│   │
│   ├── core/
│   │   ├── orchestrator.py  # Main orchestration logic
│   │   └── context.py       # Execution context
│   │
│   ├── providers/
│   │   ├── base.py          # Provider interface
│   │   ├── qwen_provider.py
│   │   ├── claude_provider.py
│   │   ├── gpt_provider.py
│   │   ├── gemini_provider.py
│   │   └── factory.py       # Provider factory
│   │
│   ├── agents/
│   │   ├── base.py          # Agent base class
│   │   ├── architect.py
│   │   ├── developer.py
│   │   ├── qa.py
│   │   ├── security.py
│   │   └── reviewer.py
│   │
│   ├── io/
│   │   ├── output_parser.py # Parse AI output
│   │   └── file_manager.py  # File operations
│   │
│   └── utils/
│       ├── logger.py        # Structured logging
│       └── security_validator.py
│
├── tests/
│   ├── test_providers.py
│   ├── test_agents.py
│   ├── test_parser.py
│   ├── test_security.py
│   └── test_context.py
│
├── config.yaml
├── .env.example
└── pyproject.toml
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
