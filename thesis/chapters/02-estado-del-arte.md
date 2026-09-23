# Capítulo 2: Estado del Arte

## 2.1 Investigación Automatizada con LLMs

### 2.1.1 Sistemas de Investigación Profunda
- **GPT Researcher** (Assaf Elovic, 2023): Agente autónomo para investigación web con citas
- **STORM** (Stanford, 2024): Síntesis de artículos tipo Wikipedia con referencias
- **PaperQA2** (FutureHouse, 2024): RAG agentic para papers científicos con evidencia y citas
- **OpenDeepResearcher** (2024): Pipeline modular de investigación profunda

### 2.1.2 Limitaciones de Sistemas Existentes
| Sistema | Fortaleza | Limitación para Tesis NS-3 |
|---------|-----------|---------------------------|
| GPT Researcher | Web research + citas | No integración NS-3, no memoria persistente |
| STORM | Artículos largos | Requiere API cloud, no local-first |
| PaperQA2 | Papers + evidencia + citas | Solo RAG, no orchestration de experimentos |
| OpenHands | SDK + MCP + workspace | 3GB RAM, orientado a coding no investigación |

## 2.2 Simulación de Redes con NS-3

### 2.2.1 NS-3.48 (2024)
- **Build system**: CMake (reemplaza waf)
- **Python bindings**: `ns3` module via pybind11
- **Módulos clave**: wifi, lte, nr, tcp, mpi, ai (contrib)

### 2.2.2 ns3-ai (HUST, 2020-2023)
- **Interfaz**: Shared memory + semáforos (Unix sockets IPC)
- **Gym interface**: `ns3ai_gym_env` compatible Gymnasium
- **Msg interface**: `Ns3AiMsgInterfaceImpl` para C++↔Python
- **Ejemplos**: RL-TCP, Multi-BSS, Rate Control, LTE CQI

### 2.2.3 Trabajo Relacionado NS-3 + RL
- **NS3-Gym** (Acosta et al.): Wrapper OpenAI Gym clásico
- **DEFIANCE** (Cisco, 2022): MARL para routing adaptativo
- **ORAN-Gym**: Interfaz RL para ORAN E2

## 2.3 Orquestación de Agentes

### 2.3.1 Frameworks
- **LangGraph** (LangChain, 2024): Grafos de estado con checkpoints, SOTA
- **AutoGen** (Microsoft, 2023): Multi-agent conversation, group chat
- **CrewAI** (2024): Role-based agents con processes
- **OpenHands SDK**: Agent + Tools + Workspace + MCP

### 2.3.2 LangGraph vs Alternativas
| Característica | LangGraph | AutoGen | CrewAI |
|----------------|-----------|---------|--------|
| State management | ✅ Checkpoints | ⚠️ Conversation history | ❌ |
| Deterministic edges | ✅ | ❌ | ❌ |
| Human-in-the-loop | ✅ | ✅ | ⚠️ |
| MCP integration | ✅ (custom) | ✅ (native) | ❌ |
| Local LLM (Ollama) | ✅ | ✅ | ✅ |

## 2.4 Memoria Agéntica

### 2.4.1 Tipos de Memoria
| Tipo | Descripción | Implementación |
|------|-------------|----------------|
| **Episódica** | Interacciones pasadas, errores, insights | Mem0 |
| **Semántica** | Conocimiento factual, papers | Qdrant + fastembed |
| **De trabajo** | Contexto actual de tarea | Context window + scratchpad |
| **Procedural** | Skills, workflows | AGENTS.md + .agents/skills/ |

### 2.4.2 Mem0 (2024)
- **Episódica**: `add_memory`, `search_memory`, `get_context_for_task`
- **Aprendizaje de errores**: `learn_from_error`, `record_insight`
- **Backend**: Vector DB (Qdrant, ChromaDB, Pinecone) + embeddings

## 2.5 Modelos Locales con Ollama

### 2.5.1 Modelos Evaluados
| Modelo | Tamaño | RAM | Uso | Tiempo (PaperQA2) |
|--------|--------|-----|-----|-------------------|
| **qwen2.5-coder:7b** | 4.7GB | ~4GB | Coding/NS-3 | 37s |
| **qwen3:8b** | 5.2GB | ~5.5GB | Reasoning/Drafting | 92s (think:false) |
| **nomic-embed-text** | 274MB | ~0.5GB | Embeddings | Local |

### 2.5.2 qwen3 Thinking Mode Issue
- **Problema**: litellm usa `/api/generate` → thinking mode → response vacía
- **Solución**: Native Ollama client + `think=false` top-level (NO en options)
- **Config PaperQA2**: `extra_body={'think': False}` + `agent_type="FakeAgent"`

## 2.6 Gap de Investigación Identificado

Ningún sistema existente integra **TODOS** estos componentes:
1. ✅ Investigación profunda con citas (PaperQA2/LDR)
2. ✅ Orquestación multi-agente (LangGraph)
3. ✅ Memoria episódica + vectorial (Mem0 + Qdrant)
4. ✅ Simulación NS-3 con trazabilidad (ns3-ai + manifest.json)
5. ✅ Local-first con Ollama (privacidad, costo cero)
6. ✅ Writer académico Markdown+Pandoc+Zotero
7. ✅ Crítico multi-agente (AutoGen group chat)

**JARVIS Research cubre este gap completo.**