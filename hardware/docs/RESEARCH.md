# Bio-Fund Technical Research: Arduino Uno R4 WiFi

## ⚡ Power & Logic
- **Operating Voltage:** 5V (standard digital pins).
- **Input Voltage (VIN):** 6-24V.
- **Microcontroller:** Renesas RA4M1 (Arm Cortex-M4).
- **Secondary Chip:** ESP32-S3 (handles WiFi/Bluetooth).

## 🔌 Pin Mapping for Sensors

| Sensor Type | Recommended Pin(s) | Protocol | Notes |
| --- | --- | --- | --- |
| **Soil Moisture** | A1 - A5 | Analog (ADC) | Capacitive sensors preferred (3.3V/5V compatible). |
| **BME280 (Air)** | A4 (SDA) / A5 (SCL) | I2C | **Standard.** High accuracy Temp/Hum/Pres for VPD. |
| **DHT22 (Alt)** | D2 | Digital | Single-bus (Optional backup). |
| **12V Water Pump** | D3 (PWM) | Digital/PWM | **MUST** use a MOSFET/Relay; Arduino cannot power this directly. |

## 🌟 Enhanced Features
- **12x8 LED Matrix:** Can be used for "Bio-Vital Signs" display (e.g., a "heartbeat" pulse or status icons).
- **12-bit DAC (A0):** Could be used for precise voltage control if we add advanced lighting or nutrient dosers later.
- **Qwiic Connector:** 3.3V I2C connector for easy sensor daisy-chaining.

## ⚠️ Hazards & Guardrails
1. **GIGO (Garbage In, Garbage Out):** Sensors like the DHT22 can drift. We need calibration logic in Ph 1.
2. **Current Limits:** The 5V pin can provide ~1.2A (on VIN), but don't pull too much for actuators.
3. **Common Ground:** Ensure the RPi 5 and Arduino share a common ground if communicating over Serial.
