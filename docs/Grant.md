# Bio-Alpha: Grant Proposal

## 1. Project Overview

**Project Name:** Bio-Alpha Autonomous Fund
**Category:** Decentralized Science (DeSci), AI Agents, Cyber-Physical Systems
**Status:** Phase 2.5 Completed (Simulation & Local Validation) -> Entering Phase 3 (Hardware Production Run)

### One-Liner
Bio-Alpha is an autonomous, multi-agent AI framework (powered by Gemini 3.1) that manages the life-support systems of a physical biological asset (a crop) as a tokenized financial portfolio, optimizing resource expenditure against biomass yield.

---

## 2. The Vision: Biological Growth as Yield

Bio-Alpha treats a *Solanum lycopersicum* (Cherry Tomato) as a living data asset. The project replaces traditional, manual greenhouse automation with a **Cyber-Physical Economic System (CPES)**. 

Using an internal `$ALPHA` token economy, the AI must "purchase" resources like water, light, and CO2. It earns `$ALPHA` dividends based on successful biomass growth and fruit yield, tracked via a local vision model. This forces the system to learn **Total Return on Carbon**—balancing the cost of inputs against the biological output, creating a true "Quant Fund" for biology.

---

## 3. Technology Stack & Sovereignty

To ensure full stack sovereignty and prevent single points of failure, Bio-Alpha runs completely locally on a three-tier architecture:

*   **L1 (Hardware/Actuation):** Arduino Uno R4 WiFi orchestrating 20+ sensors (BME280, NDIR CO2, pH, TDS, PZEM) and actuators (Pumps, Solenoids, LED Drivers).
*   **L2 (Edge Computing/Host):** Raspberry Pi 5 (8GB) acting as the local ledger, host, and 24/7 FFmpeg stream server.
*   **L3 (Cognition):** A 7-agent Orchestrator-Worker system powered by **Gemini 3.1**, utilizing the Model Context Protocol (MCP) to make autonomous decisions securely at the edge.

---

## 4. Progress So Far (Phase 1 & 2)

We have successfully built and validated the core engine:
- **High-Fidelity Simulation:** Ran 40+ Monte Carlo sequences using radCAD to model environmental stress (heat waves, drought, capital starvation).
- **Economic Proof of Concept:** Established that the minimum viable capital for a 30-day run is 40,000 `$ALPHA` (with a ~$1,070/day burn rate).
- **Global Optimization:** Calibrated system targets using peer-reviewed horticultural data (VPD targets of 1.0 kPa, CO2 at 1200 ppm, extending photoperiods to 20h for maximum ROI).
- **Architecture Readiness:** All Python orchestration layers, SQLite ledgers, and MCP tools are mapped and ready for hardware deployment.

---

## 5. Grant Ask & Use of Funds

We are requesting funding to bridge the gap from a successful simulation suite to a continuous, live, public-facing autonomous node.

### Proposed Use of Funds:
1.  **Hardware Upgrades (Institutional Standard):** Moving from DIY sensors to quantifiable, institutional-grade arrays (e.g., Multispectral NDVI cameras for the Vision Agent, Precision Dosing pumps).
2.  **API & Compute Overhead:** Covering the ongoing inference costs for Gemini 3.1 high-frequency decision cycles over the life of the crop (approx. 4-5 months).
3.  **On-Chain Oracle Integration:** Bridging the local SQLite `$ALPHA` ledger to a public blockchain (e.g., via Chainlink Functions), allowing public participation and transparent, verifiable proof of biological yield.
4.  **Open Source Expansion:** Funding developer hours to package the Bio-Alpha Python framework as a 1-click deployable standard for anyone looking to tokenize physical biological growth.

---

## 6. Why This Matters

While numerous projects exist in the "AI Agents" space, very few attempt to build **Cyber-Physical Systems** that have to keep something alive in the real world under strict economic constraints. Bio-Alpha demonstrates a novel intersection of DeSci, Token Engineering, and Autonomous AI that sets a precedent for how we might automate and financialize agriculture, conservation, and resource management in the future.