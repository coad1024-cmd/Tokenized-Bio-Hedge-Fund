/*
 * Bio-Alpha Autonomous Fund — Arduino Firmware v1.0 (Skeleton)
 * ============================================================
 * 
 * Hardware: Arduino Uno R4 WiFi
 * Purpose:  Read all sensors -> Output JSON -> Listen for commands
 * 
 * PIN MAP (from wiring_diagram.md v2):
 *   A0  = LED Dimming (DAC output)
 *   A1  = pH Sensor (ADC)
 *   A2  = TDS Sensor (ADC)
 *   A3  = Soil Moisture (ADC)
 *   A4  = BME280 SDA (I2C)
 *   A5  = BME280 SCL (I2C)
 *   A6  = LDR (ADC, analog-only)
 *   D0  = PZEM TX -> Arduino RX (Serial1)
 *   D1  = Arduino TX -> PZEM RX (Serial1)
 *   D2  = Float Switch (INT0)
 *   D3  = Exhaust Fan (PWM via IRF520)
 *   D4  = Relay CH5 -> Air Pump
 *   D5  = Relay CH4 -> CO2 Solenoid
 *   D6  = Relay CH6 -> Ultrasonic Mister
 *   D7  = MH-Z19E TX -> Arduino (SoftSerial)
 *   D8  = Arduino -> MH-Z19E RX (SoftSerial)
 *   D9  = Water Pump (PWM via IRF520)
 *   D10 = Relay CH1 -> Dosing Pump A
 *   D11 = Relay CH2 -> Dosing Pump B
 *   D12 = Relay CH3 -> Dosing Pump pH Down
 *   D13 = Built-in LED (debug)
 * 
 * Serial Protocol:
 *   OUTPUT (every POLL_INTERVAL ms):
 *     {"temp":24.5,"hum":65,"pres":1013,"co2":800,"soil":55,"ph":6.2,
 *      "tds":900,"ldr":750,"watts":98.5,"kwh":1.23,"reservoir":1,"light_on":1}
 * 
 *   INPUT (commands from RPi):
 *     {"cmd":"pump_on","dur":5000}
 *     {"cmd":"co2_burst","dur":30000}
 *     {"cmd":"dose_a","dur":3000}
 *     {"cmd":"dose_b","dur":3000}
 *     {"cmd":"dose_ph","dur":2000}
 *     {"cmd":"fan_pwm","val":128}
 *     {"cmd":"light_dim","val":2048}
 *     {"cmd":"mister_on","dur":10000}
 *     {"cmd":"air_pump","state":1}
 */

#include <Wire.h>
// #include <Adafruit_BME280.h>      // Uncomment when hardware is ready
// #include <SoftwareSerial.h>       // For MH-Z19E
// #include <ArduinoJson.h>          // JSON parsing

// Pin Definitions
#define PIN_LED_DIM      A0
#define PIN_PH           A1
#define PIN_TDS          A2
#define PIN_SOIL         A3
// A4/A5 = I2C (BME280)
#define PIN_LDR          A6

#define PIN_FLOAT_SWITCH 2
#define PIN_EXHAUST_FAN  3
#define PIN_AIR_PUMP     4   // Relay CH5
#define PIN_CO2_SOLENOID 5   // Relay CH4
#define PIN_MISTER       6   // Relay CH6
#define PIN_CO2_TX       7   // SoftSerial to MH-Z19E
#define PIN_CO2_RX       8
#define PIN_WATER_PUMP   9
#define PIN_DOSE_A       10  // Relay CH1
#define PIN_DOSE_B       11  // Relay CH2
#define PIN_DOSE_PH      12  // Relay CH3
#define PIN_DEBUG_LED    13

// Config
#define POLL_INTERVAL    10000   // ms between sensor reads
#define SERIAL_BAUD      115200

// State
unsigned long lastPoll = 0;
bool lightOn = false;

void setup() {
  Serial.begin(SERIAL_BAUD);

  // Pin modes
  pinMode(PIN_FLOAT_SWITCH, INPUT_PULLUP);
  pinMode(PIN_EXHAUST_FAN, OUTPUT);
  pinMode(PIN_WATER_PUMP, OUTPUT);
  pinMode(PIN_CO2_SOLENOID, OUTPUT);
  pinMode(PIN_AIR_PUMP, OUTPUT);
  pinMode(PIN_MISTER, OUTPUT);
  pinMode(PIN_DOSE_A, OUTPUT);
  pinMode(PIN_DOSE_B, OUTPUT);
  pinMode(PIN_DOSE_PH, OUTPUT);
  pinMode(PIN_DEBUG_LED, OUTPUT);

  // All actuators OFF at startup (relays are active-LOW)
  digitalWrite(PIN_CO2_SOLENOID, HIGH);
  digitalWrite(PIN_AIR_PUMP, HIGH);
  digitalWrite(PIN_MISTER, HIGH);
  digitalWrite(PIN_DOSE_A, HIGH);
  digitalWrite(PIN_DOSE_B, HIGH);
  digitalWrite(PIN_DOSE_PH, HIGH);
  analogWrite(PIN_EXHAUST_FAN, 0);
  analogWrite(PIN_WATER_PUMP, 0);

  // Startup blink
  for (int i = 0; i < 3; i++) {
    digitalWrite(PIN_DEBUG_LED, HIGH);
    delay(100);
    digitalWrite(PIN_DEBUG_LED, LOW);
    delay(100);
  }

  Serial.println("{\"status\":\"bioalpha_firmware_v1_ready\"}");
}

void loop() {
  if (millis() - lastPoll >= POLL_INTERVAL) {
    lastPoll = millis();
    readAndSendSensors();
  }

  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    handleCommand(input);
  }
}

void readAndSendSensors() {
  // TODO: Replace with real sensor reads when hardware arrives
  float temp = 0.0;
  float hum = 0.0;
  float pres = 0.0;
  int co2 = 0;
  float soil = analogRead(PIN_SOIL) / 1023.0 * 100.0;
  float ph = analogRead(PIN_PH) / 1023.0 * 14.0;
  int tds = analogRead(PIN_TDS);
  int ldr = analogRead(PIN_LDR);
  int reservoir = digitalRead(PIN_FLOAT_SWITCH);

  Serial.print("{\"temp\":");    Serial.print(temp, 1);
  Serial.print(",\"hum\":");    Serial.print(hum, 1);
  Serial.print(",\"pres\":");   Serial.print(pres, 1);
  Serial.print(",\"co2\":");    Serial.print(co2);
  Serial.print(",\"soil\":");   Serial.print(soil, 1);
  Serial.print(",\"ph\":");     Serial.print(ph, 2);
  Serial.print(",\"tds\":");    Serial.print(tds);
  Serial.print(",\"ldr\":");    Serial.print(ldr);
  Serial.print(",\"watts\":");  Serial.print(0.0, 1);
  Serial.print(",\"kwh\":");    Serial.print(0.0, 4);
  Serial.print(",\"reservoir\":");  Serial.print(reservoir);
  Serial.print(",\"light_on\":");   Serial.print(lightOn ? 1 : 0);
  Serial.println("}");
}

void handleCommand(String input) {
  if (input.indexOf("pump_on") >= 0) {
    int dur = extractDuration(input);
    analogWrite(PIN_WATER_PUMP, 255);
    delay(dur);
    analogWrite(PIN_WATER_PUMP, 0);
    Serial.println("{\"ack\":\"pump_done\"}");
  }
  else if (input.indexOf("co2_burst") >= 0) {
    int dur = extractDuration(input);
    digitalWrite(PIN_CO2_SOLENOID, LOW);
    delay(dur);
    digitalWrite(PIN_CO2_SOLENOID, HIGH);
    Serial.println("{\"ack\":\"co2_done\"}");
  }
  else if (input.indexOf("dose_a") >= 0) {
    int dur = extractDuration(input);
    digitalWrite(PIN_DOSE_A, LOW);
    delay(dur);
    digitalWrite(PIN_DOSE_A, HIGH);
    Serial.println("{\"ack\":\"dose_a_done\"}");
  }
  else if (input.indexOf("dose_b") >= 0) {
    int dur = extractDuration(input);
    digitalWrite(PIN_DOSE_B, LOW);
    delay(dur);
    digitalWrite(PIN_DOSE_B, HIGH);
    Serial.println("{\"ack\":\"dose_b_done\"}");
  }
  else if (input.indexOf("dose_ph") >= 0) {
    int dur = extractDuration(input);
    digitalWrite(PIN_DOSE_PH, LOW);
    delay(dur);
    digitalWrite(PIN_DOSE_PH, HIGH);
    Serial.println("{\"ack\":\"dose_ph_done\"}");
  }
  else if (input.indexOf("fan_pwm") >= 0) {
    int val = extractValue(input);
    analogWrite(PIN_EXHAUST_FAN, constrain(val, 0, 255));
    Serial.println("{\"ack\":\"fan_set\"}");
  }
  else if (input.indexOf("light_dim") >= 0) {
    int val = extractValue(input);
    analogWrite(PIN_LED_DIM, constrain(val, 0, 4095));
    lightOn = val > 0;
    Serial.println("{\"ack\":\"light_set\"}");
  }
  else if (input.indexOf("mister_on") >= 0) {
    int dur = extractDuration(input);
    digitalWrite(PIN_MISTER, LOW);
    delay(dur);
    digitalWrite(PIN_MISTER, HIGH);
    Serial.println("{\"ack\":\"mister_done\"}");
  }
  else if (input.indexOf("air_pump") >= 0) {
    int state = extractValue(input);
    digitalWrite(PIN_AIR_PUMP, state == 1 ? LOW : HIGH);
    Serial.println("{\"ack\":\"air_pump_set\"}");
  }
}

int extractDuration(String input) {
  int idx = input.indexOf("\"dur\":");
  if (idx < 0) return 1000;
  return input.substring(idx + 6).toInt();
}

int extractValue(String input) {
  int idx = input.indexOf("\"val\":");
  if (idx < 0) {
    idx = input.indexOf("\"state\":");
    if (idx < 0) return 0;
    return input.substring(idx + 8).toInt();
  }
  return input.substring(idx + 6).toInt();
}
