# MCP Servers Documentation

## Overview

4 FastMCP servers running as HTTP services on ports 8001-8004. Each provides specialized tools for the JARVIS orchestration layer.

## Servers

### 1. research-mcp (Port 8001)
**File**: `mcp/research/server.py`
**Tools**: 8
- `search_papers(query, limit)` - Search local LDR document library
- `summarize_paper(doc_id)` - Generate summary with citations
- `find_gaps(topic)` - Identify research gaps in literature
- `search_openalex(query, limit)` - OpenAlex API (papers, authors, concepts)
- `search_crossref(query, limit)` - Crossref API (DOI, metadata)
- `search_arxiv(query, limit, max_results)` - arXiv API with 60s timeout + 3 retries
- `search_knowledge(query, limit)` - Query personal knowledge base (ChromaDB)
- `save_research_note(title, content, tags, source)` - Persist to personal-mcp

**Dependencies**: `httpx`, `fastmcp`, `paper-qa`, `chromadb`

### 2. ns3-mcp (Port 8002)
**File**: `mcp/ns3/server.py`
**Tools**: 4
- `run_ns3_simulation(script, params, output_dir)` - Execute NS-3 simulation via `run_tracked.py`
- `build_ns3(target)` - Build NS-3 modules (`./ns3 build`)
- `list_ns3_modules()` - List available NS-3 modules
- `ns3_ai_status()` - Check ns3-ai gym interface availability

**Key Feature**: `run_tracked.py` generates `manifest.json` with:
- Seed, parameters, script hash, git commit
- Timestamp, duration, exit code
- Full reproducibility for 3,600+6,000 runs

**Dependencies**: `fastmcp`, NS-3.48 + ns3-ai (host)

### 3. python-mcp (Port 8003)
**File**: `mcp/python/server.py`
**Tools**: 3
- `run_python(code, packages)` - Execute Python in sandboxed venv
- `install_package(package)` - Install via uv/pip
- `list_packages()` - List installed packages

**Use Case**: Data analysis, plotting, statistical tests, experiment post-processing.

### 4. personal-mcp (Port 8004)
**File**: `mcp/personal/server.py`
**Tools**: 4
- `add_note(title, content, tags)` - Store in ChromaDB (local, ~200MB)
- `search_notes(query, limit)` - Semantic search
- `list_notes(limit)` - List recent notes
- `delete_note(note_id)` - Remove note

**Storage**: ChromaDB at `~/research-jarvis/chroma/personal/`

## Starting Servers

```bash
# Via startup script (recommended)
./scripts/start-jarvis.sh

# Manual
source .venv-science/bin/activate
python mcp/research/server.py --port 8001 &
python mcp/ns3/server.py --port 8002 &
python mcp/python/server.py --port 8003 &
python mcp/personal/server.py --port 8004 &
```

## Health Checks

```bash
curl http://localhost:8001/health  # {"status":"ok","server":"research-mcp"}
curl http://localhost:8002/health  # {"status":"ok","server":"ns3-mcp"}
curl http://localhost:8003/health  # {"status":"ok","server":"python-mcp"}
curl http://localhost:8004/health  # {"status":"ok","server":"personal-mcp"}
```

## Integration with Orchestrator

LangGraph nodes call MCP tools via HTTP:
- `ResearcherNode` → research-mcp (arXiv, OpenAlex, LDR)
- `NS3Node` → ns3-mcp (run_simulation, build)
- `WriterNode` → python-mcp (pandoc, zotero) + personal-mcp (save notes)
- `CritiquerNode` → python-mcp (analysis) + research-mcp (verify claims)