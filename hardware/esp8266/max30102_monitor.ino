/*
 * ESP8266 + MAX30102 PPG telemetry prototype.
 * Libraries: SparkFun MAX3010x Sensor Library, ESP8266 Arduino Core,
 * ArduinoJson 6. Configure Wi-Fi and the backend LAN URL below.
 * The device posts HTTP only; it never connects to a database.
 */
#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <WiFiClientSecure.h>
#include <Wire.h>
#include <ArduinoJson.h>
#include "MAX30105.h"
#include "spo2_algorithm.h"

const char *WIFI_SSID = "YOUR_WIFI_SSID";
const char *WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char *API_BASE_URL = "https://api.example.com"; // Set to deployed FastAPI origin; no localhost default.
const char *API_ROOT_CA_PEM = ""; // Add the public root CA PEM when using HTTPS.
const char *PATIENT_ID = "PATIENT-001";
const char *DEVICE_ID = "ESP8266-MAX30102-01";

constexpr uint16_t WINDOW_SIZE = 100;      // 2 seconds at 50 Hz
constexpr uint16_t PPG_HISTORY_SIZE = 1000; // 20 seconds for backend RR estimation
MAX30105 sensor;
uint32_t irWindow[WINDOW_SIZE];
uint32_t redWindow[WINDOW_SIZE];
float ppgHistory[PPG_HISTORY_SIZE];
uint16_t historyCount = 0;
uint16_t writeIndex = 0;
uint16_t windowCount = 0;
unsigned long lastWifiAttempt = 0;
unsigned long lastSensorAttempt = 0;
bool sensorReady = false;

bool beginSensor() {
  if (!sensor.begin(Wire, I2C_SPEED_FAST)) return false;
  sensor.setup(0x1F, 1, 2, 50, 411, 4096);
  sensor.setPulseAmplitudeGreen(0);
  return true;
}

void keepWifiConnected() {
  if (WiFi.status() == WL_CONNECTED || millis() - lastWifiAttempt < 5000) return;
  lastWifiAttempt = millis();
  WiFi.disconnect();
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
}

void sendTelemetry(int32_t heartRate, int32_t spo2, bool fingerPresent) {
  if (WiFi.status() != WL_CONNECTED) return;
  HTTPClient http;
  const String apiUrl = String(API_BASE_URL) + "/api/v1/ingest/hardware";
  const bool secure = apiUrl.startsWith("https://");
  WiFiClient client;
  BearSSL::WiFiClientSecure secureClient;
  BearSSL::X509List rootCert(API_ROOT_CA_PEM);
  if (secure) {
    if (strlen(API_ROOT_CA_PEM) == 0) {
      Serial.println("HTTPS selected but API_ROOT_CA_PEM is empty.");
      return;
    }
    secureClient.setTrustAnchors(&rootCert);
    if (!http.begin(secureClient, apiUrl)) return;
  } else if (!http.begin(client, apiUrl)) {
    return;
  }
  http.addHeader("Content-Type", "application/json");

  DynamicJsonDocument doc(20000);
  doc["patient_id"] = PATIENT_ID;
  doc["device_id"] = DEVICE_ID;
  doc["heart_rate"] = fingerPresent ? heartRate : 0;
  doc["spo2"] = fingerPresent ? spo2 : 0;
  float mean = 0.0f;
  for (uint16_t i = 0; i < WINDOW_SIZE; ++i) mean += irWindow[i];
  mean /= WINDOW_SIZE;
  float variance = 0.0f;
  for (uint16_t i = 0; i < WINDOW_SIZE; ++i) {
    const float delta = irWindow[i] - mean;
    variance += delta * delta;
  }
  const float pulsatility = mean > 0 ? sqrtf(variance / WINDOW_SIZE) / mean : 0;
  const float quality = fingerPresent ? constrain(pulsatility * 50.0f, 0.1f, 1.0f) : 0.05f;
  doc["signal_quality"] = quality; // Simple contact/pulsatility heuristic, not a clinical SQI.
  JsonArray samples = doc.createNestedArray("ppg_samples");
  for (uint16_t i = 0; i < historyCount; ++i) {
    const uint16_t index = (writeIndex + PPG_HISTORY_SIZE - historyCount + i) % PPG_HISTORY_SIZE;
    samples.add(ppgHistory[index]);
  }

  String body;
  serializeJson(doc, body);
  const int status = http.POST(body);
  Serial.printf("Telemetry POST status: %d\n", status);
  http.end();
}

void setup() {
  Serial.begin(115200);
  Wire.begin(D2, D1); // ESP8266: SDA=D2/GPIO4, SCL=D1/GPIO5
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  sensorReady = beginSensor();
  lastSensorAttempt = millis();
}

void loop() {
  keepWifiConnected();
  if (!sensorReady) {
    if (millis() - lastSensorAttempt >= 5000) {
      lastSensorAttempt = millis();
      sensorReady = beginSensor();
    }
    delay(10);
    return;
  }
  if (!sensor.available()) {
    sensor.check();
    delay(2);
    return;
  }

  const uint32_t ir = sensor.getIR();
  const uint32_t red = sensor.getRed();
  sensor.nextSample();
  irWindow[windowCount] = ir;
  redWindow[windowCount] = red;
  const float normalized = static_cast<float>(ir) / 100000.0f;
  ppgHistory[writeIndex] = normalized;
  writeIndex = (writeIndex + 1) % PPG_HISTORY_SIZE;
  if (historyCount < PPG_HISTORY_SIZE) ++historyCount;
  if (++windowCount < WINDOW_SIZE) return;

  int32_t calculatedSpo2 = 0;
  int32_t calculatedHeartRate = 0;
  int8_t validSpo2 = 0;
  int8_t validHeartRate = 0;
  maxim_heart_rate_and_oxygen_saturation(
      irWindow, WINDOW_SIZE, redWindow, &calculatedSpo2, &validSpo2,
      &calculatedHeartRate, &validHeartRate);
  const bool fingerPresent = ir > 50000;
  const int32_t hr = validHeartRate ? calculatedHeartRate : 0;
  const int32_t oxygen = validSpo2 ? calculatedSpo2 : 0;
  sendTelemetry(hr, oxygen, fingerPresent);
  windowCount = 0;
}
