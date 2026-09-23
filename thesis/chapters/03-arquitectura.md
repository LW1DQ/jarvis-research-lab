# Capítulo 3: Arquitectura del Sistema JARVIS

## 3.1 Visión General

```
┌─────────────────────────────────────────────────────────────┐
│                    HOST (Ubuntu 26.04)                       │
│                                                              │
│  ┌──────────────┐  ┌────────────────────────────────────┐  │
│  │   Ollama     │  │     MCP Servers (FastMCP)          │  │
│  │  :11434      │  │  research-mcp  :8001 (8 tools)     │  │
│  │  systemd     │  │  python-mcp    :8003 (3 tools)     │  │
│  │  ~5.5GB      │  │  ns3-mcp       :8002 (4 tools)     │  │
│  │  (qwen3:8b)  │  │  personal-mcp  :8004 (4 tools)     │  │
│  └──────────────┘  └────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ ~/research-jarvis/                                   │   │
│  │ papers/ projects/ agents/ mcp/                       │   │
│  │ .venv-science/ (uv, Python 3.12, todos los paquetes)│   │
│  │ chroma/personal/  (ChromaDB local)                   │   │
│  │ obsidian-vault/   (Documentación tesis)              │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────┐  ┌────────────────────────────────┐   │
│  │  NS-3.48         │  │  Paquetes Científicos          │   │
│  │  ~/ns-3.48/      │  │  darts, paper-qa, chromadb,    │   │
│  │  contrib/ns3-ai  │  │  sentence-transformers,        │   │
│  │  commit b8c9858  │  │  numpy, pandas, scipy,         │   │
│  │  (CMake build)   │  │  matplotlib, qdrant-client,    │   │
│  └──────────────────┘  │  gymnasium, grpcio, psutil     │   │
│                        └────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
          │                              │
    ┌─────┴──────┐                  ┌─────┴──────┐
    │   Docker   │                  │  SWAP      │
    │    LDR     │                  │  16GB      │
    │   :5000    │                  │  vm.swap=10│
    │ + SearXNG  │                  │ (OOM guard)│
    │  mem: 2GB  │                  └────────────┘
    └────────────┘
```

**RAM estimada: ~12-13GB de 16GB + Swap 16GB (protección OOM)**

## 3.2 Decisiones Arquitectónicas (ADRs)

### ADR-018: litellm + qwen3 thinking mode
- **Decisión**: `extra_body={'think': False}` top-level en PaperQA2 config
- **Razón**: litellm usa `/api/generate` + qwen3 thinking → `response: ''` vacío

### ADR-019: RAM OOM - Eliminar OpenHands
- **Decisión**: `docker stop openhands && docker rm openhands` + Swap 16GB
- **Razón**: Margen 0GB → 4.5GB seguro (OpenHands consumía 3GB)

### ADR-020: Swap config
- **Decisión**: 16GB + `vm.swappiness=10` (kernel swapea solo bajo presión)
- **Razón**: Evita OOM killer sin degradar performance normal

### ADR-021: Python env unificado
- **Decisión**: `.venv-science` con `uv venv --python 3.12` + TODOS los paquetes
- **Razón**: ns3-ai bindings requieren Python 3.12 compatible

### ADR-022: PaperQA2 Agent
- **Decisión**: `FakeAgent` + LangGraph orquestador
- **Razón**: qwen3 falla en tool-calling complejo; LangGraph maneja flujo

### ADR-023: Orquestador
- **Decisión**: **LangGraph** (ref Phoenix1454)
- **Razón**: Estándar SOTA, checkpoints, compatible Ollama, edges determinísticos

### ADR-024: Writer output
- **Decisión**: **Markdown + Pandoc + Zotero**
- **Razón**: Versionable Git, citas perfectas (CSL), export LaTeX/PDF/DOCX

### ADR-025: Memoria agéntica
- **Decisión**: **Mem0** (episódica) + **ChromaDB/Qdrant** (vectorial)
- **Razón**: Aprender de errores NS-3, búsqueda híbrida BM25+semántico

### ADR-026: NS-3 Execution Model
- **Decisión**: Local (Fase 1) → Remote Worker API (Fase 2)
- **Razón**: Fase 1: margen OK. Fase 2: API REST para >1K corridas paralelas

### ADR-027: Estrategia LLM Híbrida
- **Decisión**: Local Ollama + Cloud opcional
- **Razón**: Local: embeddings, coding, drafting. Cloud: reasoning complejo

### ADR-028: Vector DB
- **Decisión**: ChromDB (Fase 1) → Qdrant (Fase 2)
- **Razón**: Fase 1: <100K vectores. Fase 2: >500K, pre-ANN, filtros

### ADR-029: Documentación tesis
- **Decisión**: **Obsidian Vault** + Git
- **Razón**: Markdown, Zotero, Dataview, Canvas, version control

## 3.3 Flujos de Datos Principales

### 3.3.1 Flujo: Research → Writer → NS-3
```
User Query
    │
    ▼
┌─────────────────┐
│ Supervisor      │ ──► Decide: research / sim / write
│ (LangGraph)     │
└────────┬────────┘
         │ research
         ▼
┌─────────────────┐
│ Researcher      │ ──► PaperQA2 + arXiv + OpenAlex via research-mcp
│ (Node)          │     save_note via personal-mcp
└────────┬────────┘
         │ evidence_package
         ▼
┌─────────────────┐
│ Writer          │ ──► Markdown → Pandoc → DOCX/LaTeX
│ (Node)          │     Zotero citations (CSL)
└────────┬────────┘
         │ ns3_task
         ▼
┌─────────────────┐
│ NS-3 Simulation │ ──► run_tracked.py → manifest.json
│ (Node)          │     ns3-mcp HTTP :8002
└────────┬────────┘
         │ results
         ▼
┌─────────────────┐
│ Critiquer       │ ──► AutoGen Group Chat (5 agentes)
│ (Node)          │     5 dimensiones evaluación
└─────────────────┘
```

### 3.3.2 Flujo: Memoria Agéntica
```
Task Execution
    │
    ▼
┌─────────────────┐
│ MemoryAgent     │ ──► get_context_for_task(task) → relevant memories
│ (EpisodicMem)   │
└────────┬────────┘
         │
         ▼ (post-execution)
┌─────────────────┐
│ learn_from_error│ ──► Mem0.add_memory(error, context, solution)
│ record_insight  │ ──► Mem0.add_memory(insight, tags)
└─────────────────┘
```

## 3.4 Componentes Detallados

### 3.4.1 MCP Servers (Model Context Protocol)

| Server | Puerto | Herramientas | Descripción |
|--------|--------|--------------|-------------|
| **research-mcp** | 8001 | search_papers, summarize_paper, find_gaps, search_openalex, search_crossref, search_arxiv, search_knowledge, save_research_note | Búsqueda académica + guardar notas |
| **ns3-mcp** | 8002 | run_ns3_simulation, build_ns3, list_ns3_modules, ns3_ai_status | Ejecución NS-3 trazable |
| **python-mcp** | 8003 | run_python, install_package, list_packages | Ejecución Python sandboxed |
| **personal-mcp** | 8004 | add_note, search_notes, list_notes, delete_note | ChromaDB local personal |

### 3.4.2 Modelos LLM Operativos

| Modelo | Endpoint | Uso Principal | Config Crítica |
|--------|----------|---------------|----------------|
| **qwen2.5-coder:7b** | Ollama :11434 | Coding, NS-3 scripts | `NUM_PARALLEL=1` |
| **qwen3:8b** | Ollama :11434 | Reasoning, drafting | `think=false` nativo |
| **nomic-embed-text** | Ollama :11434 | Embeddings (dim=768) | Local, fast |

### 3.4.3 Vector Databases

| DB | Colección | Dimensión | Embedding | Uso |
|----|-----------|-----------|-----------|-----|
| **Qdrant** | `jarvis_memory` | 768 | nomic-embed-text | Mem0 episódica + híbrida BM25 |
| **ChromaDB** | `personal_notes` | 768 | nomic-embed-text | personal-mcp notas usuario |

## 3.5 Modelo de Ejecución NS-3: Fases

### Fase 1 (Días 9-13): Local Host
```
┌─────────────────────────────────────┐
│ Host: ~/ns-3.48/build/              │
│ ./ns3 run <script> --args           │
│ run_tracked.py → manifest.json      │
│ RAM: ~12-13GB + Swap 16GB           │
└─────────────────────────────────────┘
```

### Fase 2 (Post-Día 13): Remote Worker API
```
┌─────────────────┐     HTTPS/REST      ┌──────────────────────┐
│ Host (JARVIS)   │ ──────────────────► │ Worker Remoto        │
│                 │  POST /simulate     │ - NS-3.48 + GPU      │
│ LangGraph       │ ◄────────────────── │ - FastAPI + rsync    │
│ Orquestador     │  {manifest, logs}   │ - 32GB+ RAM / GPU    │
└─────────────────┘                     └──────────────────────┘
```

**Análisis**: Mover SOLO NS-3 por SSH **NO VIABLE** (ns3-ai usa Unix sockets IPC, latencia 10-100x).
**Solución Fase 2**: Stack completo de simulación en worker remoto con API REST (FastAPI) + rsync sync.

## 3.6 Seguridad y Aislamiento

| Capa | Implementación |
|------|----------------|
| **Docker** | LDR + SearXNG en contenedores aislados, memoria limitada (2GB) |
| **MCP** | Servidores HTTP locales (no expuestos a internet) |
| **SSH Tunnel** | Acceso remoto solo via `ssh -L` (puertos 8001-8004, 5000) |
| **Firewall** | UFW: deny incoming, allow OpenSSH + puertos específicos |
| **Permisos** | `.venv-science` user-owned, `chmod 600` en `.env` |
| **API Keys** | Ninguna en local (Ollama local-only); Cloud opcional via env vars |