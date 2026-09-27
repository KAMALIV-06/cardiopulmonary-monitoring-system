/*
 * ESP8266 + MAX30102 live cardiopulmonary telemetry.
 * Uses MAX30100lib PulseOximeter for HR/SpO2 and the same internal raw samples
 * for finger-presence hysteresis. No second sensor object is created.
 */
#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <WiFiClientSecure.h>
#include <Wire.h>
#include <MAX30100_PulseOximeter.h>

const char *WIFI_SSID = "YOUR_WIFI_SSID";
const char *WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char *API_BASE_URL = "https://api.example.com"; // Set to deployed FastAPI origin; no localhost default.
const char *API_ROOT_CA_PEM = ""; // Add the public root CA PEM when using HTTPS.
const char *PATIENT_ID = "PATIENT-001";
const char *DEVICE_ID = "ESP8266-MAX30102-01";

constexpr uint16_t FINGER_PRESENT_THRESHOLD = 1200;
constexpr uint16_t FINGER_ABSENT_THRESHOLD = 700;
constexpr uint32_t REPORT_INTERVAL_MS = 2000;
constexpr uint32_t FINGER_STABILIZATION_MS = 1500;
constexpr uint32_t RAW_SAMPLE_TIMEOUT_MS = 500;
constexpr uint8_t REQUIRED_FRESH_BEATS = 2;
constexpr float INTEGRATION_SIGNAL_QUALITY = 0.95f; // Existing payload field; not a measured SQI.

PulseOximeter pox;
bool sensorReady = false;
bool fingerPresent = false;
uint16_t latestIR = 0;
uint16_t latestRed = 0;
uint8_t beatsSinceFingerPresent = 0;
uint32_t fingerPresentSince = 0;
uint32_t spo2UpdatesAtFingerPresent = 0;
uint32_t lastRawSampleCount = 0;
uint32_t lastRawSampleAt = 0;
uint32_t lastReport = 0;
uint32_t lastWifiAttempt = 0;
uint32_t lastSensorAttempt = 0;

void onBeatDetected() {
  if (fingerPresent && beatsSinceFingerPresent < 255) {
    ++beatsSinceFingerPresent;
  }
}

bool beginSensor() {
  if (!pox.begin()) {
    Serial.println("MAX30100/MAX30102 initialization failed.");
    return false;
  }
  pox.setOnBeatDetectedCallback(onBeatDetected);
  Serial.println("Pulse oximeter initialized.");
  return true;
}

void keepWifiConnected() {
  if (WiFi.status() == WL_CONNECTED || millis() - lastWifiAttempt < 5000) return;
  lastWifiAttempt = millis();
  WiFi.disconnect();
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
}

bool sendTelemetry(float heartRate, uint8_t spo2) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi unavailable - sensor reading not sent.");
    return false;
  }

  HTTPClient http;
  const String apiUrl = String(API_BASE_URL) + "/api/v1/ingest/hardware";
  const bool secure = apiUrl.startsWith("https://");
  WiFiClient client;
  BearSSL::WiFiClientSecure secureClient;
  BearSSL::X509List rootCert(API_ROOT_CA_PEM);

  if (secure) {
    if (strlen(API_ROOT_CA_PEM) == 0) {
      Serial.println("HTTPS selected but API_ROOT_CA_PEM is empty.");
      return false;
    }
    secureClient.setTrustAnchors(&rootCert);
    if (!http.begin(secureClient, apiUrl)) return false;
  } else if (!http.begin(client, apiUrl)) {
    return false;
  }

  http.setTimeout(2500);
  http.addHeader("Content-Type", "application/json");

  String body;
  body.reserve(256);
  body = "{\"patient_id\":\"";
  body += PATIENT_ID;
  body += "\",\"device_id\":\"";
  body += DEVICE_ID;
  body += "\",\"heart_rate\":";
  body += String(heartRate, 2);
  body += ",\"spo2\":";
  body += String(spo2);
  body += ",\"signal_quality\":";
  body += String(INTEGRATION_SIGNAL_QUALITY, 2);
  body += ",\"ppg_samples\":[],\"ppg_red_samples\":[],\"ppg_ir_samples\":[]}";
  const int status = http.POST(body);
  Serial.printf("Telemetry POST status: %d\n", status);
  http.end();
  return status >= 200 && status < 300;
}

void printNoFinger() {
  Serial.printf("IR: %u\nRED: %u\nFinger: NO\n\n", latestIR, latestRed);
  Serial.println("NO FINGER");
  Serial.println("Heart rate: 0 bpm");
  Serial.println("SpO2: 0%");
  Serial.println("Invalid reading - NOT sending to backend.");
}

void printFingerWaiting() {
  Serial.printf("IR: %u\nRED: %u\nFinger: YES\n\n", latestIR, latestRed);
  Serial.println("FINGER PRESENT");
  Serial.println("Heart rate: -- bpm");
  Serial.println("SpO2: --%");
  Serial.println("Waiting for fresh valid HR/SpO2 calculation.");
}

void printValidReading(float heartRate, uint8_t spo2) {
  Serial.printf("IR: %u\nRED: %u\nFinger: YES\n\n", latestIR, latestRed);
  Serial.println("FINGER PRESENT");
  Serial.printf("Heart rate: %.2f bpm\n", heartRate);
  Serial.printf("SpO2: %u%%\n", spo2);
  Serial.println("Valid sensor reading.");
}

void setup() {
  Serial.begin(115200);
  Wire.begin(D2, D1); // ESP8266: SDA=D2/GPIO4, SCL=D1/GPIO5

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  sensorReady = beginSensor();
  lastSensorAttempt = millis();
  lastReport = millis() - REPORT_INTERVAL_MS;
}

void loop() {
  if (sensorReady) {
    // Keep the PulseOximeter sample-processing path running as frequently as possible.
    pox.update();

    const uint32_t rawSampleCount = pox.getRawSampleCount();
    const bool newRawSamples = rawSampleCount != lastRawSampleCount;
    if (newRawSamples) {
      lastRawSampleCount = rawSampleCount;
      lastRawSampleAt = millis();
    }

    uint16_t ir;
    uint16_t red;
    if (newRawSamples && pox.getRawValues(&ir, &red)) {
      latestIR = ir;
      latestRed = red;

      bool stateChanged = false;
      if (!fingerPresent && latestIR >= FINGER_PRESENT_THRESHOLD) {
        fingerPresent = true;
        fingerPresentSince = millis();
        beatsSinceFingerPresent = 0;
        spo2UpdatesAtFingerPresent = pox.getSpO2UpdateCount();
        stateChanged = true;
      } else if (fingerPresent && latestIR <= FINGER_ABSENT_THRESHOLD) {
        fingerPresent = false;
        beatsSinceFingerPresent = 0;
        stateChanged = true;
      }

      keepWifiConnected();

      const uint32_t now = millis();
      const bool reportDue = stateChanged || now - lastReport >= REPORT_INTERVAL_MS;
      if (reportDue) {
        lastReport = now;

        if (!fingerPresent) {
          printNoFinger();
        } else {
          const float heartRate = pox.getHeartRate();
          const uint8_t spo2 = pox.getSpO2();
          const bool stabilized = now - fingerPresentSince >= FINGER_STABILIZATION_MS;
          const bool freshHeartRate = beatsSinceFingerPresent >= REQUIRED_FRESH_BEATS;
          const bool freshSpO2 = pox.getSpO2UpdateCount() > spo2UpdatesAtFingerPresent;
          const bool freshRawSample = now - lastRawSampleAt <= RAW_SAMPLE_TIMEOUT_MS;
          const bool valid = freshRawSample && stabilized && freshHeartRate && freshSpO2 &&
                             isfinite(heartRate) && heartRate > 0.0f &&
                             spo2 > 0 && spo2 <= 100;

          if (!valid) {
            printFingerWaiting();
          } else {
            printValidReading(heartRate, spo2);
            Serial.println("Sending live sensor data...");
            sendTelemetry(heartRate, spo2);
          }
        }
      }
    }
  } else {
    keepWifiConnected();
    if (millis() - lastSensorAttempt >= 5000) {
      lastSensorAttempt = millis();
      sensorReady = beginSensor();
    }
    delay(10);
  }
}
