# Bio-Alpha Autonomous Fund

> A Quant-Focused Cyber-Physical Economic System. AI-managed plant growth with $ALPHA tokenomics, multi-agent control (Claude Opus 4.6), and radCAD Monte Carlo simulations.

## Architecture

```
L4: Strategy Optimizer (radCAD Monte Carlo / Parameter Sweeps)
L3: Agent Layer       (Governor -> Environment Agent + Nutrient Agent)
L2: Data Pipeline     (Serial Bridge + $ALPHA Vault + Actuator Dispatcher)
L1: Hardware          (Arduino R4 WiFi + Raspberry Pi 5)
```

## Quick Start

```bash
# Install
pip install -e .

# Live dashboard (simulator mode)
python -m bioalpha.cli

# Run 7-day Monte Carlo simulation (5 runs)
python -m bioalpha.simulation.model
```

## Simulation Results (7-day x 5 Monte Carlo)

```
Avg Biomass:     6.8g   (seedling -> small plant)
Avg $ALPHA Left: $92,504 (7.5% burn in 7 days)
Avg Health:      100/100
CO2 Bursts:      56     (~8/day)
Irrigations:     10     (~1.4/day)
Dosing Events:   10     (~1.4/day)
Survival Rate:   100%
```

## License

MIT
