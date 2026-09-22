# Hybrid Cloud Strategy (Local-First + Free Tier)

## Philosophy

**Local-First**: Privacy, reproducibility, zero latency for NS-3 (Unix sockets), no API costs.
**Cloud Free Tier**: Supplement for speed, reasoning quality, source-grounded research.

## Service Mapping

| Task | Local | Cloud Free | Why |
|------|-------|------------|-----|
| NS-3 Simulation | ✅ Host | ❌ | Unix IPC, 10-100x latency if remote |
| Embeddings | ✅ nomic-embed-text (274MB) | ❌ | Free, private, fast |
| Fast Coding | ✅ qwen2.5-coder:7b (~11s) | Groq llama-3.1-8b (~0.5s) | Groq 840 tok/s, 0 RAM |
| Complex Reasoning | qwen3:8b think:false (~92s) | **Nemotron 3 Ultra Free** (~2-5s) | **NVIDIA free tier: 1000 req/day** |
| Deep Research | PaperQA2 local | NotebookLM (Gemini) | Source-grounded, 0 hallucination |
| Hypothesis Verification | Local agent | Consensus (15/mo free) | Peer-reviewed consensus meter |
| Writing | Markdown + Pandoc + Zotero | Typora + Zotero | Professional workflow |
| Citation Graph | Local | Research Rabbit (free) | Literature exploration |

## Cloud Free Tier Accounts (Create Once)

| Service | Free Tier | Signup |
|---------|-----------|--------|
| **Groq** | 30 RPM, 14,400 RPD | https://console.groq.com |
| **Nemotron 3 Ultra** | 1,000 req/day | https://build.nvidia.com |
| **NotebookLM** | Unlimited (1M tokens) | https://notebooklm.google.com |
| **Consensus** | 15 analyses/month | https://consensus.app |
| **Perplexity** | 5 Pro/day | https://perplexity.ai |
| **Semantic Scholar** | 100 req/5min (no key) | https://api.semanticscholar.org |
| **Colab Free** | T4 GPU, 12h session | https://colab.research.google.com |

## Configuration

Add to `.env` (never commit):
```bash
GROQ_API_KEY=gsk_xxx
NEMOTRON_API_KEY=nvapi_xxx
TAVILY_API_KEY=tvly_xxx
```

## Orchestrator Routing (jarvis_orchestrator_v2.py)

```python
# Supervisor node decides:
if task.type == "coding" and task.urgency == "high":
    route_to("groq", model="llama-3.1-8b-instant")
elif task.type == "reasoning" and task.complexity > 0.7:
    route_to("nemotron", model="nvidia/nemotron-3-ultra")
elif task.type == "research" and task.needs_sources:
    route_to("notebooklm", export_notes=True)
else:
    route_to("local", model="qwen3:8b")
```

## Nemotron 3 Ultra Free Setup

```bash
# Test API
curl -X POST https://integrate.api.nvidia.com/v1/chat/completions \
  -H "Authorization: Bearer $NEMOTRON_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model": "nvidia/nemotron-3-ultra", "messages": [{"role": "user", "content": "Explain ARFIMA-GARCH"}], "max_tokens": 512}'
```

**Rate Limit**: 1000 requests/day, 60 RPM. Use for: complex reasoning, code review, hypothesis generation.

## NotebookLM Pipeline

```bash
# 1. Researcher saves notes to personal-mcp
# 2. Auto-export to NotebookLM format
python scripts/export_to_notebooklm.py --topic "traffic modeling ARFIMA"

# 3. Open NotebookLM, import, generate:
#    - Summary with citations
#    - Audio overview
#    - Mind map
#    - FAQ
```

## Cost Summary

| Component | Monthly Cost |
|-----------|--------------|
| Local (electricity) | ~$5-10 |
| Cloud APIs (free tiers) | $0 |
| **Total** | **~$5-10/month** |

vs. equivalent cloud GPU: $500-2000/month.