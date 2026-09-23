# Apéndice A: Configuración Técnica Completa

## A.1 Hardware y SO
```yaml
hardware:
  cpu: "AMD Ryzen 7 5700G / Intel i7-11700 (8 cores, 16 threads)"
  ram: "16 GB DDR4-3200"
  gpu: "Ninguna (CPU-only inference)"
  storage: "500 GB NVMe SSD"
  swap: "16 GB (vm.swappiness=10)"

software:
  os: "Ubuntu Server 26.04 LTS"
  kernel: "6.8+"
  docker: "29.8.0"
  ollama: "0.33.3 (systemd)"
  python: "3.12.3 (system) + 3.12.3 (.venv-science uv)"
```

## A.2 Modelos Ollama Instalados
```bash
# Modelos descargados
ollama pull nomic-embed-text      # 274 MB - embeddings
ollama pull qwen2.5-coder:7b      # 4.7 GB - coding/NS-3
ollama pull qwen3:8b              # 5.2 GB - reasoning/drafting

# Configuración systemd (/etc/systemd/system/ollama.service)
Environment="OLLAMA_NUM_PARALLEL=1"
Environment="OLLAMA_KEEP_ALIVE=0"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
```

## A.3 Docker Compose (LDR + SearXNG)
```yaml
# ~/local-deep-research/docker-compose.yml
version: '3.8'
services:
  local-deep-research:
    image: localdeepresearch/local-deep-research:latest
    ports:
      - "5000:5000"
    environment:
      - OLLAMA_HOST=http://host.docker.internal:11434
      - OLLAMA_API_BASE=http://host.docker.internal:11434
    mem_limit: 2g
    deploy:
      resources:
        limits:
          memory: 2G
    extra_hosts:
      - "host.docker.internal:host-gateway"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  searxng:
    image: searxng/searxng:latest
    ports:
      - "8080:8080"
    volumes:
      - ./searxng:/etc/searxng
    mem_limit: 512m
```

## A.4 .venv-science Requirements Completo
```txt
# ~/research-jarvis/requirements.txt
# Core científico
numpy==2.4.6
pandas==3.0.5
scipy==1.17.1
matplotlib==3.11.1

# Documentos
python-docx==1.2.0
pyzotero==1.15.1
jupyter

# Vector DBs
chromadb==1.5.9
sentence-transformers==6.0.1

# MCP
fastmcp==4.0.3
mcp==2.0.0

# PaperQA2
paper-qa==2026.8.12
litellm==1.84.1

# Time series
darts==0.47.0

# Utils
psutil
requests
httpx
openai>=1.0.0

# PyTorch CPU (para sentence-transformers)
torch==2.14.0+cpu --index-url https://download.pytorch.org/whl/cpu
```

## A.5 Configuración PaperQA2 (config_paperqa.py)
```python
# CRÍTICO: Unset ANTES de cualquier import
for var in ['AGENT', 'OPENAI_API_KEY', 'OPENAI_API_BASE', 
            'OPENROUTER_API_KEY', 'OPENAI_ADMIN_KEY', 'OPENAI_ORGANIZATION']:
    os.environ.pop(var, None)

os.environ['OPENAI_API_KEY'] = 'EMPTY'
os.environ['OPENAI_API_BASE'] = 'http://127.0.0.1:11434/v1'
os.environ['OLLAMA_API_BASE'] = 'http://127.0.0.1:11434'

OLLAMA_MODEL_NAME = "ollama/qwen3:8b"
OLLAMA_LEGACY_CONFIG = {
    "name": OLLAMA_MODEL_NAME,
    "model_list": [{
        "model_name": OLLAMA_MODEL_NAME,
        "litellm_params": {
            "model": OLLAMA_MODEL_NAME,
            "temperature": 0.0,
            "api_base": "http://127.0.0.1:11434",
            "extra_body": {"think": False},  # TOP-LEVEL, NO en options
            "timeout": 300,
        }
    }]
}

# Settings para uso
settings = Settings(
    llm=OLLAMA_MODEL_NAME,
    summary_llm=OLLAMA_MODEL_NAME,
    agent_llm=OLLAMA_MODEL_NAME,
    enrichment_llm=OLLAMA_MODEL_NAME,
    agent_type="FakeAgent",
    multimodal=0,
    embedding="ollama/nomic-embed-text",
    **OLLAMA_LEGACY_CONFIG
)
```

## A.6 Variables de Entorno (.env)
```bash
# ~/research-jarvis/config/.env
TZ=America/Argentina/Rio_Gallegos
RESEARCH_ROOT=/home/diego/research-jarvis
OLLAMA_HOST=http://127.0.0.1:11434
KHOJ_PORT=42110
OPENHANDS_PORT=3000

# MCP Servers
RESEARCH_MCP_PORT=8001
NS3_MCP_PORT=8002
PYTHON_MCP_PORT=8003
PERSONAL_MCP_PORT=8004

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333

# LangFuse
LANGFUSE_HOST=localhost
LANGFUSE_PORT=3000
```

## A.7 Swap Configuration
```bash
# Crear swap 16GB
sudo fallocate -l 16G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Persistente
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# vm.swappiness=10 (kernel swapea solo bajo presión)
echo 'vm.swappiness=10' | sudo tee /etc/sysctl.d/99-swap.conf
sudo sysctl -p /etc/sysctl.d/99-swap.conf
```

## A.8 Firewall (UFW)
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow OpenSSH
sudo ufw allow 5000/tcp   # LDR
sudo ufw allow 8001/tcp   # research-mcp
sudo ufw allow 8002/tcp   # ns3-mcp
sudo ufw allow 8003/tcp   # python-mcp
sudo ufw allow 8004/tcp   # personal-mcp
sudo ufw allow 3000/tcp   # LangFuse
sudo ufw allow 6333/tcp   # Qdrant
sudo ufw enable
```

## A.9 Systemd Services (MCP Servers)
```ini
# /etc/systemd/system/research-mcp.service
[Unit]
Description=Research MCP Server
After=network.target

[Service]
Type=simple
User=diego
WorkingDirectory=/home/diego/research-jarvis/mcp/research
Environment="PATH=/home/diego/research-jarvis/.venv-science/bin"
ExecStart=/home/diego/research-jarvis/.venv-science/bin/python server.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## A.10 NS-3.48 Build (CMake)
```bash
# Build NS-3.48 con examples y tests
cd ~/ns-allinone-3.48/ns-3.48
./ns3 configure --enable-examples --enable-tests
./ns3 build

# Verificar módulos
./ns3 list-modules | grep -E "(ai|tcp|wifi|lte|nr)"

# Verificar ns3-ai
ls build/lib/libns3.48-ai-default.so
ls build/include/ns3/ns3-ai-*.h
```