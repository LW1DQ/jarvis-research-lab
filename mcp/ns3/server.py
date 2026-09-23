from fastmcp import FastMCP
import subprocess
import json
import os
import sys

mcp = FastMCP("ns3-mcp")

NS3_HOME = "/home/diego/ns-allinone-3.48/ns-3.48"
NS3_AI_PYTHON = os.path.join(NS3_HOME, "contrib/ai/python_utils")

@mcp.tool()
def run_ns3_simulation(script_path: str) -> str:
    """Ejecuta una simulacion NS-3"""
    try:
        result = subprocess.run(
            [os.path.join(NS3_HOME, "ns3"), "run", script_path],
            capture_output=True, text=True, timeout=300,
            cwd=NS3_HOME
        )
        return result.stdout or result.stderr
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def build_ns3() -> str:
    """Compila NS-3"""
    try:
        result = subprocess.run(
            [os.path.join(NS3_HOME, "ns3"), "build"],
            capture_output=True, text=True, timeout=600,
            cwd=NS3_HOME
        )
        return result.stdout or result.stderr
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def list_ns3_modules() -> str:
    """Lista modulos NS-3 disponibles"""
    try:
        build_dir = os.path.join(NS3_HOME, "build")
        if os.path.exists(build_dir):
            modules = [d for d in os.listdir(build_dir) if os.path.isdir(os.path.join(build_dir, d)) and not d.startswith('.')]
            return f"NS-3 modules ({len(modules)}): " + ", ".join(sorted(modules))
        else:
            return "Build directory not found"
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def ns3_ai_status() -> str:
    """Verifica estado de ns3-ai"""
    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = NS3_AI_PYTHON + ":" + env.get("PYTHONPATH", "")
        result = subprocess.run(
            [sys.executable, "-c", "import ns3ai_utils; print('OK')"],
            capture_output=True, text=True, env=env
        )
        return result.stdout or result.stderr
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    import asyncio
    async def run_server():
        await mcp.run_async(transport="http", host="127.0.0.1", port=8002)
    asyncio.run(run_server())
