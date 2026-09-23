---
title: "System Architecture"
date: "{{date:YYYY-MM-DD}}"
tags: [architecture, system, mermaid]
project: "JARVIS Research"
---

# System Architecture - JARVIS Research

## 🏗️ Visión General (Híbrida Host + Docker)

```mermaid
graph TB
    subgraph HOST["HOST (Ubuntu 26.04) - ~16GB RAM"]
        OLLAMA["Ollama :11434\nqwen3:8b (5.2GB)\nqwen2.5-coder:7b (4.7GB)\nnomic-embed-text (274MB)"]
        MCP["MCP Servers (HTTP 8001-8004)\nresearch-mcp:8001\nns3-mcp:8002\npython-mcp:8003\npersonal-mcp:8004"]
        VENV[".venv-science (uv + Py3.12)\nMem0 + Qdrant Client"]
        NS3["NS-3.48 + ns3-ai (compilado)\n~/ns-3.48/contrib/ai\ncommit: b8c9858"]
        SWAP["Swap 16GB\nvm.swappiness=10"]
    end

    subgraph DOCKER["DOCKER"]
        LDR["LDR :5000\nLocal Deep Research"]
        SEARX["SearXNG (interno)\nBúsqueda web privada"]
        QFUSE["LangFuse :3000\nClickHouse + PostgreSQL + MinIO\nObservabilidad"]
        QDRANT["Qdrant :6333\nVector DB híbrida (BM25 + vector)\nCollection: jarvis_memory (dim=768)"]
    end

    HOST --- DOCKER
```

## 🔄 Flujo de Datos - Orquestador LangGraph v2

```mermaid
stateDiagram-v2
    [*] --> Supervisor
    Supervisor --> Researcher: Sin research
    Supervisor --> Writer: Research OK, sin draft
    Supervisor --> NS3_Sim: Requiere simulación
    Supervisor --> Critiquer: Draft OK, sin critique
    Supervisor --> [*]: Critique APPROVED o rev ≥ 3
    
    Researcher --> Supervisor: findings + save_note
    Writer --> Critiquer: draft completo
    NS3_Sim --> Supervisor: resultados + manifest.json
    Critiquer --> Writer: feedback + revision
    Critiquer --> Supervisor: APPROVED
```

## 🧠 Memoria Agéntica (Mem0 + Qdrant)

```mermaid
graph LR
    subgraph AGENTS["Agentes LangGraph"]
        S[Supervisor]
        R[Researcher]
        W[Writer]
        N[NS-3 Agent]
        C[Critiquer]
    end

    subgraph MEMORY["Memoria"]
        EPISODIC[EpisodicMemoryAgent\nrecord_interaction\nget_context_for_task\nlearn_from_error\nrecord_insight]
        SEMANTIC[MemoryAgent (Mem0)\nadd_memory\nsearch_memories\nrecord_error\nrecord_insight]
        QDRANT[(Qdrant :6333\njarvis_memory\ndim=768\nnomic-embed-text)]
        CHROMA[(ChromaDB\n~/chroma/personal/\npersonal-mcp)]
    end

    AGENTS --> EPISODIC
    EPISODIC --> SEMANTIC
    SEMANTIC --> QDRANT
    AGENTS -.-> CHROMA
```

## 🐳 Docker NS-3 Standalone

```mermaid
graph TB
    subgraph CONTAINER["ns3-simulation:latest (Ubuntu 22.04)"]
        BASE["Base: build-essential, cmake, ninja\nlibboost-all-dev, libssl-dev\nlibprotobuf-dev, protobuf-compiler\nlibgsl-dev, python3-dev"]
        PY["Python: numpy, scipy, matplotlib\npandas, protobuf, grpcio\ngrpcio-tools, pyyaml, pyzmq\ncppyy"]
        NS3AI["NS-3 AI bindings\n/workspace/ns3-ai\n/workspace/simulations\n/workspace/results"]
        ENTRY["docker-entrypoint.sh\nbash / ns3 / python"]
    end

    HOST_NS3["Host NS-3 (mount)\n/opt/ns-3.48"] --> CONTAINER
    QDRANT_HOST["Qdrant Host :6333"] --> CONTAINER
```

## 📊 Asignación de Modelos LLM

| Agente | Modelo | Tiempo | Config Crítica |
|--------|--------|--------|----------------|
| Supervisor | qwen3:8b | ~2s | `think:false`, timeout 300s |
| Researcher | qwen3:8b | 92s | `think:false`, timeout 300s |
| Writer | qwen3:8b | 92s | `think:false`, timeout 300s |
| NS-3 Agent | qwen2.5-coder:7b | 37s | Coding especializado |
| Critiquer | qwen3:8b | 92s | `think:false`, timeout 300s |

## 🔌 MCP Servers

| Server | Puerto | Herramientas | LLM Asociado |
|--------|--------|-------------|--------------|
| research-mcp | 8001 | search_papers, search_arxiv, search_openalex, search_crossref, summarize_paper, find_gaps, search_knowledge, save_research_note | qwen3:8b |
| python-mcp | 8003 | run_python, install_package, list_packages | qwen3:8b / qwen2.5-coder:7b |
| ns3-mcp | 8002 | run_ns3_simulation, build_ns3, list_ns3_modules, ns3_ai_status | qwen2.5-coder:7b |
| personal-mcp | 8004 | add_note, search_notes, list_notes, delete_note | qwen3:8b |

## 📈 Métricas de Rendimiento (Día 13)

| Métrica | Valor |
|---------|-------|
| RAM usada (Host) | ~12-13GB / 16GB |
| Swap usado | 0-2GB / 16GB |
| End-to-End latency | ~3-5 min |
| PaperQA2 query | 92s (qwen3:8b) |
| NS-3 build | ~5 min (incremental) |
| Memory search | <100ms (Qdrant) |

---

*Arquitectura validada Día 13 - Sistema operativo para tesis*