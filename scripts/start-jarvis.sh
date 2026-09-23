#!/bin/bash
# start-jarvis.sh - JARVIS Research Lab Startup Script
# Versión robusta con verificaciones, logs y nohup
# 2026-09-22

set -euo pipefail

# Configuración
RESEARCH_DIR="$HOME/research-jarvis"
LDR_DIR="$HOME/local-deep-research"
LOG_DIR="$RESEARCH_DIR/logs"
VENV="$RESEARCH_DIR/.venv-science"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $*"
}

success() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] ✅${NC} $*"
}

warn() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] ⚠️${NC} $*"
}

error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] ❌${NC} $*"
}

# 1. Verificar entorno
log "Iniciando JARVIS Research Lab..."

# Verificar virtualenv
if [[ ! -f "$VENV/bin/activate" ]]; then
    error "Virtualenv no encontrado en $VENV"
    error "Ejecuta: ./scripts/setup-venv.sh"
    exit 1
fi

# Configurar Python 3.11 para ns3-ai (compilado con Python 3.11)
export PYTHON311="/home/diego/.local/bin/python3.11"
export PATH="/home/diego/.local/bin:$PATH"

# NS-3 Library path para gym bindings
export NS3_BUILD_DIR="/home/diego/ns-allinone-3.48/ns-3.48/build"
export LD_LIBRARY_PATH="${NS3_BUILD_DIR}/lib:${LD_LIBRARY_PATH:-}"
export PYTHONPATH="${NS3_BUILD_DIR}/contrib/ai/model/gym-interface/py/ns3ai_gym_msg_py:${NS3_BUILD_DIR}/contrib/ai/python_utils:${PYTHONPATH:-}"

# 2. Activar virtualenv
source "$VENV/bin/activate"
success "Virtualenv activado: $(which python)"
log "Python 3.11 disponible para ns3-ai: $PYTHON311"

# 3. Verificar Ollama
log "Verificando Ollama en :11434..."
if ! curl -sf http://127.0.0.1:11434/api/tags >/dev/null; then
    error "Ollama no responde en http://127.0.0.1:11434"
    error "Verifica: systemctl status ollama"
    exit 1
fi
success "Ollama respondiendo"

# Verificar modelos cargados
MODELS=$(curl -s http://127.0.0.1:11434/api/tags | python3 -c "
import sys, json
d = json.load(sys.stdin)
for m in d.get('models', []):
    print(f\"  - {m['name']}: {m['size']/(1024**3):.1f}GB\")
")
log "Modelos disponibles:$MODELS"

# 4. Precargar qwen3:8b (evita timeout cold-start)
log "Precargando qwen3:8b (keep-alive)..."
curl -sf http://127.0.0.1:11434/api/chat \
  -d '{"model":"qwen3:8b","messages":[{"role":"user","content":"ok"}],"stream":false,"options":{"temperature":0,"num_predict":1}}' \
  >/dev/null 2>&1 &
# Esperar a que el modelo termine de cargar (polling /api/ps)
log "Esperando a que qwen3:8b termine de cargar..."
for i in {1..12}; do
    sleep 10
    LOADED=$(curl -sf http://127.0.0.1:11434/api/ps | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d.get('models',[])))")
    if [[ "$LOADED" -gt 0 ]]; then
        success "qwen3:8b cargado y retenido en memoria (OLLAMA_KEEP_ALIVE=-1)"
        break
    fi
    log "Esperando carga del modelo... ($i/12)"
done
if [[ "$LOADED" -eq 0 ]]; then
    warn "qwen3:8b no se detectó cargado tras 120s, continuando..."
fi

# 5. LDR (Docker compose)
log "Iniciando Local Deep Research (Docker)..."
cd "$LDR_DIR"
if docker compose up -d; then
    success "LDR iniciado en http://localhost:5000"
else
    warn "LDR tuvo problemas, verificando..."
    docker compose ps
fi

# 6. MCP Servers con logs
log "Iniciando MCP servers..."
mkdir -p "$LOG_DIR"

# Función para iniciar MCP server
start_mcp() {
    local name="$1"
    local script="$2"
    local logfile="$LOG_DIR/${name}.log"
    local python_cmd="python"
    local env_vars=""
    
    # Usar Python 3.11 para ns3-mcp (necesita ns3-ai compilado con Python 3.11)
    if [[ "$name" == "ns3-mcp" ]] && [[ -x "$PYTHON311" ]]; then
        python_cmd="$PYTHON311"
        log "$name usando Python 3.11: $PYTHON311"
        # Configurar entorno para NS-3 gym bindings
        env_vars="LD_LIBRARY_PATH=$NS3_BUILD_DIR/lib:\$LD_LIBRARY_PATH PYTHONPATH=$NS3_BUILD_DIR/contrib/ai/model/gym-interface/py/ns3ai_gym_msg_py:$NS3_BUILD_DIR/contrib/ai/python_utils:\$PYTHONPATH"
    fi
    
    if [[ -f "$script" ]]; then
        if [[ -n "$env_vars" ]]; then
            nohup env $env_vars "$python_cmd" "$script" > "$logfile" 2>&1 &
        else
            nohup "$python_cmd" "$script" > "$logfile" 2>&1 &
        fi
        local pid=$!
        sleep 1
        if kill -0 "$pid" 2>/dev/null; then
            success "$name iniciado (PID: $pid, log: $logfile)"
        else
            error "$name falló al iniciar (ver $logfile)"
        fi
    else
        warn "$name no encontrado: $script"
    fi
}

start_mcp "research-mcp" "$RESEARCH_DIR/mcp/research/server.py"
start_mcp "ns3-mcp" "$RESEARCH_DIR/mcp/ns3/server.py"
start_mcp "personal-mcp" "$RESEARCH_DIR/mcp/personal/server.py"
start_mcp "python-mcp" "$RESEARCH_DIR/mcp/python/server.py"

# 7. Verificar RAM
RAM_PCT=$(free | awk '/Mem/{printf "%.0f", $3/$2*100}')
log "RAM actual: ${RAM_PCT}%"
if [[ $RAM_PCT -gt 85 ]]; then
    warn "RAM alta (${RAM_PCT}%). Considera: docker stop local-deep-research"
fi

# 8. Resumen final
echo
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}  🔬 JARVIS Research Lab - ACTIVO${NC}"
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo -e "  ${BLUE}LDR:${NC}       http://localhost:5000"
echo -e "  ${BLUE}Ollama:${NC}    http://127.0.0.1:11434"
echo -e "  ${BLUE}NS-3:${NC}      ~/ns-3.48/build/"
echo -e "  ${BLUE}Logs:${NC}      $LOG_DIR/"
echo -e "  ${BLUE}RAM:${NC}       ${RAM_PCT}%"
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo
echo "Comandos útiles:"
echo "  Ver logs:      tail -f $LOG_DIR/*.log"
echo "  Ver RAM:       watch -n 5 free -h"
echo "  Parar todo:    ./scripts/stop-jarvis.sh"
echo "  Test PaperQA2: python config/config_paperqa.py"