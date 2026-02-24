"""
Lightweight Simulation Engine
=============================
A pure-Python radCAD-compatible engine for Windows development.
Uses the same state/policy/SUF pattern. Can be swapped for radCAD
when running on Linux/RPi where C extensions build cleanly.

API is identical to radCAD:
    Model(initial_state, state_update_blocks, params)
    Simulation(model, timesteps, runs).run() -> list[dict]
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class Model:
    """Defines the system dynamics model."""
    initial_state: Dict[str, Any]
    state_update_blocks: List[Dict]
    params: Dict[str, Any]


@dataclass
class Simulation:
    """Configures and runs a simulation."""
    model: Model
    timesteps: int = 100
    runs: int = 1

    def run(self) -> List[Dict]:
        results = []
        param_sets = self._resolve_params(self.model.params)

        for subset_idx, params in enumerate(param_sets):
            for run in range(1, self.runs + 1):
                state = copy.deepcopy(self.model.initial_state)

                results.append({
                    **state,
                    "simulation": 0,
                    "subset": subset_idx,
                    "run": run,
                    "substep": 0,
                    "timestep": 0,
                })

                for timestep in range(1, self.timesteps + 1):
                    for block_idx, block in enumerate(self.model.state_update_blocks):
                        policy_signals = {}
                        for policy_fn in block.get("policies", {}).values():
                            signals = policy_fn(params, block_idx, [], state)
                            if signals:
                                policy_signals.update(signals)

                        for var_name, update_fn in block.get("variables", {}).items():
                            key, value = update_fn(
                                params, block_idx, [], state, policy_signals
                            )
                            state[key] = value

                    results.append({
                        **state,
                        "simulation": 0,
                        "subset": subset_idx,
                        "run": run,
                        "substep": 0,
                        "timestep": timestep,
                    })

        return results

    @staticmethod
    def _resolve_params(params: Dict) -> List[Dict]:
        max_len = max(
            (len(v) for v in params.values() if isinstance(v, list)),
            default=1,
        )
        param_sets = []
        for i in range(max_len):
            resolved = {}
            for k, v in params.items():
                if isinstance(v, list):
                    resolved[k] = v[min(i, len(v) - 1)]
                else:
                    resolved[k] = v
            param_sets.append(resolved)
        return param_sets


@dataclass
class Experiment:
    """Run multiple simulations in parallel (A/B testing)."""
    simulations: List[Simulation]

    def run(self) -> List[Dict]:
        results = []
        for sim_idx, sim in enumerate(self.simulations):
            sim_results = sim.run()
            for row in sim_results:
                row["simulation"] = sim_idx
            results.extend(sim_results)
        return results
