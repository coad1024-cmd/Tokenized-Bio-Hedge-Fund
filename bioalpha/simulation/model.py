"""
Bio-Alpha radCAD Simulation Model
==================================
L4: Strategy Optimizer Layer

Uses radCAD to run Monte Carlo simulations of the entire grow cycle,
enabling parameter sweeps and strategy optimization BEFORE risking
the real plant or $ALPHA.

Run:  python -m bioalpha.simulation.model
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any

import pandas as pd

# Use local engine (radCAD-compatible, pure Python, no C extensions)
# Swap to: from radcad import Model, Simulation, Experiment
# when running on Linux/RPi where radcad installs cleanly.
from bioalpha.simulation.engine import Model, Simulation, Experiment


# ===================================================================
#  PARAMETERS — Sweepable configuration for A/B testing
# ===================================================================

params = {
    # Biological Policy — sweep these to find optimal ranges
    "co2_target":           [1200],
    "co2_min":              [800],
    "temp_day_min":         [21.0],
    "temp_day_max":         [27.0],
    "humidity_min":         [40.0],
    "humidity_max":         [70.0],
    "vpd_max":              [1.2],
    "ph_min":               [5.8],
    "ph_max":               [6.5],
    "tds_target":           [1000],
    "tds_min":              [800],
    "tds_max":              [1400],
    "soil_moisture_min":    [40.0],
    "soil_moisture_max":    [70.0],

    # Light schedule (hours)
    "light_on_hour":        [6],
    "light_off_hour":       [22],

    # Economics ($ALPHA costs)
    "co2_cost":             [20],
    "pump_cost_per_sec":    [5],
    "nutrient_cost":        [15],
    "fan_cost_per_hour":    [10],
    "light_cost_per_hour":  [50],
    "mister_cost":          [5],

    # Simulation settings — 1 timestep = 1 hour
    "poll_interval_hours":  [1.0],
}


# ===================================================================
#  INITIAL STATE — The system at timestep 0
# ===================================================================

initial_state = {
    # Environmental state
    "temperature_c":        24.0,
    "humidity_pct":         55.0,
    "vpd_kpa":              1.0,
    "co2_ppm":              800,
    "soil_moisture_pct":    60.0,
    "ph":                   6.2,
    "tds_ppm":              1000,
    "light_is_on":          True,

    # Economic state
    "alpha_balance":        100_000,
    "total_opex":           0,
    "total_yield":          0,

    # Plant growth (simplified biomass model)
    "biomass_grams":        1.0,    # Starting seedling
    "growth_rate":          0.0,    # grams/hour
    "health_score":         100.0,  # 0-100

    # Actuator counters
    "co2_bursts":           0,
    "irrigation_events":    0,
    "mister_events":        0,
    "dosing_events":        0,

    # Simulation metadata
    "hour_of_day":          6.0,    # Start at 6 AM
    "day":                  0,
}


# ===================================================================
#  POLICY FUNCTIONS — Agent decision logic
# ===================================================================

def p_environment(params, substep, state_history, previous_state):
    """Environment Agent: decides what actuators to fire."""
    actions = {
        "fire_co2": False,
        "fire_mister": False,
        "fire_pump": False,
        "fan_pwm": 0,
    }
    if previous_state["co2_ppm"] < params["co2_min"]:
        actions["fire_co2"] = True
    if previous_state["vpd_kpa"] > params["vpd_max"]:
        actions["fire_mister"] = True
    if previous_state["soil_moisture_pct"] < params["soil_moisture_min"]:
        actions["fire_pump"] = True
    if previous_state["temperature_c"] > params["temp_day_max"]:
        excess = previous_state["temperature_c"] - params["temp_day_max"]
        actions["fan_pwm"] = min(255, int(excess * 50))
    return actions


def p_nutrients(params, substep, state_history, previous_state):
    """Nutrient Agent: manages pH and TDS."""
    actions = {"dose_nutrients": False, "dose_ph_down": False}
    if previous_state["tds_ppm"] < params["tds_min"]:
        actions["dose_nutrients"] = True
    if previous_state["ph"] > params["ph_max"]:
        actions["dose_ph_down"] = True
    return actions


def p_growth(params, substep, state_history, previous_state):
    """Growth Oracle: calculates biomass production rate."""
    temp = previous_state["temperature_c"]
    co2 = previous_state["co2_ppm"]
    vpd = previous_state["vpd_kpa"]
    light = previous_state["light_is_on"]
    health = previous_state["health_score"]

    if not light:
        base_rate = 0.01
    else:
        temp_factor = max(0, 1.0 - ((temp - 25.0) / 10.0) ** 2)
        co2_factor = min(1.0, co2 / 1200)
        vpd_factor = max(0, 1.0 - max(0, (vpd - 1.0) / 0.5))
        health_factor = health / 100.0
        base_rate = 0.15 * temp_factor * co2_factor * vpd_factor * health_factor

    return {"growth_rate": base_rate}


# ===================================================================
#  STATE UPDATE FUNCTIONS — How the world changes
# ===================================================================

def s_advance_time(params, substep, state_history, previous_state, policy_input):
    dt = params["poll_interval_hours"]
    new_hour = (previous_state["hour_of_day"] + dt) % 24
    return ("hour_of_day", new_hour)


def s_update_day(params, substep, state_history, previous_state, policy_input):
    dt = params["poll_interval_hours"]
    new_hour = (previous_state["hour_of_day"] + dt) % 24
    new_day = previous_state["day"] + (1 if new_hour < previous_state["hour_of_day"] else 0)
    return ("day", new_day)


def s_update_light(params, substep, state_history, previous_state, policy_input):
    hour = previous_state["hour_of_day"]
    is_on = params["light_on_hour"] <= hour < params["light_off_hour"]
    return ("light_is_on", is_on)


def s_update_temperature(params, substep, state_history, previous_state, policy_input):
    hour = previous_state["hour_of_day"]
    diurnal = 3.0 * math.sin(math.pi * (hour - 8) / 12)
    led_heat = 2.5 if previous_state["light_is_on"] else 0
    fan_cooling = policy_input.get("fan_pwm", 0) / 255 * 3.0
    noise = random.gauss(0, 0.3)
    new_temp = round(24.0 + diurnal + led_heat - fan_cooling + noise, 1)
    return ("temperature_c", new_temp)


def s_update_humidity(params, substep, state_history, previous_state, policy_input):
    temp = previous_state["temperature_c"]
    base_hum = 80 - (temp - 20) * 2.5
    mister_boost = 8.0 if policy_input.get("fire_mister", False) else 0
    noise = random.gauss(0, 2)
    new_hum = round(max(30, min(95, base_hum + mister_boost + noise)), 1)
    return ("humidity_pct", new_hum)


def s_update_vpd(params, substep, state_history, previous_state, policy_input):
    temp = previous_state["temperature_c"]
    hum = previous_state["humidity_pct"]
    svp = 0.6108 * math.exp(17.27 * temp / (temp + 237.3))
    avp = svp * (hum / 100)
    vpd = round(svp - avp, 2)
    return ("vpd_kpa", vpd)


def s_update_co2(params, substep, state_history, previous_state, policy_input):
    light = previous_state["light_is_on"]
    base_co2 = 600 if light else 900
    burst_boost = 300 if policy_input.get("fire_co2", False) else 0
    noise = random.randint(-20, 20)
    new_co2 = max(400, min(2000, base_co2 + burst_boost + noise))
    return ("co2_ppm", new_co2)


def s_update_soil(params, substep, state_history, previous_state, policy_input):
    decay = 1.5  # % per hour
    irrigation = 25.0 if policy_input.get("fire_pump", False) else 0
    noise = random.gauss(0, 0.5)
    new_soil = round(max(10, min(100,
        previous_state["soil_moisture_pct"] - decay + irrigation + noise
    )), 1)
    return ("soil_moisture_pct", new_soil)


def s_update_ph(params, substep, state_history, previous_state, policy_input):
    drift = 0.01  # pH creep per hour
    correction = -0.3 if policy_input.get("dose_ph_down", False) else 0
    noise = random.gauss(0, 0.02)
    new_ph = round(max(4.0, min(9.0,
        previous_state["ph"] + drift + correction + noise
    )), 2)
    return ("ph", new_ph)


def s_update_tds(params, substep, state_history, previous_state, policy_input):
    plant_uptake = -5  # ppm per hour
    dosing_boost = 150 if policy_input.get("dose_nutrients", False) else 0
    noise = random.randint(-5, 5)
    new_tds = max(0, min(3000,
        int(previous_state["tds_ppm"] + plant_uptake + dosing_boost + noise)
    ))
    return ("tds_ppm", new_tds)


def s_update_biomass(params, substep, state_history, previous_state, policy_input):
    dt = params["poll_interval_hours"]
    rate = policy_input.get("growth_rate", 0)
    new_biomass = round(previous_state["biomass_grams"] + rate * dt, 3)
    return ("biomass_grams", new_biomass)


def s_update_growth_rate(params, substep, state_history, previous_state, policy_input):
    return ("growth_rate", policy_input.get("growth_rate", 0))


def s_update_health(params, substep, state_history, previous_state, policy_input):
    health = previous_state["health_score"]
    penalties = 0
    if previous_state["temperature_c"] > params["temp_day_max"] + 3:
        penalties += 0.5
    if previous_state["temperature_c"] < params["temp_day_min"] - 3:
        penalties += 0.5
    if previous_state["soil_moisture_pct"] < 25:
        penalties += 1.0
    if previous_state["ph"] < 5.0 or previous_state["ph"] > 7.5:
        penalties += 0.3
    recovery = 0.1 if penalties == 0 else 0
    new_health = round(max(0, min(100, health - penalties + recovery)), 1)
    return ("health_score", new_health)


def s_update_economics(params, substep, state_history, previous_state, policy_input):
    cost = 0
    if policy_input.get("fire_co2", False):
        cost += params["co2_cost"]
    if policy_input.get("fire_mister", False):
        cost += params["mister_cost"]
    if policy_input.get("fire_pump", False):
        cost += params["pump_cost_per_sec"] * 5
    if policy_input.get("dose_nutrients", False):
        cost += params["nutrient_cost"] * 2
    if policy_input.get("dose_ph_down", False):
        cost += params["nutrient_cost"]
    if previous_state["light_is_on"]:
        cost += params["light_cost_per_hour"] * params["poll_interval_hours"]
    new_balance = max(0, int(previous_state["alpha_balance"] - cost))
    return ("alpha_balance", new_balance)


def s_update_opex(params, substep, state_history, previous_state, policy_input):
    cost = max(0, previous_state["alpha_balance"] - s_update_economics(
        params, substep, state_history, previous_state, policy_input
    )[1])
    return ("total_opex", previous_state["total_opex"] + cost)


def s_count_co2(params, substep, state_history, previous_state, policy_input):
    count = previous_state["co2_bursts"] + (1 if policy_input.get("fire_co2", False) else 0)
    return ("co2_bursts", count)


def s_count_irrigation(params, substep, state_history, previous_state, policy_input):
    count = previous_state["irrigation_events"] + (1 if policy_input.get("fire_pump", False) else 0)
    return ("irrigation_events", count)


def s_count_mister(params, substep, state_history, previous_state, policy_input):
    count = previous_state["mister_events"] + (1 if policy_input.get("fire_mister", False) else 0)
    return ("mister_events", count)


def s_count_dosing(params, substep, state_history, previous_state, policy_input):
    count = previous_state["dosing_events"]
    if policy_input.get("dose_nutrients", False):
        count += 1
    if policy_input.get("dose_ph_down", False):
        count += 1
    return ("dosing_events", count)


# ===================================================================
#  STATE UPDATE BLOCKS — Wiring it all together
# ===================================================================

state_update_blocks = [
    {
        "policies": {
            "environment": p_environment,
            "nutrients": p_nutrients,
            "growth": p_growth,
        },
        "variables": {
            "hour_of_day":          s_advance_time,
            "day":                  s_update_day,
            "light_is_on":          s_update_light,
            "temperature_c":        s_update_temperature,
            "humidity_pct":         s_update_humidity,
            "vpd_kpa":              s_update_vpd,
            "co2_ppm":              s_update_co2,
            "soil_moisture_pct":    s_update_soil,
            "ph":                   s_update_ph,
            "tds_ppm":              s_update_tds,
            "biomass_grams":        s_update_biomass,
            "growth_rate":          s_update_growth_rate,
            "health_score":         s_update_health,
            "alpha_balance":        s_update_economics,
            "total_opex":           s_update_opex,
            "co2_bursts":           s_count_co2,
            "irrigation_events":    s_count_irrigation,
            "mister_events":        s_count_mister,
            "dosing_events":        s_count_dosing,
        },
    },
]


# ===================================================================
#  SIMULATION RUNNER
# ===================================================================

def run_simulation(timesteps: int = 168, runs: int = 1, custom_params: dict | None = None) -> pd.DataFrame:
    sim_params = {**params}
    if custom_params:
        sim_params.update(custom_params)
    model = Model(initial_state=initial_state, state_update_blocks=state_update_blocks, params=sim_params)
    simulation = Simulation(model=model, timesteps=timesteps, runs=runs)
    result = simulation.run()
    return pd.DataFrame(result)


def run_parameter_sweep(sweep_params: dict, timesteps: int = 168, runs_per_config: int = 3) -> pd.DataFrame:
    merged = {**params, **sweep_params}
    model = Model(initial_state=initial_state, state_update_blocks=state_update_blocks, params=merged)
    simulation = Simulation(model=model, timesteps=timesteps, runs=runs_per_config)
    result = simulation.run()
    return pd.DataFrame(result)


def run_ab_test(params_a: dict, params_b: dict, timesteps: int = 168, runs: int = 5) -> Tuple[pd.DataFrame, pd.DataFrame]:
    merged_a = {**params, **{k: [v] if not isinstance(v, list) else v for k, v in params_a.items()}}
    merged_b = {**params, **{k: [v] if not isinstance(v, list) else v for k, v in params_b.items()}}
    model_a = Model(initial_state=initial_state, state_update_blocks=state_update_blocks, params=merged_a)
    model_b = Model(initial_state=initial_state, state_update_blocks=state_update_blocks, params=merged_b)
    sim_a = Simulation(model=model_a, timesteps=timesteps, runs=runs)
    sim_b = Simulation(model=model_b, timesteps=timesteps, runs=runs)
    experiment = Experiment([sim_a, sim_b])
    result = experiment.run()
    df = pd.DataFrame(result)
    return df[df["simulation"] == 0], df[df["simulation"] == 1]


# ===================================================================
#  CLI ENTRY POINT
# ===================================================================

if __name__ == "__main__":
    print("\n Bio-Alpha radCAD Simulation")
    print("=" * 50)

    SEVEN_DAYS = 24 * 7  # 168 timesteps
    RUNS = 5
    print(f"Running {SEVEN_DAYS} hourly timesteps x {RUNS} Monte Carlo runs...")

    df = run_simulation(timesteps=SEVEN_DAYS, runs=RUNS)

    final = df[df["timestep"] == df["timestep"].max()]
    print(f"\n{'='*50}")
    print(f"Results after 7 simulated days ({len(final)} runs):")
    print(f"  Avg Biomass:     {final['biomass_grams'].mean():.1f}g")
    print(f"  Avg $ALPHA Left: ${final['alpha_balance'].mean():,.0f}")
    print(f"  Avg Health:      {final['health_score'].mean():.1f}/100")
    print(f"  Avg CO2 Bursts:  {final['co2_bursts'].mean():.0f}")
    print(f"  Avg Irrigations: {final['irrigation_events'].mean():.0f}")
    print(f"  Avg Dosing:      {final['dosing_events'].mean():.0f}")
    print(f"  Avg Day:         {final['day'].mean():.0f}")
    print(f"\n  Min Balance:     ${final['alpha_balance'].min():,}")
    print(f"  Max Balance:     ${final['alpha_balance'].max():,}")
    print(f"  Survival Rate:   {(final['health_score'] > 0).mean() * 100:.0f}%")
