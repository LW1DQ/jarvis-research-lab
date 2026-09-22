#!/usr/bin/env python3
"""
Configuración PaperQA2 HÍBRIDA: Local Ollama (default) + Cloud APIs opcional
Validada 2026-09-11: chain -> ollama/qwen3:8b (sin gpt-4o fallback)

ESTRATEGIA HÍBRIDA:
- LOCAL (Ollama): embeddings, coding, drafting, privacidad papers
- CLOUD (OpenRouter/Groq): reasoning complejo, PaperQA2 agent nativo, contexto largo
"""
import os

# CRÍTICO: Variables que rompen PaperQA2 - MUST BE BEFORE ANY IMPORTS
for var in ['AGENT', 'OPENAI_API_KEY', 'OPENAI_API_BASE', 'OPENROUTER_API_KEY', 'OPENAI_ADMIN_KEY', 'OPENAI_ORGANIZATION']:
    os.environ.pop(var, None)

# Workaround: set dummy key to prevent litellm from trying OpenAI
os.environ['OPENAI_API_KEY'] = 'EMPTY'
os.environ['OPENAI_API_BASE'] = 'http://127.0.0.1:11434/v1'  # Point to Ollama OpenAI-compatible endpoint
os.environ['OLLAMA_API_BASE'] = 'http://127.0.0.1:11434'

from paperqa import Settings
from paperqa.settings import AgentSettings, ParsingSettings

# ============================================================
# CONFIG LOCAL (Ollama) - DEFAULT para embeddings, coding, drafting
# ============================================================
# Configuración completa para LiteLLMModel - incluye config legacy + llm_config tipado
OLLAMA_MODEL_NAME = "ollama/qwen3:8b"

OLLAMA_LEGACY_CONFIG = {
    "name": OLLAMA_MODEL_NAME,
    "model_list": [{
        "model_name": OLLAMA_MODEL_NAME,
        "litellm_params": {
            "model": OLLAMA_MODEL_NAME,
            "temperature": 0.0,
            "api_base": "http://127.0.0.1:11434",
            "extra_body": {"think": False},
            "timeout": 300,
        }
    }]
}

OLLAMA_CONFIG = {
    "model_list": [{
        "model_name": OLLAMA_MODEL_NAME,
        "litellm_params": {
            "model": OLLAMA_MODEL_NAME,
            "temperature": 0.0,
            "api_base": "http://127.0.0.1:11434",
            "extra_body": {"think": False},
            "timeout": 300,
        }
    }]
}

# ============================================================
# CONFIG CLOUD (OpenRouter/Groq) - OPCIONAL para reasoning complejo
# ============================================================
# Requiere: export OPENROUTER_API_KEY=... / export GROQ_API_KEY=...
OPENROUTER_CONFIG = {
    "model_list": [
        {
            "model_name": "openrouter/anthropic/claude-3.5-sonnet",
            "litellm_params": {
                "model": "openrouter/anthropic/claude-3.5-sonnet",
                "api_base": "https://openrouter.ai/api/v1",
                "api_key": os.getenv("OPENROUTER_API_KEY"),
                "temperature": 0.0,
                "timeout": 120,
            }
        },
        {
            "model_name": "groq/llama-3.1-70b-versatile",
            "litellm_params": {
                "model": "groq/llama-3.1-70b-versatile",
                "api_base": "https://api.groq.com/openai/v1",
                "api_key": os.getenv("GROQ_API_KEY"),
                "temperature": 0.0,
                "timeout": 60,
            }
        }
    ]
}

# ============================================================
# FUNCIÓN PRINCIPAL: Retorna Settings según modo
# ============================================================
def get_paperqa_settings(use_cloud_agent: bool = False):
    """
    Args:
        use_cloud_agent: Si True, usa cloud model para agent_llm (PaperQA2 agent nativo multi-hop)
                         Si False, usa FakeAgent local (default, más seguro)
    """
    # Config base siempre local - usa OLLAMA_LEGACY_CONFIG que incluye 'name' para evitar default gpt-4o
    base_settings = dict(
        llm=OLLAMA_MODEL_NAME,
        config=OLLAMA_LEGACY_CONFIG,
        llm_config=OLLAMA_LEGACY_CONFIG,
        summary_llm=OLLAMA_MODEL_NAME,
        summary_llm_config=OLLAMA_LEGACY_CONFIG,
        embedding="ollama/nomic-embed-text",
        parsing=ParsingSettings(
            enrichment_llm=OLLAMA_MODEL_NAME,
            enrichment_llm_config=OLLAMA_LEGACY_CONFIG,
            multimodal=0,
        ),
    )

    if use_cloud_agent and (os.getenv("OPENROUTER_API_KEY") or os.getenv("GROQ_API_KEY")):
        # MODO HÍBRIDO: Agent nativo con cloud model
        cloud_agent_config = OPENROUTER_CONFIG
        agent_type = "auto"
        agent_llm = "openrouter/anthropic/claude-3.5-sonnet"
        print("☁️  PaperQA2: MODO HÍBRIDO - Agent nativo con Cloud (OpenRouter/Groq)")
    else:
        # MODO LOCAL: FakeAgent seguro
        cloud_agent_config = OLLAMA_LEGACY_CONFIG
        agent_type = "FakeAgent"
        agent_llm = OLLAMA_MODEL_NAME
        print("🏠 PaperQA2: MODO LOCAL - FakeAgent con Ollama")

    return Settings(
        **base_settings,
        agent=AgentSettings(
            agent_llm=agent_llm,
            agent_llm_config=cloud_agent_config,
            agent_type=agent_type,
        ),
    )


# Verificación rápida de la chain
if __name__ == "__main__":
    print("=" * 60)
    print("PaperQA2 Config - Verificación de chains")
    print("=" * 60)

    # Test modo local
    print("\n🏠 MODO LOCAL (FakeAgent):")
    s_local = get_paperqa_settings(use_cloud_agent=False)
    llm = s_local.get_llm()
    print(f"  Main LLM: {llm.name}")
    for spec in llm.llm_config.models:
        print(f"    -> {spec.name}")

    # Test modo híbrido (solo si hay API keys)
    if os.getenv("OPENROUTER_API_KEY") or os.getenv("GROQ_API_KEY"):
        print("\n☁️  MODO HÍBRIDO (Cloud Agent):")
        s_hybrid = get_paperqa_settings(use_cloud_agent=True)
        agent_llm = s_hybrid.get_agent_llm()
        print(f"  Agent LLM: {agent_llm.name}")
        for spec in agent_llm.llm_config.models:
            print(f"    -> {spec.name}")
    else:
        print("\n☁️  MODO HÍBRIDO: No configurado (falta OPENROUTER_API_KEY / GROQ_API_KEY)")

    print("\n" + "=" * 60)
    print("Embedding model:", s_local.embedding)
    print("Agent type:", s_local.agent.agent_type)
    print("=" * 60)