# Simulation Experiments & Results

> Bio-Alpha Autonomous Fund — radCAD Monte Carlo Strategy Optimization
>
> **Run date:** 2026-02-24 | **Engine:** Pure-Python radCAD-compatible | **Resolution:** 1 timestep = 1 hour

## How to Generate Plots

```bash
# Install matplotlib if needed
pip install matplotlib numpy

# Generate all 6 charts (saved to plots/)
python plot_experiments.py
```

---

## Baseline: 7-Day Monte Carlo (5 runs)

```
python -m bioalpha.simulation.model
```

| Metric | Result |
|--------|--------|
| Avg Biomass | 6.8g |
| Avg $ALPHA Left | $92,506 (7.5% burn) |
| Avg Health | 100.0/100 |
| CO2 Bursts | 56 (~8/day) |
| Irrigations | 10 (~1.4/day) |
| Dosing Events | 10 (~1.4/day) |
| Survival Rate | 100% |

**Chart:** `plots/01_baseline_timeseries.png` — 6-panel time-series of all state variables over 7 days

**Chart:** `plots/02_monte_carlo_fan.png` — 5 Monte Carlo runs overlaid (biomass, balance, health)

---

## Experiment 1: CO2 Cost Sensitivity Sweep

**Question:** How does CO2 burst cost affect fund economics?

**Method:** 4 parameter configs × 3 Monte Carlo runs × 168 timesteps (7 days)

| CO2 Cost | Biomass | $ALPHA Left | Health | CO2 Bursts | Total OPEX |
|----------|---------|-------------|--------|------------|------------|
| $5/burst | 6.7g | $93,342 | 100/100 | 56 | $6,658 |
| $10/burst | 6.8g | $93,080 | 100/100 | 56 | $6,920 |
| **$20/burst** | **6.9g** | **$92,520** | **100/100** | **56** | **$7,480** |
| $40/burst | 6.9g | $91,417 | 100/100 | 56 | $8,583 |

**Finding:** CO2 cost doesn't change agent behavior — it fires the same 56 bursts regardless of price. **$5–$10/burst is the cost-efficiency sweet spot.**

**Chart:** `plots/03_co2_cost_sweep.png`

---

## Experiment 2: Conservative vs Aggressive CO2 (A/B Test)

**Question:** Should we inject CO2 more aggressively?

**Method:** 2 strategies × 5 Monte Carlo runs × 168 timesteps

| Metric | Conservative (600ppm) | Aggressive (1000ppm) | Winner |
|--------|----------------------|---------------------|--------|
| Biomass | 6.5g | **7.9g** | Aggressive (+21%) |
| $ALPHA Left | **$92,828** | $90,825 | Conservative |
| Health | 100.0 | 100.0 | TIE |
| CO2 Bursts | **40** | 140 | Conservative (3.5× less) |
| Total OPEX | **$7,172** | $9,175 | Conservative |

**Finding:** Aggressive CO2 grows **21% more biomass** but costs **28% more OPEX**.

**Chart:** `plots/04_co2_ab_test.png`

---

## Experiment 3: Light Schedule Optimization (A/B Test)

**Question:** Does extending light hours from 16h to 20h pay for itself in growth?

**Method:** 2 strategies × 5 Monte Carlo runs × 168 timesteps

| Metric | 16h Light | 20h Light | Winner |
|--------|-----------|-----------|--------|
| Biomass | 6.9g | **9.1g** | 20h (+32%) |
| $ALPHA Left | **$92,501** | $90,822 | 16h |
| Health | 100.0 | 100.0 | TIE |
| CO2 Bursts | **56** | 70 | 16h |
| Total OPEX | **$7,499** | $9,178 | 16h |

**Finding:** Extended 20h light is the **single biggest growth lever**: **+32% biomass** for only 22% more OPEX.

**Chart:** `plots/05_light_ab_test.png`

---

## ROI Summary: All Strategies Compared

| Strategy | Biomass | OPEX | ROI (g/1K $ALPHA) |
|----------|---------|------|-------------------|
| Baseline (16h, 800ppm) | 6.9g | $7,499 | 0.93 |
| Aggressive CO2 (16h, 1000ppm) | 8.0g | $9,175 | 0.87 |
| Extended Light (20h, 800ppm) | 9.0g | $9,178 | 0.99 |
| **Max Growth (20h, 1000ppm)** | **10.5g** | **$10,612** | **0.97** |

**Chart:** `plots/06_roi_summary.png`

---

## Recommended Optimal Strategy

| Parameter | Recommended | Reason |
|-----------|-------------|--------|
| Light schedule | **20h** (4AM–12AM) | +32% biomass, best ROI |
| CO2 threshold | **1000 ppm** (aggressive) | +21% biomass |
| CO2 cost budget | **$10–$20/burst** | No behavioral difference below $40 |

**Projected 7-day performance:** ~10.5g biomass, ~$89K $ALPHA remaining, 100% survival.
