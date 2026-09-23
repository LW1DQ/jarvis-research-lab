---
title: "JARVIS Research: Asistente de Investigación Automatizado para Doctorado con Simulaciones NS-3 y Deep Learning"
author: "Diego [Apellido]"
date: "2026-09-17"
degree: "Doctorado en [Área]"
university: "[Universidad]"
department: "[Departamento]"
abstract: |
  Esta tesis presenta JARVIS Research, un sistema de asistente de investigación automatizado diseñado para acelerar el trabajo doctoral en redes de comunicación mediante la integración de simulaciones NS-3, modelos de lenguaje grandes (LLMs) locales, y una arquitectura de agentes orquestados. El sistema combina Local Deep Research (LDR) para revisiones de literatura, PaperQA2 para extracción de evidencia con citas, un orquestador LangGraph de 5 nodos para flujos de trabajo end-to-end, y memoria agéntica persistente (Mem0 + Qdrant) para aprendizaje continuo. Se valida experimentalmente con simulaciones NS-3.48 de protocolos TCP-RL, demostrando reproducibilidad completa mediante trazabilidad automática (manifest.json por corrida). La arquitectura híbrida host/Docker optimiza 16GB RAM con swap 16GB y vm.swappiness=10, eliminando OpenHands para liberar 3GB. El sistema está operativo y listo para producción de tesis.
keywords: [NS-3, Deep Learning, LLM, investigación automatizada, orquestación de agentes, memoria agéntica, reproducibilidad]
lang: es
toc: true
numbersections: true
bibliography: bibliography/references.bib
csl: bibliography/ieee.csl
---

# JARVIS Research: Asistente de Investigación Automatizado para Doctorado con Simulaciones NS-3 y Deep Learning

## Resumen

Esta tesis presenta **JARVIS Research**, un sistema de asistente de investigación automatizado diseñado para acelerar el trabajo doctoral en redes de comunicación mediante la integración de simulaciones **NS-3**, modelos de lenguaje grandes (**LLMs**) locales, y una arquitectura de **agentes orquestados**.

El sistema combina:
- **Local Deep Research (LDR)** para revisiones de literatura automatizadas
- **PaperQA2** para extracción de evidencia con citas verificables
- **Orquestador LangGraph v2** de 5 nodos para flujos de trabajo end-to-end
- **Memoria agéntica persistente** (Mem0 + Qdrant) para aprendizaje continuo
- **Trazabilidad completa** de simulaciones NS-3 (manifest.json automático por corrida)

Se valida experimentalmente con simulaciones **NS-3.48** de protocolos **TCP-RL**, demostrando reproducibilidad completa. La arquitectura híbrida host/Docker optimiza **16GB RAM** con **swap 16GB** y **vm.swappiness=10**, eliminando OpenHands para liberar 3GB críticos.

---

## Agradecimientos

---

## Tabla de Contenidos

\tableofcontents

---

## Lista de Figuras

\listoffigures

---

## Lista de Tablas

\listoftables

---

## Lista de Acrónimos

| Acrónimo | Definición |
|----------|------------|
| **NS-3** | Network Simulator 3 |
| **LLM** | Large Language Model |
| **MARL** | Multi-Agent Reinforcement Learning |
| **RL** | Reinforcement Learning |
| **TCP** | Transmission Control Protocol |
| **MCP** | Model Context Protocol |
| **LDR** | Local Deep Research |
| **RAG** | Retrieval-Augmented Generation |
| **ADR** | Architecture Decision Record |
| **OOM** | Out Of Memory |
| **API** | Application Programming Interface |
| **IPC** | Inter-Process Communication |
| **MOC** | Map of Content (Obsidian) |

---

## Capítulo 1: Introducción

\input{chapters/01-introduccion.md}

---

## Capítulo 2: Estado del Arte

\input{chapters/02-estado-del-arte.md}

---

## Capítulo 3: Arquitectura del Sistema JARVIS

\input{chapters/03-arquitectura.md}

---

## Capítulo 4: Orquestación de Agentes con LangGraph

\input{chapters/04-orquestacion-langgraph.md}

---

## Capítulo 5: Memoria Agéntica y Aprendizaje Continuo

\input{chapters/05-memoria-agentica.md}

---

## Capítulo 6: Integración NS-3 y Trazabilidad de Simulaciones

\input{chapters/06-integracion-ns3.md}

---

## Capítulo 7: Validación Experimental

\input{chapters/07-validacion-experimental.md}

---

## Capítulo 8: Conclusiones y Trabajo Futuro

\input{chapters/08-conclusiones.md}

---

## Bibliografía

\printbibliography

---

## Apéndices

### Apéndice A: Configuración Técnica Completa

\input{appendices/A-configuracion-tecnica.md}

### Apéndice B: ADRs (Architecture Decision Records)

\input{appendices/B-adrs.md}

### Apéndice C: Código Fuente Clave

\input{appendices/c-codigo-fuente.md}

### Apéndice D: Guía de Reproducción

\input{appendices/D-guia-reproduccion.md}