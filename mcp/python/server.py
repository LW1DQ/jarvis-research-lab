from fastmcp import FastMCP
import subprocess
import json

mcp = FastMCP("python-mcp")

@mcp.tool()
def run_python(code: str) -> str:
    """Ejecuta codigo Python y devuelve resultado"""
    try:
        result = subprocess.run(
            ["/home/diego/research-jarvis/.venv-science/bin/python", "-c", code],
            capture_output=True, text=True, timeout=30
        )
        return result.stdout or result.stderr
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def install_package(package: str) -> str:
    """Instala paquete pip en el entorno"""
    try:
        result = subprocess.run(
            ["/home/diego/research-jarvis/.venv-science/bin/pip", "install", "--break-system-packages", package],
            capture_output=True, text=True, timeout=120
        )
        return result.stdout or result.stderr
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def list_packages() -> str:
    """Lista paquetes instalados"""
    try:
        result = subprocess.run(
            ["/home/diego/research-jarvis/.venv-science/bin/pip", "list", "--break-system-packages"],
            capture_output=True, text=True
        )
        return result.stdout
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8003)
