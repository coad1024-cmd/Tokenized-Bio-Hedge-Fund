"""
Nutrient Dosing Agent
=====================
Manages pH and TDS/EC levels via peristaltic dosing pumps.

Decision flow:
  1. If TDS low  -> Dose A + B (nutrients)
  2. If TDS high -> Skip (dilution happens at next reservoir fill)
  3. If pH high  -> Dose pH Down
  4. If pH low   -> Skip (need manual correction)
"""

from __future__ import annotations

import logging
import time

from bioalpha.agents.base import BaseAgent, AgentAction
from bioalpha.actuators import ActuatorDispatcher
from bioalpha.bridge import SerialBridge
from bioalpha.ledger import Vault
from bioalpha.sensors.simulator import SensorReading
from bioalpha.config import CONFIG

log = logging.getLogger("bioalpha.dosing")


class NutrientDosingAgent(BaseAgent):
    """Worker agent for pH and nutrient management."""

    def __init__(self, vault: Vault, bridge: SerialBridge, dispatcher: ActuatorDispatcher):
        super().__init__("Nutrient Agent", vault, bridge)
        self.dispatcher = dispatcher
        self._last_dose_time: float = 0.0

    def _can_dose(self) -> bool:
        elapsed = time.time() - self._last_dose_time
        return elapsed > CONFIG.dosing_wait_sec

    async def think(self, reading: SensorReading) -> AgentAction:
        policy = CONFIG.policy

        if not self._can_dose():
            remaining = int(CONFIG.dosing_wait_sec - (time.time() - self._last_dose_time))
            return AgentAction(
                agent_name=self.name,
                thought=f"Dosing cooldown active ({remaining}s remaining). Waiting for nutrient stabilization."
            )

        if reading.tds_ppm < policy.tds_min:
            self.dispatcher.dose_nutrient_a(duration_ms=3000)
            self.dispatcher.dose_nutrient_b(duration_ms=3000)
            self._last_dose_time = time.time()
            return AgentAction(
                agent_name=self.name,
                thought=f"TDS ({reading.tds_ppm} ppm) below min ({policy.tds_min} ppm). Dosing Nutrient A+B.",
                tool="dose_nutrient_a+b", params={"duration_ms": 3000}
            )

        if reading.tds_ppm > policy.tds_max:
            return AgentAction(
                agent_name=self.name,
                thought=f"\u26a0\ufe0f TDS ({reading.tds_ppm} ppm) above max ({policy.tds_max} ppm). Dilute at next reservoir fill."
            )

        if reading.ph > policy.ph_max:
            self.dispatcher.dose_ph_down(duration_ms=2000)
            self._last_dose_time = time.time()
            return AgentAction(
                agent_name=self.name,
                thought=f"pH ({reading.ph}) above max ({policy.ph_max}). Dosing pH Down.",
                tool="dose_ph_down", params={"duration_ms": 2000}
            )

        if reading.ph < policy.ph_min:
            return AgentAction(
                agent_name=self.name,
                thought=f"\u26a0\ufe0f pH ({reading.ph}) below min ({policy.ph_min}). Manual pH Up required."
            )

        return AgentAction(
            agent_name=self.name,
            thought=f"Nutrients nominal. TDS={reading.tds_ppm}ppm pH={reading.ph}."
        )
