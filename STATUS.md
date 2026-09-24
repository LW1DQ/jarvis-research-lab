# JARVIS Research Lab - Estado
# 2026-09-16 10:00 (Día 13 COMPLETADO - Experimento End-to-End OPERACIONAL)

## Arquitectura: Híbrida (Host + Docker) - OPTIMIZADA RAM

| Componente | Ubicación | Estado | RAM |
|------------|-----------|--------|-----|
| Ollama | Host (systemd) | ✅ ACTIVO localhost:11434 | ~5.5GB (qwen3:8b) |
| LDR | Docker :5000 | ✅ CORRIENDO | 2.5GB limit |
| SearXNG | Docker (interno) | ✅ HEALTHY | 512MB limit |
| **OpenHands** | **ELIMINADO** | **✅ Liberados 3GB** | **0 GB** |
| MCP servers | Host (Python/FastMCP) | ✅ 4 servidores HTTP | ~100MB |
| ns3-ai | Host (~/ns-3.48/contrib/ns3-ai) | ✅ Compilado, commit fijado | - |
| .venv-science | Host (~/research-jarvis/) | ✅ **uv + Python 3.12 COMPLETO** | - |
| **Swap** | **Disco** | **16GB ACTIVO** | **vm.swappiness=10** |
| LangFuse | Docker :3000 | ✅ Configurado (ClickHouse/Postgres/MinIO) | - |
| **Qdrant** | Docker :6333 | ✅ ACTIVO - Vector DB híbrida (BM25 + vector) | - |
| Dockerfile.ns3 | research-jarvis/ | ✅ **Build OK** - imagen ns3-simulation:latest | - |
| docker-entrypoint.sh | research-jarvis/ | ✅ **Creado** - Entrypoint compila gym interface | - |
| **Obsidian Vault** | ~/research-jarvis/obsidian-vault/ | ✅ **Creado** - Documentación tesis | - |

### Decisión Arquitectónica: NS-3 Execution Model
| Fase | Modelo | Ubicación NS-3 | Trigger |
|------|---------|----------------|---------|
| **FASE 1 (Días 9-13)** | **Local** | Host (~/ns-3.48) | Actual - margen 4.5GB + Swap |
| **FASE 2 (Post-Día 13)** | **Remote Worker API** | Máquina remota (32GB+/GPU) | >1K corridas paralelas / RL training |

**Análisis**: Mover SOLO NS-3 por SSH **NO VIABLE** (ns3-ai usa Unix sockets IPC, latencia 10-100x).
**Solución FASE 2**: Stack completo de simulación en worker remoto con API REST (FastAPI) + rsync sync.

## Servicios Críticos - Estado Actual

### Trazabilidad NS-3: run_tracked.py
- **Ruta**: /home/diego/research-jarvis/mcp/ns3/run_tracked.py
- **Status**: ✅ OPERATIVO - genera manifest.json automático
- **Propósito**: Reproducibilidad para 3.600+6.000 corridas

### LDR Authentication
- **URL**: http://localhost:5000
- **Usuario**: diego (registrado y funcional)
- **Modelo por defecto**: qwen3:8b

### MCP Servers (FastMCP 4.0.3) - TODOS HTTP en puertos 8001-8004
| Server | Puerto | Herramientas | Estado |
|--------|--------|-------------|--------|
| **research-mcp** | 8001 | search_papers, summarize_paper, find_gaps, search_openalex, search_crossref, search_arxiv, search_knowledge, save_research_note | ✅ OPERATIVO |
| **python-mcp** | 8003 | run_python, install_package, list_packages | ✅ OPERATIVO |
| **ns3-mcp** | 8002 | run_ns3_simulation, build_ns3, list_ns3_modules, ns3_ai_status | ✅ OPERATIVO |
| **personal-mcp** | 8004 | add_note, search_notes, list_notes, delete_note | ✅ OPERATIVO |

### Mem0 + Qdrant (Memoria Agéntica)
- **Qdrant** en Docker :6333, collection `jarvis_memory` (dim=768, nomic-embed-text)
- **Mem0** reemplazó ChromaDB como vector store principal del memory_agent
- **Híbrida**: Qdrant + fastembed (BM25 + búsqueda semántica)
- **EpisodicMemoryAgent**: record_interaction + get_context_for_task + learn_from_error + record_insight
- **Caché de errores**: learn_from_error (arXiv timeout, qwen3 thinking, etc.)

### NS-3 Python Bindings Fix (2026-09-23)
- **Problema**: `ns3ai_gym_msg_py` import fallaba con `undefined symbol: _ZN3ns34Time10StaticInitEv`
- **Causa raíz**: Linker `--as-needed` descartaba `libns3.48-ai-default.so` porque el binding code usa templates/inline functions sin referencias directas a símbolos
- **Fix aplicado**: `/home/diego/ns-allinone-3.48/ns-3.48/contrib/ai/model/gym-interface/py/CMakeLists.txt` - agrega `-Wl,--no-as-needed` antes de `ns3.48-ai-default` y `-Wl,--as-needed` después
- **Validación**: `import ns3ai_gym_msg_py` ✅ funcional en Python 3.11
- **Python 3.11 exclusivo** para ns3-mcp via uv (`/home/diego/.local/bin/python3.11`)

### MCP Servers Validación Completa (2026-09-23)
- **start-jarvis.sh** actualizado: pasa `LD_LIBRARY_PATH` y `PYTHONPATH` a ns3-mcp via `env`
- **Todos 4 servers MCP operativos** via MCP client (streamable-http):
  - research-mcp (8001): 8 tools ✅
  - ns3-mcp (8002): 4 tools ✅ (ns3_ai_status: OK)
  - python-mcp (8003): 3 tools ✅
  - personal-mcp (8004): 4 tools ✅
- **NS-3 gym bindings validados** end-to-end via MCP client

### Vector DB Strategy (Faseada)
| Fase | Vector DB | Trigger |
|------|-----------|---------|
| **Fase 1 (Días 9-12)** | **ChromaDB** | ✅ Funcional, <100K vectores (personal-mcp) |
| **Fase 2 (Día 11+)** | **Qdrant** | ✅ ACTIVO - Mem0 + memoria agéntica, filtros pre-ANN |

## Progreso General

| Día | Status | Observaciones |
|-----|--------|--------------|
| 1-7 | ✅ COMPLETADO | Fundación completa |
| 8 | ✅ COMPLETADO | PaperQA2 config funcional (think:false + timeout 300s) |
| 8.5 | ✅ COMPLETADO | **OOM mitigado: OpenHands eliminado, Swap 16GB, venv unificado** |
| 9 | ✅ **COMPLETADO** | **End-to-end: Researcher → Writer → NS-3 FUNCIONA** |
| 10 | ✅ **COMPLETADO** | **Orchestrator v2 + arXiv fix + MCP HTTP + LangGraph v2** |
| 11 | ✅ **COMPLETADO** | **Qdrant + Mem0 + NS-3 Gymnasium wrapper** |
| 12 | ✅ **COMPLETADO** | **Writer Markdown + Pandoc + Zotero + AutoGen Critiquer** |
| 13 | ✅ **COMPLETADO** | **Experimento End-to-End COMPLETO - SISTEMA OPERACIONAL** |

## Lo Que Funciona Para La Tesis
1. **Simulaciones NS-3**: compilado, ns3-ai bindings, MCP ns3-mcp operativo, commit fijado b8c9858
2. **Trazabilidad**: run_tracked.py genera manifest.json automático
3. **Búsqueda papers**: LDR + SearXng, Zotero, Document Library
4. **Búsqueda académica**: OpenAlex, Crossref, arXiv via research-mcp
5. **Análisis datos**: numpy, pandas, scipy, matplotlib, chromadb, darts
6. **MCP servers**: 4 servidores FastMCP operativos en HTTP (8001-8004) - **100% validados via MCP client**
7. **Modelos LLM**: qwen2.5-coder:7b (~11s fast), qwen3:8b (92s think:false), **Nemotron 3 Ultra Free (NVIDIA) ~2-5s cloud**
8. **Memoria personal**: ChromaDB personal via personal-mcp
9. **Memoria agéntica**: Mem0 + Qdrant (episódica + vectorial)
10. **PaperQA2**: Config funcional con Ollama (chain -> ollama/qwen3:8b)
11. **End-to-End flow**: Researcher (arXiv) → save_note → Writer (Markdown) → NS-3 (compila/ejecuta)
11. **LangGraph Orchestrator v2**: 5 nodos funcionando
12. **arXiv fix**: 60s timeout + 3 retries con backoff exponencial
12. **Writer Agent**: Markdown + Pandoc + Zotero, versionable en Git
13. **AutoGen Critiquer**: revisión multi-agente (Coverage, Evidence, Structure, Clarity, Actionability)
13. **Dockerfile.ns3**: NS-3.48 standalone con todo lo necesario
14. **Memory Agent**: Mem0 + Qdrant con get_context_for_task, learn_from_error, record_insight
14. **Obsidian Vault**: Documentación tesis (Markdown, Zotero, Dataview, Canvas, Git)

## Riesgos Mitigados (Día 10-13)
| Riesgo | Estado | Mitigación |
|--------|--------|-----------|
| git pull ns3-ai sin testear | BLOQUEADO | Commit fijado b8c9858, backup en ~/backups/ |
| Sin manifest.json | SOLUCIONADO | run_tracked.py automático |
| Khoj 1.5GB RAM | SOLUCIONADO | personal-mcp + ChromaDB (200MB) |
| LDR auth | SOLUCIONADO | Usuario diego funcional |
| **OOM RAM (margen 0GB)** | **MITIGADO** | **OpenHands eliminado + Swap 16GB + swappiness=10** |
| **ns3-ai sin backup** | **SOLUCIONADO** | **git archive b8c9858 → ~/backups/ns3-ai-b8c9858.zip** |
| **OpenHands docker.sock root** | **ELIMINADO** | **Container removido** |
| Python 3.12 vs 3.11 | **SOLUCIONADO** | **.venv-science recreado con uv + Py3.12** |
| AGENT=1 rompe PaperQA2 | IDENTIFICADO | unset AGENT antes de PaperQA2 |
| PaperQA2 FakeAgent limita RAG | ACEPTADO | LangGraph orquestará, PaperQA2 solo extrae evidencia |
| **arXiv timeout** | **SOLUCIONADO** | **60s timeout + 3 retries con backoff exponencial** |
| qwen3 thinking mode | **SOLUCIONADO** | **Native Ollama client + think=false** |
| ChromaDB sin keyword search | **SOLUCIONADO** | **Qdrant + fastembed (BM25 + vector)** |
| MemoryAgent get_context_for_task | **SOLUCIONADO** | **Fix en EpisodicMemoryAgent + MemoryAgent** |

## Hallazgos Críticos Día 8-10

### 1. litellm + Ollama + qwen3:8b - DIAGNÓSTICO CORREGIDO
- **NO es aiohttp timeout** — litellm usa httpx con aiohttp_transport
- **NO funciona DISABLE_AIOHTTP_TRANSPORT** — litellm lo ignora
- **PROBLEMA REAL**: qwen3:8b thinking mode + `/api/generate` endpoint
- **SOLUCIÓN**: Native Ollama client + `think=false` top-level (NO en options={})
- **Config PaperQA2 funcional**: chain `-> ollama/qwen3:8b` (sin gpt-4o fallback)

### 2. PaperQA2 tiene 4 modelos separados (TODOS default gpt-4o)
- `llm`, `summary_llm`, `agent.agent_llm`, `parsing.enrichment_llm`
- Hay que override TODOS + pasar `settings=` a `aadd()` y `aquery()`

### 3. Variables de entorno problemáticas
- `AGENT=1` rompe PaperQA2 Settings (pydantic la parsea como AgentSettings)
- `OPENAI_API_KEY` + `OPENAI_API_BASE` apuntan a OpenRouter (fallback gpt-4o)

### 4. Python environment inconsistency
- Paquetes en system-wide Python 3.12
- `.venv-science` tenía Python 3.11.16 SIN binario `python`
- **Solución**: Recrear `.venv-science` con `uv venv --python 3.12` ✅

### 5. arXiv timeout
- **SOLUCIÓN**: 60s timeout + 3 retries con backoff exponencial (10s, 20s, 40s)
- Rate limit handling (HTTP 429) con backoff exponencial

### 6. ChromaDB keyword search no soportado
- **DIAGNÓSTICO**: ChromaDB solo soporta búsqueda semántica (vector)
- **SOLUCIÓN**: Qdrant + fastembed (BM25 + búsqueda semántica híbrida)
- **Validado**: collection `jarvis_memory` dim=768 (nomic-embed-text)

### 7. MemoryAgent EpisodicMemoryAgent fix (Día 13)
- **PROBLEMA**: `get_context_for_task` estaba en la clase `MemoryEnhancedAgent` en lugar de `EpisodicMemoryAgent`
- **PROBLEMA**: `learn_from_error` y `record_insight` llamaban a `self.memory.record_error` que no existía en MemoryAgent
- **SOLUCIÓN**: Movido `get_context_for_task` a `EpisodicMemoryAgent`, agregado `record_error` y `record_insight` a `MemoryAgent`

---

## Próximos Pasos Inmediatos (Día 15+)

| Tarea | Herramienta | Prioridad | Estado |
|-------|-------------|-----------|--------|
| **Dockerfile.ns3 multi-stage runtime fix** | docker | 🔴 CRÍTICA | ✅ **COMPLETADO** (build NS-3 completo + protobuf + gym interface) |
| Validar Dockerfile.ns3 runtime gym interface | docker | 🔴 CRÍTICA | ✅ **COMPLETADO** (ns3-ai gym interface funcional) |
| **Groq Free API integration** | python | 🟡 ALTA | ⏳ Pendiente |
| **PaperQA2 con Nemotron 3 Ultra** | python | 🟡 ALTA | ✅ **COMPLETADO** (config funcional) |
| NotebookLM auto-export pipeline | python | 🟡 ALTA | ⏳ Pendiente |
| **End-to-End test NS-3 AI gym** | python | 🔴 CRÍTICA | ✅ **COMPLETADO** (ns3_ai_status, list_ns3_modules, run_ns3_simulation) |
| Optimizar NS-3 Gymnasium wrapper | python | 🟡 ALTA | ⏳ Pendiente |
| **AI CM Integration: dissemination-mcp + scientific-reviewer** | python | 🟡 ALTA | 📋 **PLANIFICADO** (14h/2d, difusión científica automatizada) |

---

*Actualizado: 2026-09-22 12:30 (Dockerfile.ns3 multi-stage build ✅ COMPLETADO, Nemotron 3 Ultra Free ✅ FUNCIONANDO, qwen2.5-coder:7b default LLM (~11s), Groq Free + Nemotron 3 Ultra + NotebookLM cloud options, all MCP servers async, thesis docs updated, NS-3 gym interface ✅ FUNCIONANDO. Próximo objetivo: Groq Free API integration + PaperQA2 con Nemotron)*

---
*Actualizado: 2026-09-17 15:30 (Dockerfile.ns3 multi-stage build EN PROGRESO - build NS-3 completo en container ~40 min transcurridos, CMakeLists.txt en examples/scratch/utils creados, build en progreso paso 10/1399, Nemotron 3 Ultra Free ✅ FUNCIONANDO, qwen2.5-coder:7b default LLM (~11s), Groq Free + Nemotron 3 Ultra + NotebookLM cloud options, all MCP servers async, thesis docs updated. Próximo: esperar build NS-3 completo ~20 min restantes)*
*Actualizado: 2026-09-22 12:40 (Dockerfile.ns3 multi-stage build ✅ COMPLETADO - build NS-3 completo + protobuf + gym interface funcional, Nemotron 3 Ultra Free ✅ FUNCIONANDO, qwen2.5-coder:7b default LLM (~11s), Groq Free + Nemotron 3 Ultra + NotebookLM cloud options, all MCP servers async, thesis docs updated, NS-3 gym interface ✅ FUNCIONANDO. Próximo objetivo: Groq Free API integration + PaperQA2 con Nemotron)*
*Actualizado: 2026-09-23 09:30 (NS-3 Python bindings FIXED ✅ - ns3ai_gym_msg_py undefined symbol _ZN3ns34Time10StaticInitEv resuelto. Causa: linker --as-needed descartaba libns3.48-ai-default.so por no tener referencias directas en binding code (usa templates/inline). Fix: CMakeLists.txt agrega -Wl,--no-as-needed antes de ns3.48-ai-default y -Wl,--as-needed después. Python 3.11 via uv usado exclusivamente para ns3-mcp. Todos los 4 MCP servers operativos (8001-8004). NS-3 gym environment import funcional. End-to-end pipeline listo.)*
*Actualizado: 2026-09-23 11:00 (TODOS LOS 4 MCP SERVERS FUNCIONANDO ✅ - research-mcp:8001 (8 tools), ns3-mcp:8002 (4 tools, ns3_ai_status OK), python-mcp:8003 (3 tools), personal-mcp:8004 (4 tools). start-jarvis.sh actualizado con LD_LIBRARY_PATH/PYTHONPATH para ns3-mcp. NS-3 gym bindings validados via MCP client. Sistema end-to-end 100% operativo.)*
*Actualizado: 2026-09-23 15:30 (PLAN INTEGRACIÓN AI CM CIENTÍFICO → JARVIS DOCUMENTADO - Módulo dissemination-mcp (puerto 8005) + subagente scientific-reviewer en LangGraph. 6 tools MCP: propose_research, review_draft, approve_draft, export_to_obsidian, list_pending_reviews, get_pipeline_status. Wrapper sobre scripts AI CM probados (propose.sh, review.sh, verify_claims.py, check_draft.py, seal_review.py). Nemotron 3 Ultra para analista/redactor/revisor. Export auto a obsidian-vault/projects/. Integración en grafo: supervisor→researcher→writer→scientific_reviewer→critiquer. Estimado 14h/2 días. PENDIENTE IMPLEMENTACIÓN.)*
*Actualizado: 2026-09-24 08:30 (SISTEMA DETENIDO Y MEMORIA LIBERADA ✅ - JARVIS MCP servers (4) detenidos via stop-jarvis.sh, LDR+SearXNG Docker detenidos, contenedores RAG limpiados (rag-ingest, rag-frontend-bake, rag-app-bake, strange_austin), Qdrant detenido. Memoria: 5.2GB usado → 10GB disponible (15GB total). Sistema listo para reinicio con ./scripts/start-jarvis.sh. Documentación completa actualizada.)*
