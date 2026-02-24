# Bio-Alpha: Engineering the First Autonomous Biological Hedge Fund

### A Simulation Study on Resource Optimization and Adversarial Robustness

---

## 🏗️ The Premise: Biological Growth as Yield

The **Bio-Alpha Autonomous Fund** is a decentralized, closed-loop system where biological growth (yield) is converted into digital value ($ALPHA). By utilizing an array of sensors and actuators, an autonomous agent layer manages the life-support system of a cherry tomato crop to maximize return on investment (ROI).

To validate the fund before hardware deployment, we developed a high-fidelity **radCAD** system dynamics simulation. This article summarizes our findings across 40+ Monte Carlo configurations.

---

## 🔬 Phase 1: The "Happy Path" (Yield Optimization)

Our first objective was to find the optimal growth strategy. We compared baseline conditions against aggressive CO2 and light schedules.

![ROI Summary](plots/06_roi_summary.png)

**Key Findings:**
- **Max Growth Strategy:** Extending light to 20 hours and CO2 to 1000 ppm tripled the final biomass relative to baseline.
- **ROI Efficiency:** "Extended Light" offered the best cost-to-biomass ratio, as CO2 injection costs exhibition diminishing returns if not balanced with light intensity.

---

## ⚡ Phase 2: Stress Testing (Adversarial Robustness)

We subjected the fund to 7 adversarial scenarios to identify failure points.

![Stress Dashboard](plots/07_stress_test_dashboard.png)

### The "Perfect Storm" Analysis
Under a combination of Heat Wave (35°C), Drought, and Capital Starvation, the system reached a **CRITICAL** state. While the plant survived (health ~23/100), the fund balance hit **$0**, causing liquidation.

**Conclusion:** The system is remarkably robust to humidity and pH drift (agent compensation), but highly vulnerable to **thermal stress** and **liquidity crunches**.

---

## 📉 Phase 3: Capital Dynamics & Runway

To determine the **Minimum Viable Capital (MVC)**, we swept starting balances from $1,000 to $100,000 over 7-day and 30-day horizons.

![30-Day Runway](plots/09_runway_30day.png)

- **7-Day Survival:** Required at least **$8,000 $ALPHA**.
- **30-Day Runway:** Required at least **$40,000 $ALPHA**.
- **Burn Rate:** Baseline operations cost approximately **$1,070/day**, dominated by lighting and CO2 burst costs.

**Strategic Insight:** Starting with less than $40K leads to a 100% probability of bankruptcy before the first harvest cycle is complete.

---

## 🎯 Phase 4: Research-Backed Global Optimization

We cross-referenced our simulation with peer-reviewed data from institutions like **Ohio State University** and **Wageningen University** to find the global optimum for all resources.

![Radar Comparison](plots/14_optimal_radar.png)

### The "Optimal" Configuration:
- **Light:** 18-22 Hours (DLI 30+)
- **CO2:** 1000-1200 ppm
- **pH:** 5.5 - 6.0
- **TDS:** 1400 - 2100 ppm (EC 2.0-3.0)
- **MVC:** $40,000 $ALPHA

---

## 🚀 The Path Ahead

The Bio-Alpha simulation has successfully mapped the economic and biological boundaries of the fund. Our next steps include:
1. **Model Calibration:** Incorporating non-linear health penalties for pH and Temperature outliers discovered in research.
2. **On-Chain Integration:** Linking the simulation engine to the Ledger module for real-time state-sync.
3. **Hardware Pilot:** Deploying the v1 Firmware to the RPi 5/ESP32 stack based on these optimized 40K parameters.

---
*Published by the Bonding Curve Research Group*
