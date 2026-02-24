# Bio-Alpha: The Autonomous Biological Hedge Fund

Bio-Alpha is an autonomous greenhouse system managed by a multi-agent AI framework (using Claude 3.x). It treats biological growth as financial yield, using a tokenized economy ($ALPHA) to optimize resource allocation (water, light, CO2) for maximum ROI.

## 🚀 Overview

- **Sovereign AI**: Runs locally on a Raspberry Pi 5 to ensure full stack sovereignty.
- **Economic Logic**: Every action costs $ALPHA; growth earns $ALPHA.
- **Three-Tier Architecture**:
    - **L1 (Hardware)**: Arduino Uno R4 WiFi for sensing and actuation.
    - **L2 (Host)**: Raspberry Pi 5 for data orchestration and local agent execution.
    - **L3 (Intelligence)**: Claude 3.x for high-level strategy.

## 📁 Repository Structure

- `bioalpha/`: Core Python package (Agents, Simulation, Serial Bridge).
- `experiments/`: Optimization notebooks and parameter sweep scripts.
- `hardware/`: Bill of Materials, Wiring Diagrams, and Arduino Firmware.
- `docs/`: Technical specifications, architecture docs, and project roadmaps.
- `research/`: Simulation findings and market differentiation articles.
- `plots/`: Data visualizations from simulation runs.

## 🛠️ Setup

1. **Clone the Repo**:
   ```bash
   git clone https://github.com/coad1024-cmd/Tokenized-Bio-Hedge-Fund.git
   cd Tokenized-Bio-Hedge-Fund
   ```

2. **Install Dependencies**:
   ```bash
   pip install -e .
   ```

3. **Configure Environment**:
   ```bash
   cp .env.example .env
   # Add your API keys to .env
   ```

4. **Run Simulation**:
   ```bash
   python experiments/run_experiments.py
   ```

5. **Launch Dashboard**:
   ```bash
   bioalpha
   ```

## 📄 License

MIT
