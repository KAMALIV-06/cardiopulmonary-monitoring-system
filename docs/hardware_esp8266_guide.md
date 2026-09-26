# ESP8266 + MAX30102 Firmware Guide

The sketch is [`hardware/esp8266/max30102_monitor.ino`](../hardware/esp8266/max30102_monitor.ino). It reads optical red/IR samples over I²C, calculates heart rate and SpO₂ with the SparkFun MAX3010x library algorithm, keeps up to 20 seconds of PPG samples, and POSTs JSON to FastAPI. It never connects to PostgreSQL.

## Setup

1. Install ESP8266 Arduino board support, SparkFun MAX3010x Sensor Library, and ArduinoJson 6.
2. Open the sketch and set `WIFI_SSID`, `WIFI_PASSWORD`, `API_BASE_URL`, the public `API_ROOT_CA_PEM` for HTTPS, `PATIENT_ID`, and `DEVICE_ID`.
3. Wire a MAX30102 breakout to the board's I²C pins (common NodeMCU: SDA D2/GPIO4, SCL D1/GPIO5), common ground, and a voltage compatible with the exact breakout.
4. Select the matching ESP8266 board and flash. The sketch retries Wi-Fi and sensor initialization; it skips HTTP requests while Wi-Fi is disconnected. HTTPS requires the deployment's trusted public root CA; HTTP may be used only on a trusted local network.
5. Start the backend and validate with the fake HTTP request in [`hardware-integration.md`](hardware-integration.md) before using the sensor.

The SpO₂/heart-rate algorithm is a vendor example baseline and requires empirical validation for the specific sensor module, fit, and user population. The firmware's contact and pulsatility score is a heuristic. This prototype is not a certified medical device. Battery protection and charging are board-specific and are not implemented in the sketch.
