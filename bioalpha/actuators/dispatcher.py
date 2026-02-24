"""
Actuator Dispatcher
===================
Translates agent decisions into hardware commands.

In SIMULATOR mode: logs the command + debits $ALPHA.
In HARDWARE mode: sends JSON to Arduino over serial + debits $ALPHA.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from bioalpha.config import RunMode, FundConfig
from bioalpha.ledger import Vault

log = logging.getLogger("bioalpha.actuators")


class ActuatorDispatcher:
    """Central command router for all actuators."""

    def __init__(self, config: FundConfig, vault: Vault, serial_port=None):
        self._config = config
        self._vault = vault
        self._serial = serial_port
        self._last_actions: Dict[str, str] = {}

    def co2_burst(self, duration_ms: int = 30_000) -> str:
        cost = self._config.co2_cost_per_burst
        if not self._check_balance(cost, "CO2 burst"):
            return "REJECTED: insufficient $ALPHA"
        self._send_command("co2_burst", dur=duration_ms)
        self._vault.log_actuator("co2_solenoid", f"BURST {duration_ms}ms", duration_ms, cost)
        log.info(f"CO2 burst: {duration_ms}ms (${cost} ALPHA)")
        return f"CO2 injected for {duration_ms}ms"

    def dose_nutrient_a(self, duration_ms: int = 3_000) -> str:
        return self._dose("dose_a", "Nutrient A", duration_ms)

    def dose_nutrient_b(self, duration_ms: int = 3_000) -> str:
        return self._dose("dose_b", "Nutrient B", duration_ms)

    def dose_ph_down(self, duration_ms: int = 2_000) -> str:
        return self._dose("dose_ph", "pH Down", duration_ms)

    def _dose(self, cmd: str, label: str, duration_ms: int) -> str:
        cost = self._config.nutrient_cost_per_dose
        if not self._check_balance(cost, f"{label} dose"):
            return "REJECTED: insufficient $ALPHA"
        self._send_command(cmd, dur=duration_ms)
        self._vault.log_actuator(f"dosing_{cmd}", f"{label} {duration_ms}ms", duration_ms, cost)
        log.info(f"Dosed {label}: {duration_ms}ms (${cost} ALPHA)")
        return f"{label} dosed for {duration_ms}ms"

    def irrigate(self, duration_ms: int = 5_000) -> str:
        cost = int(self._config.pump_cost_per_sec * (duration_ms / 1000))
        if not self._check_balance(cost, "irrigation"):
            return "REJECTED: insufficient $ALPHA"
        self._send_command("pump_on", dur=duration_ms)
        self._vault.log_actuator("water_pump", f"ON {duration_ms}ms", duration_ms, cost)
        log.info(f"Irrigation: {duration_ms}ms (${cost} ALPHA)")
        return f"Irrigated for {duration_ms}ms"

    def set_fan_speed(self, pwm_value: int = 128) -> str:
        pwm_value = max(0, min(255, pwm_value))
        self._send_command("fan_pwm", val=pwm_value)
        status = "OFF" if pwm_value == 0 else f"PWM={pwm_value}/255 ({pwm_value*100//255}%)"
        self._vault.log_actuator("exhaust_fan", status)
        log.info(f"Fan: {status}")
        return f"Fan set to {status}"

    def set_light_intensity(self, dac_value: int = 4095) -> str:
        dac_value = max(0, min(4095, dac_value))
        self._send_command("light_dim", val=dac_value)
        pct = dac_value * 100 // 4095
        self._vault.log_actuator("led_light", f"DAC={dac_value} ({pct}%)")
        log.info(f"Light: {pct}% (DAC={dac_value})")
        return f"Light set to {pct}%"

    def activate_mister(self, duration_ms: int = 10_000) -> str:
        cost = 5
        if not self._check_balance(cost, "mister"):
            return "REJECTED: insufficient $ALPHA"
        self._send_command("mister_on", dur=duration_ms)
        self._vault.log_actuator("mister", f"ON {duration_ms}ms", duration_ms, cost)
        log.info(f"Mister: {duration_ms}ms (${cost} ALPHA)")
        return f"Mister activated for {duration_ms}ms"

    def set_air_pump(self, state: bool = True) -> str:
        val = 1 if state else 0
        self._send_command("air_pump", state=val)
        self._vault.log_actuator("air_pump", "ON" if state else "OFF")
        log.info(f"Air pump: {'ON' if state else 'OFF'}")
        return f"Air pump {'ON' if state else 'OFF'}"

    def _check_balance(self, cost: int, action: str) -> bool:
        if self._vault.balance < cost:
            log.warning(f"REJECTED {action}: need ${cost}, have ${self._vault.balance}")
            return False
        return True

    def _send_command(self, cmd: str, **kwargs):
        payload = {"cmd": cmd, **kwargs}
        if self._config.run_mode == RunMode.SIMULATOR:
            log.debug(f"[SIM] Would send: {json.dumps(payload)}")
            self._last_actions[cmd] = datetime.now().isoformat()
        elif self._serial and self._serial.is_open:
            self._serial.write((json.dumps(payload) + "\n").encode())
            log.info(f"[HW] Sent: {json.dumps(payload)}")
        else:
            log.error(f"Cannot send command: {payload}")

    @property
    def last_actions(self) -> Dict[str, str]:
        return self._last_actions.copy()
