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
Template Library for Qwen-Agentes.

Pre-built project templates for common use cases.
100% local - no external dependencies.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass
class ProjectTemplate:
    """A project template."""
    name: str
    description: str
    category: str
    files: dict[str, str]
    instructions: str
    tags: list[str]


class TemplateLibrary:
    """Library of project templates."""
    
    _templates: dict[str, ProjectTemplate] = {}
    
    @classmethod
    def register(cls, template: ProjectTemplate) -> None:
        """Register a template."""
        cls._templates[template.name] = template
    
    @classmethod
    def get(cls, name: str) -> ProjectTemplate | None:
        """Get a template by name."""
        return cls._templates.get(name)
    
    @classmethod
    def list_all(cls, category: str | None = None) -> list[dict]:
        """List all templates, optionally filtered by category."""
        templates = cls._templates.values()
        if category:
            templates = [t for t in templates if t.category == category]
        return [
            {
                "name": t.name,
                "description": t.description,
                "category": t.category,
                "tags": t.tags
            }
            for t in templates
        ]
    
    @classmethod
    def search(cls, query: str) -> list[dict]:
        """Search templates by name, description, or tags."""
        query = query.lower()
        results = []
        for template in cls._templates.values():
            if (query in template.name.lower() or
                query in template.description.lower() or
                any(query in tag.lower() for tag in template.tags)):
                results.append({
                    "name": template.name,
                    "description": template.description,
                    "category": template.category,
                    "tags": template.tags
                })
        return results


# ── Template: FastAPI REST API ────────────────────────────────────────────────

FASTAPI_TEMPLATE = ProjectTemplate(
    name="fastapi-rest",
    description="REST API com FastAPI, SQLAlchemy e Pydantic",
    category="web",
    tags=["fastapi", "rest", "api", "sqlalchemy", "pydantic"],
    files={
        "main.py": '''# SPDX-License-Identifier: MIT
"""FastAPI REST API - Main entry point."""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="My API",
    description="Minha API REST",
    version="1.0.0"
)


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    quantity: int = 1


@app.get("/")
def read_root():
    """Root endpoint."""
    return {"message": "Welcome to My API!"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/items")
def create_item(item: Item):
    """Create a new item."""
    return {
        "message": "Item created",
        "item": item,
        "total_value": item.price * item.quantity
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
''',
        "requirements.txt": '''fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
sqlalchemy>=2.0.0
''',
        "README.md": '''# My FastAPI REST API

## Instalação

```bash
pip install -r requirements.txt
```

## Execução

```bash
python main.py
```

A API estará disponível em http://localhost:8000

## Documentação

A documentação interativa (Swagger UI) está em:
http://localhost:8000/docs

## Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `POST /items` - Create item
'''
    },
    instructions='''
Este template cria uma API REST básica com FastAPI.

Próximos passos sugeridos:
1. Adicionar modelos SQLAlchemy para banco de dados
2. Implementar endpoints CRUD completos
3. Adicionar autenticação (JWT)
4. Configurar migrations com Alembic
5. Adicionar testes com pytest
'''
)

TemplateLibrary.register(FASTAPI_TEMPLATE)


# ── Template: CLI com Typer ────────────────────────────────────────────────────

TYPER_CLI_TEMPLATE = ProjectTemplate(
    name="typer-cli",
    description="CLI moderna com Typer e Rich",
    category="cli",
    tags=["typer", "cli", "rich", "click"],
    files={
        "main.py": '''# SPDX-License-Identifier: MIT
"""CLI application with Typer."""

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Minha CLI Application")
console = Console()


@app.command()
def hello(name: str = typer.Option("World", "--name", "-n")):
    """Greet someone."""
    console.print(f"[bold green]Hello, {name}![/bold green]")


@app.command()
def list_items():
    """List sample items."""
    table = Table(title="Items")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="magenta")
    table.add_column("Status", style="green")
    
    table.add_row("1", "Item 1", "Active")
    table.add_row("2", "Item 2", "Active")
    table.add_row("3", "Item 3", "Inactive")
    
    console.print(table)


@app.command()
def process(
    input_file: str = typer.Argument(..., help="Input file path"),
    output_file: str = typer.Option("output.txt", "--output", "-o"),
    verbose: bool = typer.Option(False, "--verbose", "-v")
):
    """Process a file."""
    if verbose:
        console.print(f"[yellow]Processing {input_file}...[/yellow]")
    
    # Simulate processing
    console.print(f"[green]✓[/green] Output saved to {output_file}")


if __name__ == "__main__":
    app()
''',
        "requirements.txt": '''typer>=0.9.0
rich>=13.0.0
''',
        "README.md": '''# My Typer CLI

## Instalação

```bash
pip install -r requirements.txt
```

## Uso

```bash
# Ver ajuda
python main.py --help

# Comando hello
python main.py hello --name Alice

# Listar items
python main.py list-items

# Processar arquivo
python main.py process input.txt -o output.txt -v
```
'''
    },
    instructions='''
Este template cria uma CLI moderna com Typer e Rich.

Próximos passos sugeridos:
1. Adicionar mais comandos conforme necessidade
2. Implementar processamento real de arquivos
3. Adicionar configuração com config files
4. Implementar logging estruturado
5. Adicionar testes com pytest
'''
)

TemplateLibrary.register(TYPER_CLI_TEMPLATE)


# ── Template: Discord Bot ──────────────────────────────────────────────────────

DISCORD_BOT_TEMPLATE = ProjectTemplate(
    name="discord-bot",
    description="Bot para Discord com discord.py",
    category="bot",
    tags=["discord", "bot", "async"],
    files={
        "main.py": '''# SPDX-License-Identifier: MIT
"""Discord Bot with discord.py."""

import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    """Called when bot is ready."""
    print(f"{bot.user} está online!")
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")


@bot.command(name="hello", help="Saudação simples")
async def hello(ctx):
    """Greet the user."""
    await ctx.send(f"Olá, {ctx.author.name}! 👋")


@bot.command(name="ping", help="Testar latência")
async def ping(ctx):
    """Check bot latency."""
    latency = round(bot.latency * 1000)
    await ctx.send(f"Pong! Latência: {latency}ms 🏓")


@bot.command(name="info", help="Informações do servidor")
async def server_info(ctx):
    """Get server info."""
    embed = discord.Embed(
        title=f"Informações de {ctx.guild.name}",
        color=discord.Color.blue()
    )
    embed.add_field(name="Membros", value=ctx.guild.member_count)
    embed.add_field(name="Canais", value=len(ctx.guild.channels))
    embed.add_field(name="Cargo mais alto", value=ctx.guild.roles[-1].name)
    
    await ctx.send(embed=embed)


if __name__ == "__main__":
    if not TOKEN:
        print("Erro: DISCORD_TOKEN não encontrado no .env")
    else:
        bot.run(TOKEN)
''',
        "requirements.txt": '''discord.py>=2.3.0
python-dotenv>=1.0.0
''',
        ".env.example": '''DISCORD_TOKEN=seu_token_aqui
''',
        "README.md": '''# My Discord Bot

## Configuração

1. Crie um bot em https://discord.com/developers/applications
2. Copie o token para o arquivo `.env`

```bash
cp .env.example .env
# Edite .env e adicione seu token
```

## Instalação

```bash
pip install -r requirements.txt
```

## Execução

```bash
python main.py
```

## Comandos

- `!hello` - Saudação
- `!ping` - Testar latência
- `!info` - Informações do servidor
'''
    },
    instructions='''
Este template cria um bot básico para Discord.

Próximos passos sugeridos:
1. Adicionar mais comandos conforme necessidade
2. Implementar banco de dados para persistência
3. Adicionar sistemas de níveis/economia
4. Implementar moderação automática
5. Adicionar cogs para organizar comandos
'''
)

TemplateLibrary.register(DISCORD_BOT_TEMPLATE)


# ── Template: Python Package ──────────────────────────────────────────────────

PYTHON_PACKAGE_TEMPLATE = ProjectTemplate(
    name="python-package",
    description="Pacote Python com estrutura profissional",
    category="library",
    tags=["package", "library", "pypi", "setup"],
    files={
        "pyproject.toml": '''[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my-package"
version = "0.1.0"
description = "Meu pacote Python"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.10"
authors = [
    {name = "Seu Nome", email = "seu@email.com"}
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
]
''',
        "src/__init__.py": '''# SPDX-License-Identifier: MIT
"""My Package."""

__version__ = "0.1.0"


def hello(name: str = "World") -> str:
    """Greet someone."""
    return f"Hello, {name}!"
''',
        "tests/__init__.py": '''# Tests package.''',
        "tests/test_main.py": '''# SPDX-License-Identifier: MIT
"""Tests for my package."""

import pytest
from src import hello


def test_hello_default():
    """Test hello with default name."""
    assert hello() == "Hello, World!"


def test_hello_custom():
    """Test hello with custom name."""
    assert hello("Alice") == "Hello, Alice!"
''',
        "README.md": '''# My Python Package

## Instalação

```bash
pip install -e .
```

## Uso

```python
from src import hello

print(hello())  # Hello, World!
print(hello("Alice"))  # Hello, Alice!
```

## Desenvolvimento

```bash
# Instalar em modo desenvolvimento
pip install -e ".[dev]"

# Rodar testes
pytest

# Formatar código
black src/ tests/

# Lint
ruff check src/ tests/
```
'''
    },
    instructions='''
Este template cria um pacote Python com estrutura profissional.

Próximos passos sugeridos:
1. Adicionar mais módulos em src/
2. Implementar funcionalidades principais
3. Adicionar mais testes
4. Configurar CI/CD (GitHub Actions)
5. Publicar no PyPI quando pronto
'''
)

TemplateLibrary.register(PYTHON_PACKAGE_TEMPLATE)
