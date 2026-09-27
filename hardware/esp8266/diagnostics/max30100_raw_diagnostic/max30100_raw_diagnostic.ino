/*
 * Temporary MAX30100 raw optical diagnostic.
 * Prints the latest IR/RED sample every 500 ms. No Wi-Fi or backend traffic.
 * Uses the installed MAX30100lib low-level public API because PulseOximeter's
 * MAX30100 instance is private and cannot be read from a sketch.
 */
#include <Arduino.h>
#include <Wire.h>
#include <MAX30100.h>

MAX30100 sensor;
constexpr uint32_t REPORT_INTERVAL_MS = 500;
uint32_t lastReport = 0;
uint16_t latestIR = 0;
uint16_t latestRed = 0;
uint32_t samplesSinceReport = 0;
bool haveSample = false;

void setup() {
  Serial.begin(115200);
  Serial.println();
  Serial.println("MAX30100 raw IR/RED diagnostic");
  Serial.println("No Wi-Fi; no backend transmission.");

  // MAX30100::begin() uses Wire defaults, 100 Hz, 1600 us pulse width,
  // high-resolution mode, and initial 50 mA LED currents.
  if (!sensor.begin()) {
    Serial.println("Sensor initialization FAILED. Check power, wiring, and I2C.");
    while (true) delay(1000);
  }

  // Match PulseOximeter::begin(): SpO2+HR mode, IR 50 mA, RED 27.1 mA.
  sensor.setMode(MAX30100_MODE_SPO2_HR);
  sensor.setLedsCurrent(MAX30100_LED_CURR_50MA, MAX30100_LED_CURR_27_1MA);
  Serial.println("Sensor initialized. Place/remove finger and compare raw values.");
  Serial.println("IR\tRED\tSAMPLES/500ms");
}

void loop() {
  sensor.update();

  uint16_t ir;
  uint16_t red;
  while (sensor.getRawValues(&ir, &red)) {
    latestIR = ir;
    latestRed = red;
    ++samplesSinceReport;
    haveSample = true;
  }

  const uint32_t now = millis();
  if (now - lastReport >= REPORT_INTERVAL_MS) {
    if (haveSample) {
      Serial.print(latestIR);
      Serial.print('\t');
      Serial.print(latestRed);
      Serial.print('\t');
      Serial.println(samplesSinceReport);
    } else {
      Serial.println("NO SAMPLE\tNO SAMPLE\t0");
    }
    lastReport = now;
    samplesSinceReport = 0;
    haveSample = false;
  }

  delay(1);
}
