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

"""Qwen-Agentes CLI - Multi-agent software development system."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from .config import Config, ProviderType, get_config, ExecutionMode
from .providers.factory import ProviderFactory
from .core.orchestrator import Orchestrator, OrchestratorConfig
from .utils.logger import setup_logging
from .utils.code_scorer import CodeQualityScorer
from .utils.commit_generator import CommitGenerator

app = typer.Typer(
    name="SwarmCode",
    help="Multi-agent software development system powered by AI",
    add_completion=True
)

console = Console()


@app.command()
def run(
    task: str = typer.Argument(..., help="O que deseja construir"),
    provider: str = typer.Option("qwen", "--provider", "-p", help="AI provider to use"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model name"),
    mode: ExecutionMode = typer.Option(ExecutionMode.STANDARD, "--mode", "-m", help="Execution mode"),
    iterations: int = typer.Option(5, "--max-iter", "-i", help="Maximum iterations"),
    timeout: int = typer.Option(300, "--timeout", "-t", help="Timeout in seconds"),
    output: Path = typer.Option("./output", "--output", "-o", help="Output directory"),
    config_file: Optional[Path] = typer.Option(None, "--config", "-c", help="Config file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """
    Run the multi-agent development process.

    Examples:

        swarmcode run "crie um servidor REST"                    # Standard mode
        swarmcode run "corrige bug no auth" --mode quick         # Quick fix
        swarmcode run "crie um SaaS completo" --mode deep        # Full project
        swarmcode run "task" -p claude -t 600                    # Custom timeout

    Execution Modes:
        quick    - 1 iteration, minimal agents (fast fixes)
        standard - 3 iterations, full pipeline (default)
        deep     - 5 iterations, + docs + tests (complex projects)
    """
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(level=log_level, log_format="console")

    console.print(f"\n[bold blue]🐝 SwarmCode[/bold blue] - Development System")
    console.print(f"[dim]Task: {task}[/dim]")
    console.print(f"[dim]Mode: {mode.value} (max {mode.max_iterations} iterations)[/dim]\n")

    try:
        # Load configuration
        config = Config.load(config_file) if config_file else get_config()

        # Override with CLI options
        config.provider = ProviderType(provider)
        config.model = model or config.model
        config.mode = mode  # Set execution mode
        config.max_iterations = mode.max_iterations  # Override based on mode
        config.timeout = timeout  # Override timeout from CLI
        config.output_dir = output

        # Create provider
        console.print(f"[green]✓[/green] Initializing {config.provider.value} provider...")
        provider_instance = ProviderFactory.create(config)

        # Create orchestrator
        orch_config = OrchestratorConfig(
            max_iterations=config.max_iterations,
            save_artifacts=config.features.save_artifacts,
            run_security_validation=config.features.security_validation,
            enable_docs=config.mode.enable_docs,
            enable_tests=config.mode.enable_tests
        )

        orchestrator = Orchestrator(
            provider=provider_instance,
            config=orch_config,
            output_dir=config.output_dir
        )

        # Run development with visual progress
        console.print(f"[green]✓[/green] Starting development process...\n")
        
        # Simple spinner during execution
        with Progress(
            SpinnerColumn(),
            TextColumn("[cyan]{task.description}"),
            console=console
        ) as progress:
            
            progress.add_task("Agents working...", total=None)  # Infinite spinner
            
            # Run orchestrator
            ctx = orchestrator.run(task)
        
        console.print("\n[bold green]✅ Development Complete![/bold green]\n")

        if ctx.is_approved:
            console.print(f"[green]Status:[/green] APROVADO após {len(ctx.iterations)} iteração(ões)")
        else:
            console.print(f"[yellow]Status:[/yellow] Não aprovado após {len(ctx.iterations)} iterações")

        console.print(f"[green]Output:[/green] {ctx.output_dir / f'run_{ctx.id}'}")

        # Print summary
        _print_summary(ctx)

    except TimeoutError as e:
        console.print(f"\n[bold red]❌ Timeout Error:[/bold red] {e}")
        console.print("\n[yellow]Sugestões:[/yellow]")
        console.print("  • Aumente o timeout: swarmcode run \"task\" -t 600")
        console.print("  • Use um modelo mais rápido")
        console.print("  • Verifique se o qwen CLI está funcionando: qwen --help")
        raise typer.Exit(1)
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        console.print("\n[dim]Hint: Make sure your .env file has the required API keys[/dim]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        raise typer.Exit(1)


@app.command()
def list_providers():
    """List all available AI providers."""
    providers = ProviderFactory.list_providers()

    table = Table(title="Available AI Providers")
    table.add_column("Provider", style="cyan")
    table.add_column("Default Model", style="green")
    table.add_column("Requires API Key", style="yellow")

    api_keys = {
        "qwen": "No (local)",
        "claude": "Yes (ANTHROPIC_API_KEY)",
        "gpt": "Yes (OPENAI_API_KEY)",
        "gemini": "Yes (GEMINI_API_KEY)",
    }

    for p in providers:
        default_model = ProviderFactory.get_default_model(ProviderType(p))
        table.add_row(p, default_model, api_keys.get(p, "Unknown"))

    console.print(table)


@app.command()
def health():
    """Check health of configured providers."""
    config = get_config()

    table = Table(title="Provider Health Status")
    table.add_column("Provider", style="cyan")
    table.add_column("Status", style="green")

    try:
        provider = ProviderFactory.create(config)
        is_healthy = provider.check_health()
        status = "[green]✓ Healthy[/green]" if is_healthy else "[red]✗ Unhealthy[/red]"
        table.add_row(config.provider.value, status)
    except Exception as e:
        table.add_row(config.provider.value, f"[red]✗ Error: {e}[/red]")

    console.print(table)


@app.command()
def init():
    """Initialize configuration and environment files."""
    console.print("[bold blue]Initializing Qwen-Agentes configuration...[/bold blue]\n")

    # Create .env if not exists
    env_file = Path(".env")
    if not env_file.exists():
        env_template = Path(".env.example")
        if env_template.exists():
            import shutil
            shutil.copy(env_template, env_file)
            console.print(f"[green]✓[/green] Created {env_file}")
        else:
            # Create default .env
            with open(env_file, "w") as f:
                f.write("# API Keys\n")
                f.write("ANTHROPIC_API_KEY=\n")
                f.write("OPENAI_API_KEY=\n")
                f.write("GEMINI_API_KEY=\n")
            console.print(f"[green]✓[/green] Created {env_file}")
    else:
        console.print(f"[yellow]![/yellow] {env_file} already exists")

    # Create config.yaml if not exists
    config_file = Path("config.yaml")
    if not config_file.exists():
        default_config = """# Qwen-Agentes Configuration
provider: qwen
timeout: 120
max_iterations: 5
output_dir: ./output

features:
  save_artifacts: true
  run_tests: false
  security_validation: true
"""
        with open(config_file, "w") as f:
            f.write(default_config)
        console.print(f"[green]✓[/green] Created {config_file}")
    else:
        console.print(f"[yellow]![/yellow] {config_file} already exists")

    console.print("\n[green]Initialization complete![/green]")
    console.print("\n[dim]Next steps:")
    console.print("1. Edit .env and add your API keys")
    console.print("2. Edit config.yaml to customize settings")
    console.print("3. Run: SwarmCode run \"your task\"[/dim]")


@app.command()
def templates(
    category: str = typer.Option(None, "--category", "-c", help="Filter by category"),
    search: str = typer.Option(None, "--search", "-s", help="Search templates")
):
    """List available project templates."""
    from .templates import TemplateLibrary
    
    console.print("[bold blue]Qwen-Agentes - Templates[/bold blue]\n")
    
    if search:
        results = TemplateLibrary.search(search)
        table = Table(title=f"Search results for '{search}'")
    else:
        results = TemplateLibrary.list_all(category)
        table = Table(title="Available Templates")
    
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="green")
    table.add_column("Category", style="yellow")
    table.add_column("Tags", style="magenta")
    
    for t in results:
        tags_str = ", ".join(t["tags"])
        table.add_row(t["name"], t["description"], t["category"], tags_str)
    
    console.print(table)
    
    if not results:
        console.print("[yellow]No templates found.[/yellow]")


@app.command()
def webui(
    port: int = typer.Option(7860, "--port", "-p", help="Server port"),
    share: bool = typer.Option(False, "--share", "-s", help="Create public link")
):
    """Launch the Web UI (Gradio)."""
    from .gui.webui import WebUI
    
    console.print("[bold blue]Qwen-Agentes - WebUI[/bold blue]\n")
    console.print(f"Starting server on http://localhost:{port}\n")
    
    webui = WebUI(server_port=port, share=share)
    webui.run()


@app.command()
def tools():
    """List available local tools."""
    from .tools import ToolRegistry
    
    console.print("[bold blue]Qwen-Agentes - Local Tools[/bold blue]\n")
    console.print("[dim]Tools that work 100% locally (no internet required)[/dim]\n")
    
    tools = ToolRegistry.list_all()
    
    table = Table(title="Available Tools")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="green")
    table.add_column("Parameters", style="yellow")
    
    for t in tools:
        params = ", ".join(p["name"] for p in t["parameters"])
        table.add_row(t["name"], t["description"], params)
    
    console.print(table)


def _print_summary(ctx):
    """Print execution summary."""
    from .core.context import Issue

    table = Table(title="Execution Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Task", ctx.task[:50] + "..." if len(ctx.task) > 50 else ctx.task)
    table.add_row("Mode", ctx.mode.value if hasattr(ctx, 'mode') else 'standard')
    table.add_row("Iterations", str(len(ctx.iterations)))
    table.add_row("Status", "APPROVED" if ctx.is_approved else "NOT APPROVED")

    if ctx.last_iteration:
        table.add_row("Code Blocks", str(len(ctx.last_iteration.code_blocks)))
        table.add_row("QA Issues", str(len(ctx.last_iteration.qa_issues)))
        table.add_row("Security Issues", str(len(ctx.last_iteration.security_issues)))
        
        # Calculate and display code quality score
        if ctx.last_iteration.code_blocks:
            scorer = CodeQualityScorer()
            all_code = "\n".join([block.content for block in ctx.last_iteration.code_blocks])
            score = scorer.score(all_code, has_tests=False, has_docs=False)
            
            table.add_row("Code Quality", f"{score.overall:.1f}/10 {score.stars()}")
            
            # Generate conventional commit message
            commit_gen = CommitGenerator()
            commit = commit_gen.generate(all_code, ctx.task, has_tests=False)
            table.add_row("Suggested Commit", f"`{commit.type.value}: {commit.description[:40]}...`")

    console.print(table)


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    app()
