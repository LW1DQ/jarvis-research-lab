# Capítulo 5: Memoria Agéntica y Aprendizaje Continuo

## 5.1 Motivación: ¿Por Qué Memoria en un Asistente de Investigación?

Un asistente de investigación que **no aprende de sus errores** repite los mismos fallos:
- Timeouts en arXiv → mismo timeout configurado
- qwen3 thinking mode → response vacía cada vez
- NS-3 build failures → mismos flags CMake erróneos
- PaperQA2 config incorrecta → mismos env vars problemáticas

**JARVIS Research** implementa memoria en tres capas:

| Capa | Tecnología | Propósito | Persistencia |
|------|------------|-----------|--------------|
| **Episódica** | Mem0 | Interacciones, errores, insights, soluciones | Qdrant (vector) + SQLite (metadata) |
| **Semántica** | Qdrant + fastembed | Papers, conceptos, conocimiento factual | Híbrida BM25 + vectorial (dim=768) |
| **Personal** | ChromaDB | Notas del usuario, preferencias, contexto tesis | Local SQLite |

## 5.2 Mem0: Memoria Episódica

### 5.2.1 Arquitectura Mem0
```
┌─────────────────────────────────────────────────────────┐
│                      MemoryAgent                         │
│  (EpisodicMemoryAgent + MemoryAgent)                    │
└──────────────────────────┬──────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  add_memory()   │ │ search_memory() │ │ get_context_    │
│  - content      │ │ - query         │ │   for_task()    │
│  - metadata     │ │ - filters       │ │ - task          │
│  - tags         │ │ - limit         │ │ - limit         │
└─────────────────┘ └─────────────────┘ └─────────────────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           ▼
              ┌────────────────────────┐
              │      Mem0 Core         │
              │  - Embedding (nomic)   │
              │  - Deduplication       │
              │  - Importance scoring  │
              └───────────┬────────────┘
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
       ┌─────────────┐         ┌─────────────┐
       │   Qdrant    │         │   SQLite    │
       │  (vectors)  │         │  (metadata) │
       │  collection │         │  - user_id  │
       │  jarvis_    │         │  - tags     │
       │  _memory    │         │  - timestamp│
       └─────────────┘         └─────────────┘
```

### 5.2.2 API Principal

```python
class MemoryAgent:
    def __init__(self, user_id: str = "diego"):
        self.mem0 = Mem0.from_config({
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "host": "localhost",
                    "port": 6333,
                    "collection_name": "jarvis_memory"
                }
            },
            "embedder": {
                "provider": "ollama",
                "config": {"model": "nomic-embed-text"}
            }
        })
        self.user_id = user_id
    
    def record_interaction(self, task: str, action: str, result: str, success: bool):
        """Registra una interacción completa"""
        self.mem0.add(
            content=f"Task: {task}\nAction: {action}\nResult: {result}\nSuccess: {success}",
            user_id=self.user_id,
            tags=["interaction", task[:50]],
            metadata={"success": success, "task_type": "research"}
        )
    
    def learn_from_error(self, error: str, context: str, solution: str):
        """APRENDIZAJE CRÍTICO: evita repetir errores"""
        self.mem0.add(
            content=f"ERROR: {error}\nCONTEXT: {context}\nSOLUTION: {solution}",
            user_id=self.user_id,
            tags=["error", "learned", error[:50]],
            metadata={"type": "error_resolution", "resolved": True}
        )
    
    def record_insight(self, insight: str, tags: List[str]):
        """Insights valiosos para futuras tareas"""
        self.mem0.add(
            content=f"INSIGHT: {insight}",
            user_id=self.user_id,
            tags=["insight"] + tags,
            metadata={"type": "insight"}
        )
    
    def get_context_for_task(self, task: str, limit: int = 5) -> List[Dict]:
        """Recupera memoria relevante ANTES de ejecutar tarea"""
        return self.mem0.search(
            query=task,
            user_id=self.user_id,
            limit=limit,
            filters={"tags": {"$in": ["interaction", "error", "insight"]}}
        )
```

### 5.2.3 Ejemplos de Memorias Registradas

| Tipo | Contenido | Tags | Uso Futuro |
|------|-----------|------|------------|
| **Error** | `arXiv timeout 30s` → `60s + 3 retries backoff` | `error, arxiv, timeout` | Auto-configura timeouts |
| **Error** | `qwen3 thinking mode → response vacía` → `think=false` | `error, qwen3, paperqa2` | Config PaperQA2 correcta |
| **Error** | `AGENT=1 rompe PaperQA2 Settings` → `unset AGENT` | `error, paperqa2, env` | Limpia env antes de PaperQA2 |
| **Insight** | `ns3-ai usa Unix sockets IPC, no mover por SSH` | `insight, ns3-ai, architecture` | Decide Fase 2: worker remoto completo |
| **Insight** | `ChromaDB solo vectorial → Qdrant para BM25+semántico` | `insight, vectordb, search` | Migra a Qdrant Fase 2 |
| **Interacción** | `TCP-RL 3600 corridas → manifest.json OK` | `interaction, tcp-rl, ns3` | Referencia para experimentos similares |

## 5.3 Qdrant: Búsqueda Híbrida BM25 + Vectorial

### 5.3.1 Por Qué Qdrant (no solo ChromaDB)

| Feature | ChromaDB | Qdrant |
|---------|----------|--------|
| Búsqueda vectorial | ✅ | ✅ |
| **Búsqueda keyword (BM25)** | ❌ | ✅ **Sparse vectors** |
| **Híbrida (RRF fusion)** | ❌ | ✅ **Native** |
| Filtros pre-ANN | ⚠️ Limitados | ✅ **Payload indexes** |
| Escalabilidad | <100K | >1M vectores |
| Multi-tenancy | ❌ | ✅ |

### 5.3.2 Configuración Colección `jarvis_memory`

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, SparseVectorParams

client = QdrantClient(host="localhost", port=6333)

# Colección híbrida: dense (nomic-embed-text) + sparse (BM25 via fastembed)
client.create_collection(
    collection_name="jarvis_memory",
    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    sparse_vectors_config={
        "bm25": SparseVectorParams(
            index=SparseIndexParams(
                on_disk=False,
                full_scan_threshold=10000
            )
        )
    },
    # Payload indexes para filtros rápidos
    payload_schema={
        "user_id": "keyword",
        "tags": "keyword",
        "type": "keyword",
        "timestamp": "datetime",
        "success": "bool"
    }
)
```

### 5.3.3 Búsqueda Híbrida (RRF - Reciprocal Rank Fusion)

```python
def hybrid_search(query: str, user_id: str, limit: int = 10):
    """Combina vectorial + BM25 con RRF"""
    results = client.query_points(
        collection_name="jarvis_memory",
        query=query,
        query_filter=Filter(
            must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]
        ),
        limit=limit,
        with_payload=True,
        # RRF fusion nativo
        prefetch=[
            Prefetch(
                query=embed_query(query),  # vectorial
                limit=limit*2,
                using="default"
            ),
            Prefetch(
                query=query,  # BM25 via fastembed sparse
                limit=limit*2,
                using="bm25"
            )
        ]
    )
    return results.points
```

## 5.4 ChromaDB: Memoria Personal del Usuario

### 5.4.1 personal-mcp (HTTP :8004)

```python
# personal_mcp_server.py - FastMCP server
from fastmcp import FastMCP
import chromadb

mcp = FastMCP("personal-memory")
chroma = chromadb.PersistentClient(path="~/research-jarvis/chroma/personal")
collection = chroma.get_or_create_collection("personal_notes")

@mcp.tool()
def add_note(title: str, content: str, tags: List[str] = None) -> str:
    """Agrega nota personal con embedding automático"""
    doc_id = str(uuid.uuid4())
    collection.add(
        ids=[doc_id],
        documents=[f"{title}\n{content}"],
        metadatas=[{"title": title, "tags": tags or [], "timestamp": datetime.now().isoformat()}]
    )
    return doc_id

@mcp.tool()
def search_notes(query: str, limit: int = 10) -> List[Dict]:
    """Búsqueda semántica en notas personales"""
    results = collection.query(
        query_texts=[query],
        n_results=limit,
        include=["documents", "metadatas", "distances"]
    )
    return format_results(results)

@mcp.tool()
def list_notes(limit: int = 50) -> List[Dict]:
    """Lista notas recientes"""
    results = collection.get(limit=limit, include=["metadatas"])
    return format_results(results)

@mcp.tool()
def delete_note(note_id: str) -> bool:
    """Elimina nota por ID"""
    collection.delete(ids=[note_id])
    return True
```

### 5.4.2 Uso en Flujo de Trabajo

```python
# En researcher_node: guardar hallazgos
await mcp_call("personal-mcp", "add_note", {
    "title": f"Research: {query[:50]}",
    "content": evidence_summary,
    "tags": ["research", "paperqa2", "auto-generated"]
})

# En daily note: recuperar contexto
notes = await mcp_call("personal-mcp", "search_notes", {
    "query": "TCP-RL congestion control",
    "limit": 5
})
```

## 5.5 Integración en Orquestador LangGraph

### 5.5.1 Memory-Enhanced State
```python
class JARVISState(TypedDict):
    # ... campos existentes ...
    
    # Memoria
    memory_context: List[Dict]      # Resultados get_context_for_task
    learned_errors: List[Dict]      # Errores previos relevantes
    insights_applied: List[str]     # Insights usados en esta tarea
```

### 5.5.2 Pre-Execution: Cargar Contexto
```python
async def load_memory_context(state: JARVISState) -> JARVISState:
    """SE EJECUTA ANTES DE CADA NODO PRINCIPAL"""
    memory_agent = MemoryAgent(user_id="diego")
    
    # Contexto relevante para la tarea actual
    context = memory_agent.get_context_for_task(
        task=state["user_query"],
        limit=5
    )
    
    # Filtrar errores ya resueltos
    learned_errors = [
        m for m in context 
        if m.get("metadata", {}).get("type") == "error_resolution"
    ]
    
    return {
        **state,
        "memory_context": context,
        "learned_errors": learned_errors
    }
```

### 5.5.3 Post-Execution: Aprender
```python
async def post_execution_learning(state: JARVISState) -> JARVISState:
    """SE EJECUTA DESPUÉS DE CADA NODO PRINCIPAL"""
    memory_agent = MemoryAgent(user_id="diego")
    
    # Si hubo error, aprender
    if state.get("error"):
        memory_agent.learn_from_error(
            error=state["error"],
            context=f"Node: {state['current_node']}, Task: {state['user_query']}",
            solution=state.get("solution_applied", "Pendiente")
        )
    
    # Si éxito notable, registrar insight
    if state.get("notable_success"):
        memory_agent.record_insight(
            insight=state["notable_success"],
            tags=[state["current_node"], "success"]
        )
    
    # Registrar interacción completa
    memory_agent.record_interaction(
        task=state["user_query"],
        action=state["current_node"],
        result=state.get("summary", "Completado"),
        success=state.get("error") is None
    )
    
    return state
```

## 5.6 Evaluación de Memoria: Casos de Éxito

### 5.6.1 Caso 1: arXiv Timeout (Día 10)
```
ANTES: Timeout 30s → fallo silencioso → paper perdido
DESPUÉS: learn_from_error registrado
         → Próxima ejecución: config 60s + 3 retries backoff
         → Éxito: 100% papers recuperados
```

### 5.6.2 Caso 2: qwen3 Thinking Mode (Día 8)
```
ANTES: litellm + qwen3 → response '' → PaperQA2 falla
DESPUÉS: learn_from_error registrado
         → Próxima ejecución: native Ollama client + think=false
         → Éxito: PaperQA2 funcional 92s
```

### 5.6.3 Caso 3: NS-3 SSH IPC (Día 11)
```
ANÁLISIS: ns3-ai usa Unix domain sockets para shared memory
INSIGHT: Mover solo NS-3 por SSH añade 10-100x latencia
DECISIÓN: Fase 2 = worker remoto COMPLETO (NS-3 + API REST)
```

## 5.7 Métricas de Memoria

| Métrica | Valor | Descripción |
|---------|-------|-------------|
| **Memorias totales** | ~200 | Interacciones + errores + insights |
| **Errores aprendidos** | 12 | Únicos, no repetidos |
| **Insights registrados** | 8 | Decisiones arquitectónicas |
| **Hit rate get_context_for_task** | 73% | Memoria relevante recuperada |
| **Tiempo búsqueda Qdrant** | <50ms | Híbrida BM25+vectorial |
| **Tiempo búsqueda ChromaDB** | <30ms | Personal notes |

---

**Conclusión**: La memoria agétnica transforma a JARVIS de un ejecutor reactivo a un **investigador que aprende**, reduciendo drásticamente errores repetidos y acelerando la convergencia experimental.