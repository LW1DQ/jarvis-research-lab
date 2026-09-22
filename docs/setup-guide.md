# Setup Guide - JARVIS Research Lab

## Prerequisites

- Ubuntu Server 26.04 (or 24.04 LTS)
- 16GB+ RAM (swap 16GB recommended)
- CPU-only (no GPU required)
- sudo access
- Internet for initial downloads

## 1. System Preparation

```bash
# Update system
sudo apt update && sudo apt full-upgrade -y

# Base tools
sudo apt install -y git curl wget unzip jq tree htop tmux build-essential \
  pkg-config ca-certificates gnupg lsb-release python3 python3-pip python3-venv

# Docker (Ubuntu repo)
sudo apt install -y docker.io docker-compose
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
# Logout and login again
docker run --rm hello-world  # Verify (no sudo)
```

## 2. Create Workspace

```bash
mkdir -p ~/research-jarvis/{papers,projects,agents,mcp,config,logs,backups,notebooks,datasets,experiments,thesis}
cd ~/research-jarvis

# Clone this repo
git clone https://github.com/LW1DQ/jarvis-research-lab.git .
```

## 3. Environment Configuration

```bash
# Copy template and edit
cp .env.example .env
# Edit .env with your values (API keys, paths, etc.)
chmod 600 .env
```

## 4. Install uv + Python 3.12

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
uv python install 3.12
uv venv --python 3.12 .venv-science
source .venv-science/bin/activate
uv pip install -r config/requirements.txt
```

## 5. Install Ollama + Models

```bash
curl -fsSL https://ollama.com/install.sh | sh
systemctl status ollama --no-pager

# Pull models (adjust for your RAM)
ollama pull nomic-embed-text      # 274MB - embeddings
ollama pull qwen2.5-coder:7b      # 4.7GB - fast coding
ollama pull qwen3:8b              # 5.2GB - reasoning (think:false)
# For 32GB+ RAM: ollama pull qwen3:14b
```

## 6. NS-3.48 + ns3-ai (Host Build)

```bash
# NS-3.48
cd ~
wget https://www.nsnam.org/release/ns-allinone-3.48.tar.bz2
tar xjf ns-allinone-3.48.tar.bz2
cd ns-3.48
./ns3 configure --enable-examples --enable-tests
./ns3 build

# ns3-ai (pinned commit)
cd ~/ns-3.48/contrib
git clone https://github.com/ns3-ai/ns3-ai.git
cd ns3-ai
git checkout b8c9858294b1d6a7f122b5154a3ce25057a54740
cd ~/ns-3.48
./ns3 build
```

## 7. Docker Services

```bash
cd ~/research-jarvis

# LDR + SearXNG + Qdrant + LangFuse
docker compose -f docker/docker-compose.yml up -d

# Verify
docker compose ps
curl http://localhost:5000/health  # LDR
curl http://localhost:6333/health  # Qdrant
```

## 8. Start MCP Servers

```bash
# From research-jarvis root
source .venv-science/bin/activate
./scripts/start-jarvis.sh

# Or manually:
python mcp/research/server.py &
python mcp/ns3/server.py &
python mcp/personal/server.py &
python mcp/python/server.py &
```

## 9. Verify Installation

```bash
# Check all services
curl http://localhost:11434/api/tags     # Ollama
curl http://localhost:5000               # LDR
curl http://localhost:8001/health        # research-mcp
curl http://localhost:8002/health        # ns3-mcp
curl http://localhost:8003/health        # python-mcp
curl http://localhost:8004/health        # personal-mcp

# Test PaperQA2
python config_paperqa.py

# Test orchestrator
python orchestration/jarvis_orchestrator_v2.py --help
```

## 10. Daily Usage

```bash
# Start everything
./scripts/start-jarvis.sh

# Monitor
./scripts/monitor_ram.py
watch -n 5 free -h

# Logs
tail -f logs/*.log

# Stop
./scripts/stop-jarvis.sh
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Ollama not responding | `systemctl restart ollama` |
| OOM kills | Check swap: `free -h`, increase swapfile |
| NS-3 build fails | `rm -rf ~/ns-3.48/build ~/ns-3.48/cmake-cache && ./ns3 build` |
| MCP server port in use | `lsof -ti:8001 | xargs kill -9` |
| PaperQA2 timeout | Increase timeout in `config_paperqa.py` |
| qwen3 empty response | Ensure `think=false` in config, not in options |

## RAM Budget (16GB System)

| Component | RAM |
|-----------|-----|
| Ollama (qwen3:8b) | ~5.5GB |
| LDR + SearXNG (Docker) | 2.5GB limit |
| MCP servers (4x) | ~100MB |
| Qdrant + LangFuse (Docker) | ~1GB |
| System + buffer | ~3GB |
| **Swap (OOM guard)** | **16GB** |
| **Total used** | **~9-10GB** |
| **Margin** | **~6-7GB + swap** |