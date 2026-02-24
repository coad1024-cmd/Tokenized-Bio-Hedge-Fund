"""
Bio-Alpha Configuration
=======================
Central configuration for the entire fund. Uses Pydantic for
validation so bad config crashes BEFORE it reaches the plant.
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings


# Resolve project root at module load time
_PROJECT_ROOT = Path(__file__).resolve().parent.parent


class RunMode(str, Enum):
    """Controls whether we talk to real hardware or simulate."""
    SIMULATOR = "simulator"   # No hardware — generates fake sensor data
    HARDWARE = "hardware"     # Real Arduino + RPi connected


class BiologicalPolicy(BaseSettings):
    """The 'Investment Policy' for the plant. These are the target ranges
    that the Environment Agent tries to maintain."""

    # Temperature (°C)
    temp_day_min: float = 21.0
    temp_day_max: float = 27.0
    temp_night_min: float = 15.0
    temp_night_max: float = 18.0

    # Humidity (%)
    humidity_min: float = 40.0
    humidity_max: float = 70.0

    # VPD (kPa) — Vapor Pressure Deficit
    vpd_target: float = 1.0
    vpd_max: float = 1.2

    # CO2 (ppm)
    co2_target: int = 1200
    co2_min: int = 800

    # pH
    ph_min: float = 5.8
    ph_max: float = 6.5

    # TDS/EC (ppm)
    tds_target: int = 1000
    tds_min: int = 800
    tds_max: int = 1400

    # Soil Moisture (% — capacitive sensor normalized)
    soil_moisture_min: float = 40.0
    soil_moisture_max: float = 70.0

    # Light Schedule
    light_hours_per_day: int = 16
    light_on_hour: int = 6    # 6 AM
    light_off_hour: int = 22  # 10 PM


class FundConfig(BaseSettings):
    """Master configuration for the Bio-Alpha Fund."""

    model_config = {"env_prefix": "BIOALPHA_"}

    # --- Mode ---
    run_mode: RunMode = RunMode.SIMULATOR

    # --- Paths ---
    project_root: Path = _PROJECT_ROOT
    data_dir: Optional[Path] = None
    images_dir: Optional[Path] = None
    db_path: Optional[Path] = None

    # --- Serial (Arduino) ---
    serial_port: str = "COM3"         # Windows default; /dev/ttyACM0 on RPi
    serial_baud: int = 115200

    # --- Fund Economics ---
    initial_alpha_balance: int = 100_000
    pump_cost_per_sec: int = 5         # $ALPHA per second of pump
    light_cost_per_hour: int = 50      # $ALPHA per hour of light
    co2_cost_per_burst: int = 20       # $ALPHA per CO2 solenoid burst
    nutrient_cost_per_dose: int = 15   # $ALPHA per peristaltic dose
    fan_cost_per_hour: int = 10        # $ALPHA per hour of exhaust

    # --- Sensor Polling ---
    poll_interval_sec: float = 10.0    # How often to read sensors
    dosing_wait_sec: float = 300.0     # 5 min wait after dosing to re-read

    # --- Biological Policy ---
    policy: BiologicalPolicy = BiologicalPolicy()

    @model_validator(mode="after")
    def _set_derived_paths(self) -> "FundConfig":
        """Set derived paths and create directories."""
        if self.data_dir is None:
            self.data_dir = self.project_root / "data"
        if self.images_dir is None:
            self.images_dir = self.project_root / "data" / "growth_photos"
        if self.db_path is None:
            self.db_path = self.project_root / "data" / "vault.db"

        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.images_dir.mkdir(parents=True, exist_ok=True)
        return self


# Global singleton
CONFIG = FundConfig()
