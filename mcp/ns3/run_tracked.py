#!/usr/bin/env python3
"""Script wrapper que ejecuta simulaciones NS-3 y genera manifest.json de trazabilidad.

Uso:
    python run_tracked.py <script_path> [seed] [parameters_json]

Ejemplo:
    python run_tracked.py my_experiment.py 42 '{"alfa": 0.8, "nodes": 50}'

El script generará un manifest.json junto a los resultados de la simulacion.
"""

import sys
import os
import json
import hashlib
import subprocess
from datetime import datetime, timezone


def main():
    if len(sys.argv) < 2:
        print("Uso: python run_tracked.py <script_path> [seed] [parameters_json]")
        sys.exit(1)

    script_path = sys.argv[1]
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else None
    parameters = {}

    if len(sys.argv) > 3:
        try:
            parameters = json.loads(sys.argv[3])
        except json.JSONDecodeError:
            print("Warning: Invalid parameters JSON, using empty dict")
            parameters = {}

    # --- Generar manifest.json ---
    script_abs_path = os.path.abspath(script_path)
    script_dir = os.path.dirname(script_abs_path)
    script_basename = os.path.basename(script_abs_path)

    # Hash del script (sha256)
    try:
        with open(script_abs_path, "rb") as f:
            script_hash = hashlib.sha256(f.read()).hexdigest()
    except FileNotFoundError:
        script_hash = "unknown"

    # Git commit del repositorio (si estamos en él)
    git_commit = "unknown"
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True,
            cwd=script_dir
        )
        if result.returncode == 0:
            git_commit = result.stdout.strip()
    except Exception:
        pass

    # Timestamp ISO8601
    timestamp = datetime.now(timezone.utc).isoformat()

    # Manifest
    manifest = {
        "run_id": os.environ.get("RUN_ID", f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
        "timestamp": timestamp,
        "script_path": script_abs_path,
        "script_hash": script_hash,
        "ns3_version": "3.48",
        "ns3_ai_commit": "b8c9858294b1d6a7f122b5154a3ce25057a54740",
        "seed": seed,
        "parameters": parameters,
        "output_files": [],
        "git_commit": git_commit
    }

    manifest_path = os.path.join(script_dir, "manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Manifest generado: {manifest_path}")

    # --- Ejecutar simulacion NS-3 ---
    ns3_bin = "/home/diego/ns-3.48/ns3"
    cmd = [ns3_bin, "run", script_abs_path]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=300,
            cwd="/home/diego/ns-3.48"
        )

        # Actualizar manifest con archivos de salida (si existen)
        # Buscar archivos generados en el directorio del script
        generated_files = []
        if os.path.isdir(script_dir):
            for f in os.listdir(script_dir):
                fpath = os.path.join(script_dir, f)
                if os.path.isfile(fpath):
                    ext = os.path.splitext(f)[1].lower()
                    if ext in [".csv", ".pcap", ".tr", ".xml", ".json"]:
                        generated_files.append(f)

        manifest["output_files"] = generated_files
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        # Mostrar salida
        if result.stdout:
            print("=== STDOUT ===")
            print(result.stdout)
        if result.stderr:
            print("=== STDERR ===")
            print(result.stderr)

        if result.returncode != 0:
            print(f"Simulacion finalizada con codigo de retorno: {result.returncode}")

    except subprocess.TimeoutExpired:
        print("Error: Simulacion excedio el tiempo limite de 300s")
        manifest["output_files"] = []
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        sys.exit(1)
    except Exception as e:
        print(f"Error ejecutando simulacion: {e}")
        manifest["output_files"] = []
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        sys.exit(1)


if __name__ == "__main__":
    main()