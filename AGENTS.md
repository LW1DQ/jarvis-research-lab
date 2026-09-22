# AGENTS.md - JARVIS Research Agents
*Actualizado 2026-09-16 - Arquitectura real operativa Día 13*

---

## ARQUITECTURA REAL: 4 MCP Servers + LangGraph Orchestrator + Mem0 + Qdrant

### MCP Servers (Herramientas HTTP/JSON-RPC 2.0)
| Server | Puerto | Ruta | Herramientas | Estado |
|--------|--------|------|-------------|--------|
| **research-mcp** | 8001 | ~/research-jarvis/mcp/research/server.py | search_papers, summarize_paper, find_gaps, search_openalex, search_crossref, search_arxiv, search_knowledge, save_research_note | ✅ OPERATIVO |
| **python-mcp** | 8003 | ~/research-jarvis/mcp/python/server.py | run_python, install_package, list_packages | ✅ OPERATIVO |
| **ns3-mcp** | 8002 | ~/research-jarvis/mcp/ns3/server.py | run_ns3_simulation, build_ns3, list_ns3_modules, ns3_ai_status | ✅ OPERATIVO |
| **personal-mcp** | 8004 | ~/research-jarvis/mcp/personal/server.py | add_note, search_notes, list_notes, delete_note | ✅ OPERATIVO |

### MCP Clients (HTTP/JSON-RPC 2.0 + SSE)
- **Protocolo**: JSON-RPC 2.0 sobre HTTP con SSE
- **Autenticación**: Session ID via header `mcp-session-id`
- **Endpoints**: `http://127.0.0.1:{8001,8002,8003,8004}/mcp`
- **Transport**: FastMCP 4.0.3 con `transport="http"`

---

## AGENTES DEL ORQUESTADOR LANGGRAPH v2

### 1. Supervisor Agent
- **Rol**: Decide el siguiente paso basado en lógica determinística + LLM fallback
- **LLM**: qwen3:8b (think:false, timeout 300s)
- **Entrada**: Estado completo del workflow
- **Salida**: `next_step` + `current_sub_task`
- **Lógica**:
  1. Sin research → researcher
  2. Research sí, draft no → writer
  3. Draft sí, critique no → critiquer
  4. Critique feedback + revision < 3 → writer
  5. Critique APPROVED o revision ≥ 3 → END

### 2. Researcher Agent
- **Rol**: Búsqueda bibliográfica multi-fuente
- **Herramientas**: research-mcp (arXiv, OpenAlex, Crossref, save_note)
- **LLM**: qwen3:8b (síntesis, think:false, timeout 300s)
- **Entrada**: `current_sub_task` o `main_task`
- **Salida**: Lista de findings (arXiv, OpenAlex, Crossref, síntesis LLM)
- **Memoria**: Guarda en personal-mcp via `add_note`

### 3. Writer Agent
- **Rol**: Redacción técnica Markdown + Pandoc + Zotero para tesis
- **Herramientas**: python-mcp (run_python → markdown/pandoc)
- **LLM**: qwen3:8b (think:false, timeout 300s)
- **Entrada**: research_findings, ns3_results, draft previo, critique_notes
- **Salida**: Draft completo (1500-2500 palabras) + Markdown versionable en Git
- **Estructura**: Executive Summary → Background → Methodology → Results → Discussion → Conclusion

### 4. NS-3 Simulation Agent
- **Rol**: Ejecución y gestión de simulaciones NS-3
- **Herramientas**: ns3-mcp (run_ns3_simulation, build_ns3, list_ns3_modules, ns3_ai_status)
- **LLM**: qwen2.5-coder:7b (coding especializado, 37s)
- **Entrada**: Parámetros de simulación / sub-tarea
- **Salida**: Resultados de simulación, logs, manifest.json (via run_tracked.py)
- **Wrapper**: ns3_gym_wrapper.py (Gymnasium interface para RL)

### 5. Critiquer Agent
- **Rol**: Revisión de calidad en 5 dimensiones
- **LLM**: qwen3:8b (reasoning crítico, think:false, timeout 300s)
- **Entrada**: Draft completo
- **Salida**: Critique + decisión (APPROVED / revisiones)
- **5 Dimensiones**:
  1. **Coverage** - Cobertura del tema
  2. **Evidence** - Respaldo con datos
  3. **Structure** - Orden lógico
  4. **Clarity** - Explicación técnica
  5. **Actionability** - Conclusiones accionables

---

## MODELOS ASIGNADOS (Validados 2026-09-16)

| Agente | Modelo Ollama | Tiempo | Razón |
|--------|---------------|--------|-------|
| Supervisor | qwen3:8b | ~2s | Decisiones rápidas |
| Researcher | qwen3:8b | 92s | Síntesis + reasoning |
| Writer | qwen3:8b | 92s | Redacción académica |
| NS-3 Agent | qwen2.5-coder:7b | 37s | Código/NS-3 debugging |
| Critiquer | qwen3:8b | 92s | Análisis crítico |

**Configuración crítica**: `think=false` para qwen3:8b (evita thinking mode), `timeout: 300s`

---

## COMUNICACIÓN ENTRE AGENTES

```
Supervisor (qwen3:8b)
    │
    ├──→ Researcher → research-mcp (arXiv/OpenAlex/Crossref)
    │                └──→ personal-mcp (add_note)
    │
    ├──→ Writer → python-mcp → Markdown/Pandoc/Zotero
    │
    ├──→ NS-3 Sim → ns3-mcp → manifest.json
    │
    └──→ Critiquer → Feedback → Writer (loop máx 3)
```

**Memoria compartida**: Mem0 + Qdrant (`jarvis_memory`, dim=768) como memoria agéntica persistente
**Memoria personal**: ChromaDB personal via personal-mcp (`~/research-jarvis/chroma/personal/`)

---

## MEMORIA AGÉNTICA (Mem0 + Qdrant)

### Configuración
- **Vector store**: Qdrant en Docker :6333
- **Collection**: `jarvis_memory`
- **Dimensión**: 768 (nomic-embed-text)
- **LLM**: Ollama qwen3:8b (think:false)
- **Embedder**: Ollama nomic-embed-text
- **Híbrida**: BM25 (fastembed) + búsqueda semántica vectorial

### memory_agent.py
- `create_memory_agent()` - Memoria agéntica Mem0 + Qdrant
- `create_episodic_agent(memory)` - Memoria episódica
- `add_memory(text, tags, importance)`
- `search_memories(query, limit)`
- `record_interaction(user_msg, agent_msg, outcome, tags)`
- `get_context_for_task(task)`
- `learn_from_error(error, context, resolution)`
- `record_insight(insight, context)`

### Fixes Aplicados Día 13
- **Fix 1**: `get_context_for_task` movido a `EpisodicMemoryAgent` (estaba en `MemoryEnhancedAgent`)
- **Fix 2**: Agregado `record_error` y `record_insight` a `MemoryAgent` (llamadas desde EpisodicMemoryAgent)
- **Fix 3**: `EpisodicMemoryAgent.learn_from_error` ahora llama a `self.record_error` (no `self.memory.record_error`)
- **Fix 4**: `EpisodicMemoryAgent.record_insight` ahora llama a `self.record_insight` (no `self.memory.record_insight`)

---

## REGLAS DE OPERACIÓN

1. **No entrenar modelos localmente** — solo inferencia
2. **Un agente a la vez** — RAM limitada (16GB, margen ~4GB)
3. **Resultados a disco** — `/home/diego/research-jarvis/projects/`
4. **Citas con PyZotero** — sincronizar con Zotero local
5. **Documentos en Markdown** — Pandoc para DOCX/PDF, versionable en Git
6. **Trazabilidad NS-3** — run_tracked.py genera manifest.json por corrida
7. **Commit ns3-ai fijado** — NO hacer git pull sin testear (b8c9858)
8. **Monitor RAM** — threshold 90%, kill no-críticos (LDR, OpenHands)
9. **unset AGENT** — antes de usar PaperQA2 (rompe pydantic-settings)
10. **Memoria en Qdrant** — Mem0 usa Qdrant para memoria agéntica, ChromaDB solo personal-mcp
11. **Documentación en Obsidian** — Vault en `obsidian-vault/`, commit a Git, sync Zotero

---

## WORKSPACE DELIMITADO

Todos los agentes operan dentro de:
```
~/research-jarvis/
├── papers/              # Bibliografía (NO modificar originales)
├── projects/            # Código y resultados
├── thesis/              # Borradores de tesis
├── datasets/            # Datos experimentales
├── experiments/         # Resultados de simulaciones
├── notebooks/           # Jupyter notebooks
├── mcp/                 # Servidores MCP
├── agents/              # Configuración de agentes (prompts, configs)
├── logs/                # Logs de ejecución + observabilidad JSONL
├── backups/             # Backups automatizados
├── chroma/              # ChromaDB collections (personal-mcp)
├── qdrant_data/         # Qdrant storage (Mem0)
└── obsidian-vault/      # Documentación tesis (Markdown, Zotero, Dataview)
```

Nunca modificar directamente:
- `/home/diego/` (HOME del usuario)
- `~/ns-3.48/` (compilación NS-3)
- `~/.ollama/` (modelos)

---

## CONFIGURACIÓN PAPERQA2 FUNCIONAL

Ver `~/research-jarvis/config_paperqa.py`:
- Override TODOS los 4 modelos: llm, summary_llm, agent_llm, enrichment_llm
- `extra_body={'think': False}` para qwen3:8b
- `timeout: 300` para cold-start CPU
- `multimodal=0` (deshabilitar enriquecimiento imágenes)
- `agent_type="FakeAgent"` (evitar tool-calling agent quebrado)
- `unset AGENT` + `unset OPENAI_*` antes de ejecutar

---

## PRÓXIMOS PASOS ARQUITECTÓNICOS (Día 14+)

| Paso | Acción | Esfuerzo |
|------|--------|----------|
| 1 | Validar Dockerfile.ns3 standalone | 2-4h |
| 2 | Preparar documentación final para tesis (Obsidian → Pandoc) | 8-12h |
| 3 | Optimizar NS-3 Gymnasium wrapper | 4-8h |

---
*Actualizado: 2026-09-16 10:30 - Día 13 COMPLETADO - Experimento End-to-End + Obsidian Vault + Docker NS-3 build OK - SISTEMA LISTO PARA TESIS*