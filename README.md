# JARVIS Research Lab

> **Local-first AI research infrastructure for PhD thesis** — NS-3 simulations + Deep Learning + Agentic RAG on Ubuntu Server 26.04 (CPU-only, 16GB RAM).

[![Docker Build](https://github.com/LW1DQ/jarvis-research-lab/actions/workflows/docker-build.yml/badge.svg)](https://github.com/LW1DQ/jarvis-research-lab/actions/workflows/docker-build.yml)
[![Lint](https://github.com/LW1DQ/jarvis-research-lab/actions/workflows/lint.yml/badge.svg)](https://github.com/LW1DQ/jarvis-research-lab/actions/workflows/lint.yml)
[![MCP Test](https://github.com/LW1DQ/jarvis-research-lab/actions/workflows/mcp-test.yml/badge.svg)](https://github.com/LW1DQ/jarvis-research-lab/actions/workflows/mcp-test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    JARVIS Research Lab                          │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Ollama    │  │    MCP      │  │  LangGraph  │             │
│  │  (Local LLMs)│  │  Servers    │  │ Orchestrator│             │
│  │             │  │             │  │             │             │
│  │ qwen3:8b    │  │ research    │  │ Supervisor  │             │
│  │ qwen2.5:7b  │──▶│ ns3         │──▶│ Researcher  │             │
│  │ nomic-embed │  │ python      │  │ Writer      │             │
│  └─────────────┘  │ personal    │  │ NS-3        │             │
│                   └─────────────┘  │ Critiquer   │             │
│                          │         └─────────────┘             │
│                          ▼                                     │
│  ┌─────────────────────────────────────────────┐              │
│  │           Memory & Knowledge                │              │
│  │  Mem0 (Episodic) + Qdrant (Vector/BM25)     │              │
│  │  ChromaDB (Personal) + Obsidian Vault       │              │
│  └─────────────────────────────────────────────┘              │
│                          │                                     │
│         ┌────────────────┼────────────────┐                   │
│         ▼                ▼                ▼                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │   NS-3.48   │  │  PaperQA2   │  │   Docker    │           │
│  │  + ns3-ai   │  │  (RAG)      │  │  Services   │           │
│  │  (Gym/SB3)  │  │             │  │  LDR/SEARX  │           │
│  └─────────────┘  └─────────────┘  │  Qdrant     │           │
│                                     │  LangFuse   │           │
│                                     └─────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

## Key Features

- **🧠 Local LLMs**: Ollama with qwen3:8b (reasoning), qwen2.5-coder:7b (coding), nomic-embed-text (embeddings)
- **🔬 NS-3 Integration**: NS-3.48 + ns3-ai (pinned commit) with Gymnasium wrapper for RL
- **📚 Agentic RAG**: PaperQA2 configured for local models, 4 MCP servers for tools
- **🤖 Multi-Agent Orchestration**: LangGraph v2 with 5 nodes (Supervisor, Researcher, Writer, NS-3, Critiquer)
- **💾 Memory**: Mem0 (episodic) + Qdrant (hybrid BM25+vector) + ChromaDB (personal notes)
- **📝 Reproducibility**: `run_tracked.py` generates `manifest.json` for every NS-3 run
- **☁️ Hybrid Cloud**: Optional free-tier APIs (Groq, Nemotron 3 Ultra, NotebookLM, Consensus)
- **📖 Documentation**: Obsidian vault with Dataview, Canvas, Git, Zotero integration

## Quick Start

```bash
# 1. Clone
git clone https://github.com/LW1DQ/jarvis-research-lab.git
cd jarvis-research-lab

# 2. Setup (see docs/setup-guide.md for full details)
cp .env.example .env
# Edit .env with your API keys

# 3. Install dependencies
uv venv --python 3.12 .venv-science
source .venv-science/bin/activate
uv pip install -r config/requirements.txt

# 4. Start services
./scripts/start-jarvis.sh

# 5. Verify
curl http://localhost:11434/api/tags  # Ollama
curl http://localhost:8001/health     # research-mcp
curl http://localhost:8002/health     # ns3-mcp
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Ollama | 11434 | Local LLM inference |
| LDR + SearXNG | 5000 | Local Deep Research web UI |
| research-mcp | 8001 | Papers, OpenAlex, Crossref, arXiv, knowledge |
| ns3-mcp | 8002 | NS-3 simulation, build, module listing |
| python-mcp | 8003 | Python execution, package management |
| personal-mcp | 8004 | Personal knowledge base (ChromaDB) |
| Qdrant | 6333 | Vector database (Mem0) |
| LangFuse | 3000 | Observability (ClickHouse/Postgres/MinIO) |

## Models (16GB RAM Optimized)

| Model | Size | Use Case | Speed |
|-------|------|----------|-------|
| nomic-embed-text | 274MB | Embeddings | Local |
| qwen2.5-coder:7b | 4.7GB | Fast coding, routing | ~11s |
| qwen3:8b (think:false) | 5.2GB | Reasoning, drafting | ~92s |

**Cloud Fallback** (free tier): Groq llama-3.1-8b (~0.5s), Nemotron 3 Ultra (~2-5s), NotebookLM (source-grounded).

## Documentation

- [Architecture & ADRs](docs/architecture.md) — 12 architectural decisions
- [Setup Guide](docs/setup-guide.md) — Complete installation steps
- [MCP Servers](docs/mcp-servers.md) — 4 servers, 19 tools
- [NS-3 Integration](docs/ns3-integration.md) — Compilation, gym, Docker
- [Hybrid Cloud Strategy](docs/hybrid-cloud.md) — Local-first + free cloud

## Project Structure

```
jarvis-research-lab/
├── .github/workflows/      # CI/CD (Docker, lint, MCP test)
├── config/                 # requirements.txt, .env.example
├── docker/                 # Dockerfile.ns3, compose files
├── docs/                   # Architecture, setup, MCP, NS-3, cloud
├── mcp/                    # 4 FastMCP servers (HTTP 8001-8004)
├── orchestration/          # LangGraph, PaperQA2, Memory, Writer, Gym
├── scripts/                # start/stop/monitor/setup-venv
├── thesis/obsidian-vault/  # Thesis docs (structure only)
├── .gitignore
├── LICENSE (MIT)
├── README.md
└── AGENTS.md               # Agent rules for Open Interpreter
```

## Reproducibility

Every NS-3 simulation via `run_tracked.py` produces `manifest.json`:

```json
{
  "timestamp": "2026-09-17T10:30:00Z",
  "seed": 42,
  "params": {"nNodes": 10, "duration": 100},
  "script_hash": "sha256:...",
  "git_commit": "b8c9858",
  "ns3_version": "3.48",
  "duration_seconds": 45.2,
  "exit_code": 0
}
```

## Status

**Day 13+ Complete** — System operational:
- ✅ End-to-end: Researcher → Writer → NS-3 → Critiquer
- ✅ PaperQA2 functional (think:false + 300s timeout)
- ✅ LangGraph orchestrator v2 (5 nodes)
- ✅ Mem0 + Qdrant (episodic memory)
- ✅ NS-3 Gymnasium wrapper + SB3 compatible
- ⏳ Dockerfile.ns3 runtime gym interface (multi-stage build in progress)

## License

MIT — See [LICENSE](LICENSE)

## Citation

If you use this infrastructure in your research, please cite:

```bibtex
@software{jarvis_research_lab,
  author = {Diego (LW1DQ)},
  title = {JARVIS Research Lab: Local-First AI Infrastructure for NS-3 + Deep Learning Research},
  year = {2026},
  url = {https://github.com/LW1DQ/jarvis-research-lab}
}
```