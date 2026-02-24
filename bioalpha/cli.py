"""
Bio-Alpha CLI — The Fund Dashboard
===================================
Beautiful terminal UI showing real-time sensor data, $ALPHA balance,
and fund health status. Uses Rich for premium formatting.

Run:  python -m bioalpha.cli
"""

from __future__ import annotations

import logging
import time
import sys
from typing import List

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text

from bioalpha.config import CONFIG
from bioalpha.bridge import SerialBridge
from bioalpha.ledger import Vault
from bioalpha.sensors.simulator import SensorReading
from bioalpha.actuators import ActuatorDispatcher
from bioalpha.agents import Governor, EnvironmentAgent, NutrientDosingAgent, AgentAction


console = Console()
log = logging.getLogger("bioalpha")


def build_sensor_table(reading: SensorReading, policy) -> Table:
    table = Table(title="Sensor Readings", show_header=True, header_style="bold cyan", border_style="green")
    table.add_column("Sensor", style="bold")
    table.add_column("Value", justify="right")
    table.add_column("Target Range", justify="center")
    table.add_column("Status", justify="center")

    def status_icon(val, lo, hi):
        if lo <= val <= hi:
            return "OK"
        elif val < lo:
            return "LOW"
        else:
            return "HIGH"

    table.add_row("Temperature", f"{reading.temperature_c} C", f"{policy.temp_day_min}-{policy.temp_day_max} C", status_icon(reading.temperature_c, policy.temp_day_min, policy.temp_day_max))
    table.add_row("Humidity", f"{reading.humidity_pct}%", f"{policy.humidity_min}-{policy.humidity_max}%", status_icon(reading.humidity_pct, policy.humidity_min, policy.humidity_max))
    table.add_row("VPD", f"{reading.vpd_kpa} kPa", f"<= {policy.vpd_max} kPa", status_icon(reading.vpd_kpa, 0.4, policy.vpd_max))
    table.add_row("CO2", f"{reading.co2_ppm} ppm", f">= {policy.co2_min} ppm", "OK" if reading.co2_ppm >= policy.co2_min else "LOW")
    table.add_row("Soil Moisture", f"{reading.soil_moisture_pct}%", f"{policy.soil_moisture_min}-{policy.soil_moisture_max}%", status_icon(reading.soil_moisture_pct, policy.soil_moisture_min, policy.soil_moisture_max))
    table.add_row("pH", f"{reading.ph}", f"{policy.ph_min}-{policy.ph_max}", status_icon(reading.ph, policy.ph_min, policy.ph_max))
    table.add_row("TDS", f"{reading.tds_ppm} ppm", f"{policy.tds_min}-{policy.tds_max} ppm", status_icon(reading.tds_ppm, policy.tds_min, policy.tds_max))
    table.add_row("Light", f"{reading.light_level} (ADC)", "ON" if reading.light_is_on else "OFF", "ON" if reading.light_is_on else "OFF")
    table.add_row("Power", f"{reading.power_watts} W", f"{reading.energy_kwh} kWh total", "")
    table.add_row("Reservoir", "OK" if reading.reservoir_ok else "LOW", "", "OK" if reading.reservoir_ok else "EMPTY")
    return table


def build_fund_panel(vault: Vault) -> Panel:
    balance = vault.balance
    burn = vault.get_daily_burn_rate()
    if balance > 50_000:
        style = "bold green"
        health = "HEALTHY"
    elif balance > 20_000:
        style = "bold yellow"
        health = "CAUTION"
    elif balance > 5_000:
        style = "bold red"
        health = "CRITICAL"
    else:
        style = "bold red blink"
        health = "NEAR LIQUIDATION"
    days_left = f"{balance / burn:.1f} days" if burn > 0 else "inf"
    text = Text()
    text.append(f"  Balance: ", style="bold")
    text.append(f"${balance:,} ALPHA\n", style=style)
    text.append(f"  24h Burn: ", style="bold")
    text.append(f"${burn:,.0f} ALPHA/day\n", style="dim")
    text.append(f"  Runway: ", style="bold")
    text.append(f"{days_left}\n", style="dim")
    text.append(f"  Status: ", style="bold")
    text.append(f"{health}\n", style=style)
    return Panel(text, title="$ALPHA Fund", border_style="green")


def build_agent_panel(actions: List[AgentAction]) -> Panel:
    if not actions:
        text = Text("Waiting for next reasoning cycle...", style="dim italic")
    else:
        text = Text()
        for action in actions[-5:]:
            text.append(f" {action.timestamp} ", style="dim")
            text.append(f"[{action.agent_name}] ", style="bold cyan")
            text.append(f"{action.thought}\n")
            if action.tool:
                text.append(f"   -> ACTION: ", style="bold yellow")
                text.append(f"{action.tool}({action.params})\n", style="yellow")
            text.append("\n")
    return Panel(text, title="Agent Intelligence", border_style="cyan")


def build_dashboard(reading: SensorReading, vault: Vault, agent_actions: List[AgentAction]) -> Layout:
    layout = Layout()
    layout.split_column(Layout(name="header", size=3), Layout(name="body"))
    layout["body"].split_row(Layout(name="sensors", ratio=3), Layout(name="sidebar", ratio=2))
    layout["sidebar"].split_column(Layout(name="fund", ratio=1), Layout(name="agents", ratio=2))
    mode_label = "SIMULATOR" if CONFIG.run_mode.value == "simulator" else "HARDWARE"
    header = Panel(Text(f" Bio-Alpha Autonomous Fund v0.1 | {mode_label} | {reading.timestamp}", style="bold white on dark_green"), style="green")
    layout["header"].update(header)
    layout["sensors"].update(build_sensor_table(reading, CONFIG.policy))
    layout["fund"].update(build_fund_panel(vault))
    layout["agents"].update(build_agent_panel(agent_actions))
    return layout


def main():
    import asyncio
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(name)s | %(message)s", datefmt="%H:%M:%S")
    console.print("\n[bold green]Bio-Alpha Autonomous Fund[/]")
    console.print(f"[dim]Mode: {CONFIG.run_mode.value} | DB: {CONFIG.db_path}[/]\n")
    bridge = SerialBridge(CONFIG)
    vault = Vault(CONFIG.db_path, CONFIG.initial_alpha_balance)
    dispatcher = ActuatorDispatcher(CONFIG, vault)
    governor = Governor(vault, bridge)
    env_worker = EnvironmentAgent(vault, bridge, dispatcher)
    nutrient_worker = NutrientDosingAgent(vault, bridge, dispatcher)
    governor.add_worker(env_worker)
    governor.add_worker(nutrient_worker)
    console.print(f"[green]Fund initialized with ${vault.balance:,} ALPHA[/]")
    console.print("[dim]Press Ctrl+C to stop[/]\n")
    agent_history = []

    async def run_loop():
        nonlocal agent_history
        try:
            with Live(console=console, refresh_per_second=1, screen=True) as live:
                while True:
                    new_actions = await governor.run_cycle()
                    agent_history.extend(new_actions)
                    if len(agent_history) > 20:
                        agent_history = agent_history[-20:]
                    reading = bridge.last_reading or bridge.read()
                    if reading.light_is_on:
                        cost = int(CONFIG.light_cost_per_hour * (CONFIG.poll_interval_sec / 3600))
                        if cost > 0:
                            vault.log_actuator("light", "ON", cost=cost)
                    live.update(build_dashboard(reading, vault, agent_history))
                    await asyncio.sleep(CONFIG.poll_interval_sec)
        except KeyboardInterrupt:
            console.print("\n[yellow]Fund paused by operator[/]")
        finally:
            bridge.close()
            console.print(f"[green]Final balance: ${vault.balance:,} ALPHA[/]")

    asyncio.run(run_loop())


if __name__ == "__main__":
    main()
