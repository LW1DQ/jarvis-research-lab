---
title: "ADR Index"
date: "{{date:YYYY-MM-DD}}"
tags: [adr, index, architecture]
project: "JARVIS Research"
---

# ADR Index - Architecture Decision Records

| ADR | Título | Estado | Fecha | Relacionado |
|-----|--------|--------|-------|-------------|
| ADR-018 | litellm + qwen3: `extra_body={'think': False}` | ✅ Accepted | 2026-09-08 | PaperQA2 config |
| ADR-019 | RAM OOM: Eliminar OpenHands + Swap 16GB | ✅ Accepted | 2026-09-11 | Infrastructure |
| ADR-020 | Swap config: 16GB + vm.swappiness=10 | ✅ Accepted | 2026-09-11 | Infrastructure |
| ADR-021 | Python env: Unificar .venv-science uv + Py3.12 | ✅ Accepted | 2026-09-11 | Infrastructure |
| ADR-022 | PaperQA2 Agent: FakeAgent + LangGraph | ✅ Accepted | 2026-09-08 | Orchestrator |
| ADR-023 | Orquestador: LangGraph (ref Phoenix1454) | ✅ Accepted | 2026-09-09 | Orchestrator |
| ADR-024 | Writer output: Markdown + Pandoc + Zotero | ✅ Accepted | 2026-09-12 | Writer Agent |
| ADR-025 | Memoria agéntica: Mem0 + ChromaDB/Qdrant | ✅ Accepted | 2026-09-11 | Memory |
| ADR-026 | NS-3 Execution: Local → Remote Worker API | ✅ Accepted | 2026-09-10 | NS-3 |
| ADR-027 | LLM Híbrido: Local Ollama + Cloud opcional | ✅ Accepted | 2026-09-10 | LLM Strategy |
| ADR-028 | Vector DB: ChromaDB → Qdrant (Fase 2) | ✅ Accepted | 2026-09-11 | Memory |

## 📋 Próximos ADRs pendientes

- [ ] ADR-029: Obsidian Vault para documentación tesis
- [ ] ADR-030: Docker NS-3 standalone validation
- [ ] ADR-031: Stable Baselines 3 integration para RL training

---

*Ver templates/adr.md para crear nuevos ADRs*