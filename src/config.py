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

"""Configuration system for Qwen-Agentes."""

from enum import Enum
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ProviderType(str, Enum):
    """Supported AI providers."""
    QWEN = "qwen"
    CLAUDE = "claude"
    GPT = "gpt"
    GEMINI = "gemini"


class ExecutionMode(str, Enum):
    """Execution mode for development tasks."""
    QUICK = "quick"       # 1 iteration, minimal agents
    STANDARD = "standard" # 3 iterations, full pipeline
    DEEP = "deep"         # 5 iterations, + documentation + tests
    
    @property
    def max_iterations(self) -> int:
        """Get max iterations for this mode."""
        return {
            ExecutionMode.QUICK: 1,
            ExecutionMode.STANDARD: 3,
            ExecutionMode.DEEP: 5,
        }[self]
    
    @property
    def enable_docs(self) -> bool:
        """Check if documentation generation is enabled."""
        return self == ExecutionMode.DEEP
    
    @property
    def enable_tests(self) -> bool:
        """Check if test generation is enabled."""
        return self in (ExecutionMode.STANDARD, ExecutionMode.DEEP)


class AgentConfig(BaseModel):
    """Configuration for a single agent."""
    temperature: float = 0.2


class AgentsConfig(BaseModel):
    """Configuration for all agents."""
    architect: AgentConfig = Field(default_factory=AgentConfig)
    developer: AgentConfig = Field(default_factory=AgentConfig)
    qa: AgentConfig = Field(default_factory=AgentConfig)
    security: AgentConfig = Field(default_factory=AgentConfig)
    reviewer: AgentConfig = Field(default_factory=AgentConfig)


class LoggingConfig(BaseModel):
    """Logging configuration."""
    level: str = "INFO"
    format: str = "json"
    output: str = "./logs/app.log"


class FeaturesConfig(BaseModel):
    """Feature flags configuration."""
    save_artifacts: bool = True
    run_tests: bool = False
    security_validation: bool = True
    structured_output: bool = True


class Config(BaseSettings):
    """Main application configuration."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Provider settings
    provider: ProviderType = ProviderType.QWEN
    model: Optional[str] = None
    timeout: int = 300  # 5 minutes for complex tasks
    max_iterations: int = 5
    mode: ExecutionMode = ExecutionMode.STANDARD

    # API keys
    qwen_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None

    # Paths
    project_dir: Optional[Path] = None  # Target project for YOLO mode
    output_dir: Path = Path("./output")
    config_file: Path = Path("./config.yaml")

    # Features
    features: FeaturesConfig = Field(default_factory=FeaturesConfig)
    agents: AgentsConfig = Field(default_factory=AgentsConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "Config":
        """Load configuration from YAML file and environment."""
        config_file = config_path or Path("./config.yaml")
        
        # Start with defaults from pydantic
        config_data = {}
        
        # Load YAML if exists
        if config_file.exists():
            with open(config_file, "r") as f:
                yaml_data = yaml.safe_load(f)
                if yaml_data:
                    config_data.update(yaml_data)
        
        # Convert nested dicts to proper models
        if "agents" in config_data:
            agents_data = config_data["agents"]
            for agent_name, agent_config in agents_data.items():
                if isinstance(agent_config, dict):
                    agents_data[agent_name] = AgentConfig(**agent_config)
            config_data["agents"] = AgentsConfig(**agents_data)
        
        if "features" in config_data:
            config_data["features"] = FeaturesConfig(**config_data["features"])
        
        if "logging" in config_data:
            config_data["logging"] = LoggingConfig(**config_data["logging"])
        
        return cls(**config_data)

    def save(self, path: Optional[Path] = None) -> None:
        """Save current configuration to YAML file."""
        save_path = path or self.config_file
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = self.model_dump(mode="json")
        with open(save_path, "w") as f:
            yaml.dump(data, f, indent=2, default_flow_style=False)


def get_config() -> Config:
    """Get application configuration."""
    return Config.load()
