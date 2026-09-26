# ESP8266 + MAX30102 Hardware Integration

The physical target is an ESP8266, MAX30102 optical PPG sensor, and Li-ion battery. There is no ECG or AD8232 connection in this design. Use a properly protected/regulated battery supply suitable for the exact ESP8266 board and MAX30102 breakout; verify board voltage and I²C pull-up requirements before wiring.

## Proposed I²C connection

| MAX30102 | ESP8266 NodeMCU example | Purpose |
|---|---|---|
| SDA | D2 / GPIO4 | I²C data |
| SCL | D1 / GPIO5 | I²C clock |
| GND | GND | Common ground |
| VIN | Board-supported supply only | Check breakout documentation |

The pin mapping is an example for common NodeMCU boards, not verified against the user's exact board. Do not connect a bare sensor outside its specified voltage range.

## Firmware and libraries

See [`hardware/esp8266/max30102_monitor.ino`](../hardware/esp8266/max30102_monitor.ino). Install the ESP8266 Arduino board support, SparkFun MAX3010x Sensor Library, and ArduinoJson 6. SparkFun's library supports MAX30102 and includes a heart-rate/SpO₂ example algorithm ([library](https://github.com/sparkfun/SparkFun_MAX3010x_Sensor_Library), [SpO₂ example](https://github.com/sparkfun/SparkFun_MAX3010x_Sensor_Library/tree/master/examples/Example8_SPO2)). Configure Wi-Fi credentials and `API_BASE_URL` for the deployed FastAPI origin. For HTTPS, configure `API_ROOT_CA_PEM` with the server's trusted root CA; the device verifies TLS. Firmware sends to `/api/v1/ingest/hardware`; it has no database credentials or direct database access.

The device samples at 50 Hz, calculates heart rate and SpO₂ on-device using the library example algorithm, and sends a rolling PPG history (up to 20 seconds) for waveform display and a cautious respiratory modulation estimate. PPG-derived RR is returned as unavailable until the history is long enough. The firmware's signal-quality field is a simple contact/pulsatility heuristic, not clinically validated.

## Fake hardware request

With the backend running and PostgreSQL configured, send this from PowerShell before connecting the physical sensor:

```powershell
$payload = @{
  patient_id = 'PATIENT-001'
  device_id = 'ESP8266-MAX30102-TEST'
  heart_rate = 78
  spo2 = 97
  signal_quality = 0.82
  ppg_samples = @(0.02, 0.14, 0.41, 0.18, 0.03)
} | ConvertTo-Json
Invoke-RestMethod 'http://localhost:8000/api/v1/ingest/hardware' -Method Post -ContentType 'application/json' -Body $payload
```

The short sample list is accepted but does not produce a respiratory-rate estimate. A production sample window contains 1,000 PPG points at 50 Hz. Confirm stored history through `GET /api/v1/vitals/PATIENT-001/latest` and live delivery through the dashboard/WebSocket.
