"""
Environment Agent (Refactored)
==============================
Controls atmospheric and soil conditions via the ActuatorDispatcher.

Decision priority (survival first):
  1. Soil moisture — wilting kills fastest
  2. CO2 — stunts growth if chronically low
  3. VPD — transpiration stress
  4. Temperature — fan control
"""

from __future__ import annotations

import logging
from bioalpha.agents.base import BaseAgent, AgentAction
from bioalpha.actuators import ActuatorDispatcher
from bioalpha.bridge import SerialBridge
from bioalpha.ledger import Vault
from bioalpha.sensors.simulator import SensorReading
from bioalpha.config import CONFIG

log = logging.getLogger("bioalpha.environment")


class EnvironmentAgent(BaseAgent):
    """Worker agent focused on atmospheric and soil control."""

    def __init__(self, vault: Vault, bridge: SerialBridge, dispatcher: ActuatorDispatcher):
        super().__init__("Environment Agent", vault, bridge)
        self.dispatcher = dispatcher

    async def think(self, reading: SensorReading) -> AgentAction:
        policy = CONFIG.policy

        if reading.soil_moisture_pct < policy.soil_moisture_min:
            self.dispatcher.irrigate(duration_ms=5000)
            return AgentAction(
                agent_name=self.name,
                thought=f"CRITICAL: Soil moisture ({reading.soil_moisture_pct}%) below wilting threshold ({policy.soil_moisture_min}%). Irrigating.",
                tool="irrigate", params={"duration_ms": 5000}
            )

        if reading.co2_ppm < policy.co2_min:
            self.dispatcher.co2_burst(duration_ms=30000)
            return AgentAction(
                agent_name=self.name,
                thought=f"CO2 ({reading.co2_ppm} ppm) below policy min ({policy.co2_min} ppm). Injecting CO2.",
                tool="co2_burst", params={"duration_ms": 30000}
            )

        if reading.vpd_kpa > policy.vpd_max:
            self.dispatcher.activate_mister(duration_ms=15000)
            return AgentAction(
                agent_name=self.name,
                thought=f"VPD ({reading.vpd_kpa} kPa) exceeds max ({policy.vpd_max} kPa). Activating mister.",
                tool="activate_mister", params={"duration_ms": 15000}
            )

        if reading.temperature_c > policy.temp_day_max:
            pwm = min(255, int((reading.temperature_c - policy.temp_day_max) * 50))
            self.dispatcher.set_fan_speed(pwm)
            return AgentAction(
                agent_name=self.name,
                thought=f"Temperature ({reading.temperature_c}\u00b0C) exceeds day max ({policy.temp_day_max}\u00b0C). Setting fan to PWM={pwm}.",
                tool="set_fan_speed", params={"pwm_value": pwm}
            )

        return AgentAction(
            agent_name=self.name,
            thought="All atmospheric parameters within policy. No action required."
        )
