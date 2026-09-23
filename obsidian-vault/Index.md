---
title: "JARVIS Research Vault Index"
date: "{{date:YYYY-MM-DD}}"
tags: [index, jarvis, thesis]
project: "JARVIS Research"
---

# 🧠 JARVIS Research Vault

> Vault de Obsidian para el proyecto de tesis: **Asistente de investigación para doctorado con simulaciones NS-3 + Deep Learning**

## 🚀 Quick Links

### 📅 Daily Notes
- `[[Daily Note - {{date:YYYY-MM-DD}}]]` - Nota de hoy

### 🏗️ Arquitectura
- `[[ADR Index]]` - Decisiones arquitectónicas
- `[[System Architecture]]` - Visión general del sistema

### 📚 Literatura
- `[[Paper Index]]` - Índice de papers revisados
- `[[Concept Index]]` - Mapa de conceptos (MOCs)

### 🧪 Experimentos
- `[[Experiment Index]]` - Registro de experimentos NS-3
- `[[Experiment Template]]` - Template para nuevos experimentos

### 🤖 Agentes JARVIS
- `[[Agent - Supervisor]]`
- `[[Agent - Researcher]]`
- `[[Agent - Writer]]`
- `[[Agent - NS3 Simulation]]`
- `[[Agent - Critiquer]]`

## 📊 Estado del Proyecto (Día 15)

| Componente | Estado |
|------------|--------|
| Ollama + Modelos | ✅ Operativo (qwen3:8b retenido, qwen2.5-coder:7b default ~11s, **Nemotron 3 Ultra Free ~2-5s cloud**) |
| MCP Servers (4) | ✅ HTTP 8001-8004 (async) |
| LangGraph Orchestrator v2 | ✅ 5 nodos (default: qwen2.5-coder:7b) |
| Mem0 + Qdrant | ✅ Memoria agéntica híbrida (BM25 + vectorial) |
| Writer Agent (Markdown+Pandoc+Zotero) | ✅ |
| Docker NS-3 | ✅ Image built + runtime validado |
| End-to-End Test | ✅ PASS (default model ~11s) |
| Ollama Retention | ✅ `OLLAMA_KEEP_ALIVE=-1` systemd + polling |
| **NS-3 Python Bindings (gym)** | ✅ **FIXED - `ns3ai_gym_msg_py` import working** |
| **MCP Servers (4/4)** | ✅ **All operational via MCP client (8001-8004)** |

## 🗂️ Estructura del Vault

```
jarvis-vault/
├── daily/           # Daily notes
├── papers/          # Paper reviews (linked from Zotero)
├── experiments/     # Experiment logs with manifest.json refs
├── concepts/        # MOCs: MARL, WiFi, TCP-RL, ns3-ai
├── architecture/    # ADRs, system diagrams
├── templates/       # Templates for new notes
└── assets/          # Images, diagrams, exports
```

## 🔧 Plugins recomendados

| Plugin | Propósito |
|--------|-----------|
| **Obsidian Git** | Version control del vault |
| **Dataview** | Queries SQL-like sobre papers/experimentos |
| **Templater** | Templates dinámicos |
| **Zotero Integration** | Sync bidireccional con Zotero |
| **Mermaid** | Diagramas de arquitectura |
| **Canvas** | Diagramas visuales de flujo |

## 📝 Workflow sugerido

1. **Mañana**: Abrir daily note `[[Daily Note - {{date:YYYY-MM-DD}}]]`
2. **Investigación**: Crear `[[Paper Review]]` desde Zotero
3. **Experimentos**: Log en `[[Experiment Log]]` con link a manifest.json
4. **Conceptos**: Actualizar MOCs en `concepts/`
5. **Decisiones**: Documentar ADRs en `architecture/`
6. **Noche**: Commit vault a Git

---

*Vault creado: {{date:YYYY-MM-DD}} | Proyecto: JARVIS Research | Tesis: NS-3 + Deep Learning | Actualizado: 2026-09-17 15:30 (Dockerfile.ns3 multi-stage build EN PROGRESO - build NS-3 completo en container ~40 min transcurridos, CMakeLists.txt en examples/scratch/utils creados, build en progreso paso 10/1399, Nemotron 3 Ultra Free ✅ + Groq Free + NotebookLM cloud options, all MCP servers async, thesis docs updated. Próximo: esperar build NS-3 completo ~20 min restantes)*
*Vault creado: {{date:YYYY-MM-DD}} | Proyecto: JARVIS Research | Tesis: NS-3 + Deep Learning | Actualizado: 2026-09-22 (Dockerfile.ns3 multi-stage build ✅ COMPLETADO + Nemotron 3 Ultra Free ✅ FUNCIONANDO + Groq Free + NotebookLM cloud options)*
*Vault creado: {{date:YYYY-MM-DD}} | Proyecto: JARVIS Research | Tesis: NS-3 + Deep Learning | **Actualizado: 2026-09-23 (NS-3 Python bindings FIXED ✅ - ns3ai_gym_msg_py undefined symbol _ZN3ns34Time10StaticInitEv resuelto con -Wl,--no-as-needed en CMakeLists.txt, Python 3.11 exclusivo para ns3-mcp, todos los 4 MCP servers operativos, gym environment import funcional, end-to-end pipeline listo)***
