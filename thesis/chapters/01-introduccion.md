# Capítulo 1: Introducción

## 1.1 Motivación

La investigación doctoral en redes de comunicación enfrenta desafíos crecientes:

1. **Volumen de literatura**: Miles de papers nuevos por año en conferencias top (SIGCOMM, NSDI, MobiCom, CoNEXT)
2. **Complejidad experimental**: Simulaciones NS-3 con miles de corridas para validación estadística
3. **Reproducibilidad**: Falta de trazabilidad automática de parámetros, semillas, versiones de código
4. **Ciclo de iteración lento**: Investigación → Simulación → Análisis → Redacción → Revisión

**JARVIS Research** nace para automatizar y acelerar este ciclo, integrando herramientas modernas de IA con el ecosistema NS-3.

## 1.2 Objetivos

### Objetivo General
Diseñar, implementar y validar un asistente de investigación automatizado que integre:
- Búsqueda y síntesis de literatura con citas verificables
- Orquestación de simulaciones NS-3 con trazabilidad completa
- Memoria agéntica para aprendizaje continuo entre experimentos
- Generación de documentos académicos (Markdown → Pandoc → LaTeX/PDF/DOCX)

### Objetivos Específicos
1. **Arquitectura híbrida host/Docker** optimizada para 16GB RAM
2. **Orquestador LangGraph** de 5 nodos (Supervisor, Researcher, Writer, NS-3, Critiquer)
3. **Integración NS-3.48 + ns3-ai** con Python bindings funcionales
4. **Memoria episódica + vectorial** (Mem0 + Qdrant) para aprendizaje de errores
5. **Validación end-to-end** con experimentos TCP-RL reproducibles

## 1.3 Contribuciones

| # | Contribución | Descripción |
|---|--------------|-------------|
| **C1** | Arquitectura híbrida RAM-optimizada | Host (Ollama, MCP, NS-3) + Docker (LDR, SearXNG) con swap 16GB |
| **C2** | Orquestador LangGraph v2 | 5 nodos con fallback determinístico + LLM, timeouts y reintentos |
| **C3** | PaperQA2 config funcional local | `think:false` + `FakeAgent` + native Ollama client para qwen3:8b |
| **C4** | Trazabilidad NS-3 automática | `run_tracked.py` genera `manifest.json` (seed, params, hash, commit) |
| **C5** | Memoria agéntica híbrida | Mem0 (episódica) + Qdrant (vectorial BM25+semántico) + ChromaDB (personal) |
| **C6** | Writer Agent Markdown+Pandoc+Zotero | Salida versionable Git, citas perfectas, export LaTeX/PDF/DOCX |
| **C7** | AutoGen Critiquer multi-agente | 5 dimensiones: Coverage, Evidence, Structure, Clarity, Actionability |

## 1.4 Estructura de la Tesis

- **Capítulo 2**: Estado del arte en investigación automatizada, NS-3, LLMs para ciencia
- **Capítulo 3**: Arquitectura del sistema (host/Docker, componentes, flujos de datos)
- **Capítulo 4**: Orquestación con LangGraph (nodos, edges, state, checkpoints)
- **Capítulo 5**: Memoria agéntica (Mem0, Qdrant, aprendizaje de errores)
- **Capítulo 6**: Integración NS-3 (ns3-ai, gym interface, trazabilidad)
- **Capítulo 7**: Validación experimental (TCP-RL, reproducibilidad, métricas)
- **Capítulo 8**: Conclusiones, limitaciones, trabajo futuro