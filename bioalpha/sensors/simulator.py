"""
Sensor Simulator
================
Generates realistic fake sensor data when no Arduino is connected.
Uses sinusoidal patterns + noise to mimic real-world diurnal cycles.

This allows the ENTIRE software stack to be developed and tested
on a Windows PC before any hardware arrives.
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class SensorReading:
    """A single snapshot of all sensor values from the Arduino.
    This is the universal data format that flows through the entire system."""

    timestamp: str = ""

    # BME280
    temperature_c: float = 0.0
    humidity_pct: float = 0.0
    pressure_hpa: float = 0.0

    # Derived
    vpd_kpa: float = 0.0

    # MH-Z19E
    co2_ppm: int = 0

    # Capacitive Soil Moisture
    soil_moisture_pct: float = 0.0

    # pH Sensor
    ph: float = 0.0

    # TDS/EC Sensor
    tds_ppm: int = 0

    # LDR
    light_level: int = 0  # 0-1023 (ADC raw)

    # PZEM-004T
    power_watts: float = 0.0
    energy_kwh: float = 0.0

    # Water Float Switch
    reservoir_ok: bool = True

    # Derived — calculated by bridge
    light_is_on: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


class SensorSimulator:
    """Generates biologically plausible sensor data with diurnal cycles.

    The simulator models a 24-hour cycle where:
    - Temperature peaks at 2 PM and dips at 4 AM
    - Humidity inversely correlates with temperature
    - CO2 drops during light hours (photosynthesis) and rises at night
    - Soil moisture slowly decays and gets "watered" periodically
    """

    def __init__(self, light_on_hour: int = 6, light_off_hour: int = 22):
        self._light_on = light_on_hour
        self._light_off = light_off_hour
        self._soil_moisture = 60.0  # Start at 60%
        self._last_water_time = time.time()
        self._energy_accumulator = 0.0
        self._tds_base = 900  # starting TDS

    def _hour_fraction(self) -> float:
        """Current hour as a float (e.g., 14.5 = 2:30 PM)."""
        now = datetime.now()
        return now.hour + now.minute / 60.0

    def _is_light_on(self) -> bool:
        h = self._hour_fraction()
        return self._light_on <= h < self._light_off

    def _noise(self, amplitude: float = 1.0) -> float:
        return random.gauss(0, amplitude)

    def read(self) -> SensorReading:
        """Generate one complete sensor reading."""
        h = self._hour_fraction()
        light_on = self._is_light_on()

        # --- Temperature: sinusoidal diurnal cycle ---
        # Peak at 14:00 (2 PM), trough at 02:00 (2 AM)
        # Range: 18°C (night) to 26°C (day)
        temp_base = 22.0
        temp_amplitude = 4.0
        phase = (h - 14.0) / 24.0 * 2 * math.pi
        temperature = temp_base + temp_amplitude * math.cos(phase) + self._noise(0.3)

        # If light is on, add LED heat contribution
        if light_on:
            temperature += 2.5

        temperature = round(max(15.0, min(35.0, temperature)), 1)

        # --- Humidity: inversely correlated with temperature ---
        humidity = 75.0 - (temperature - 18.0) * 2.5 + self._noise(2.0)
        humidity = round(max(30.0, min(90.0, humidity)), 1)

        # --- VPD Calculation ---
        # SVP = 0.6108 * exp(17.27 * T / (T + 237.3))
        svp = 0.6108 * math.exp(17.27 * temperature / (temperature + 237.3))
        avp = svp * (humidity / 100.0)
        vpd = round(svp - avp, 2)

        # --- Pressure ---
        pressure = round(1013.25 + self._noise(0.5), 1)

        # --- CO2: drops during day (photosynthesis), rises at night ---
        if light_on:
            co2 = int(1000 + self._noise(30))   # Aligned with co2_target
        else:
            co2 = int(1400 + self._noise(40))   # Higher nocturnal accumulation
        co2 = max(400, min(2500, co2))

        # --- Soil Moisture: slowly decays, jumps when "watered" ---
        elapsed = time.time() - self._last_water_time
        decay_rate = 0.5 if light_on else 0.2  # Faster drying under light
        self._soil_moisture -= decay_rate * (elapsed / 3600)  # per hour
        self._soil_moisture += self._noise(0.5)

        # Auto-water if too dry (simulates the pump firing)
        if self._soil_moisture < 45.0:
            self._soil_moisture = 65.0
            self._last_water_time = time.time()

        self._soil_moisture = round(max(10.0, min(95.0, self._soil_moisture)), 1)

        # --- pH: slow drift ---
        ph = round(6.2 + self._noise(0.15), 2)
        ph = max(4.0, min(8.0, ph))

        # --- TDS: slow drift around base ---
        tds = int(self._tds_base + self._noise(30))
        tds = max(200, min(2000, tds))

        # --- Light Level (LDR) ---
        if light_on:
            light_level = int(800 + self._noise(30))
        else:
            light_level = int(50 + self._noise(15))
        light_level = max(0, min(1023, light_level))

        # --- Power ---
        if light_on:
            power = round(98.0 + self._noise(2.0), 1)   # ~100W LED
        else:
            power = round(5.0 + self._noise(1.0), 1)     # Standby (Pi + Arduino)
        power = max(0.0, power)

        # Energy accumulator
        self._energy_accumulator += power / 1000.0 * (10.0 / 3600.0)  # kWh per poll

        # --- Reservoir ---
        reservoir_ok = random.random() > 0.02  # 2% chance of "low water" event

        return SensorReading(
            timestamp=datetime.now().isoformat(timespec="seconds"),
            temperature_c=temperature,
            humidity_pct=humidity,
            pressure_hpa=pressure,
            vpd_kpa=vpd,
            co2_ppm=co2,
            soil_moisture_pct=self._soil_moisture,
            ph=ph,
            tds_ppm=tds,
            light_level=light_level,
            power_watts=power,
            energy_kwh=round(self._energy_accumulator, 4),
            reservoir_ok=reservoir_ok,
            light_is_on=light_on,
        )
