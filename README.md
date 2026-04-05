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
  - Qwen (local CLI, default)
  - Anthropic Claude
  - OpenAI GPT
  - Google Gemini

- 🚀 **YOLO Mode**: Zero-interruption development — Qwen auto-execute all tool calls without approval prompts

- 📺 **Full Terminal Output**: All Qwen output (file changes, progress, errors) is shown in real-time in the terminal

- ⏱️ **Smart Timeout**: Timeout only triggers when Qwen is silent for too long — resets on every output chunk. Long-running tasks never get killed while actively streaming.

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

## Prerequisites

### Qwen (local, default)
The Qwen CLI must be installed and authenticated:
```bash
qwen auth status          # Check auth status
qwen auth qwen-oauth      # Configure OAuth (interactive)
# Or set up API key via settings
```

### Cloud Providers (optional)
Just set the appropriate API key in `.env`.

## Quick Start

```bash
# Initialize configuration
swarmcode init

# Edit .env and add your API keys (if using Claude/GPT/Gemini)
# Or use local Qwen (auth via qwen auth)

# Run a development task with full output visible
swarmcode run "crie um servidor REST com FastAPI"

# Target a specific project directory (auto-enables YOLO mode)
swarmcode run "add unit tests" -d /path/to/project

# Use a different provider
swarmcode run "crie um jogo da velha" -p claude -i 10
```

## CLI Commands

### run

Execute the multi-agent development process.

```bash
swarmcode run "task description" [options]

Options:
  -p, --provider TEXT     AI provider: qwen, claude, gpt, gemini
  -m, --model TEXT        Model name (optional)
  --mode TEXT             Execution mode: quick, standard, deep
  -i, --max-iter INTEGER  Maximum iterations (default: 5)
  -t, --timeout INTEGER   Idle timeout in seconds (default: 300)
  -o, --output PATH       Output directory (default: ./output)
  -d, --project-dir PATH  Target project directory (enables YOLO mode)
  -c, --config PATH       Config file path
  -v, --verbose           Verbose output
```

**YOLO Mode**: When `--project-dir` is specified, SwarmCode automatically configures Qwen to run in YOLO mode for that project — no approval prompts, all tool calls executed automatically.

**Smart Timeout**: The timeout counter only advances when Qwen is silent. Every new token or output line resets the countdown. This means a 300s timeout allows Qwen to work for hours as long as it keeps producing output.

### list-providers

List all available AI providers.

```bash
swarmcode list-providers
```

### health

Check health of configured providers.

```bash
swarmcode health
```

### init

Initialize configuration files.

```bash
swarmcode init
```

### webui

Launch the web interface.

```bash
swarmcode webui
```

## Configuration

### config.yaml

```yaml
# Provider selection: qwen, claude, gpt, gemini
provider: qwen

# Target project directory (for YOLO mode)
project_dir: null

# Model name (optional)
model: null

# Idle timeout for AI requests (seconds)
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

## How Qwen Integration Works

When using the Qwen provider, SwarmCode calls the `qwen` CLI exactly as you would from the terminal:

```
SwarmCode Agent → subprocess.Popen(["qwen", "--yolo"])
                   ↓
              Prompt sent via stdin
                   ↓
              All output shown in real-time (stdout + stderr)
                   ↓
              Smart idle timeout: resets on every output chunk
                   ↓
              Response captured and returned to agent
```

Key behaviors:
- **`--yolo` flag**: Automatically passed — no approval prompts
- **`.qwen/settings.json`**: Auto-created in the target project with `"approvalMode": "yolo"`
- **Output visibility**: Everything Qwen does is printed to the terminal (file writes, tool calls, progress)
- **No questions**: YOLO mode means Qwen never asks for confirmation — it just executes

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

Each agent communicates with the AI provider (Qwen by default) through a unified interface, allowing seamless swapping between different AI backends.

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
│   ├── main.py              # CLI entry point (Typer)
│   ├── config.py            # Configuration system (Pydantic)
│   │
│   ├── core/
│   │   ├── orchestrator.py  # Main orchestration logic
│   │   └── context.py       # Execution context
│   │
│   ├── providers/
│   │   ├── base.py          # Provider interface (ABC)
│   │   ├── qwen_provider.py # Qwen CLI via subprocess
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
│   │   ├── reviewer.py
│   │   └── tester.py        # Test generation agent
│   │
│   ├── io/
│   │   ├── output_parser.py # Parse AI output
│   │   └── file_manager.py  # File operations
│   │
│   ├── utils/
│   │   ├── logger.py        # Structured logging
│   │   ├── security_validator.py
│   │   └── code_scorer.py   # Code quality scoring
│   │
│   ├── tools/
│   │   └── local_tools.py   # Local tool definitions
│   │
│   └── gui/
│       └── webui.py         # Gradio web interface
│
├── tests/
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
