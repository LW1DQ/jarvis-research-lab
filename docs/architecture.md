# Architecture Decision Records (ADR)

## ADR-018: litellm + qwen3 Thinking Mode Fix
**Date**: 2026-09-09
**Status**: Accepted
**Context**: PaperQA2 using litellm + Ollama + qwen3:8b returned empty responses.
**Decision**: Use native Ollama client with `think=false` top-level parameter (not in options).
**Consequence**: PaperQA2 config uses `extra_body={'think': False}` + `timeout: 300` for all 4 model slots.

## ADR-019: OOM Mitigation - Remove OpenHands
**Date**: 2026-09-11
**Status**: Accepted
**Context**: 16GB RAM system, OpenHands Docker container consumed ~3GB with root docker.sock access.
**Decision**: Remove OpenHands entirely (`docker stop openhands && docker rm openhands`).
**Consequence**: Freed 3GB RAM, eliminated root socket security risk. Use local MCP + LangGraph instead.

## ADR-020: Swap Configuration
**Date**: 2026-09-11
**Status**: Accepted
**Decision**: 16GB swapfile + `vm.swappiness=10` (kernel prefers RAM, swap as OOM guard).
**Consequence**: Stable operation under memory pressure, no OOM kills.

## ADR-021: Unified Python Environment
**Date**: 2026-09-11
**Status**: Accepted
**Decision**: Single `.venv-science` with `uv venv --python 3.12` + all packages.
**Consequence**: ns3-ai pybind11 bindings compatible, no version conflicts.

## ADR-022: PaperQA2 Agent = FakeAgent
**Date**: 2026-09-12
**Status**: Accepted
**Context**: qwen3:8b fails at complex tool-calling loops in PaperQA2 default agent.
**Decision**: Use `agent_type="FakeAgent"` + LangGraph orchestrator handles multi-step reasoning.
**Consequence**: PaperQA2 extracts evidence only; orchestration moved to LangGraph.

## ADR-023: LangGraph Orchestrator
**Date**: 2026-09-13
**Status**: Accepted
**Decision**: LangGraph v2 with 5 nodes (Supervisor, Researcher, Writer, NS-3, Critiquer).
**Consequence**: Deterministic flow, LLM fallback for decisions, compatible with Ollama local models.

## ADR-024: Writer Output = Markdown + Pandoc + Zotero
**Date**: 2026-09-14
**Status**: Accepted
**Decision**: Writer produces Markdown + YAML frontmatter; Pandoc converts to DOCX/LaTeX; Zotero manages citations.
**Consequence**: Versionable in Git, professional output, citation integrity.

## ADR-025: Agentic Memory = Mem0 + Qdrant
**Date**: 2026-09-14
**Status**: Accepted
**Decision**: Mem0 for episodic memory (learn_from_error, record_insight) + Qdrant vector store (BM25 + semantic).
**Consequence**: Agents learn from past failures, hybrid search outperforms ChromaDB keyword-only.

## ADR-026: NS-3 Execution Model (Phased)
**Date**: 2026-09-15
**Status**: Accepted
**Phase 1 (Local)**: NS-3 on host via Unix sockets (IPC, low latency).
**Phase 2 (Remote)**: Full simulation stack on remote worker with REST API + rsync sync.
**Reason**: SSH-only NS-3 not viable (ns3-ai uses Unix sockets, 10-100x latency).

## ADR-027: Hybrid LLM Strategy
**Date**: 2026-09-16
**Status**: Accepted
**Local**: Embeddings (nomic-embed-text), coding (qwen2.5-coder:7b ~11s), drafting (qwen3:8b think:false ~92s).
**Cloud Free**: Groq (llama-3.1-8b ~0.5s), Nemotron 3 Ultra Free (NVIDIA, 1000 req/day), NotebookLM (source-grounded), Colab Free (T4 GPU).

## ADR-028: Vector DB Phased Migration
**Date**: 2026-09-16
**Status**: Accepted
**Phase 1**: ChromaDB (personal-mcp, <100K vectors).
**Phase 2**: Qdrant + fastembed (Mem0, >500K vectors, pre-filter ANN, BM25 hybrid).

## ADR-029: Thesis Documentation = Obsidian Vault + Git
**Date**: 2026-09-16
**Status**: Accepted
**Decision**: Markdown files in Obsidian vault, tracked by Git, with Dataview/Canvas plugins, Zotero integration.
**Consequence**: Living documentation, queryable, versioned, portable.