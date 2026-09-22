# NS-3 Integration Guide

## Overview

NS-3.48 with ns3-ai (commit `b8c9858`) compiled on host. Gymnasium wrapper enables RL training. Dockerfile.ns3 provides standalone simulation environment.

## Host Installation (Current - Phase 1)

```bash
# NS-3.48
cd ~
wget https://www.nsnam.org/release/ns-allinone-3.48.tar.bz2
tar xjf ns-allinone-3.48.tar.bz2
cd ns-3.48
./ns3 configure --enable-examples --enable-tests
./ns3 build

# ns3-ai (pinned)
cd ~/ns-3.48/contrib
git clone https://github.com/ns3-ai/ns3-ai.git
cd ns3-ai
git checkout b8c9858294b1d6a7f122b5154a3ce25057a54740
cd ~/ns-3.48
./ns3 build
```

## Verification

```bash
# Check NS-3
~/ns-3.48/ns3 run hello-simulator

# Check ns3-ai gym interface
cd ~/research-jarvis
source .venv-science/bin/activate
python -c "
import gymnasium as gym
env = gym.make('ns3ai_gym_env/Ns3-v0', targetName='ns3ai_apb_gym', ns3Path='/home/diego/ns-3.48')
print('NS-3 Gym interface OK')
env.close()
"
```

## run_tracked.py - Reproducible Simulations

**Location**: `mcp/ns3/run_tracked.py`

**Usage**:
```bash
python run_tracked.py \
  --script ~/ns-3.48/scratch/my_simulation.cc \
  --params '{"nNodes": 10, "duration": 100}' \
  --output-dir ~/research-jarvis/experiments/exp_001
```

**Output**: `manifest.json`
```json
{
  "timestamp": "2026-09-17T10:30:00Z",
  "seed": 42,
  "params": {"nNodes": 10, "duration": 100},
  "script_hash": "sha256:...",
  "git_commit": "b8c9858",
  "ns3_version": "3.48",
  "duration_seconds": 45.2,
  "exit_code": 0,
  "output_files": ["flowmonitor.xml", "trace.pcap"]
}
```

## Gymnasium Wrapper

**File**: `orchestration/ns3_gym_wrapper.py`

**Features**:
- `Ns3GymWrapper` - Standard Gymnasium interface
- `Ns3VecEnv` - Vectorized environments for SB3
- Automatic `manifest.json` generation
- Parameter validation and defaults

**Usage with Stable Baselines3**:
```python
from stable_baselines3 import PPO
from orchestration.ns3_gym_wrapper import Ns3VecEnv

env = Ns3VecEnv(n_envs=4, ns3_path="~/ns-3.48", target="ns3ai_apb_gym")
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=10000)
```

## Dockerfile.ns3 (Phase 2 - Remote Worker)

**Status**: Build ✅ OK, Runtime gym interface ⏳ Pending

**Build**:
```bash
cd ~/research-jarvis
docker build -f docker/Dockerfile.ns3 -t ns3-simulation:latest .
```

**Run** (mounts host NS-3 for compilation):
```bash
docker run --rm -it \
  -v ~/ns-3.48:/opt/ns-3.48 \
  -v $(pwd)/experiments:/workspace/experiments \
  ns3-simulation:latest
```

**Known Issue**: pybind11 v2.11.1 in Ubuntu 24.04 has C++ stdlib incompatibilities (strncmp, strdup, assert). Fix: multi-stage build compiles gym interface in Stage 1 (see `docker/Dockerfile.ns3`).

## Phase 2: Remote Worker Architecture

```
Local (Orchestrator)          Remote Worker (32GB+ RAM / GPU)
┌─────────────────────┐       ┌─────────────────────┐
│ LangGraph           │       │ FastAPI Server      │
│ NS3Node             │ HTTPS │ /run-simulation     │
│                     │──────▶│ /build              │
│ HTTP → ns3-mcp      │       │ NS-3 + ns3-ai       │
└─────────────────────┘       │ Gymnasium + SB3     │
                              └─────────────────────┘
         rsync sync ◀─────────────────────▶
```

**Trigger for Phase 2**: >1,000 parallel runs or RL training requiring GPU.

## Key Files

| File | Purpose |
|------|---------|
| `~/ns-3.48/build/` | Compiled NS-3 (gitignored) |
| `~/ns-3.48/contrib/ai/` | ns3-ai source (pinned commit) |
| `mcp/ns3/run_tracked.py` | Reproducible execution + manifest |
| `orchestration/ns3_gym_wrapper.py` | Gymnasium + SB3 interface |
| `docker/Dockerfile.ns3` | Multi-stage standalone image |
| `docker/docker-entrypoint.sh` | Container entrypoint |