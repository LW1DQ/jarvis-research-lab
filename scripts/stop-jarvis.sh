#!/bin/bash
# stop-jarvis.sh - Detener todos los servicios JARVIS

set -euo pipefail

LOG_DIR="$HOME/research-jarvis/logs"

echo "🛑 Deteniendo JARVIS Research Lab..."

# 1. Matar MCP servers
for pid in $(pgrep -f "mcp/.*/server.py"); do
    kill "$pid" 2>/dev/null && echo "  Matado MCP server (PID: $pid)"
done

# 2. Parar LDR Docker
cd "$HOME/local-deep-research"
docker compose down 2>/dev/null && echo "  LDR detenido" || echo "  LDR ya detenido"

# 3. Verificar
REMAINING=$(pgrep -f "mcp/.*/server.py" | wc -l)
if [[ $REMAINING -eq 0 ]]; then
    echo "✅ Todos los servicios JARVIS detenidos"
else
    echo "⚠️ Quedan $REMAINING procesos MCP"
fi