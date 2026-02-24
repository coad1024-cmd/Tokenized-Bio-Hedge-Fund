"""
Serial Bridge
=============
The data pipeline between Arduino (L1) and the Agent Host (L3).

In SIMULATOR mode: reads from SensorSimulator.
In HARDWARE mode: reads JSON from the Arduino over USB serial.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import TYPE_CHECKING

from bioalpha.config import RunMode, FundConfig
from bioalpha.sensors.simulator import SensorReading, SensorSimulator

if TYPE_CHECKING:
    import serial

log = logging.getLogger("bioalpha.bridge")


class SerialBridge:
    """Unified interface to sensor data — real or simulated."""

    def __init__(self, config: FundConfig):
        self._config = config
        self._simulator: SensorSimulator | None = None
        self._serial: serial.Serial | None = None
        self._last_reading: SensorReading | None = None

        if config.run_mode == RunMode.SIMULATOR:
            log.info("\U0001f9ea Bridge running in SIMULATOR mode")
            self._simulator = SensorSimulator(
                light_on_hour=config.policy.light_on_hour,
                light_off_hour=config.policy.light_off_hour,
            )
        else:
            log.info(f"\U0001f50c Bridge connecting to {config.serial_port} @ {config.serial_baud}")
            self._connect_serial()

    def _connect_serial(self):
        try:
            import serial as pyserial
            self._serial = pyserial.Serial(
                port=self._config.serial_port,
                baudrate=self._config.serial_baud,
                timeout=2.0,
            )
            log.info(f"\u2705 Connected to Arduino on {self._config.serial_port}")
        except Exception as e:
            log.error(f"\u274c Failed to connect to Arduino: {e}")
            log.warning("\u26a0\ufe0f Falling back to SIMULATOR mode")
            self._simulator = SensorSimulator()

    def read(self) -> SensorReading:
        if self._simulator:
            reading = self._simulator.read()
        else:
            reading = self._read_from_serial()
        self._last_reading = reading
        return reading

    def _read_from_serial(self) -> SensorReading:
        try:
            line = self._serial.readline().decode("utf-8").strip()
            if not line:
                log.warning("Empty serial read")
                return self._last_reading or SensorReading()
            data = json.loads(line)
            return SensorReading(
                timestamp=datetime.now().isoformat(timespec="seconds"),
                temperature_c=data.get("temp", 0.0),
                humidity_pct=data.get("hum", 0.0),
                pressure_hpa=data.get("pres", 0.0),
                co2_ppm=data.get("co2", 0),
                soil_moisture_pct=data.get("soil", 0.0),
                ph=data.get("ph", 0.0),
                tds_ppm=data.get("tds", 0),
                light_level=data.get("ldr", 0),
                power_watts=data.get("watts", 0.0),
                energy_kwh=data.get("kwh", 0.0),
                reservoir_ok=data.get("reservoir", True),
                light_is_on=data.get("light_on", False),
            )
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            log.warning(f"Serial parse error: {e}")
            return self._last_reading or SensorReading()

    @property
    def last_reading(self) -> SensorReading | None:
        return self._last_reading

    def close(self):
        if self._serial and self._serial.is_open:
            self._serial.close()
            log.info("Serial connection closed")
