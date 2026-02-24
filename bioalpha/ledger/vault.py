"""
The $ALPHA Vault (SQLite Ledger)
================================
This is the economic engine of the Bio-Alpha Fund.

Every action (pump, light, CO2) costs $ALPHA.
Every milestone (new leaf, fruit) earns $ALPHA.
If balance hits 0, the fund is "liquidated" — experiment fails.

Tables:
  - alpha_transactions: Debit/Credit log
  - sensor_logs: Time-series of all sensor readings
  - actuator_events: Log of every command sent to hardware
  - growth_milestones: Vision Oracle's detected achievements
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Generator

from bioalpha.sensors.simulator import SensorReading


# ─── Schema ─────────────────────────────────────────────────────────────

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS alpha_transactions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   TEXT    NOT NULL,
    category    TEXT    NOT NULL,   -- 'OPEX', 'YIELD', 'INIT', 'PENALTY'
    description TEXT    NOT NULL,
    amount      INTEGER NOT NULL,   -- positive = credit, negative = debit
    balance     INTEGER NOT NULL    -- running balance after this tx
);

CREATE TABLE IF NOT EXISTS sensor_logs (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp         TEXT    NOT NULL,
    temperature_c     REAL,
    humidity_pct      REAL,
    pressure_hpa      REAL,
    vpd_kpa           REAL,
    co2_ppm           INTEGER,
    soil_moisture_pct REAL,
    ph                REAL,
    tds_ppm           INTEGER,
    light_level       INTEGER,
    power_watts       REAL,
    energy_kwh        REAL,
    reservoir_ok      INTEGER,
    light_is_on       INTEGER
);

CREATE TABLE IF NOT EXISTS actuator_events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   TEXT    NOT NULL,
    actuator    TEXT    NOT NULL,
    action      TEXT    NOT NULL,
    duration_ms INTEGER,
    cost_alpha  INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS growth_milestones (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   TEXT    NOT NULL,
    milestone   TEXT    NOT NULL,
    details     TEXT,
    reward      INTEGER NOT NULL DEFAULT 0,
    image_path  TEXT
);
"""


class Vault:
    """The $ALPHA Economic Ledger."""

    def __init__(self, db_path: Path, initial_balance: int = 100_000):
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_balance = initial_balance
        self._init_db()

    @contextmanager
    def _conn(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self):
        with self._conn() as conn:
            conn.executescript(SCHEMA_SQL)
            row = conn.execute(
                "SELECT COUNT(*) as cnt FROM alpha_transactions"
            ).fetchone()
            if row["cnt"] == 0:
                now = datetime.now().isoformat(timespec="seconds")
                conn.execute(
                    "INSERT INTO alpha_transactions "
                    "(timestamp, category, description, amount, balance) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (now, "INIT", "Fund Genesis — Initial Capital Injection",
                     self._init_balance, self._init_balance),
                )

    @property
    def balance(self) -> int:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT balance FROM alpha_transactions "
                "ORDER BY id DESC LIMIT 1"
            ).fetchone()
            return row["balance"] if row else 0

    @property
    def is_solvent(self) -> bool:
        return self.balance > 0

    def debit(self, category: str, description: str, amount: int) -> int:
        new_balance = self.balance - abs(amount)
        now = datetime.now().isoformat(timespec="seconds")
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO alpha_transactions "
                "(timestamp, category, description, amount, balance) "
                "VALUES (?, ?, ?, ?, ?)",
                (now, category, description, -abs(amount), new_balance),
            )
        return new_balance

    def credit(self, category: str, description: str, amount: int) -> int:
        new_balance = self.balance + abs(amount)
        now = datetime.now().isoformat(timespec="seconds")
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO alpha_transactions "
                "(timestamp, category, description, amount, balance) "
                "VALUES (?, ?, ?, ?, ?)",
                (now, category, description, abs(amount), new_balance),
            )
        return new_balance

    def log_sensors(self, reading: SensorReading):
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO sensor_logs "
                "(timestamp, temperature_c, humidity_pct, pressure_hpa, "
                "vpd_kpa, co2_ppm, soil_moisture_pct, ph, tds_ppm, "
                "light_level, power_watts, energy_kwh, reservoir_ok, light_is_on) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    reading.timestamp, reading.temperature_c,
                    reading.humidity_pct, reading.pressure_hpa,
                    reading.vpd_kpa, reading.co2_ppm,
                    reading.soil_moisture_pct, reading.ph,
                    reading.tds_ppm, reading.light_level,
                    reading.power_watts, reading.energy_kwh,
                    int(reading.reservoir_ok), int(reading.light_is_on),
                ),
            )

    def log_actuator(
        self, actuator: str, action: str,
        duration_ms: int | None = None, cost: int = 0
    ):
        now = datetime.now().isoformat(timespec="seconds")
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO actuator_events "
                "(timestamp, actuator, action, duration_ms, cost_alpha) "
                "VALUES (?, ?, ?, ?, ?)",
                (now, actuator, action, duration_ms, cost),
            )
        if cost > 0:
            self.debit("OPEX", f"{actuator}: {action}", cost)

    def log_milestone(
        self, milestone: str, details: str = "",
        reward: int = 0, image_path: str = ""
    ):
        now = datetime.now().isoformat(timespec="seconds")
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO growth_milestones "
                "(timestamp, milestone, details, reward, image_path) "
                "VALUES (?, ?, ?, ?, ?)",
                (now, milestone, details, reward, image_path),
            )
        if reward > 0:
            self.credit("YIELD", f"{milestone}: {details}", reward)

    def get_recent_transactions(self, limit: int = 20) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM alpha_transactions ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_daily_burn_rate(self) -> float:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT COALESCE(SUM(ABS(amount)), 0) as total "
                "FROM alpha_transactions "
                "WHERE category = 'OPEX' "
                "AND timestamp >= datetime('now', '-1 day')"
            ).fetchone()
            return float(row["total"])
