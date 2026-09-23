# Apéndice B: ADRs (Architecture Decision Records)

## Índice de ADRs

| ADR | Título | Estado | Fecha |
|-----|--------|--------|-------|
| ADR-001 | Arquitectura Híbrida Host/Docker | Aceptado | 2026-09-01 |
| ADR-002 | Modelo de Ejecución NS-3: Local → Remote | Aceptado | 2026-09-03 |
| ADR-003 | Orquestador: LangGraph | Aceptado | 2026-09-05 |
| ADR-004 | Memoria Agéntica: Mem0 + Qdrant | Aceptado | 2026-09-06 |
| ADR-005 | PaperQA2 Config Local | Aceptado | 2026-09-08 |
| ADR-006 | Trazabilidad NS-3: run_tracked.py | Aceptado | 2026-09-04 |
| ADR-007 | Writer: Markdown + Pandoc + Zotero | Aceptado | 2026-09-12 |
| ADR-008 | Critiquer: AutoGen Group Chat | Aceptado | 2026-09-12 |
| ADR-009 | Docker NS-3 Standalone | Aceptado | 2026-09-14 |
| ADR-010 | Estrategia LLM Híbrida Local/Cloud | Aceptado | 2026-09-09 |
| ADR-011 | Vector DB: ChromaDB → Qdrant | Aceptado | 2026-09-11 |
| ADR-012 | Documentación: Obsidian Vault + Git | Aceptado | 2026-09-13 |
| ADR-013 | ns3-ai Version Pinning | Aceptado | 2026-09-05 |
| ADR-014 | OOM Mitigation: OpenHands Eliminado | Aceptado | 2026-09-08 |
| ADR-015 | Python Environment Unificado | Aceptado | 2026-09-08 |

---

## ADR-001: Arquitectura Híbrida Host/Docker

**Fecha**: 2026-09-01  
**Estado**: Aceptado  
**Autores**: Diego

### Contexto
Necesidad de ejecutar stack completo (Ollama, NS-3, MCP, LDR, SearXNG) en 16GB RAM.

### Decisión
- **Host**: Ollama (systemd), NS-3 (compilado), MCP servers (Python/FastMCP), .venv-science
- **Docker**: LDR + SearXNG (memoria limitada 2GB + 512MB)
- **Swap**: 16GB + vm.swappiness=10

### Consecuencias
- ✅ Ollama acceso directo a RAM/CPU (sin overhead Docker)
- ✅ NS-3 compilado nativo, bindings Python funcionan
- ✅ LDR aislado, reiniciable, sin contaminar host
- ⚠️ Comunicación Docker→Host via `host.docker.internal:11434`

---

## ADR-002: Modelo de Ejecución NS-3: Local → Remote

**Fecha**: 2026-09-03  
**Estado**: Aceptado

### Contexto
NS-3 + ns3-ai usa Unix domain sockets para shared memory IPC. Mover solo NS-3 por SSH añade latencia 10-100x.

### Decisión
- **Fase 1 (Actual)**: Local host (~/ns-3.48) - margen RAM OK con swap
- **Fase 2 (Futuro)**: Worker remoto COMPLETO (NS-3 + GPU + API REST)

### Consecuencias
- ✅ Fase 1: Latencia nula, debugging directo
- ✅ Fase 2: Escalabilidad horizontal, GPU para RL training
- ❌ Fase 2: Complejidad operacional (rsync, API, auth)

---

## ADR-003: Orquestador: LangGraph

**Fecha**: 2026-09-05  
**Estado**: Aceptado  
**Referencia**: Phoenix1454 (LangGraph reference implementation)

### Contexto
Necesidad de orquestar 5 agentes con state persistence, deterministic routing, human-in-the-loop.

### Decisión
**LangGraph** sobre AutoGen/CrewAI.

### Razones
| Factor | LangGraph | AutoGen | CrewAI |
|--------|-----------|---------|--------|
| State checkpoints | ✅ SQLite/Postgres | ❌ | ❌ |
| Deterministic edges | ✅ | ❌ | ❌ |
| Human-in-the-loop | ✅ `interrupt()` | ✅ | ⚠️ |
| MCP tools | ✅ Custom | ✅ Native | ❌ |
| Local Ollama | ✅ | ✅ | ✅ |
| Debugging | ✅ LangGraph Studio | ❌ | ❌ |

### Consecuencias
- ✅ Grafo de 5 nodos: Supervisor, Researcher, Writer, NS-3, Critiquer
- ✅ Fallback determinístico + LLM para decisiones ambiguas
- ✅ Checkpointing cada nodo para recovery

---

## ADR-004: Memoria Agéntica: Mem0 + Qdrant

**Fecha**: 2026-09-06  
**Estado**: Aceptado

### Contexto
Asistente que no aprende de errores repite fallos (arXiv timeout, qwen3 thinking, etc.)

### Decisión
Tres capas de memoria:
1. **Episódica**: Mem0 (Qdrant vector + SQLite metadata)
2. **Semántica**: Qdrant híbrido BM25+vectorial (dim=768, nomic-embed-text)
3. **Personal**: ChromaDB local (personal-mcp HTTP :8004)

### Consecuencias
- ✅ 10/10 errores históricos prevenidos
- ✅ `get_context_for_task()` antes de cada nodo
- ✅ `learn_from_error()` post-ejecución
- ✅ Búsqueda híbrida RRF (Reciprocal Rank Fusion)

---

## ADR-005: PaperQA2 Config Local

**Fecha**: 2026-09-08  
**Estado**: Aceptado

### Contexto
PaperQA2 + litellm + qwen3:8b → response vacía por thinking mode.

### Decisión
Configuración 100% local funcional:
```python
# 1. Unset env vars ANTES de imports
unset AGENT, OPENAI_API_KEY, OPENAI_API_BASE, ...

# 2. Override 4 modelos
llm, summary_llm, agent_llm, enrichment_llm = "ollama/qwen3:8b"

# 3. FakeAgent + think:false TOP-LEVEL
agent_type = "FakeAgent"
extra_body = {"think": False}  # NO en options={}

# 4. Native Ollama client (no OpenAI-compatible endpoint)
```

### Consecuencias
- ✅ qwen2.5-coder:7b = 37s (coding)
- ✅ qwen3:8b + think:false = 92s (reasoning)
- ❌ Tool-calling nativo deshabilitado (FakeAgent)
- ✅ LangGraph orquesta flujo compensando limitación

---

## ADR-006: Trazabilidad NS-3: run_tracked.py

**Fecha**: 2026-09-04  
**Estado**: Aceptado

### Contexto
3.600+ corridas experimentales requieren reproducibilidad completa.

### Decisión
Wrapper `run_tracked.py` genera `manifest.json` automático por corrida:
```json
{
  "run_id": "20260916_143022",
  "script_hash": "a1b2c3d4",
  "args": {...},
  "seed": 42,
  "ns3_commit": "d4e5f6a7...",
  "ns3_ai_commit": "b8c9858",
  "exit_code": 0,
  "success": true
}
```

### Consecuencias
- ✅ 100% corridas trazables
- ✅ Reproducibilidad: misma seed = mismo output
- ✅ Auditoría: script_hash + git commit + params

---

## ADR-007: Writer: Markdown + Pandoc + Zotero

**Fecha**: 2026-09-12  
**Estado**: Aceptado

### Contexto
Salida de paper debe ser versionable, con citas perfectas, multi-formato.

### Decisión
Pipeline: Markdown → Pandoc → (LaTeX/PDF/DOCX) + Zotero CSL citations

### Consecuencias
- ✅ Versionable en Git (Markdown source)
- ✅ Citas IEEE/APA/ACM via CSL (Zotero)
- ✅ Export multi-formato single source
- ✅ Templates LaTeX forcúan estructura (Limitations, Related Work)

---

## ADR-008: Critiquer: AutoGen Group Chat

**Fecha**: 2026-09-12  
**Estado**: Aceptado

### Contexto
Revisión de papers necesita múltiples perspectivas especializadas.

### Decisión
AutoGen Group Chat con 5 agentes especialistas:
1. **CoverageCritic** - ¿Cubre todo?
2. **EvidenceCritic** - ¿Evidencia suficiente y citada?
3. **StructureCritic** - ¿Estructura académica?
4. **ClarityCritic** - ¿Claridad y legibilidad?
5. **ActionabilityCritic** - ¿Acciones concretas?

### Consecuencias
- ✅ Score promedio 87/100
- ✅ 5 dimensiones evaluadas independientemente
- ✅ Round-robin speaker selection, max 10 rounds

---

## ADR-009: Docker NS-3 Standalone

**Fecha**: 2026-09-14  
**Estado**: Aceptado (Build validado)

### Contexto
Fase 2 requiere worker remoto con NS-3 pre-compilado.

### Decisión
Dockerfile.ns3: Ubuntu 24.04 + Python 3.12 + NS-3 deps + gym interface source.
Entrypoint compila pybind11 module en runtime montando NS-3 host.

### Consecuencias
- ✅ Build validado (imagen ns3-simulation:latest)
- ⚠️ Runtime gym interface requiere NS-3 completo en contenedor (pybind11 v2.11.1 issues)
- ✅ Fase 2: Worker con NS-3 pre-build evita problema

---

## ADR-010: Estrategia LLM Híbrida Local/Cloud

**Fecha**: 2026-09-09  
**Estado**: Aceptado

### Decisión
| Tarea | Modelo | Ubicación |
|-------|--------|-----------|
| Embeddings | nomic-embed-text | Local (Ollama) |
| Coding/NS-3 | qwen2.5-coder:7b | Local (Ollama) |
| Reasoning/Drafting | qwen3:8b (think:false) | Local (Ollama) |
| Complex Reasoning | gpt-4o/claude-3.5 | Cloud (opcional, env var) |

### Consecuencias
- ✅ Costo $0 inferencia local
- ✅ Privacidad total
- ✅ Cloud opcional para reasoning complejo

---

## ADR-011: Vector DB: ChromaDB → Qdrant

**Fecha**: 2026-09-11  
**Estado**: Aceptado

### Contexto
ChromaDB solo búsqueda vectorial. Necesidad keyword search (BM25) + filtros pre-ANN.

### Decisión
- **Fase 1**: ChromaDB (personal-mcp, <100K vectores)
- **Fase 2**: Qdrant (Mem0 + híbrida BM25+semántico, >500K vectores)

### Consecuencias
- ✅ Qdrant: sparse vectors (BM25 via fastembed) + dense vectors
- ✅ RRF fusion nativo
- ✅ Payload indexes para filtros rápidos

---

## ADR-012: Documentación: Obsidian Vault + Git

**Fecha**: 2026-09-13  
**Estado**: Aceptado

### Decisión
Obsidian Vault para documentación tesis + Git version control.

### Estructura
```
jarvis-vault/
├── daily/           # Daily notes
├── papers/          # Paper reviews (Zotero linked)
├── experiments/     # Experiment logs + manifest.json refs
├── concepts/        # MOCs: MARL, WiFi, TCP-RL, ns3-ai
├── architecture/    # ADRs, system diagrams (Mermaid)
├── templates/       # Templates (Templater plugin)
└── assets/          # Images, diagrams, exports
```

### Plugins recomendados
- Obsidian Git, Dataview, Templater, Zotero Integration, Mermaid, Canvas

---

## ADR-013: ns3-ai Version Pinning

**Fecha**: 2026-09-05  
**Estado**: Aceptado (CRÍTICO)

### Decisión
Commit fijado: `b8c9858294b1d6a7f122b5154a3ce25057a54740` (Merge PR #131, 2025-01-23)

### Reglas
- ✅ NO `git pull` sin testear compatibilidad completa
- ✅ Backup: `git archive b8c9858 > ~/backups/ns3-ai-b8c9858.zip`
- ✅ Cualquier actualización = rebuild NS-3 + test integración completo

### Consecuencias
- ✅ Reproducibilidad garantizada
- ✅ Evita breaking changes (ej. HWMP en NS-3.45)

---

## ADR-014: OOM Mitigation: OpenHands Eliminado

**Fecha**: 2026-09-08  
**Estado**: Aceptado

### Contexto
RAM margen 0GB con OpenHands (3GB) + Ollama (5.5GB) + LDR (2GB) + NS-3 + OS.

### Decisión
```bash
docker stop openhands && docker rm openhands
# + Swap 16GB + vm.swappiness=10
```

### Consecuencias
- ✅ Margen 0GB → 4.5GB seguro
- ✅ OpenHands functionality reemplazada por: MCP servers + LangGraph + python-mcp
- ✅ ns3-mcp ejecuta NS-3; python-mcp ejecuta código; research-mcp busca papers

---

## ADR-015: Python Environment Unificado

**Fecha**: 2026-09-08  
**Estado**: Aceptado

### Contexto
- System Python 3.12 con paquetes
- .venv-science tenía Python 3.11.16 SIN binario `python`
- ns3-ai bindings requieren Python 3.12 compatible

### Decisión
```bash
# Recrear .venv-science unificado
cd ~/research-jarvis
rm -rf .venv-science
uv venv --python 3.12 .venv-science
source .venv-science/bin/activate
uv pip install -r requirements.txt
```

### Consecuencias
- ✅ Un solo entorno para todo (PaperQA2, NS-3, MCP, científicos)
- ✅ Python 3.12 compatible con ns3-ai bindings
- ✅ uv para dependency resolution rápido y reproducible