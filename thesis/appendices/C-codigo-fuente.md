# Apéndice C: Código Fuente Clave

## C.1 Orquestador Principal (jarvis_orchestrator_v2.py)

```python
#!/usr/bin/env python3
"""
JARVIS Research Orchestrator v2
LangGraph 5-node orchestrator for research workflows.
"""

from typing import TypedDict, List, Optional, Literal, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
import asyncio
import json
from datetime import datetime

# ============================================================
# STATE DEFINITION
# ============================================================

class Evidence(TypedDict):
    paper_id: str
    title: str
    authors: List[str]
    year: int
    venue: str
    doi: Optional[str]
    snippet: str
    relevance_score: float

class NS3Task(TypedDict):
    script: str
    params: Dict[str, Any]
    seed: int
    repetitions: int

class Critique(TypedDict):
    coverage: int
    evidence: int
    structure: int
    clarity: int
    actionability: int
    overall: int
    comments: List[str]

class JARVISState(TypedDict):
    # Input
    user_query: str
    task_type: Literal["research", "simulation", "writing", "review", "full"]
    
    # Research
    evidence_package: List[Evidence]
    research_notes: List[str]
    
    # Writing
    draft_markdown: str
    docx_path: Optional[str]
    tex_path: Optional[str]
    
    # Simulation
    ns3_task: Optional[NS3Task]
    ns3_manifest: Optional[Dict]
    ns3_results: Optional[Dict]
    
    # Review
    critique_report: Optional[Critique]
    
    # Memory
    memory_context: List[Dict]
    learned_errors: List[Dict]
    insights_applied: List[str]
    
    # Control
    current_node: str
    retry_count: int
    error: Optional[str]
    notable_success: Optional[str]

# ============================================================
# NODE IMPLEMENTATIONS
# ============================================================

async def supervisor_node(state: JARVISState) -> JARVISState:
    """Deterministic routing with LLM fallback."""
    # 1. Deterministic rules first
    if state.get("error"):
        return {**state, "current_node": "critiquer"}
    
    if not state.get("evidence_package") and needs_research(state["user_query"]):
        return {**state, "current_node": "researcher"}
    
    if state.get("ns3_task") and not state.get("ns3_results"):
        return {**state, "current_node": "ns3_simulation"}
    
    if state.get("draft_markdown") and not state.get("docx_path"):
        return {**state, "current_node": "writer"}
    
    if state.get("docx_path") and not state.get("critique_report"):
        return {**state, "current_node": "critiquer"}
    
    # 2. LLM fallback for ambiguous decisions
    decision = await llm_decide_next_node(state)
    return route(decision, state)

def needs_research(query: str) -> bool:
    """Heuristic: queries about literature need research."""
    research_keywords = ["paper", "literature", "review", "state of the art", 
                         "related work", "survey", "comparison"]
    return any(kw in query.lower() for kw in research_keywords)

async def llm_decide_next_node(state: JARVISState) -> str:
    """LLM decides next node when deterministic rules don't apply."""
    prompt = f"""
    Current state: {state['current_node']}
    User query: {state['user_query']}
    Has evidence: {bool(state.get('evidence_package'))}
    Has draft: {bool(state.get('draft_markdown'))}
    Has simulation results: {bool(state.get('ns3_results'))}
    Has critique: {bool(state.get('critique_report'))}
    
    Decide next node: researcher, writer, ns3_simulation, critiquer, or END
    """
    # Use qwen2.5-coder:7b for fast routing decisions
    response = await ollama_chat("qwen2.5-coder:7b", prompt, temperature=0.0)
    return response.strip().lower()

def route(decision: str, state: JARVISState) -> JARVISState:
    valid_nodes = ["researcher", "writer", "ns3_simulation", "critiquer", "END"]
    next_node = decision if decision in valid_nodes else "END"
    return {**state, "current_node": next_node}

# ============================================================
# RESEARCHER NODE
# ============================================================

async def researcher_node(state: JARVISState) -> JARVISState:
    """PaperQA2 + arXiv + OpenAlex via research-mcp."""
    from paperqa import Settings, ask
    from mcp_client import MCPClient
    
    # 1. PaperQA2 query con evidencia
    settings = get_paperqa_settings()
    answer = await ask(
        query=state["user_query"],
        settings=settings
    )
    
    evidence = []
    for ctx in answer.contexts:
        evidence.append(Evidence(
            paper_id=ctx.doc.docid,
            title=ctx.doc.title,
            authors=ctx.doc.authors,
            year=ctx.doc.year,
            venue=ctx.doc.journal or ctx.doc.conference,
            doi=ctx.doc.doi,
            snippet=ctx.text[:500],
            relevance_score=ctx.score
        ))
    
    # 2. Búsqueda complementaria via research-mcp
    mcp = MCPClient("http://localhost:8001")
    
    arxiv_results = await mcp.call("search_arxiv", {
        "query": state["user_query"],
        "max_results": 10
    })
    
    openalex_results = await mcp.call("search_openalex", {
        "query": state["user_query"],
        "max_results": 10
    })
    
    # 3. Guardar notas en personal-mcp
    personal_mcp = MCPClient("http://localhost:8004")
    for i, note in enumerate(evidence + arxiv_results + openalex_results):
        await personal_mcp.call("add_note", {
            "title": f"Research: {state['user_query'][:50]} - {i}",
            "content": json.dumps(note, indent=2),
            "tags": ["research", "paperqa2", "auto-generated"]
        })
    
    return {
        **state,
        "evidence_package": evidence,
        "research_notes": [f"note_{i}" for i in range(len(evidence))],
        "current_node": "researcher"
    )

def get_paperqa_settings() -> Settings:
    """Configuración PaperQA2 para qwen3:8b local."""
    return Settings(
        llm="ollama/qwen3:8b",
        summary_llm="ollama/qwen3:8b",
        agent_llm="ollama/qwen3:8b",
        enrichment_llm="ollama/qwen3:8b",
        agent_type="FakeAgent",
        multimodal=0,
        embedding="ollama/nomic-embed-text",
        temperature=0.0,
        timeout=300,
    )

# ============================================================
# WRITER NODE
# ============================================================

async def writer_node(state: JARVISState) -> JARVISState:
    """Markdown + Pandoc + Zotero."""
    import subprocess
    from pyzotero import zotero
    
    # 1. Generar Markdown con evidencia
    markdown = generate_academic_markdown(
        query=state["user_query"],
        evidence=state["evidence_package"],
        template="ieee_conference"
    )
    
    # 2. Pandoc: Markdown → DOCX/LaTeX
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    docx_path = f"outputs/paper_{timestamp}.docx"
    tex_path = f"outputs/paper_{timestamp}.tex"
    
    # DOCX
    subprocess.run([
        "pandoc", "-s", "-o", docx_path,
        "--citeproc", "--csl=ieee.csl",
        "--bibliography=references.bib",
        "-f", "markdown", "-t", "docx"
    ], input=markdown.encode(), check=True)
    
    # LaTeX
    subprocess.run([
        "pandoc", "-s", "-o", tex_path,
        "--citeproc", "--csl=ieee.csl",
        "--bibliography=references.bib",
        "-f", "markdown", "-t", "latex",
        "--template=ieee.latex"
    ], input=markdown.encode(), check=True)
    
    # 3. Zotero: crear entradas bibliográficas
    zot = zotero.Zotero(library_id, library_type, api_key)
    for ev in state["evidence_package"]:
        if ev.get("doi"):
            zot.create_items([{
                "itemType": "journalArticle",
                "title": ev["title"],
                "creators": [{"creatorType": "author", "firstName": a.split()[0], "lastName": " ".join(a.split()[1:])} for a in ev["authors"]],
                "publicationTitle": ev["venue"],
                "year": str(ev["year"]),
                "DOI": ev["doi"]
            }])
    
    return {
        **state,
        "draft_markdown": markdown,
        "docx_path": docx_path,
        "tex_path": tex_path,
        "current_node": "writer"
    }

def generate_academic_markdown(query: str, evidence: List[Evidence], template: str) -> str:
    """Genera paper académico estructurado."""
    # Template IEEE conference
    sections = [
        "# Title: " + query_to_title(query),
        "",
        "## Abstract",
        generate_abstract(evidence),
        "",
        "## 1. Introduction",
        generate_introduction(evidence),
        "",
        "## 2. Related Work",
        generate_related_work(evidence),
        "",
        "## 3. Methodology",
        "TBD - Based on evidence package",
        "",
        "## 4. Experimental Setup",
        "NS-3.48 + ns3-ai (commit b8c9858)",
        "",
        "## 5. Results",
        "TBD - From simulation",
        "",
        "## 6. Discussion",
        "TBD",
        "",
        "## 7. Limitations",
        "TBD - Required by template",
        "",
        "## 8. Conclusion and Future Work",
        "TBD",
        "",
        "## References",
        generate_references(evidence)
    ]
    return "\n".join(sections)

# ============================================================
# NS-3 SIMULATION NODE
# ============================================================

async def ns3_simulation_node(state: JARVISState) -> JARVISState:
    """Ejecuta simulación NS-3 via ns3-mcp + run_tracked.py."""
    from mcp_client import MCPClient
    
    task = state["ns3_task"]
    if not task:
        return {**state, "error": "No NS-3 task defined"}
    
    mcp = MCPClient("http://localhost:8002")
    
    result = await mcp.call("run_ns3_simulation", {
        "script": task["script"],
        "params": task["params"],
        "seed": task["seed"],
        "repetitions": task["repetitions"],
        "trace": True
    })
    
    # Leer manifest.json
    manifest = result.get("manifest", {})
    
    # Parsear resultados
    parsed = await parse_ns3_results(result.get("output_dir", ""))
    
    return {
        **state,
        "ns3_manifest": manifest,
        "ns3_results": parsed,
        "current_node": "ns3_simulation"
    }

async def parse_ns3_results(output_dir: str) -> Dict:
    """Parsea FlowMonitor XML, PCAP, logs."""
    import xml.etree.ElementTree as ET
    from pathlib import Path
    
    results = {}
    out_path = Path(output_dir)
    
    # FlowMonitor
    fm_files = list(out_path.glob("*.xml"))
    if fm_files:
        tree = ET.parse(fm_files[0])
        root = tree.getroot()
        # Extraer métricas...
        results["flowmonitor"] = extract_flowmonitor_metrics(root)
    
    return results

# ============================================================
# CRITIQUER NODE
# ============================================================

async def critiquer_node(state: JARVISState) -> JARVISState:
    """AutoGen Group Chat 5 agentes."""
    from autogen import GroupChat, GroupChatManager, AssistantAgent
    
    agents = [
        AssistantAgent(
            name="CoverageCritic",
            system_message="Evalúa coverage: ¿Cubre todos los aspectos necesarios? Score 0-100."
        ),
        AssistantAgent(
            name="EvidenceCritic",
            system_message="Evalúa evidencia: ¿Citas suficientes, verificables, DOIs? Score 0-100."
        ),
        AssistantAgent(
            name="StructureCritic",
            system_message="Evalúa estructura: ¿IMRAD, related work, limitations? Score 0-100."
        ),
        AssistantAgent(
            name="ClarityCritic",
            system_message="Evalúa claridad: ¿Legibilidad, notación, figuras? Score 0-100."
        ),
        AssistantAgent(
            name="ActionabilityCritic",
            system_message="Evalúa actionability: ¿Trabajo futuro concreto, reproducibilidad? Score 0-100."
        )
    ]
    
    group_chat = GroupChat(
        agents=agents,
        messages=[],
        max_round=10,
        speaker_selection_method="round_robin"
    )
    
    manager = GroupChatManager(
        groupchat=group_chat,
        llm_config={"model": "qwen3:8b", "temperature": 0.0}
    )
    
    task_msg = f"""
    Revisar paper académico:
    
    QUERY: {state['user_query']}
    
    DRAFT:
    {state['draft_markdown']}
    
    EVIDENCE PACKAGE: {len(state['evidence_package'])} papers
    """
    
    critique_result = await manager.a_initiate_chat(
        recipient=agents[0],
        message=task_msg
    )
    
    # Parsear resultado
    critique = parse_critique(critique_result)
    
    return {
        **state,
        "critique_report": critique,
        "current_node": "critiquer"
    }

# ============================================================
# GRAPH CONSTRUCTION
# ============================================================

def build_graph() -> StateGraph:
    """Construye el grafo LangGraph."""
    workflow = StateGraph(JARVISState)
    
    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("writer", writer_node)
    workflow.add_node("ns3_simulation", ns3_simulation_node)
    workflow.add_node("critiquer", critiquer_node)
    
    # Entry point
    workflow.set_entry_point("supervisor")
    
    # Conditional edges from supervisor
    workflow.add_conditional_edges(
        "supervisor",
        lambda state: state["current_node"],
        {
            "researcher": "researcher",
            "writer": "writer",
            "ns3_simulation": "ns3_simulation",
            "critiquer": "critiquer",
            "END": END
        }
    )
    
    # Return edges to supervisor
    for node in ["researcher", "writer", "ns3_simulation", "critiquer"]:
        workflow.add_edge(node, "supervisor")
    
    return workflow

# ============================================================
# MAIN
# ============================================================

async def main():
    # Checkpointer para persistence
    checkpointer = SqliteSaver.from_conn_string("sqlite:///checkpoints.db")
    
    graph = build_graph().compile(checkpointer=checkpointer)
    
    # Config
    config = {"configurable": {"thread_id": "thesis_experiment_001"}}
    
    # Initial state
    initial_state = JARVISState(
        user_query="TCP congestion control reinforcement learning ns3",
        task_type="full",
        evidence_package=[],
        research_notes=[],
        draft_markdown="",
        docx_path=None,
        tex_path=None,
        ns3_task=NS3Task(
            script="tcp-rl-simulation",
            params={"duration": 1000, "transport_prot": "TcpRlTimeBased"},
            seed=42,
            repetitions=30
        ),
        ns3_manifest=None,
        ns3_results=None,
        critique_report=None,
        memory_context=[],
        learned_errors=[],
        insights_applied=[],
        current_node="supervisor",
        retry_count=0,
        error=None,
        notable_success=None
    )
    
    # Run
    async for state in graph.astream(initial_state, config=config):
        print(f"Node: {list(state.keys())[0]}")
        print(f"  State keys: {list(state[list(state.keys())[0]].keys())}")

if __name__ == "__main__":
    asyncio.run(main())
```

## C.2 run_tracked.py (Trazabilidad NS-3)

```python
#!/usr/bin/env python3
"""
run_tracked.py - Ejecuta simulación NS-3 y genera manifest.json automático.
Ubicación: ~/research-jarvis/mcp/ns3/run_tracked.py
"""

import json
import hashlib
import subprocess
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

NS3_HOME = Path.home() / "ns-allinone-3.48" / "ns-3.48"
EXPERIMENTS_DIR = Path.home() / "experiments"
NS3_AI_COMMIT = "b8c9858"  # FIJADO - NO CAMBIAR

def get_git_commit(repo_path: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path, capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except:
        return "unknown"

def get_script_hash(script_path: Path) -> str:
    if script_path.exists():
        return hashlib.sha256(script_path.read_bytes()).hexdigest()[:16]
    return "unknown"

def run_tracked(
    script: str,
    args: Dict[str, Any],
    output_dir: Path,
    seed: int = 42,
    repetitions: int = 1
) -> Dict[str, Any]:
    
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = output_dir / f"experiment_{run_id}"
    run_dir.mkdir(parents=True, exist_ok=True)
    
    # Comando NS-3
    cmd = [
        "./ns3", "run", script,
        "--"
    ] + [f"--{k}={v}" for k, v in args.items()]
    
    # Ejecutar
    env = os.environ.copy()
    env["NS_LOG"] = "*=info"
    
    start_time = datetime.now()
    result = subprocess.run(
        cmd, cwd=NS3_HOME, env=env,
        capture_output=True, text=True, timeout=3600
    )
    end_time = datetime.now()
    
    # Manifest
    manifest = {
        "run_id": run_id,
        "timestamp": start_time.isoformat(),
        "duration_seconds": (end_time - start_time).total_seconds(),
        "script": script,
        "script_hash": get_script_hash(NS3_HOME / "scratch" / f"{script}.cc"),
        "args": args,
        "seed": seed,
        "repetitions": repetitions,
        "ns3_commit": get_git_commit(NS3_HOME),
        "ns3_ai_commit": NS3_AI_COMMIT,
        "exit_code": result.returncode,
        "stdout_tail": result.stdout[-5000:] if result.stdout else "",
        "stderr_tail": result.stderr[-5000:] if result.stderr else "",
        "output_dir": str(run_dir),
        "success": result.returncode == 0
    }
    
    # Guardar manifest
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    
    # Copiar outputs NS-3 a run_dir
    copy_ns3_outputs(NS3_HOME, run_dir)
    
    return manifest

def copy_ns3_outputs(ns3_home: Path, run_dir: Path):
    """Copia FlowMonitor, PCAP, logs a directorio de corrida."""
    patterns = ["*.xml", "*.pcap", "*.log", "*.txt", "*.csv"]
    for pattern in patterns:
        for f in ns3_home.glob(pattern):
            try:
                f.copy(run_dir / f.name)
            except:
                pass

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("script")
    parser.add_argument("--args", type=json.loads, default="{}")
    parser.add_argument("--output", default=str(EXPERIMENTS_DIR))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--reps", type=int, default=1)
    args = parser.parse_args()
    
    manifest = run_tracked(
        script=args.script,
        args=args.args,
        output_dir=Path(args.output),
        seed=args.seed,
        repetitions=args.reps
    )
    print(json.dumps(manifest, indent=2))
```

## C.3 Memory Agent (memory_agent.py)

```python
#!/usr/bin/env python3
"""
Memory Agent - Mem0 + Qdrant + ChromaDB
Ubicación: ~/research-jarvis/memory_agent.py
"""

from mem0 import Mem0
from qdrant_client import QdrantClient
import chromadb
from typing import List, Dict, Any, Optional
from datetime import datetime

class MemoryAgent:
    def __init__(self, user_id: str = "diego"):
        self.user_id = user_id
        
        # Mem0 para memoria episódica
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
        
        # Qdrant directo para búsqueda híbrida
        self.qdrant = QdrantClient(host="localhost", port=6333)
        
        # ChromaDB para notas personales
        self.chroma = chromadb.PersistentClient(
            path="/home/diego/research-jarvis/chroma/personal"
        )
        self.personal_collection = self.chroma.get_or_create_collection("personal_notes")
    
    # ============================================================
    # MEM0 EPISÓDICA
    # ============================================================
    
    def record_interaction(self, task: str, action: str, result: str, success: bool):
        self.mem0.add(
            content=f"Task: {task}\nAction: {action}\nResult: {result}\nSuccess: {success}",
            user_id=self.user_id,
            tags=["interaction", task[:50]],
            metadata={"success": success, "task_type": "research", "timestamp": datetime.now().isoformat()}
        )
    
    def learn_from_error(self, error: str, context: str, solution: str):
        """APRENDIZAJE CRÍTICO: evita repetir errores."""
        self.mem0.add(
            content=f"ERROR: {error}\nCONTEXT: {context}\nSOLUTION: {solution}",
            user_id=self.user_id,
            tags=["error", "learned", error[:50]],
            metadata={"type": "error_resolution", "resolved": True, "timestamp": datetime.now().isoformat()}
        )
    
    def record_insight(self, insight: str, tags: List[str]):
        self.mem0.add(
            content=f"INSIGHT: {insight}",
            user_id=self.user_id,
            tags=["insight"] + tags,
            metadata={"type": "insight", "timestamp": datetime.now().isoformat()}
        )
    
    def get_context_for_task(self, task: str, limit: int = 5) -> List[Dict]:
        """Recupera memoria relevante ANTES de ejecutar tarea."""
        return self.mem0.search(
            query=task,
            user_id=self.user_id,
            limit=limit,
            filters={"tags": {"$in": ["interaction", "error", "insight"]}}
        )
    
    # ============================================================
    # QDRANT HÍBRIDA (BM25 + Vectorial)
    # ============================================================
    
    def hybrid_search(self, query: str, limit: int = 10) -> List[Dict]:
        """Búsqueda híbrida RRF: vectorial + BM25."""
        from qdrant_client.models import Prefetch
        
        results = self.qdrant.query_points(
            collection_name="jarvis_memory",
            query=query,
            query_filter={
                "must": [{"key": "user_id", "match": {"value": self.user_id}}]
            },
            limit=limit,
            with_payload=True,
            prefetch=[
                Prefetch(
                    query=query,  # BM25 via fastembed sparse
                    limit=limit*2,
                    using="bm25"
                )
            ]
        )
        return results.points
    
    # ============================================================
    # CHROMADB PERSONAL
    # ============================================================
    
    def add_personal_note(self, title: str, content: str, tags: List[str] = None) -> str:
        import uuid
        doc_id = str(uuid.uuid4())
        self.personal_collection.add(
            ids=[doc_id],
            documents=[f"{title}\n{content}"],
            metadatas=[{
                "title": title, 
                "tags": tags or [], 
                "timestamp": datetime.now().isoformat()
            }]
        )
        return doc_id
    
    def search_personal_notes(self, query: str, limit: int = 10) -> List[Dict]:
        results = self.personal_collection.query(
            query_texts=[query],
            n_results=limit,
            include=["documents", "metadatas", "distances"]
        )
        return self._format_chroma_results(results)
    
    def _format_chroma_results(self, results) -> List[Dict]:
        notes = []
        for i, doc in enumerate(results.get("documents", [[]])[0]):
            notes.append({
                "id": results["ids"][0][i],
                "content": doc,
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            })
        return notes
```

## C.4 Docker Entrypoint (docker-entrypoint.sh)

```bash
#!/bin/bash
# docker-entrypoint.sh - NS-3 Simulation Environment
# Ubicación: ~/research-jarvis/docker-entrypoint.sh

set -e

echo "=========================================="
echo "  NS-3.48 Simulation Environment Ready"
echo "=========================================="
echo ""
echo "Environment:"
echo "  NS3_HOME=$NS3_HOME"
echo "  NS3_AI_PATH=$NS3_AI_PATH"
echo "  WORKDIR=$PWD"
echo ""

# Check NS-3 installation
if [ -d "$NS3_HOME" ]; then
    echo "NS-3 found at $NS3_HOME"
    if [ -f "$NS3_HOME/ns3" ]; then
        echo "NS-3 executable found"
    fi
else
    echo "NS-3 not found. Build from source or mount NS-3 volume."
    echo "Example: docker run -v ~/ns-allinone-3.48/ns-3.48:/opt/ns-3.48 ..."
fi

# Check ns3-ai
if [ -d "$NS3_AI_PATH" ]; then
    echo "ns3-ai found at $NS3_AI_PATH"
    echo "Python bindings available"
fi

# Build/install ns3-ai gym interface if NS-3 is mounted
if [ -d "$NS3_HOME/build/lib" ] && [ -f "/opt/ns3-ai-gym-interface/py/setup.py" ]; then
    echo ""
    echo "Building ns3-ai gym interface..."
    
    export LD_LIBRARY_PATH=$NS3_HOME/build/lib:$LD_LIBRARY_PATH
    
    # Remove old compiled .so files
    rm -f /opt/ns3-ai-gym-interface/py/ns3ai_gym_msg_py/*.so
    
    # Compile pybind11 module directly
    PYTHON_INCLUDE=$(python3 -c "import sysconfig; print(sysconfig.get_path('include'))")
    PYBIND11_INCLUDE=$(python3 -c "import pybind11; print(pybind11.get_include())")
    
    NS3_SRC=$NS3_HOME
    NS3_CONTRIB_AI=$NS3_HOME/contrib/ai/model
    
    g++ -O3 -Wall -shared -std=c++17 -fPIC \
        -I$PYTHON_INCLUDE \
        -I$PYBIND11_INCLUDE \
        -I$NS3_CONTRIB_AI \
        -I$NS3_CONTRIB_AI/gym-interface \
        -I$NS3_CONTRIB_AI/msg-interface \
        -I$NS3_SRC/src/core/model \
        -I$NS3_SRC/src/network/model \
        -I$NS3_SRC/src/internet/model \
        -I$NS3_SRC/build/include \
        /workspace/msg_py_binding_docker.cc \
        -L$NS3_HOME/build/lib \
        -lns3.48-ai-default \
        -o /opt/ns3-ai-gym-interface/py/ns3ai_gym_msg_py/ns3ai_gym_msg_py.so 2>&1 | tail -20
    
    # Install Python package
    cd /opt/ns3-ai-gym-interface/py
    pip3 install --no-cache-dir --break-system-packages . 2>&1 | tail -5
    echo "ns3-ai gym interface installed"
fi

echo ""
echo "Available commands:"
echo "  ./docker-entrypoint.sh bash     # Interactive shell"
echo "  ./docker-entrypoint.sh ns3      # Run NS-3"
echo "  ./docker-entrypoint.sh python   # Python REPL"
echo ""

exec "$@"
```