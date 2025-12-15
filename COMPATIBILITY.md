# Qwen-Agentes - Guia de Compatibilidade

## Compatibilidade com a Versão Original

A nova implementação mantém **100% de compatibilidade** com a versão original do SwarmCode que usava o `qwen` via linha de comando.

### O Que Mudou

| Aspecto | Versão Original | Nova Versão | Compatível? |
|---------|----------------|-------------|-------------|
| Comando Qwen | `qwen` via subprocess | `qwen` via subprocess | ✅ Sim |
| Formato do Prompt | `{system}\n\nTAREFA:\n{user}` | `{system}\n\nTAREFA:\n{user}` | ✅ Sim |
| Timeout | 120s | 120s (configurável) | ✅ Sim |
| Agents | Arquivos .txt | Arquivos .txt + Classes | ✅ Sim |
| Fluxo | 5 agentes iterativos | 5 agentes iterativos | ✅ Sim |

### O Que Melhorou

- ✅ Provider abstraction (pode usar Claude, GPT, Gemini também)
- ✅ CLI profissional com Typer
- ✅ Persistência de execução
- ✅ Parser estruturado de código
- ✅ Validação automática de segurança
- ✅ Logging estruturado
- ✅ 44 testes unitários
- ✅ CI/CD com GitHub Actions

## Modos de Uso

### 1. Legacy Compatibility Mode (Idêntico ao Original)

Usa os arquivos de prompt da pasta `orchestrator/agents/` e o fluxo original:

```bash
cd /home/marco/Dvl/projetos/GitHub/SwarmCode
source venv/bin/activate

python legacy_compat.py
```

Este modo:
- ✅ Usa os mesmos prompts (architect.txt, developer.txt, etc.)
- ✅ Mesma ordem de execução (Architect → Developer → QA → Security → Reviewer)
- ✅ Mesmo formato de saída
- ✅ Mesma lógica de iteração (max 5, feedback loop)

### 2. New CLI Mode (Recomendado)

Usa a nova CLI profissional:

```bash
# Com Qwen (local, mesmo que a versão original)
SwarmCode run "crie um servidor REST com FastAPI"

# Com Claude
SwarmCode run "crie um servidor REST" -p claude

# Com GPT-4
SwarmCode run "crie um servidor REST" -p gpt
```

Este modo:
- ✅ Prompts otimizados nas classes dos agentes
- ✅ Parser estruturado de código
- ✅ Salva artefatos automaticamente
- ✅ Validação de segurança automática
- ✅ Contexto persistente

### 3. Programmatic Mode (API)

Use via código Python:

```python
from src.providers.qwen_provider import QwenProvider
from src.agents import ArchitectAgent, DeveloperAgent
from src.core.orchestrator import Orchestrator, OrchestratorConfig

# Provider (usa qwen CLI - 100% compatível)
provider = QwenProvider(timeout=120)

# Agentes
architect = ArchitectAgent(provider)
developer = DeveloperAgent(provider)

# Ou use o orchestrator completo
config = OrchestratorConfig(max_iterations=5)
orchestrator = Orchestrator(provider, config)

# Executar
ctx = orchestrator.run("crie um servidor REST")
```

## Testes de Compatibilidade

Execute os testes para verificar compatibilidade:

```bash
# Testes unitários
pytest tests/ -v

# Validação completa da estrutura
python test_structure.py

# Testar disponibilidade do qwen
SwarmCode health
```

## Migrando da Versão Original

Se você já usava a versão original:

### Antes (original)
```bash
cd orchestrator
python main.py
# Digita: "crie um servidor REST"
```

### Depois (nova versão)
```bash
# Opção 1: Legacy mode (idêntico)
python legacy_compat.py

# Opção 2: Nova CLI (recomendado)
SwarmCode run "crie um servidor REST"
```

## Arquivos de Prompt Originais

Os arquivos de prompt originais foram mantidos em `orchestrator/agents/`:

- `architect.txt` - Prompt do Architect
- `developer.txt` - Prompt do Developer
- `qa.txt` - Prompt do QA
- `security.txt` - Prompt do Security
- `reviewer.txt` - Prompt do Reviewer
- `tester.txt` - Prompt do Tester (não usado no pipeline principal)

Estes arquivos continuam funcionando no **Legacy Compatibility Mode**.

## Conclusão

**Sim, a compatibilidade com o qwen via linha de comando está 100% mantida!**

Você pode:
1. Usar o `legacy_compat.py` para comportamento idêntico ao original
2. Usar a nova CLI `SwarmCode run` com `-p qwen` (usa o mesmo provider)
3. Usar programaticamente com `QwenProvider` (mesmo formato de prompt)

A única diferença é que agora você também tem a opção de usar outros providers (Claude, GPT, Gemini) se desejar!
