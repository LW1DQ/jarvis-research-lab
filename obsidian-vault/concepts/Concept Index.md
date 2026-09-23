---
title: "Concept Index - MOCs"
date: "{{date:YYYY-MM-DD}}"
tags: [concept, moc, index]
project: "JARVIS Research"
---

# Concept Index - Map of Content (MOCs)

## 🗺️ MOCs Principales

### 🤖 MARL (Multi-Agent Reinforcement Learning)
- `[[Concept - MARL Fundamentals]]` - CTDE, QMIX, MAPPO, IPPO
- `[[Concept - MARL for WiFi]]` - Scheduling, resource allocation
- `[[Concept - MARL Communication]]` - Message passing, attention

### 📡 WiFi / 802.11
- `[[Concept - 802.11ax/be]]` - OFDMA, MU-MIMO, TWT
- `[[Concept - WiFi Scheduling]]` - MU-RTS/CTS, SR, OBSS-PD
- `[[Concept - Dense Networks]]` - BSS coloring, spatial reuse

### 🌐 TCP / Congestion Control
- `[[Concept - TCP Variants]]` - Cubic, BBR, PCC, RL-based
- `[[Concept - RL for CC]]` - State, action, reward design
- `[[Concept - NS-3 TCP Models]]` - TcpSocketBase, congestion ops

### 🧠 NS-3 + AI Integration
- `[[Concept - ns3-ai Architecture]]` - Gym interface, shared memory
- `[[Concept - ns3-ai Scenarios]]` - a-plus-b, rl-tcp, lte-cqi
- `[[Concept - ns3-ai Python Bindings]]` - cppyy, Ns3Env, Ns3AIGym

### 🔬 Reproducibilidad / Experiment Tracking
- `[[Concept - Manifest.json]]` - Schema, seed, params, git commit
- `[[Concept - Experiment Tracking]]` - MLflow, Sacred, custom
- `[[Concept - Statistical Rigor]]` - Confidence intervals, seeds

### 🏗️ System Architecture (JARVIS)
- `[[Concept - LangGraph Orchestrator]]` - 5 nodes, state, edges
- `[[Concept - MCP Servers]]` - research, python, ns3, personal
- `[[Concept - Memory Architecture]]` - Mem0, Qdrant, Episodic
- `[[Concept - LLM Strategy]]` - Local Ollama, think:false, hybrid

## 🔗 Cross-references

```dataview
LIST
FROM "concepts"
WHERE contains(tags, "moc")
SORT file.name
```

## 📝 MOCs a crear

- [ ] `[[Concept - MARL Fundamentals]]`
- [ ] `[[Concept - 802.11ax/be]]`
- [ ] `[[Concept - RL for TCP CC]]`
- [ ] `[[Concept - ns3-ai Architecture]]`
- [ ] `[[Concept - LangGraph Orchestrator]]`
- [ ] `[[Concept - Memory Architecture]]`