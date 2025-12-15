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
WebUI for Qwen-Agentes using Gradio.

Provides a web interface for interacting with agents.
100% local - no external dependencies (except Gradio).
"""

import os
import sys
from pathlib import Path
from typing import Callable

# Try to import gradio
try:
    import gradio as gr
except ImportError:
    raise ImportError(
        "Gradio not installed. Install with: pip install gradio"
    )

from ..core.orchestrator import Orchestrator, OrchestratorConfig
from ..providers.qwen_provider import QwenProvider


class WebUI:
    """Web interface for Qwen-Agentes using Gradio."""
    
    def __init__(
        self,
        orchestrator: Orchestrator | None = None,
        server_port: int = 7860,
        share: bool = False
    ):
        """
        Initialize WebUI.
        
        Args:
            orchestrator: Orchestrator instance (creates default if None)
            server_port: Port to run the web server
            share: Create public shareable link
        """
        self.orchestrator = orchestrator or self._create_default_orchestrator()
        self.server_port = server_port
        self.share = share
        self.chat_history = []
    
    def _create_default_orchestrator(self) -> Orchestrator:
        """Create default orchestrator with Qwen provider."""
        provider = QwenProvider(timeout=120)
        config = OrchestratorConfig(
            max_iterations=5,
            save_artifacts=True,
            run_security_validation=True
        )
        return Orchestrator(provider, config)
    
    def _format_response(self, ctx) -> str:
        """Format execution context as readable response."""
        if not ctx.iterations:
            return "Nenhuma iteração executada."
        
        lines = []
        lines.append("## 📊 Resultado\n")
        
        # Status
        status = "✅ APROVADO" if ctx.is_approved else "⚠️ Não aprovado"
        lines.append(f"**Status:** {status}")
        lines.append(f"**Iterações:** {len(ctx.iterations)}\n")
        
        # Last iteration summary
        last = ctx.last_iteration
        if last:
            lines.append("### 📝 Resumo da Última Iteração")
            lines.append(f"- **Blocos de código:** {len(last.code_blocks)}")
            lines.append(f"- **Issues QA:** {len(last.qa_issues)}")
            lines.append(f"- **Issues Security:** {len(last.security_issues)}")
            lines.append(f"- **Reviewer:** {last.reviewer_notes[:100]}...\n")
        
        # Output path
        if ctx.output_dir:
            lines.append(f"### 📁 Arquivos Gerados")
            lines.append(f"Saída: `{ctx.output_dir / f'run_{ctx.id}'}`\n")
        
        return "\n".join(lines)
    
    def _run_task(self, task: str, progress=gr.Progress()) -> tuple:
        """
        Run a task and return formatted response.
        
        Args:
            task: Task description
            progress: Gradio progress tracker
            
        Returns:
            Tuple of (chat_history, formatted_response)
        """
        if not task.strip():
            return self.chat_history, "Por favor, descreva o que deseja construir."
        
        try:
            # Add user message
            self.chat_history.append((task, ""))
            
            # Run orchestrator
            ctx = self.orchestrator.run(task)
            
            # Format response
            response = self._format_response(ctx)
            
            # Update chat history
            self.chat_history[-1] = (task, response)
            
            return self.chat_history, response
            
        except Exception as e:
            error_msg = f"❌ Erro: {str(e)}"
            self.chat_history[-1] = (task, error_msg)
            return self.chat_history, error_msg
    
    def _clear_chat(self) -> tuple:
        """Clear chat history."""
        self.chat_history = []
        return [], ""
    
    def _show_templates(self) -> str:
        """Show available templates."""
        from .templates import TemplateLibrary
        
        templates = TemplateLibrary.list_all()
        
        lines = ["## 📦 Templates Disponíveis\n"]
        
        by_category = {}
        for t in templates:
            cat = t["category"]
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(t)
        
        for category, items in by_category.items():
            lines.append(f"### {category.title()}")
            for item in items:
                tags = ", ".join(f"`{tag}`" for tag in item["tags"])
                lines.append(f"- **{item['name']}**: {item['description']}")
                lines.append(f"  Tags: {tags}\n")
        
        lines.append("\n💡 Use: `Use o template: <nome>` para usar um template")
        
        return "\n".join(lines)
    
    def create_interface(self) -> "gr.Blocks":
        """Create Gradio interface."""
        
        with gr.Blocks(
            title="Qwen-Agentes",
            theme=gr.themes.Soft()
        ) as demo:
            
            # Header
            gr.Markdown("""
                # 🤖 Qwen-Agentes
                
                Sistema multi-agente para desenvolvimento de software.
                Descreva o que deseja construir e os agentes trabalharão juntos.
            """)
            
            # Main UI
            with gr.Row():
                # Left column - Chat
                with gr.Column(scale=2):
                    chatbot = gr.Chatbot(
                        label="Qwen-Agentes",
                        height=500,
                        show_copy_button=True
                    )
                    
                    with gr.Row():
                        msg_input = gr.Textbox(
                            label="O que deseja construir?",
                            placeholder="Ex: crie um servidor REST com FastAPI...",
                            scale=4
                        )
                        send_btn = gr.Button("Enviar", variant="primary", scale=1)
                    
                    with gr.Row():
                        clear_btn = gr.Button("🗑️ Limpar")
                        templates_btn = gr.Button("📦 Templates")
                
                # Right column - Info
                with gr.Column(scale=1):
                    gr.Markdown("### 📊 Status")
                    status_box = gr.Textbox(
                        label="Última Resposta",
                        lines=20,
                        max_lines=30
                    )
                    
                    gr.Markdown("""
                        ### ℹ️ Como Usar
                        
                        1. Descreva o que deseja construir
                        2. Os agentes trabalharão juntos:
                           - 🏗️ Architect: Define arquitetura
                           - 👨‍💻 Developer: Implementa código
                           - 🔍 QA: Encontra bugs
                           - 🔒 Security: Audit segurança
                           - ✅ Reviewer: Aprova ou reprova
                        3. Receba o código pronto!
                    """)
            
            # Event handlers
            send_btn.click(
                fn=self._run_task,
                inputs=[msg_input],
                outputs=[chatbot, status_box]
            )
            
            msg_input.submit(
                fn=self._run_task,
                inputs=[msg_input],
                outputs=[chatbot, status_box]
            )
            
            clear_btn.click(
                fn=self._clear_chat,
                outputs=[chatbot, status_box]
            )
            
            templates_btn.click(
                fn=self._show_templates,
                outputs=[status_box]
            )
            
            # Footer
            gr.Markdown("""
                ---
                **Qwen-Agentes** - Desenvolvido com ❤️ usando Qwen CLI
            """)
        
        return demo
    
    def run(self) -> None:
        """Run the web interface."""
        print("=" * 60)
        print("  Qwen-Agentes WebUI")
        print("=" * 60)
        print(f"\n🌐 Servidor iniciando em http://localhost:{self.server_port}")
        print("\n💡 Dica: Use Ctrl+C para parar o servidor\n")
        
        demo = self.create_interface()
        demo.launch(
            server_port=self.server_port,
            share=self.share
        )


def main():
    """Main entry point for WebUI."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Qwen-Agentes WebUI")
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=7860,
        help="Port to run the server (default: 7860)"
    )
    parser.add_argument(
        "--share", "-s",
        action="store_true",
        help="Create public shareable link"
    )
    
    args = parser.parse_args()
    
    webui = WebUI(server_port=args.port, share=args.share)
    webui.run()


if __name__ == "__main__":
    main()
