# Apéndice D: Guía de Reproducción Completa

## D.1 Requisitos Previos

### Hardware Mínimo
- **CPU**: 8 cores (recomendado 16 threads)
- **RAM**: 16 GB (mínimo 12 GB disponibles)
- **Storage**: 100 GB libres (SSD recomendado)
- **GPU**: Opcional (para Fase 2 RL training)

### Software Base
```bash
# Ubuntu 26.04 LTS
sudo apt update && sudo apt upgrade -y

# Herramientas base
sudo apt install -y git curl wget build-essential cmake ninja-build \
    python3 python3-dev python3-venv python3-pip python3-pybind11 \
    libboost-all-dev libssl-dev libsqlite3-dev libxml2-dev \
    libprotobuf-dev protobuf-compiler libgsl-dev libboost-python-dev \
    docker.io docker-compose ufw tmux htop tree jq

# Usuario docker
sudo usermod -aG docker $USER
newgrp docker
```

## D.2 Instalación Paso a Paso

### 1. Ollama + Modelos
```bash
# Instalar Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Configurar systemd para memoria
sudo mkdir -p /etc/systemd/system/ollama.service.d
cat <<EOF | sudo tee /etc/systemd/system/ollama.service.d/override.conf
[Service]
Environment="OLLAMA_NUM_PARALLEL=1"
Environment="OLLAMA_KEEP_ALIVE=0"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
EOF
sudo systemctl daemon-reload
sudo systemctl restart ollama

# Descargar modelos
ollama pull nomic-embed-text      # 274 MB
ollama pull qwen2.5-coder:7b      # 4.7 GB
ollama pull qwen3:8b              # 5.2 GB

# Verificar
ollama list
curl http://127.0.0.1:11434/api/tags
```

### 2. Swap 16GB + vm.swappiness=10
```bash
# Crear swap
sudo fallocate -l 16G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Configurar swappiness
echo 'vm.swappiness=10' | sudo tee /etc/sysctl.d/99-swap.conf
sudo sysctl -p /etc/sysctl.d/99-swap.conf

# Verificar
free -h
cat /proc/sys/vm/swappiness
```

### 3. Docker + LDR + SearXNG
```bash
# Clonar Local Deep Research
cd ~
git clone https://github.com/local-deep-research/local-deep-research.git
cd local-deep-research

# Modificar docker-compose.yml para Ollama host
# Añadir en services.local-deep-research:
#   extra_hosts:
#     - "host.docker.internal:host-gateway"
#   environment:
#     - OLLAMA_HOST=http://host.docker.internal:11434

docker compose up -d

# Verificar
curl http://localhost:5000/health
# Registrar usuario en http://localhost:5000
```

### 4. NS-3.48 + ns3-ai (Commit Fijado)
```bash
# Descargar NS-3.48
cd ~
wget https://www.nsnam.org/releases/ns-allinone-3.48.tar.bz2
tar -xjf ns-allinone-3.48.tar.bz2
cd ns-allinone-3.48/ns-3.48

# Clonar ns3-ai en contrib/
cd contrib
git clone https://github.com/ns3-ai/ns3-ai.git ai
cd ai
git checkout b8c9858294b1d6a7f122b5154a3ce25057a54740  # COMMIT FIJADO

# Backup versión fijada
cd ~
git -C ns-allinone-3.48/ns-3.48/contrib/ai archive b8c9858 > ~/backups/ns3-ai-b8c9858.zip

# Build NS-3.48 con CMake
cd ~/ns-allinone-3.48/ns-3.48
./ns3 configure --enable-examples --enable-tests
./ns3 build

# Verificar
./ns3 run ns3ai_rltcp_gym -- --duration=10 --simSeed=1
ls build/lib/libns3.48-ai-default.so
```

### 5. uv + .venv-science
```bash
# Instalar uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Crear entorno unificado
cd ~/research-jarvis
uv venv --python 3.12 .venv-science
source .venv-science/bin/activate

# Instalar requirements
uv pip install -r requirements.txt

# Verificar
python -c "import ns3ai_utils; print('ns3-ai OK')"
python -c "import gymnasium; print('gym OK')"
python -c "import paperqa; print('paper-qa OK')"
```

### 5. research-jarvis Setup
```bash
# Clonar/crear directorio
cd ~
mkdir -p research-jarvis
cd research-jarvis

# Estructura
mkdir -p papers projects agents mcp config datasets experiments notebooks backups
mkdir -p mcp/research mcp/ns3 mcp/python mcp/personal

# Copiar archivos de configuración
# - config/.env
# - config_paperqa.py
# - requirements.txt
# - jarvis_orchestrator_v2.py
# - memory_agent.py
# - run_tracked.py (en mcp/ns3/)
# - Dockerfile.ns3
# - docker-entrypoint.sh
# - msg_py_binding_docker.cc
```

### 6. MCP Servers (4 servicios)
```bash
# En cada directorio mcp/*/ crear server.py con FastMCP
# research-mcp: puerto 8001 (8 tools)
# ns3-mcp: puerto 8002 (4 tools + run_tracked.py)
# python-mcp: puerto 8003 (3 tools)
# personal-mcp: puerto 8004 (4 tools + ChromaDB)

# Instalar como systemd services
sudo cp mcp/*/service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now research-mcp ns3-mcp python-mcp personal-mcp

# Verificar
curl http://localhost:8001/tools
curl http://localhost:8002/tools
curl http://localhost:8003/tools
curl http://localhost:8004/tools
```

### 7. Qdrant + Mem0
```bash
# Qdrant Docker
docker run -d --name qdrant \
  -p 6333:6333 -p 6334:6334 \
  -v ~/qdrant_data:/qdrant/storage \
  qdrant/qdrant:latest

# Crear colección híbrida
python3 -c "
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, SparseVectorParams, SparseIndexParams

client = QdrantClient(host='localhost', port=6333)
client.create_collection(
    collection_name='jarvis_memory',
    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    sparse_vectors_config={
        'bm25': SparseVectorParams(
            index=SparseIndexParams(on_disk=False, full_scan_threshold=10000)
        )
    }
)
print('Collection jarvis_memory created')
"
```

### 8. LangFuse (Observabilidad)
```bash
# docker-compose.yml para LangFuse
# Incluye: ClickHouse, Postgres, MinIO, LangFuse
cd ~/research-jarvis
docker compose -f langfuse-docker-compose.yml up -d

# Verificar
curl http://localhost:3000/api/public/health
```

### 9. Dockerfile.ns3 Build
```bash
cd ~/research-jarvis

# Copiar ns3-ai gym interface source
cp -r ~/ns-allinone-3.48/ns-3.48/contrib/ai/model/gym-interface ns3-ai-gym-interface-full

# Build imagen
docker build -f Dockerfile.ns3 -t ns3-simulation:latest .

# Verificar
docker images | grep ns3-simulation
```

### 10. Obsidian Vault
```bash
# Crear vault
mkdir -p ~/research-jarvis/obsidian-vault
cd ~/research-jarvis/obsidian-vault

# Estructura
mkdir -p daily papers experiments concepts architecture templates assets

# Copiar templates
# - templates/adr.md
# - templates/experiment-log.md
# - templates/paper-review.md
# - templates/concept-note.md
# - templates/daily-note.md

# Index.md principal
# Ver archivo en repositorio

# Git init
git init
git add .
git commit -m "Initial vault commit"
```

## D.3 Verificación End-to-End

### Test 1: PaperQA2
```bash
cd ~/research-jarvis
source .venv-science/bin/activate
python3 -c "
from paperqa import Settings, ask
settings = Settings(
    llm='ollama/qwen3:8b',
    agent_type='FakeAgent',
    embedding='ollama/nomic-embed-text',
    temperature=0.0,
    timeout=300
)
answer = ask('What is TCP congestion control?', settings=settings)
print(answer.answer[:200])
"
# Debe responder en ~92s sin errores
```

### Test 2: NS-3 + run_tracked.py
```bash
cd ~/research-jarvis/mcp/ns3
python3 run_tracked.py tcp-rl-simulation \
  --args '{"duration": 10, "transport_prot": "TcpRlTimeBased"}' \
  --seed 42 --reps 1

# Verificar manifest.json
cat ~/experiments/experiment_*/manifest.json
```

### Test 3: Orquestador Completo
```bash
cd ~/research-jarvis
source .venv-science/bin/activate
python3 jarvis_orchestrator_v2.py

# Debe ejecutar: Research → Writer → NS-3 → Critiquer
# Tiempo esperado: ~26 minutos
# Outputs en: outputs/20260916_*/
```

## D.4 Comandos de Administración Diaria

```bash
# Ver estado de todo
sudo systemctl status ollama research-mcp ns3-mcp python-mcp personal-mcp
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Logs en vivo
journalctl -u ollama -f
journalctl -u research-mcp -f
docker logs -f local-deep-research-local-deep-research-1

# Reiniciar servicios
sudo systemctl restart ollama research-mcp ns3-mcp python-mcp personal-mcp
docker compose -f ~/local-deep-research/docker-compose.yml restart

# Verificar RAM
free -h
~/research-jarvis/monitor_ram.py

# Backup diario
cd ~/research-jarvis
git add -A && git commit -m "Daily backup $(date +%Y%m%d)"
git push origin main
```

## D.5 Troubleshooting Común

| Problema | Solución |
|----------|----------|
| **Ollama OOM** | `OLLAMA_NUM_PARALLEL=1`, `OLLAMA_KEEP_ALIVE=0` |
| **PaperQA2 response vacía** | `extra_body={'think': False}` TOP-LEVEL, native Ollama client |
| **arXiv timeout** | 60s timeout + 3 retries backoff (10s, 20s, 40s) |
| **ns3-ai gym import fail** | Build NS-3 completo en contenedor (Fase 2) |
| **ChromaDB solo vectorial** | Migrar a Qdrant BM25+vectorial |
| **Python 3.11 vs 3.12** | Recrear `.venv-science` con `uv venv --python 3.12` |
| **AGENT=1 rompe PaperQA2** | `unset AGENT` antes de imports |
| **Docker ns3-simulation build fail** | Verificar `msg_py_binding_docker.cc` incluye `<cassert>` |

## D.6 Referencias de Archivos Clave

| Archivo | Ubicación | Descripción |
|---------|-----------|-------------|
| `config_paperqa.py` | `~/research-jarvis/` | Config PaperQA2 funcional |
| `requirements.txt` | `~/research-jarvis/` | Dependencias Python |
| `jarvis_orchestrator_v2.py` | `~/research-jarvis/` | Orquestador LangGraph 5 nodos |
| `memory_agent.py` | `~/research-jarvis/` | Mem0 + Qdrant + ChromaDB |
| `run_tracked.py` | `~/research-jarvis/mcp/ns3/` | Trazabilidad NS-3 |
| `Dockerfile.ns3` | `~/research-jarvis/` | Imagen NS-3 standalone |
| `docker-entrypoint.sh` | `~/research-jarvis/` | Entrypoint compila gym interface |
| `msg_py_binding_docker.cc` | `~/research-jarvis/` | pybind11 module self-contained |
| `thesis/main.md` | `~/research-jarvis/thesis/` | Documento principal tesis |
| `obsidian-vault/` | `~/research-jarvis/` | Documentación tesis (Obsidian) |