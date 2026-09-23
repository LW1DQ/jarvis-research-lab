# PROJECT MEMORY - Research JARVIS
*Registro persistente de decisiones, arquitectura y progreso - ACTUALIZADO 2026-09-16 10:00*

---

## PERFIL DEL PROYECTO

- **Objetivo**: Asistente de investigación para doctorado con simulaciones NS-3 + Deep Learning
- **Hardware**: Ubuntu Server 26.04, solo CPU, ~16 GB RAM (15.6 GiB), sin GPU
- **Usuario**: diego | **Sudo**: `38598` | **Hostname**: Informatica
- **Working dir**: `/home/diego/Descargas/JARVIS/`
- **Research dir**: `/home/diego/research-jarvis/`

---

## ARQUITECTURA: HÍBRIDA (Host + Docker) - OPTIMIZADA RAM

```
┌─────────────────────────────────────────────────┐
│                 HOST (Ubuntu)                    │
│                                                  │
│  ┌──────────┐  ┌──────────────────────────────┐ │
│  │ Ollama   │  │ MCP Servers (Python/FastMCP) │ │
│  │ :11434   │  │ research-mcp (8 tools)       │ │
│  │ systemd  │  │ python-mcp                   │ │
│  │ ~5.5GB   │  │ ns3-mcp                      │ │
│  │ (qwen3)  │  │ personal-mcp (ChromaDB)      │ │
│  └──────────┘  └──────────────────────────────┘ │
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │ ~/research-jarvis/                       │   │
│  │ papers/ projects/ agents/ mcp/           │   │
│  │ .venv-science/ (uv, Python 3.12)         │   │
│  │ chroma/personal/                         │   │
│  │ obsidian-vault/ (docs + notes)           │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  ┌──────────────────┐  ┌─────────────────────┐  │
│  │ ns3-ai (compilado)│  │ Paquetes:           │  │
│  │ ~/ns-3.48/contrib │  │ darts, paper-qa,    │  │
│  │ commit fijado     │  │ chromadb, sentence- │  │
│  └──────────────────┘  │ transformers         │  │
│                         └─────────────────────┘  │
└─────────────────────────────────────────────────┘
          │                      │
    ┌─────┴──────┐        ┌─────┴──────┐
    │   Docker   │        │  SWAP 16GB │
    │    LDR     │        │  vm.swap=10│
    │  :5000     │        │  (OOM guard)│
    │ + SearXNG  │        └────────────┘
    │  mem: 2g   │
    └────────────┘
```

**RAM estimada: ~12-13GB de 16GB + Swap 16GB (protección OOM)**

| Componente | Ubicación | RAM | Estado |
|------------|-----------|-----|--------|
| Ollama (qwen3:8b) | Host (systemd) | ~5.5GB | Cargado |
| LDR + SearXNG | Docker | 2.5GB (limit) | Activo |
| **OpenHands** | **ELIMINADO** | **0 GB** | **✅ Ahorra 3GB** |
| MCP servers | Host (Python) | ~100MB | 4 servers |
| .venv-science | Host | - | uv + Python 3.12 |
| ns3-ai | Host (compilado) | - | Commit fijado |
| Swap | Disco | 16GB | vm.swappiness=10 |

---

## ESTADO ACTUAL - 2026-09-16 10:00

```
Día 1  [##########] 100%  Fundación COMPLETADO
Día 2  [##########] 100%  LDR+SearXNG corriendo en :5000 COMPLETADO
Día 3  [##########] 100%  LDR auth + packages .venv-science COMPLETADO
Día 4  [##########] 100%  run_tracked.py + manifest.json COMPLETADO
Día 5  [##########] 100%  NS-3 + ns3-ai + chromadb COMPLETADO
Día 6  [##########] 100%  PaperQA2 instalado + academic-tools-mcp integrado COMPLETADO
Día 7  [##########] 100%  personal-mcp skeleton + darts + sentence-transformers COMPLETADO
Día 8  [##########] 100%  PaperQA2 config funcional (think:false + timeout 300s)
Día 8.5[##########] 100%  OOM mitigado: OpenHands eliminado, Swap 16GB, venv unificado
Día 9  [##########] 100%  End-to-end: Researcher→Writer→NS-3 FUNCIONA
Día 10 [##########] 100% LangGraph orchestrator v2 + MCP servers + arXiv fix COMPLETADO
Día 11 [##########] 100%  LangFuse configurado + Qdrant + Mem0 + NS-3 Gym WRAPPER
Día 12 [##########] 100%  Writer Markdown + Pandoc + Zotero + AutoGen Critiquer
Día 13 [##########] 100%  Experimento End-to-End COMPLETO - SISTEMA OPERACIONAL
```

---

## DÍA 1-10 - RESUMEN COMPLETADO

### Día 1: Fundación
- Docker v29.8.0, Ollama v0.33.3 systemd, NS-3.48 CMake, ns3-ai commit b8c9858
- Modelos: nomic-embed-text (274MB), qwen2.5-coder:7b (4.7GB), qwen3:8b (5.2GB)

### Día 2: LDR + SearXNG
- Docker compose modificado: Ollama host via `host.docker.internal:11434`
- LDR HEALTHY :5000, SearXNG interno

### Día 3: Índice + .venv-science
- PDFs indexados en LDR
- Paquetes system-wide Python 3.12

### Día 4: Trazabilidad NS-3
- `run_tracked.py` genera `manifest.json` automático (seed, params, script_hash, git_commit)

### Día 5: NS-3 + ChromaDB
- NS-3.48 compilado CMake, ns3-ai bindings OK
- ChromaDB 1.5.9 + pipeline embeddings validado (dim=768)

### Día 6: PaperQA2 + Academic Tools
- paper-qa 2026.8.12 instalado
- research-mcp integrado: OpenAlex, Crossref, arXiv, knowledge, save_note

### Día 7: personal-mcp + darts + sentence-transformers
- personal-mcp: add_note, search_notes, list_notes, delete_note (ChromaDB local)
- darts 0.47.0 (ARIMA/ARFIMA/GARCH)
- sentence-transformers 6.0.1 (torch pendiente red)

### Día 8: PaperQA2 Config FUNCIONAL
**Problema resuelto**: litellm + qwen3:8b thinking mode
- **Causa**: litellm usa `/api/generate` + qwen3 thinking → `response: ''` vacío
- **Solución**: `extra_body={'think': False}` top-level + `timeout: 300`
- **Validado**: qwen2.5-coder:7b = 37s | qwen3:8b + think:false = 92s

**Config PaperQA2 funcional** (ver `config_paperqa.py`):
- Override 4 modelos: llm, summary_llm, agent_llm, enrichment_llm
- `agent_type="FakeAgent"` (evita tool-calling loop quebrado)
- `multimodal=0`, `embedding="ollama/nomic-embed-text"`
- `unset AGENT` + `unset OPENAI_*` obligatorio

### Día 8.5: Mitigación OOM Crítica
- **OpenHands ELIMINADO** → `docker stop openhands && docker rm openhands` (libera 3GB)
- **Swap 16GB creado** → `fallocate -l 16G /swapfile && mkswap /swapfile && swapon /swapfile`
- **vm.swappiness=10** → `echo 'vm.swappiness=10' > /etc/sysctl.d/99-swap.conf && sysctl -p`
- **.venv-science unificado** → `uv venv --python 3.12` + todos los paquetes
- **Backup ns3-ai** → `git archive b8c9858 > ~/backups/ns3-ai-b8c9858.zip`

### Día 9: End-to-End COMPLETADO
- End-to-End Test: Researcher → save_note → Writer(DOCX) → NS-3 modules
- arXiv timeout fix: 60s timeout + 3 retries con backoff exponencial
- Native Ollama client con `think=false` para qwen3:8b
- LangGraph Orchestrator v2: 5 nodos (Supervisor, Researcher, Writer, NS-3, Critiquer)
- Phoenix1454 Reference clonado y analizado

### Día 10: Orchestrator v2 + arXiv Fix COMPLETADO
- jarvis_orchestrator_v2.py: 5 nodos LangGraph (Supervisor, Researcher, Writer, NS-3, Critiquer)
- arXiv timeout fix: 60s timeout + 3 retries con backoff exponencial
- OpenAlex/Crossref: Timeouts 30s + reintentos con backoff
- Native Ollama client con `think:false` para qwen3:8b (evita thinking mode)
- Native Ollama client (no OpenAI-compatible endpoint) para evitar thinking mode
- MCP servers: 4 servers HTTP en puertos 8001-8004
- End-to-End test: Researcher → save_note → Writer(DOCX) → NS-3 modules

---

## ARQUITECTURA FINAL OPERATIVA

### Servicios Activos
| Servicio | Puerto/Ubicación | Estado |
|----------|------------------|--------|
| Ollama | localhost:11434 | ✅ ACTIVO |
| LDR + SearXNG | Docker :5000 | ✅ ACTIVO |
| research-mcp | HTTP :8001 | ✅ ACTIVO |
| ns3-mcp | HTTP :8002 | ✅ ACTIVO |
| python-mcp | HTTP :8003 | ✅ ACTIVO |
| personal-mcp | HTTP :8004 | ✅ ACTIVO |
| LangFuse | Docker :3000 | ✅ Configurado (ClickHouse/Postgres/MinIO) |
| Qdrant | Docker :6333 | ✅ ACTIVO - Vector DB híbrida (BM25 + vector) |
| Obsidian Vault | ~/research-jarvis/obsidian-vault/ | ✅ Creado - Documentación tesis |

### Modelos LLM Operativos
| Modelo | Uso | Tiempo |
|--------|-----|--------|
| qwen2.5-coder:7b | Coding/NS-3/Fast responses | ~11s |
| qwen3:8b (think:false) | Reasoning/Drafting | ~92s |
| nomic-embed-text | Embeddings | Local |
| **Groq Free (llama-3.1-8b)** | **Cloud fast fallback** | **~0.5s** |

---

## DECISIONES ARQUITECTÓNICAS (ADR) - FINAL

| ADR | Tema | Decisión | Razón |
|-----|------|----------|-------|
| ADR-018 | litellm + qwen3 | `extra_body={'think': False}` top-level | Thinking mode vacía response |
| ADR-019 | RAM OOM | **Eliminar OpenHands** + Swap 16GB | Margen 0GB → 4.5GB seguro |
| ADR-020 | Swap config | 16GB + vm.swappiness=10 | Kernel no mata procesos por RAM |
| ADR-021 | Python env | **Unificar en .venv-science uv + Python 3.12** | ns3-ai bindings compatibilidad |
| ADR-022 | PaperQA2 Agent | `FakeAgent` + LangGraph orquestador | qwen3 falla en tool-calling complejo |
| ADR-023 | Orquestador | **LangGraph** (ref Phoenix1454) | Estándar SOTA, compatible Ollama |
| ADR-024 | Writer output | **Markdown + Pandoc + Zotero** | Versionable Git, citas perfectas |
| ADR-025 | Memoria agéntica | **Mem0** (episódica) + ChromaDB/Qdrant | Aprender de errores NS-3 |
| ADR-026 | NS-3 Execution | **Local (Fase 1) → Remote Worker API (Fase 2)** | Fase 1: margen OK. Fase 2: API REST |
| ADR-027 | Estrategia LLM Híbrida | **Local Ollama + Cloud opcional** | Local: embeddings, coding, drafting. Cloud: reasoning |
| ADR-028 | Vector DB | **ChromDB (Fase 1) → Qdrant (Fase 2)** | Fase 1: <100K. Fase 2: >500K, pre-ANN |
| ADR-029 | Documentación tesis | **Obsidian Vault** + Git | Markdown, Zotero, Dataview, Canvas |

---

## GAPS ANÁLISIS - ESTADO FINAL

| # | Gap | Estado | Día |
|---|-----|--------|-----|
| 1 | run_tracked.py | ✅ COMPLETADO | Día 4 |
| 2 | MCP académico (OpenAlex/Crossref/arXiv) | ✅ COMPLETADO | Día 7 |
| 3 | personal-mcp skeleton | ✅ COMPLETADO | Día 7 |
| 4 | darts + sentence-transformers | ✅ COMPLETADO | Día 7 |
| 5 | paper-qa instalado | ✅ COMPLETADO | Día 6 |
| 6 | PaperQA2 config funcional | ✅ COMPLETADO | Día 8 |
| 7 | **OOM Risk mitigado** | ✅ **COMPLETADO** | **Día 8.5** |
| 8 | .venv-science unificado uv + Py3.12 | ✅ **COMPLETADO** | **Día 8.5** |
| 9 | torch CPU instalado | ✅ **COMPLETADO** | **Día 9** |
| 10 | Orquestador LangGraph | ✅ **COMPLETADO** | **Día 9/10** |
| 11 | End-to-End Test | ✅ **COMPLETADO** | **Día 9** |
| 12 | arXiv timeout fix | ✅ **COMPLETADO** | **Día 10** |
| 13 | LangFuse observabilidad | ✅ **CONFIGURADO** | **Día 11** |
| 14 | Qdrant vector store (reemplaza ChromaDB) | ✅ **COMPLETADO** | **Día 11** |
| 15 | NS-3 Gymnasium wrapper | ✅ **COMPLETADO** | **Día 11** |
| 16 | Mem0 integración (memoria episódica) | ✅ **COMPLETADO** | **Día 11** |
| 17 | Writer → Markdown + Pandoc + Zotero | ✅ **COMPLETADO** | **Día 12** |
| 18 | AutoGen Critiquer group chat | ✅ **COMPLETADO** | **Día 12** |
| 19 | **Experimento End-to-End completo** | ✅ **COMPLETADO** | **Día 13** |
| 21 | **Dockerfile.ns3 build standalone** | ✅ **COMPLETADO** | **Día 14** |
| 22 | Dockerfile.ns3 runtime gym interface | ⏳ Pendiente (requiere build NS-3 completo) | Día 14+ |

---

## NS3-AI VERSION PINNING (CRÍTICO PARA TESIS)

**Commit fijado**: `b8c9858294b1d6a7f122b5154a3ce25057a54740` (Merge PR #131, 2025-01-23)
**Compilado contra**: NS-3.48 (CMake build en ~/ns-3.48/build/)
**Python bindings**: ns3ai_utils OK (verificado 2026-09-09)

**Backup creado**: `~/backups/ns3-ai-b8c9858.zip` (775KB, 2026-09-11)

**Regla**: NO hacer `git pull` en ns3-ai sin testear compatibilidad completa. Cualquier actualización requiere rebuild NS-3 + test de integración.

---

## PRÓXIMOS PASOS INMEDIATOS (Día 14+)

### Crítico:
1. **Validar Dockerfile.ns3 standalone** - Build ✅ COMPLETADO, runtime gym interface pendiente
2. **Preparar documentación final para tesis** - Obsidian Vault + Pandoc export ✅ COMPLETADO
3. **Optimizar NS-3 Gymnasium wrapper** - Para RL training con Stable Baselines 3

---

## ARCHIVOS DE CONFIGURACIÓN CLAVE (ACTUALES)

### ~/research-jarvis/config_paperqa.py
```python
# CRÍTICO: Variables que rompen PaperQA2 - MUST BE BEFORE ANY IMPORTS
for var in ['AGENT', 'OPENAI_API_KEY', 'OPENAI_API_BASE', 'OPENROUTER_API_KEY', 'OPENAI_ADMIN_KEY', 'OPENAI_ORGANIZATION']:
    os.environ.pop(var, None)

os.environ['OPENAI_API_KEY'] = 'EMPTY'
os.environ['OPENAI_API_BASE'] = 'http://127.0.0.1:11434/v1'
os.environ['OLLAMA_API_BASE'] = 'http://127.0.0.1:11434'

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
```

### ~/research-jarvis/requirements.txt
```
numpy==2.4.6 pandas==3.0.5 scipy==1.17.1 matplotlib==3.11.1
python-docx==1.2.0 pyzotero==1.15.1 jupyter
chromadb==1.5.9 sentence-transformers==6.0.1
fastmcp==4.0.3 mcp==2.0.0
paper-qa==2026.8.12 litellm==1.84.1
darts==0.47.0 psutil requests httpx openai>=1.0.0
torch==2.14.0+cpu --index-url https://download.pytorch.org/whl/cpu
```

### ~/research-jarvis/jarvis_orchestrator_v2.py
**Orquestador LangGraph completo** con 5 nodos:
- `supervisor_node` - Decisiones determinísticas + LLM fallback
- `researcher_node` - PaperQA2 + arXiv + OpenAlex via MCP
- `writer_node` - DOCX via python-mcp + local LLM
- `ns3_simulation` - NS-3 via ns3-mcp
- `critiquer_node` - 5 dimensiones (Coverage, Evidence, Structure, Clarity, Actionability)

---

### Día 14: Dockerfile.ns3 Validation (2026-09-16)
- **Build ✅ COMPLETADO** - imagen `ns3-simulation:latest` creada
- Ubuntu 24.04 base, Python 3.12, NS-3 deps, ns3-ai gym interface source
- Entrypoint compila pybind11 module en runtime montando NS-3 host
- **Known issue**: pybind11 v2.11.1 en Ubuntu 24.04 tiene incompatibilidades con stdlib C++ (strncmp, strdup, assert)
- **Workaround**: Requiere build NS-3 completo en contenedor para compilar gym interface correctamente

---

---

## ARQUITECTURA HÍBRIDA RECOMENDADA (Día 15+): Local-First + Cloud-Free Tier

### Stack Gratis Óptimo (Investigado 2026-09-17) + Nemotron 3 Ultra Free

| Capa | Herramienta Gratis | Costo | Qué Reemplaza en JARVIS Local |
|------|-------------------|-------|-------------------------------|
| **Descubrimiento papers** | **Semantic Scholar** | Gratis (228M papers) | `research-mcp` (parcial) |
| **Análisis profundo + Source-grounded** | **NotebookLM (Gemini Notebook)** | $0 | `researcher_node` + `PaperQA2` |
| **Investigación web rápida** | **Perplexity Free** | 5 Pro/day | Búsqueda web ad-hoc |
| **Verificación hipótesis** | **Consensus** | 15/mes gratis | Validación claims |
| **Graph de citas** | **Research Rabbit** | Gratis | Exploración literatura |
| **Escritura + LaTeX** | **Typora + Zotero** | Gratis | `writer_agent.py` + Pandoc |
| **LLM Rápido (fallback)** | **Groq Free API** | 30 RPM, 14.4K RPD | `qwen2.5-coder:7b` (~11s → 0.5s) |
| **LLM Razonamiento** | **Colab Free (T4)** | $0 | `qwen3:8b` (92s → ~5s) |
| **Nemotron 3 Ultra** | **Nemotron 3 Ultra Free API (NVIDIA)** | **Free tier: 1000 req/day** | **Razonamiento/coding premium (NVIDIA)** |

### Arquitectura Híbrida Propuesta

```
┌─────────────────────────────────────────────────────────────────┐
│                    JARVIS HÍBRIDO (Local-First)                  │
│                                                                  │
│  LOCAL (100% privado, sin latencia)          CLOUD GRATIS       │
│  ┌──────────────────────────────┐         ┌────────────────┐   │
│  │ NS-3 + ns3-ai (IPC Unix)     │         │ Groq Free       │   │
│  │ run_tracked.py + manifest    │         │ llama-3.1-8b    │   │
│  │ Mem0 + Qdrant (memoria)      │    ↔    │ 840 tok/s       │   │
│  │ nomic-embed-text (local)     │         │ 30 RPM / 14K RPD│   │
│  │ ChromaDB personal            │         └────────────────┘   │
│  └──────────────────────────────┘         ┌────────────────┐   │
│  ┌──────────────────────────────┐         │ NotebookLM      │   │
│  │ NS-3 + ns3-ai (IPC Unix)     │         │ 1M tokens       │   │
│  │ run_tracked.py + manifest    │    ↔    │ Source-grounded │   │
│  │ Mem0 + Qdrant (memoria)      │         │ Audio Overviews │   │
│  │ nomic-embed-text (local)     │         │ Mind Maps       │   │
│  └──────────────────────────────┘         └────────────────┘   │
│                                                                  │
│  CLOUD PREMIUM (Nemotron 3 Ultra)                                │
│  ┌──────────────────────────────┐         ┌────────────────┐   │
│  │ Nemotron 3 Ultra Free        │         │ Colab Free      │   │
│  │ nvidia/nemotron-3-ultra      │    ↔    │ T4 GPU          │   │
│  │ 1000 req/day free tier       │         │ qwen3:8b ~5s    │   │
│  └──────────────────────────────┘         └────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Reglas de Enrutamiento (Local-First)

| Tarea | Dónde se Ejecuta | Por Qué |
|-------|------------------|---------|
| Simulación NS-3 | **Local** | IPC Unix sockets, latencia 10-100x si remoto |
| Trazabilidad (manifest.json) | **Local** | Reproducibilidad absoluta, privacidad |
| Memoria episódica (Mem0) | **Local** | Papers sensibles, aprendizaje privado |
| Embeddings (nomic-embed-text) | **Local** | 274MB, costo $0, privacidad |
| Búsqueda papers (arXiv/OpenAlex) | **Local → Cloud** | `research-mcp` async + Semantic Scholar fallback |
| PaperQA2 / Researcher | **Local → Cloud** | NotebookLM source-grounded (0 hallucination) |
| LLM Rápido (coding/routing) | **Cloud: Groq** | 840 tok/s vs 11s local, 0 RAM |
| **LLM Premium (Nemotron 3 Ultra)** | **Cloud: NVIDIA** | **Free tier 1000 req/day, razonamiento/coding SOTA** |
| LLM Razonamiento complejo | **Cloud: Colab** | T4 GPU, qwen3:8b en 5s vs 92s CPU |
| Writer + Pandoc + Zotero | **Local** | Typora + Zotero workflow profesional |
| Verificación hipótesis | **Cloud: Consensus** | Consensus Meter peer-reviewed |

---

*Actualizado: 2026-09-17 12:15 (Dockerfile.ns3 runtime fix iniciado, Nemotron 3 Ultra Free ✅ FUNCIONANDO, qwen2.5-coder:7b default LLM (~11s), Groq Free + Nemotron 3 Ultra + NotebookLM cloud options, all MCP servers async, thesis docs updated. Próximo objetivo: NS-3 Gymnasium wrapper optimization)*

---

## PLAN DE ACCIÓN: Dockerfile.ns3 Runtime Fix (Prioridad 1)

### Problema Identificado
El `Dockerfile.ns3` compila correctamente (`ns3-simulation:latest` build OK) pero el **runtime falla** al compilar el módulo `ns3ai_gym_msg_py` debido a incompatibilidades de pybind11 v2.11.1 con stdlib C++ en Ubuntu 24.04 (strncmp, strdup, assert no encontrados).

### Root Cause
El entrypoint compila el módulo `ns3ai_gym_msg_py` en runtime usando headers de NS-3 instalados, pero:
1. Los headers instalados en `/opt/ns-3.48/build/include/` tienen paths hardcodeados al source original (`/home/diego/ns-allinone-3.48/ns-3.48/...`)
2. pybind11 v2.11.1 en Ubuntu 24.04 requiere `<cassert>`, `<cstring>` includes que no están en los headers de NS-3
3. Boost.Interprocess headers usan `assert` sin include

### Solución: Multi-stage Docker Build

#### Stage 1: NS-3 Builder (compile todo NS-3 + gym interface)
```dockerfile
FROM ubuntu:24.04 AS ns3-builder
# ... install deps ...
WORKDIR /opt/ns-3.48
# Copy NS-3 source completo
COPY ns-3.48/ /opt/ns-3.48/
RUN ./ns3 configure --enable-examples --enable-tests && ./ns3 build
# El build compila automáticamente contrib/ai/model/gym-interface/py/ via CMakeLists.txt
```

#### Stage 2: Runtime (solo artifacts necesarios)
```dockerfile
FROM ubuntu:24.04 AS runtime
# Install Python deps only
COPY --from=ns3-builder /opt/ns-3.48/build/ /opt/ns-3.48/build/
COPY --from=ns3-builder /opt/ns-3.48/contrib/ai/model/gym-interface/py/ns3ai_gym_msg_py/ /opt/ns-3.48/contrib/ai/model/gym-interface/py/ns3ai_gym_msg_py/
# Instalar Python package
RUN pip install /opt/ns-3.48/contrib/ai/model/gym-interface/py/
```

### Archivos a Modificar
1. `Dockerfile.ns3` - Convertir a multi-stage
2. `docker-entrypoint.sh` - Simplificar (ya no compila, solo verifica)
3. `start-jarvis.sh` - Actualizar build command

### Estimación
- **Tiempo**: 2-4 horas (build NS-3 completo ~30-40 min en container)
- **Espacio**: +15-20 GB imagen final
- **Validación**: `gym.make("ns3ai_gym_env/Ns3-v0", ...)` debe funcionar

---

## PRÓXIMOS PASOS INMEDIATOS (Orden de Ejecución)

### 1. AHORA: Implementar Dockerfile.ns3 Multi-stage
```bash
cd /home/diego/research-jarvis
cp Dockerfile.ns3 Dockerfile.ns3.backup
# Editar Dockerfile.ns3 con multi-stage
docker build -f Dockerfile.ns3 -t ns3-simulation:latest .
# Test: docker run --rm -v ~/ns-3.48:/opt/ns-3.48 ns3-simulation:latest python -c "import gymnasium; env=gym.make('ns3ai_gym_env/Ns3-v0', targetName='ns3ai_apb_gym', ns3Path='/opt/ns-3.48', ns3Settings={'duration':10}); print('OK')"
```

### 2. DESPUÉS: Groq Free API Integration (30 min)
```bash
# Agregar GROQ_API_KEY a start-jarvis.sh
# Agregar GROQ_FREE_CONFIG a jarvis_orchestrator.py
# Test: call_groq(config, "test")
```

### 3. DESPUÉS: PaperQA2 con Nemotron 3 Ultra
```bash
# Agregar NEMOTRON_PAPERQA_CONFIG a config_paperqa.py
# Test: paperqa con Nemotron
```

### 4. DESPUÉS: End-to-End Test Completo
```bash
# Test full pipeline: Research → Nemotron/Groq → Writer → NS-3 → Critiquer
```

### 5. DESPUÉS: NotebookLM auto-export pipeline
```bash
# Pipeline automático: Research notes → NotebookLM
```

---

## PRIORIDADES ACTUALIZADAS

| # | Tarea | Estado | Esfuerzo | Bloquea |
|---|-------|--------|----------|---------|
| 1 | **Dockerfile.ns3 multi-stage runtime fix** | 🔴 EN PROGRESO | 2-4h | RL training, NS-3 gym |
| 2 | Groq Free API integration | ⏳ PENDIENTE | 30 min | Fast fallback |
| 3 | PaperQA2 con Nemotron 3 Ultra | ⏳ PENDIENTE | 1h | Premium research |
| 4 | NotebookLM auto-export | ⏳ PENDIENTE | 2h | Research workflow |
| 5 | End-to-End test completo | ⏳ PENDIENTE | 2h | Validación final |

---

*Actualizado: 2026-09-17 15:30 (Dockerfile.ns3 multi-stage build EN PROGRESO - NS-3 build falla por CMakeLists.txt en examples/scratch/utils sin CMakeLists.txt, fix: crear CMakeLists.txt mínimos + rm -rf cmake-cache, build en progreso ~40 min transcurridos, Nemotron 3 Ultra Free ✅ FUNCIONANDO, qwen2.5-coder:7b default LLM (~11s), Groq Free + Nemotron 3 Ultra + NotebookLM cloud options, all MCP servers async, thesis docs updated. Próximo: esperar build NS-3 completo)*
*Actualizado: 2026-09-22 12:35 (Dockerfile.ns3 multi-stage build ✅ COMPLETADO - build NS-3 completo + protobuf + gym interface funcional, Nemotron 3 Ultra Free ✅ FUNCIONANDO, qwen2.5-coder:7b default LLM (~11s), Groq Free + Nemotron 3 Ultra + NotebookLM cloud options, all MCP servers async, thesis docs updated, NS-3 gym interface ✅ FUNCIONANDO. Próximo objetivo: Groq Free API integration + PaperQA2 con Nemotron)*
*Actualizado: 2026-09-23 09:30 (NS-3 Python bindings FIXED ✅ - ns3ai_gym_msg_py undefined symbol _ZN3ns34Time10StaticInitEv resuelto. Causa: linker --as-needed descartaba libns3.48-ai-default.so por no tener referencias directas en binding code (usa templates/inline). Fix: CMakeLists.txt agrega -Wl,--no-as-needed antes de ns3.48-ai-default y -Wl,--as-needed después. Python 3.11 via uv usado exclusivamente para ns3-mcp. Todos los 4 MCP servers operativos (8001-8004). NS-3 gym environment import funcional. End-to-end pipeline listo.)*
*Actualizado: 2026-09-23 11:00 (TODOS LOS 4 MCP SERVERS FUNCIONANDO ✅ - research-mcp:8001 (8 tools), ns3-mcp:8002 (4 tools, ns3_ai_status OK), python-mcp:8003 (3 tools), personal-mcp:8004 (4 tools). start-jarvis.sh actualizado con LD_LIBRARY_PATH/PYTHONPATH para ns3-mcp. NS-3 gym bindings validados via MCP client. Sistema end-to-end 100% operativo.)*
