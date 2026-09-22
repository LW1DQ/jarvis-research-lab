#!/usr/bin/env python3
"""
monitor_ram.py - Monitor de RAM con kill automático de procesos no-críticos
Ejecuta como daemon o cron cada 30s
Umbral por defecto: 90% RAM
"""

import psutil
import subprocess
import time
import sys
import signal
import os

THRESHOLD_PCT = 90  # % RAM para activar kill
CHECK_INTERVAL = 30  # segundos

# Procesos NO-críticos a matar primero (orden de prioridad)
NON_CRITICAL = [
    ("docker", "local-deep-research"),  # LDR container
    ("docker", "openhands"),             # OpenHands container
    ("python", "mcp"),                   # MCP servers
    ("python", "local-deep-research"),  # LDR processes
]

CRITICAL_KEYWORDS = [
    "ollama",
    "ns3",
    "systemd",
    "sshd",
    "kernel",
]

def is_critical(proc_info):
    """Verifica si un proceso es crítico (no matar)"""
    try:
        name = proc_info.info['name'].lower()
        cmdline = ' '.join(proc_info.info['cmdline'] or []).lower()
        for kw in CRITICAL_KEYWORDS:
            if kw in name or kw in cmdline:
                return True
    except:
        pass
    return False

def kill_non_critical():
    """Mata procesos no-críticos en orden de prioridad"""
    killed = []
    for keyword, target in NON_CRITICAL:
        try:
            # Buscar procesos que coincidan
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if keyword in proc.info['name'].lower() and target in cmdline:
                        if not is_critical(proc):
                            print(f"⚠️ Matando {proc.info['name']} (PID: {proc.info['pid']}) - {target}")
                            proc.terminate()
                            killed.append(proc.info['pid'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"Error matando {target}: {e}")
    
    # Esperar y forzar kill si necesario
    if killed:
        time.sleep(3)
        for pid in killed:
            try:
                p = psutil.Process(pid)
                if p.is_running():
                    p.kill()
                    print(f"  Forzado kill -9 PID: {pid}")
            except:
                pass
    return len(killed)

def get_ram_usage():
    """Retorna (percent, used_gb, total_gb)"""
    ram = psutil.virtual_memory()
    return ram.percent, ram.used / (1024**3), ram.total / (1024**3)

def monitor_loop():
    """Loop principal de monitoreo"""
    print(f"🔍 Monitor RAM iniciado - Threshold: {THRESHOLD_PCT}% - Check cada {CHECK_INTERVAL}s")
    print(f"  Procesos a proteger: {', '.join(CRITICAL_KEYWORDS)}")
    
    consecutive_high = 0
    
    while True:
        try:
            pct, used, total = get_ram_usage()
            
            if pct >= THRESHOLD_PCT:
                consecutive_high += 1
                print(f"⚠️ RAM al {pct:.1f}% ({used:.1f}GB/{total:.1f}GB) - Alta #{consecutive_high}")
                
                if consecutive_high >= 2:  # 2 checks consecutivos = 60s
                    killed = kill_non_critical()
                    if killed:
                        print(f"  ✅ {killed} procesos no-críticos terminados")
                    consecutive_high = 0
            else:
                consecutive_high = 0
                # Log periódico cada 10 checks (5 min)
                if int(time.time()) % 300 < CHECK_INTERVAL:
                    print(f"✅ RAM OK: {pct:.1f}% ({used:.1f}GB/{total:.1f}GB)")
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            print("\n🛑 Monitor detenido por usuario")
            break
        except Exception as e:
            print(f"Error en monitor: {e}")
            time.sleep(CHECK_INTERVAL)

def signal_handler(sig, frame):
    print("\n🛑 Señal recibida, deteniendo monitor...")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Verificar psutil
    try:
        import psutil
    except ImportError:
        print("❌ psutil no instalado: pip install psutil")
        sys.exit(1)
    
    # Ejecutar loop
    monitor_loop()