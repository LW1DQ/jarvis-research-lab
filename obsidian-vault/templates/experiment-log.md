---
title: "{{title}}"
date: "{{date:YYYY-MM-DD}}"
tags: [experiment, ns3, simulation]
experiment_id: "EXP-{{date:YYYYMMDD}}-{{time:HHmm}}"
scenario: 
status: "planned"  # planned, running, completed, failed, analyzing
project: "JARVIS Research"
---

# Experiment Log: {{title}}

## 📋 Metadata
- **Experiment ID**: `{{experiment_id}}`
- **Fecha**: {{date:YYYY-MM-DD}}
- **Scenario NS-3**: 
- **Commit ns3-ai**: `b8c9858`
- **Estado**: {{status}}

## 🎯 Objetivo


## ⚙️ Configuración
### Parámetros NS-3
```json
{
  "scenario": "",
  "duration": "",
  "nodes": ,
  "seed": ,
  "runId": 
}
```

### Parámetros RL (si aplica)
```json
{
  "algorithm": "",
  "policy": "",
  "timesteps": ,
  "lr": 
}
```

## 📊 Resultados
### Métricas principales
| Métrica | Valor | Unidad | Baseline |
|---------|-------|--------|----------|
| Throughput |  | Mbps |  |
| Latency |  | ms |  |
| Packet Loss |  | % |  |
| Reward (RL) |  |  |  |

### Archivos generados
- `manifest.json`: 
- `trace.pcap`: 
- `rewards.csv`: 
- Logs: 

## 📈 Análisis


## 🔄 Comparación con experimentos previos
- vs `[[Experiment - ...]]`: 

## ⚠️ Issues / Lecciones aprendidas


## 🔗 Enlaces
- Manifest: `file:///home/diego/research-jarvis/experiments/{{experiment_id}}/manifest.json`
- Código: 
- Paper relacionado: `[[Paper - ...]]`

## 🏷️ Tags
#experiment #ns3 #{{scenario:lower}} #status:{{status}}