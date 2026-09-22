#!/usr/bin/env python3
"""
NS-3 Gymnasium Wrapper for Stable Baselines 3 and RLlib
Wrapper around ns3-ai Gymnasium interface with SB3/RLlib compatibility
"""

import os
import sys
import warnings
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path

import gymnasium as gym
import numpy as np
from gymnasium import spaces

# Add ns3-ai to path
NS3_AI_PATH = "/home/diego/ns-allinone-3.48/ns-3.48/contrib/ai/model/gym-interface/py"
if NS3_AI_PATH not in sys.path:
    sys.path.insert(0, NS3_AI_PATH)

from ns3ai_gym_env.envs.ns3_environment import Ns3Env


class NS3GymWrapper(gym.Env):
    """
    Gymnasium wrapper for NS-3 environments compatible with Stable Baselines 3 and RLlib.
    
    This wrapper provides:
    - Standard Gymnasium API compliance
    - Automatic observation/action space handling
    - Support for multiple NS-3 scenarios
    - Compatibility with Stable Baselines 3 and RLlib
    - Proper seeding for reproducibility
    - Parallel environment support via vectorized environments
    """
    
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 30}
    
    def __init__(
        self,
        scenario: str,
        ns3_path: str = "/home/diego/ns-allinone-3.48/ns-3.48",
        ns3_settings: Optional[Dict[str, Any]] = None,
        trial_name: Optional[str] = None,
        shm_size: int = 4096,
        debug: bool = False,
        seed: Optional[int] = None,
    ):
        """
        Initialize NS-3 Gymnasium environment.
        
        Args:
            scenario: Name of the NS-3 scenario (e.g., "a-plus-b", "rl-tcp", "lte-cqi")
            ns3_path: Path to NS-3 installation
            ns3_settings: Additional NS-3 settings dictionary
            trial_name: Unique trial identifier for parallel execution
            shm_size: Shared memory size in KB
            debug: Enable debug output
            seed: Random seed for reproducibility
        """
        super().__init__()
        
        self.scenario = scenario
        self.ns3_path = Path(ns3_path).resolve()
        self.ns3_settings = ns3_settings or {}
        self.trial_name = trial_name or f"{scenario}_trial"
        self.shm_size = shm_size
        self.debug = debug
        self._seed = seed
        
        # Build target path for the scenario
        self.target_path = self._resolve_scenario_path(scenario)
        
        # Initialize the underlying NS3Env
        self._env = Ns3Env(
            targetName=str(self.target_path),
            ns3Path=str(self.ns3_path),
            ns3Settings=self.ns3_settings,
            debug=debug,
            shmSize=shm_size,
            segName="ns3-ai",
            trial_name=self.trial_name,
        )
        
        # Gym spaces are automatically set by Ns3Env
        self.action_space = self._env.action_space
        self.observation_space = self._env.observation_space
        
        # Set seed if provided
        if seed is not None:
            self.seed(seed)
        
        # Episode tracking
        self._episode_count = 0
        self._step_count = 0
        self._episode_reward = 0.0
        
    def _resolve_scenario_path(self, scenario: str) -> Path:
        """Resolve scenario name to actual NS-3 example path."""
        base_path = Path("/home/diego/ns-allinone-3.48/ns-3.48/contrib/ai/examples")
        
        scenario_map = {
            "a-plus-b": "a-plus-b",
            "apb": "a-plus-b",
            "rl-tcp": "rl-tcp",
            "lte-cqi": "lte-cqi",
            "rate-control": "rate-control",
            "multi-agent": "multi-agent",
            "multi-bss": "multi-bss",
            "rate-control": "rate-control",
        }
        
        scenario_dir = scenario_map.get(scenario.lower(), scenario)
        scenario_path = base_path / scenario_dir
        
        if not scenario_path.exists():
            # Try to find in contrib/ai/examples
            alt_path = Path("/home/diego/ns-allinone-3.48/ns-3.48/contrib/ai/examples") / scenario_dir
            if alt_path.exists():
                return alt_path
            # Try to find any matching directory
            for d in base_path.iterdir():
                if d.is_dir() and scenario.lower() in d.name.lower():
                    return d
            raise FileNotFoundError(f"Scenario '{scenario}' not found in {base_path}")
        
        return scenario_path
    
    def reset(
        self, 
        *, 
        seed: Optional[int] = None, 
        options: Optional[Dict[str, Any]] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Reset environment to initial state."""
        if seed is not None:
            self.seed(seed)
        
        obs, info = self._env.reset(seed=seed, options=options)
        
        self._episode_count += 1
        self._step_count = 0
        self._episode_reward = 0.0
        
        return obs, info
    
    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """Execute one step in the environment."""
        obs, reward, terminated, truncated, info = self._env.step(action)
        
        self._step_count += 1
        self._episode_reward += reward
        
        terminated = bool(reward is not None and self._env.gameOver)
        truncated = False  # NS-3 simulations typically don't truncate
        
        info = {
            "episode": self._episode_count,
            "step": self._step_count,
            "episode_reward": self._episode_reward,
        }
        
        return self._convert_obs(obs), float(reward), terminated, truncated, {}
    
    def _convert_obs(self, obs: Any) -> np.ndarray:
        """Convert observation to numpy array if needed."""
        if isinstance(obs, np.ndarray):
            return obs
        elif isinstance(obs, (list, tuple)):
            return np.array(obs, dtype=np.float32)
        return np.array([obs], dtype=np.float32)
    
    def render(self, mode: str = "human") -> Optional[np.ndarray]:
        """Render environment (not supported for NS-3)."""
        if self.debug:
            print(f"Episode: {self._episode_count}, Step: {self._step_count}")
        return None
    
    def close(self) -> None:
        """Close environment and cleanup resources."""
        if hasattr(self, '_env'):
            self._env.close()
    
    def seed(self, seed: Optional[int] = None) -> List[int]:
        """Set random seed for reproducibility."""
        self._seed = seed
        if seed is not None:
            np.random.seed(seed)
            # NS-3 uses runId for random seed variation
            self.ns3_settings["runId"] = seed
        return [seed] if seed is not None else []
    
    def get_state(self) -> Dict[str, Any]:
        """Get environment state for checkpointing."""
        return {
            "episode_count": self._episode_count,
            "step_count": self._step_count,
            "episode_reward": self._episode_reward,
            "ns3_settings": self.ns3_settings,
        }
    
    def set_state(self, state: Dict[str, Any]) -> None:
        """Restore environment state."""
        self._episode_count = state.get("episode_count", 0)
        self._step_count = state.get("step_count", 0)
        self._episode_reward = state.get("episode_reward", 0.0)
        if "ns3_settings" in state:
            self.ns3_settings.update(state["ns3_settings"])
    
    def get_wrapper_attr(self, name: str) -> Any:
        """Get attribute from wrapped environment."""
        return getattr(self._env, name)
    
    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to wrapped environment."""
        return getattr(self._env, name)


def make_ns3_env(
    scenario: str,
    ns3_path: str = "/home/diego/ns-allinone-3.48/ns-3.48",
    ns3_settings: Optional[Dict[str, Any]] = None,
    trial_name: Optional[str] = None,
    shm_size: int = 4096,
    debug: bool = False,
    seed: Optional[int] = None,
) -> NS3GymWrapper:
    """
    Factory function to create NS-3 Gymnasium environment.
    
    Args:
        scenario: Scenario name (e.g., "a-plus-b", "rl-tcp", "lte-cqi")
        ns3_path: Path to NS-3 installation
        ns3_settings: Additional NS-3 settings
        trial_name: Unique trial identifier
        shm_size: Shared memory size in KB
        debug: Enable debug output
        seed: Random seed
        
    Returns:
        NS3GymWrapper instance
    """
    return NS3GymWrapper(
        scenario=scenario,
        ns3_path=ns3_path,
        ns3_settings=ns3_settings,
        trial_name=trial_name,
        shm_size=shm_size,
        debug=debug,
        seed=seed,
    )


# ============================================================
# Multi-Environment Support for Parallel Training
# ============================================================

class VecNS3Env(gym.vector.VectorEnv):
    """
    Vectorized NS-3 environment for parallel training.
    
    Supports both synchronous and asynchronous vectorized environments
    compatible with Stable Baselines 3 and RLlib.
    """
    
    def __init__(
        self,
        scenario: str,
        num_envs: int = 4,
        ns3_path: str = "/home/diego/ns-allinone-3.48/ns-3.48",
        ns3_settings: Optional[Dict[str, Any]] = None,
        shm_size: int = 4096,
        debug: bool = False,
        seed: Optional[int] = None,
    ):
        self.num_envs = num_envs
        self.envs = []
        
        for i in range(num_envs):
            trial_name = f"{scenario}_env_{i}"
            if ns3_settings and "runId" not in ns3_settings:
                ns3_settings = ns3_settings.copy()
                ns3_settings["runId"] = i
            
            env = NS3GymWrapper(
                scenario=scenario,
                ns3_path=ns3_path,
                ns3_settings=ns3_settings,
                trial_name=trial_name,
                shm_size=shm_size,
                debug=debug,
                seed=seed + i if seed is not None else None,
            )
            self.envs.append(env)
        
        # Initialize vector env properties
        self.single_action_space = self.envs[0].action_space
        self.single_observation_space = self.envs[0].observation_space
        self.action_space = spaces.Tuple([self.single_action_space] * num_envs)
        self.observation_space = spaces.Tuple([self.single_observation_space] * num_envs)
        
        super().__init__(num_envs, self.single_observation_space, self.single_action_space)
    
    def reset(self, *, seed=None, options=None):
        seeds = [seed + i for i in range(self.num_envs)] if seed is not None else [None] * self.num_envs
        observations = []
        infos = []
        for i, (env, seed) in enumerate(zip(self.envs, seeds)):
            obs, info = env.reset(seed=seed, options=options)
            observations.append(obs)
            infos.append(info)
        return np.array(observations), infos
    
    def step_async(self, actions):
        self._actions = actions
    
    def step_wait(self):
        observations = []
        rewards = []
        terminated = []
        truncated = []
        infos = []
        
        for i, env in enumerate(self.envs):
            obs, reward, terminated, truncated, info = env.step(self._actions[i])
            observations.append(obs)
            rewards.append(reward)
            terminated.append(terminated)
            truncated.append(truncated)
            infos.append(info)
        
        return (
            np.array(observations),
            np.array(rewards),
            np.array(terminated),
            np.array(truncated),
            infos,
        )
    
    def close_extras(self, **kwargs):
        for env in self.envs:
            env.close()


# ============================================================
# Scenario Registry
# ============================================================

SCENARIO_REGISTRY = {
    "a-plus-b": {
        "description": "Simple A+B example for testing",
        "observation_space": "Box(2, uint32, [0, 10])",
        "action_space": "Discrete(21)",
        "reward_type": "sparse",
    },
    "rl-tcp": {
        "description": "RL-based TCP congestion control",
        "observation_space": "Dict/Box",
        "action_space": "Discrete/Box",
        "reward_type": "dense",
    },
    "lte-cqi": {
        "description": "LTE CQI prediction",
        "observation_space": "Box",
        "action_space": "Discrete",
        "reward_type": "dense",
    },
    "rate-control": {
        "description": "Rate adaptation control",
        "observation_space": "Dict",
        "action_space": "Discrete",
        "reward_type": "dense",
    },
    "multi-agent": {
        "description": "Multi-agent RL scenario",
        "observation_space": "Dict/Tuple",
        "action_space": "Tuple",
        "reward_type": "cooperative",
    },
    "multi-bss": {
        "description": "Multi-BSS WiFi management",
        "observation_space": "Dict",
        "action_space": "Discrete",
        "reward_type": "dense",
    },
}


def get_scenario_info(scenario: str) -> Dict[str, Any]:
    """Get scenario information."""
    return SCENARIO_REGISTRY.get(scenario.lower(), {
        "description": f"Custom scenario: {scenario}",
        "observation_space": "unknown",
        "action_space": "unknown",
        "reward_type": "unknown",
    })


def list_available_scenarios() -> List[str]:
    """List all available NS-3 scenarios."""
    base_path = Path("/home/diego/ns-allinone-3.48/ns-3.48/contrib/ai/examples")
    scenarios = [d.name for d in base_path.iterdir() if d.is_dir()]
    return sorted(scenarios)


# ============================================================
# Stable Baselines 3 Integration Helper
# ============================================================

def make_sb3_env(
    scenario: str,
    n_envs: int = 1,
    seed: int = 42,
    **kwargs
) -> gym.Env:
    """
    Create environment compatible with Stable Baselines 3.
    
    Args:
        scenario: Scenario name
        n_envs: Number of parallel environments
        seed: Random seed
        **kwargs: Additional arguments passed to NS3GymWrapper
        
    Returns:
        Gymnasium environment (single or vectorized)
    """
    if n_envs == 1:
        return make_ns3_env(scenario=scenario, seed=42, **kwargs)
    else:
        return VecNS3Env(
            scenario=scenario,
            num_envs=n_envs,
            seed=seed,
            **kwargs
        )


# ============================================================
# RLlib Integration Helper
# ============================================================

def make_rllib_env(
    scenario: str,
    num_workers: int = 1,
    **kwargs
) -> callable:
    """
    Create environment creator function for RLlib.
    
    Args:
        scenario: Scenario name
        num_workers: Number of RLlib workers
        **kwargs: Additional arguments
        
    Returns:
        Environment creator function for RLlib
    """
    def env_creator(env_config):
        worker_index = env_config.get("worker_index", 0)
        return NS3GymWrapper(
            scenario=scenario,
            trial_name=f"{scenario}_worker_{worker_index}",
            seed=env_config.get("seed", 42) + worker_index,
            **kwargs
        )
    
    return env_creator


# ============================================================
# Example Usage
# ============================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="NS-3 Gymnasium Wrapper")
    parser.add_argument("--scenario", default="a-plus-b", help="Scenario name")
    parser.add_argument("--test", action="store_true", help="Run quick test")
    parser.add_argument("--n-envs", type=int, default=1, help="Number of parallel envs")
    parser.add_argument("--steps", type=int, default=10, help="Number of steps to run")
    
    args = parser.parse_args()
    
    if args.test:
        print("Testing NS-3 Gymnasium Wrapper...")
        
        # Test single environment
        env = make_ns3_env(scenario=args.scenario, seed=42)
        
        obs, info = env.reset(seed=42)
        print(f"Observation space: {env.observation_space}")
        print(f"Action space: {env.action_space}")
        print(f"Initial obs: {env.get_obs()}")
        
        for step in range(args.steps):
            action = env.action_space.sample()
            obs, reward, terminated, truncated, info = env.step(action)
            print(f"Step {step}: reward={reward:.3f}, terminated={terminated}")
            if terminated or truncated:
                break
        
        env.close()
        print("Test completed successfully!")