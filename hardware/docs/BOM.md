# 🧾 Bio-Alpha: Bill of Materials (Verified Prices)

> Prices in **₹ INR**, cross-verified Feb 2026 from 10+ Indian vendors.
> ✅ = verified via live browse or multiple search sources

---

## Tier 1 — Core Computing

| # | Component | Cheapest ✅ | Recommended ✅ | Notes |
|---|-----------|------------|---------------|-------|
| 1 | **Arduino Uno R4 WiFi** | ₹1,085 — [QuartzComponents](https://quartzcomponents.com) | ₹1,598 — [Robu.in](https://robu.in) (official, Made in India) | QuartzComponents is cheapest but verify it's genuine. Robu.in confirmed ₹1,598 live. |
| 2 | **Raspberry Pi 5 (8GB)** | ₹8,209 — [Robocraze](https://robocraze.com) | ₹9,699 — [Robomart](https://robomart.com) | **Recommended.** Best value for 4K vision + AI. |
| 3 | **RPi Camera Module 3** | ~₹2,547 — [Thingbits](https://thingbits.in) | ~₹2,800 — [Robocraze](https://robocraze.com) | **Oracle Standard:** 12MP, autofocus. Good all-rounder. |
| - | *Arducam 64MP Hawkeye* | *₹7,924 — [Ubuy](https://ubuy.co.in)* | — | **Oracle Alpha:** Ultra-high resolution for detecting minute pests/stress. |
| - | *Multispectral NDVI Kit* | *~₹12,000 — DIY (NoIR + Standard)* | — | **Oracle Quant:** Calculates mathematical health score (NDVI). Real quant fund edge. |
| 4 | **RPi 5 PSU (27W USB-C)** | ~₹800 | Robu.in / Robocraze | **Must** be 5V/5A. Generic chargers will throttle the Pi 5. |
| 4a | **Official RPi 5 Active Cooler** | [~₹470 — Robu.in](https://robu.in/product/official-raspberry-pi-5-active-cooler/) | **MANDATORY** | 24/7 Streaming/AI is CPU-heavy. Passive cooling **will fail**. |
| 5 | **MicroSD 64GB (A2)** | ~₹500 | Amazon.in (SanDisk Extreme) | Class 10 / A2 for OS + Claude Code. |

**Subtotal: ~₹13,500–₹16,500**

---

## Tier 2 — Sensors

| # | Component | Cheapest ✅ | Where | Notes |
|---|-----------|------------|-------|-------|
| 6 | **MH-Z19E CO2 Sensor** | ₹1,751 — [Robu.in](https://robu.in) | ✅ Live verified | NDIR sensor. MH-Z19C variant is ₹3,015. The MH-Z19E is best value. |
| 7 | **BME280 (Precision Temp/Hum/Pres)** | ₹258 — [Flyrobo](https://flyrobo.in) | Recommended for **VPD** | 10x more accurate than DHT22. Crucial for the $ALPHA Quant edge. |
| 8 | **Capacitive Soil Moisture v1.2** | ₹41 — IndiaMART (Technosam) | — | Buy 2× (one spare). Do NOT buy resistive type. |

**Subtotal: ~₹2,200–₹3,000**

---

## Tier 3 — Actuators

| # | Component | Cheapest ✅ | Where | Notes |
|---|-----------|------------|-------|-------|
| 9 | **12V Mini Water Pump** | ₹110 — IndiaMART | Also ₹269 on MakerBazar | Submersible, 250-350mA. Buy 2×. |
| 10 | **IRF520 MOSFET Driver** | ₹79 — IndiaMART / [Robu.in](https://robu.in) | — | Drives pump + exhaust fan via PWM from Arduino. Buy 2×. |
| 11 | **5V 8-Ch Relay Module** | ₹250 — [Robu.in](https://robu.in) | ✅ Live verified | **Standard Requirement.** Replaces 2-Ch. Drives CO2, Mister, Air Pump, and 3 Dosing Pumps. |
| 12 | **12V 2A Power Supply** | ~₹150 | Robu.in / Amazon.in | Powers pump + CO2 solenoid + exhaust fan. |
| 12a | **12V 80mm Exhaust Fan** | ~₹55 — [ElectronicSpices](https://electronicspices.com) | — | **Thermal control.** PWM-driven via IRF520. Mounts at top of Alpha Zone to vent hot air. |
| 12b | **USB Clip Fan (5V)** | ~₹200 — Amazon.in | — | **Circulation.** Prevents hot spots + strengthens stems. Always-on, powered from RPi USB. |

**Subtotal: ~₹650–₹750**

---

## Tier 4 — Enclosure & Lighting

| # | Component | Cheapest ✅ | Recommended | Notes |
|---|-----------|------------|-------------|-------|
| 13 | **Trekking Tent (8-Person)** | ₹0 (User Owned) | — | Massive ~140 sq ft volume. Will require partitioning. |
| 14 | **Mylar Partitioning Kit** | ~₹800 | Amazon.in (10-pack) | Create a 3x3x5 ft "sealed zone" inside the tent to trap CO2/Heat. |
| 15 | **100W LED Grow Light** | ₹2,230 — [IndiaMART](https://www.indiamart.com) | ₹4,500 — "Budget Dimmable" (Board + [Philips Driver](https://indiamart.com)) | **Budget:** On/Off only. **Best Fit:** Budget board + dimmable driver (₹4.5k) allows AI control without the ₹8.5k Nexsel price. |
| 16 | **CO2 Regulator + Solenoid** | ~₹3,490 — [AquaZones.in](https://aquazones.in) | — | **Best Fit.** Precision needle valve + 12V solenoid. Allows Claude to timing "Capital Injections" perfectly. |
| 17 | **CO2 Cylinder (2kg)** | ~₹1,500 — local welding supply | — | Refills ~₹200. Lasts months in 2×2. |

**Subtotal: ~₹5,500–₹15,000**

---

## 🚀 Alpha Tier Upgrades (The Quant Edge)

| # | Upgrade | Price ✅ | Benefit |
|---|---------|---------|---------|
| 22 | **Analog pH Sensor Kit** | [₹764 — Robu.in](https://robu.in/product/liquid-ph-value-detection-sensor-module-monitoring-control-for-arduino/) | Tracks nutrient lockout. High-alpha yield protection. |
| 23 | **Analog TDS/EC Sensor** | [₹470 — Robu.in](https://robu.in/product/analog-tds-sensor-module-water-quality-sensor-for-arduino/) | Measures nutrient concentration. Prevents "Capital Waste". |
| 24 | **LDR (Light Level) Sensor** | [~₹20 — Robu.in](https://robu.in/product/ldr-5mm-light-dependent-resistor/) | Verifies "Sun" uptime. Critical for Vision Oracle safety. |
| 25 | **PZEM-004T Power Monitor** | [₹509 — Robu.in](https://robu.in/product/pzem-004t-ac-multi-function-electric-energy-metering-power-monitor/) | Measures real **Electricity Opex** (Watts). Quant fund essential. |
| 29 | **12V Peristaltic Dosing Pump ×3** | [~₹590 each — CircuitCentral.in](https://circuitcentral.in) | **Autonomous Nutrition.** One each for Nutrient A, Nutrient B, pH Down. |
| 30 | **8-Ch Relay Module (UPGRADE)** | ~₹250 — Robu.in / IndiaMART | Replaces 4-Ch. Drives 3 dosing pumps, CO2, Air Pump, Mister, and 2 spares. |
| 31 | **IP65 Electronics Enclosure** | ~₹450 — Amazon.in / local | Protects Pi 5 + Arduino from 80% humidity in the tent. |
| 32 | **12V Air Pump + Air Stone Kit** | ~₹350 — [MakerBazar](https://makerbazar.in) | **Aeration.** Essential to prevent root rot in the nutrient reservoir. |
| 33 | **5V Ultrasonic Mister (USB)** | ~₹150 — Robu.in / Amazon.in | **Humidification.** Active VPD control during dry weather. |

**Subtotal: ~₹5,850**

---

## 🌱 Tier 0 — Biological Assets (The Fund's Capital)

| # | Item | Est. Cost | Notes |
|---|------|-----------|-------|
| B1 | **Cherry Tomato Seeds** | ~₹50 | Fastest to fruit = fastest $ALPHA generation. |
| B2 | **Coco Coir + Perlite (5kg)** | ~₹200 | Growing medium. Superior pH stability & drainage vs soil. |
| B3 | **Fabric Grow Bags (10L, 2×)** | ~₹100 | Air-prune roots for healthier growth. |
| B4 | **Hydroponic Nutrients A+B (1L ea)** | ~₹350 | Concentrated NPK. Dilute to ~800-1200 ppm (TDS sensor monitors). |
| B5 | **pH Down Solution (250ml)** | ~₹150 | Phosphoric acid. Tomato optimal: pH 5.8-6.5. |
| B6 | **pH Calibration Buffers (4.0 & 7.0)** | ~₹200 | **Mandatory** for sensor accuracy. Calibrate before first run. |
| B7 | **Water Reservoir (15L bucket)** | ~₹100 | Float switch mounts here. Pump draws from here. |

**Subtotal: ~₹1,150**

---

## Tier 5 — Wiring & Misc

| # | Item | Price |
|---|------|-------|
| 17 | Breadboard 830-pt | ~₹80 |
| 18 | Jumper wires kit (M-M, M-F, F-F) | ~₹100 |
| 19 | USB-A to USB-C cable (Arduino) | ~₹100 |
| 20 | Silicone tubing 6mm (5m) | ~₹150 | Increased length for dosing + watering. |
| 21 | Cable ties + tape + Glands | ~₹100 |
| 22 | **Ethernet Cable (Cat6, 3m)** | ~₹100 | Mandatory for 24/7 stream stability. |
| 23 | **Surge Protected Power Strip** | ~₹450 | 5+ outlets for Pi, 12V PSU, LED, Dosing, etc. |

**Subtotal: ~₹1,180**

---

## 💰 Total (Verified)

| Scenario | Estimate | Key Choices |
|----------|----------|-------------|
| **Budget** | **₹18,000–₹22,000** | QuartzComponents Arduino, Robocraze Pi 5, AliExpress grow light, DIY PVC tent |
| **Recommended** | **₹28,000–₹33,000** | Robu.in Arduino, Robomart Pi 5, AliExpress grow light, pre-built tent |
| **Alpha (Hedge Fund)** | **₹45,000–₹53,000**| **BME280**, **pH**, **TDS**, **Power Monitor**, **RTC**, Spider Farmer, Blazen |

---

## 🏪 Best Batch Order Strategy

> [!TIP]
> Order from **3 vendors max** to reduce shipping costs:

| Order From | Items | Est. Total |
|------------|-------|-----------|
| **Robu.in** | Arduino R4 WiFi, MH-Z19E, pH, TDS, Power Monitor, Float Switch, MOSFET | ~₹7,500 (Free shipping) |
| **Robocraze / Flyrobo** | Raspberry Pi 5 8GB, Camera 3, BME280, RTC Battery | ~₹12,000–₹14,500 |
| **IndiaMART / Voltros** | Capacitive Soil Moisture ×2, Pump ×2 | ~₹500 |
| **AquaZones / local** | CO2 regulator, CO2 cylinder | ~₹5,000 |
| **AliExpress / local** | LED Grow light (100W+), Mylar Sheets | ~₹3,500–₹10,000 |
