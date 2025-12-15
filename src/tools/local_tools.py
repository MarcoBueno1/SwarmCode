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
Local Tools System for Qwen-Agentes.

All tools are 100% local - no external APIs or internet required.
Perfect for qwen CLI default mode.
"""

import json
import os
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseTool(ABC):
    """Base class for all local tools."""
    
    name: str
    description: str
    parameters: list[dict]
    
    @abstractmethod
    def call(self, params: str) -> str:
        """
        Execute the tool.
        
        Args:
            params: JSON string with tool parameters
            
        Returns:
            Tool output as string
        """
        pass
    
    def validate_params(self, params: str) -> dict:
        """Validate and parse tool parameters."""
        try:
            return json.loads(params)
        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON: {str(e)}"}


class FileReadTool(BaseTool):
    """Read contents of a local file."""
    
    name = "file_read"
    description = "Lê o conteúdo de um arquivo local. Útil para entender código existente."
    parameters = [{
        "name": "filepath",
        "type": "string",
        "description": "Caminho do arquivo para ler",
        "required": True
    }]
    
    def call(self, params: str) -> str:
        parsed = self.validate_params(params)
        if "error" in parsed:
            return json.dumps(parsed)
        
        filepath = Path(parsed.get("filepath", ""))
        
        if not filepath.exists():
            return json.dumps({"error": f"File not found: {filepath}"})
        
        if not filepath.is_file():
            return json.dumps({"error": f"Not a file: {filepath}"})
        
        try:
            content = filepath.read_text(encoding="utf-8")
            return json.dumps({
                "filepath": str(filepath),
                "size": len(content),
                "content": content
            })
        except Exception as e:
            return json.dumps({"error": f"Cannot read file: {str(e)}"})


class FileWriteTool(BaseTool):
    """Write content to a local file."""
    
    name = "file_write"
    description = "Escreve conteúdo em um arquivo local. Cria diretórios se necessário."
    parameters = [
        {
            "name": "filepath",
            "type": "string",
            "description": "Caminho do arquivo para escrever",
            "required": True
        },
        {
            "name": "content",
            "type": "string",
            "description": "Conteúdo para escrever no arquivo",
            "required": True
        }
    ]
    
    def call(self, params: str) -> str:
        parsed = self.validate_params(params)
        if "error" in parsed:
            return json.dumps(parsed)
        
        filepath = Path(parsed.get("filepath", ""))
        content = parsed.get("content", "")
        
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(content, encoding="utf-8")
            return json.dumps({
                "success": True,
                "filepath": str(filepath),
                "size": len(content)
            })
        except Exception as e:
            return json.dumps({"error": f"Cannot write file: {str(e)}"})


class DirectoryListTool(BaseTool):
    """List contents of a directory."""
    
    name = "directory_list"
    description = "Lista arquivos e diretórios em um diretório local."
    parameters = [{
        "name": "path",
        "type": "string",
        "description": "Caminho do diretório para listar",
        "required": True
    }]
    
    def call(self, params: str) -> str:
        parsed = self.validate_params(params)
        if "error" in parsed:
            return json.dumps(parsed)
        
        path = Path(parsed.get("path", "."))
        
        if not path.exists():
            return json.dumps({"error": f"Directory not found: {path}"})
        
        if not path.is_dir():
            return json.dumps({"error": f"Not a directory: {path}"})
        
        try:
            items = []
            for item in path.iterdir():
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else 0
                })
            
            return json.dumps({
                "path": str(path),
                "items": items,
                "count": len(items)
            })
        except Exception as e:
            return json.dumps({"error": f"Cannot list directory: {str(e)}"})


class FileSearchTool(BaseTool):
    """Search for files by pattern."""
    
    name = "file_search"
    description = "Busca arquivos por padrão (glob). Útil para encontrar arquivos específicos."
    parameters = [
        {
            "name": "pattern",
            "type": "string",
            "description": "Padrão de busca (ex: *.py, **/*.txt)",
            "required": True
        },
        {
            "name": "path",
            "type": "string",
            "description": "Diretório base para busca",
            "required": False,
            "default": "."
        }
    ]
    
    def call(self, params: str) -> str:
        parsed = self.validate_params(params)
        if "error" in parsed:
            return json.dumps(parsed)
        
        pattern = parsed.get("pattern", "*")
        base_path = Path(parsed.get("path", "."))
        
        if not base_path.exists():
            return json.dumps({"error": f"Path not found: {base_path}"})
        
        try:
            matches = list(base_path.rglob(pattern))
            results = [
                {
                    "path": str(m),
                    "type": "directory" if m.is_dir() else "file",
                    "size": m.stat().st_size if m.is_file() else 0
                }
                for m in matches[:100]  # Limit to 100 results
            ]
            
            return json.dumps({
                "pattern": pattern,
                "base_path": str(base_path),
                "matches": results,
                "count": len(results)
            })
        except Exception as e:
            return json.dumps({"error": f"Search failed: {str(e)}"})


class CalculatorTool(BaseTool):
    """Safe mathematical calculator."""
    
    name = "calculator"
    description = "Calculadora matemática segura para operações básicas."
    parameters = [{
        "name": "expression",
        "type": "string",
        "description": "Expressão matemática (ex: 2 + 2 * 3)",
        "required": True
    }]
    
    def call(self, params: str) -> str:
        parsed = self.validate_params(params)
        if "error" in parsed:
            return json.dumps(parsed)
        
        expression = parsed.get("expression", "")
        
        # Safety: only allow safe math operations
        safe_pattern = re.compile(r'^[\d\s\+\-\*\/\.\(\)]+$')
        if not safe_pattern.match(expression):
            return json.dumps({
                "error": "Invalid expression. Only numbers and + - * / allowed"
            })
        
        try:
            result = eval(expression, {"__builtins__": {}}, {})
            return json.dumps({
                "expression": expression,
                "result": result
            })
        except Exception as e:
            return json.dumps({"error": f"Calculation failed: {str(e)}"})


class TextTransformTool(BaseTool):
    """Transform text (uppercase, lowercase, etc.)."""
    
    name = "text_transform"
    description = "Transforma texto (maiúsculas, minúsculas, etc.)."
    parameters = [
        {
            "name": "text",
            "type": "string",
            "description": "Texto para transformar",
            "required": True
        },
        {
            "name": "operation",
            "type": "string",
            "description": "Operação: upper, lower, title, reverse",
            "required": True
        }
    ]
    
    def call(self, params: str) -> str:
        parsed = self.validate_params(params)
        if "error" in parsed:
            return json.dumps(parsed)
        
        text = parsed.get("text", "")
        operation = parsed.get("operation", "upper")
        
        try:
            if operation == "upper":
                result = text.upper()
            elif operation == "lower":
                result = text.lower()
            elif operation == "title":
                result = text.title()
            elif operation == "reverse":
                result = text[::-1]
            else:
                return json.dumps({"error": f"Unknown operation: {operation}"})
            
            return json.dumps({
                "original": text,
                "operation": operation,
                "result": result
            })
        except Exception as e:
            return json.dumps({"error": f"Transform failed: {str(e)}"})


class ToolRegistry:
    """Registry for local tools."""
    
    _tools: dict[str, BaseTool] = {}
    
    @classmethod
    def register(cls, tool: BaseTool) -> None:
        """Register a tool."""
        cls._tools[tool.name] = tool
    
    @classmethod
    def get(cls, name: str) -> BaseTool | None:
        """Get a tool by name."""
        return cls._tools.get(name)
    
    @classmethod
    def list_all(cls) -> list[dict]:
        """List all registered tools."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for tool in cls._tools.values()
        ]


# Register default tools
ToolRegistry.register(FileReadTool())
ToolRegistry.register(FileWriteTool())
ToolRegistry.register(DirectoryListTool())
ToolRegistry.register(FileSearchTool())
ToolRegistry.register(CalculatorTool())
ToolRegistry.register(TextTransformTool())
