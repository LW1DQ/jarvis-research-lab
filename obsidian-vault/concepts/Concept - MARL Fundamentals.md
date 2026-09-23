---
title: "MARL Fundamentals"
date: "{{date:YYYY-MM-DD}}"
tags: [concept, moc, marl, rl]
aliases: ["Multi-Agent RL", "MARL"]
project: "JARVIS Research"
---

# Concept: MARL Fundamentals

## 📖 Definición

**Multi-Agent Reinforcement Learning (MARL)** extiende RL single-agent a múltiples agentes que interactúan en un entorno compartido. Cada agente aprende una política que maximiza su recompensa, considerando las acciones de otros agentes.

## 🔑 Paradigmas Principales

### 1. CTDE (Centralized Training Decentralized Execution)
- **Entrenamiento**: Acceso a información global (state, acciones de todos)
- **Ejecución**: Solo observaciones locales
- **Algoritmos**: QMIX, MAPPO, MADDPG, MAAC

### 2. Fully Decentralized
- Sin coordinación central
- **Algoritmos**: IPPO, IA2C, VDN

### 3. Communication-based
- Agentes intercambian mensajes
- **Algoritmos**: CommNet, ATOC, TarMAC

## 📊 Comparativa Algoritmos

| Algoritmo | Paradigma | Value-based/Policy | Comunicación | Escalabilidad |
|-----------|-----------|-------------------|--------------|---------------|
| QMIX | CTDE | Value | No | Media (monotonicity) |
| MAPPO | CTDE | Policy | No | Alta |
| IPPO | Decentralized | Policy | No | Muy alta |
| MADDPG | CTDE | Actor-Critic | No | Baja-Media |
| CommNet | Communication | Policy | Sí (continua) | Media |
| TarMAC | Communication | Policy | Sí (atención) | Media |

## 🎯 Aplicación: WiFi Scheduling

### Estado (por agente/AP)
- Colas de tráfico por AC (VO, VI, BE, BK)
- Canal occupancy (CCA)
- Vecinos detectados (beacons)
- Historial de colisiones

### Acciones
- TXOP duration
- CWmin/CWmax por AC
- Modulación (MCS)
- Potencia de transmisión

### Recompensa
- Throughput agregado
- Latencia 99th percentile
- Fairness (Jain's index)
- Eficiencia energética

## 📚 Papers Fundamentales

### CTDE Classics
- `[[Paper - QMIX]]` - Rashid et al. 2018
- `[[Paper - MAPPO]]` - Yu et al. 2021
- `[[Paper - MADDPG]]` - Lowe et al. 2017

### MARL para Redes
- `[[Paper - MARL WiFi Scheduling]]` - 
- `[[Paper - Multi-BSS RL]]` - 

### Surveys
- `[[Paper - MARL Survey]]` - Zhang et al. 2021

## 🧪 Experimentos JARVIS Relacionados

- `[[Experiment - MARL WiFi Dense]]` - 
- `[[Experiment - QMIX vs IPPO]]` - 

## 🔗 Conexiones

### Sub-conceptos
- `[[Concept - CTDE]]`
- `[[Concept - Value Factorization]]`
- `[[Concept - Policy Gradient MARL]]`

### Conceptos padre
- `[[Concept - Reinforcement Learning]]`

### Conceptos relacionados
- `[[Concept - 802.11ax/be]]`
- `[[Concept - Dense Networks]]`
- `[[Concept - ns3-ai Scenarios]]` (multi-agent, multi-bss)

## ❓ Preguntas Abiertas

1. **Escalabilidad**: ¿Hasta cuántos agentes maneja QMIX en WiFi denso?
2. **Partial Observability**: ¿Cómo afecta la observabilidad parcial en 802.11?
3. **Non-stationarity**: ¿Mitigación efectiva en entornos WiFi reales?
4. **Transfer Learning**: ¿Pre-entrenamiento en sim → deploy real?

## 🏷️ Tags
#concept #moc #marl #rl #wifi #ctde