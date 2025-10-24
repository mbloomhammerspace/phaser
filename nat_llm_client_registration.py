#!/usr/bin/env python3
"""
NAT LLM Client Registration Fix

Registers LLM client wrappers for native NAT providers (NIM, OpenAI).
This fixes the "no LangChain-compatible LLM client" error by providing
a direct client interface without LangChain dependency.

Usage:
  1. Copy this file to the NAT container
  2. Import it before running workflows: `python3 -c "import nat_llm_client_registration"`
"""

import asyncio
import logging
from typing import Any

from nat.builder.builder import Builder
from nat.builder.framework_enum import LLMFrameworkEnum
from nat.builder.llm import LLMProviderInfo
from nat.cli.register_workflow import register_llm_client
from nat.cli.type_registry import GlobalTypeRegistry
from nat.llm.nim_llm import NIMModelConfig
from nat.llm.openai_llm import OpenAIModelConfig

logger = logging.getLogger(__name__)


# ============================================================================
# Direct LLM Client Classes (No LangChain Dependency)
# ============================================================================

class DirectNIMClient:
    """Direct NIM client without LangChain wrapper"""
    
    def __init__(self, config: NIMModelConfig):
        self.config = config
        self.base_url = config.base_url or "http://nim-llm:8000"
        self.model_name = config.model_name
        self.api_key = config.api_key or "nvidia"
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens
    
    async def generate(self, prompt: str) -> str:
        """Generate text using the NIM model"""
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                },
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    async def __call__(self, prompt: str) -> str:
        """Make the client callable"""
        return await self.generate(prompt)


class DirectOpenAIClient:
    """Direct OpenAI-compatible client without LangChain wrapper"""
    
    def __init__(self, config: OpenAIModelConfig):
        self.config = config
        self.base_url = config.base_url or "https://api.openai.com/v1"
        self.model_name = config.model_name
        self.api_key = config.api_key or "sk-dummy"
        self.temperature = config.temperature
        self.max_tokens = config.max_tokens
    
    async def generate(self, prompt: str) -> str:
        """Generate text using OpenAI or compatible endpoint"""
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                },
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    async def __call__(self, prompt: str) -> str:
        """Make the client callable"""
        return await self.generate(prompt)


# ============================================================================
# Registration Functions
# ============================================================================

@register_llm_client(config_type=NIMModelConfig, wrapper_type="native")
async def nim_native_client(config: NIMModelConfig, builder: Builder):
    """Register NIM as a native client (no framework wrapper)"""
    logger.info("Registering NIM native client")
    
    client = DirectNIMClient(config)
    
    # Yield a callable that can be used by workflows
    yield client


@register_llm_client(config_type=OpenAIModelConfig, wrapper_type="native")
async def openai_native_client(config: OpenAIModelConfig, builder: Builder):
    """Register OpenAI as a native client (no framework wrapper)"""
    logger.info("Registering OpenAI native client")
    
    client = DirectOpenAIClient(config)
    
    # Yield a callable that can be used by workflows
    yield client


if __name__ == "__main__":
    logger.info("✅ LLM client registrations loaded")
    logger.info(f"Registered clients: NIM (native), OpenAI (native)")
