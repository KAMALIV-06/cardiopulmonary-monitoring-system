# API Reference

Base URL: `http://localhost:8000/api/v1`

## Hardware ingestion

`POST /ingest/hardware` accepts the ESP8266 + MAX30102 JSON payload and sends it through the shared validation, PPG processing, risk, persistence, alert, and WebSocket pipeline.

```json
{
  "patient_id": "PATIENT-001",
  "device_id": "ESP8266-MAX30102-01",
  "timestamp": "2026-09-25T12:30:00Z",
  "heart_rate": 78,
  "spo2": 97,
  "signal_quality": 0.82,
  "ppg_samples": [0.02, 0.14, 0.41, 0.18, 0.03]
}
```

`timestamp` and `signal_quality` are optional. When quality is omitted, the backend estimates it from PPG. Raw `ppg_ir_samples` / `ppg_red_samples` can be sent if useful; IR is used as the waveform when `ppg_samples` is absent. Heart rate and SpO₂ are required device-derived values. Respiratory rate is not an input because MAX30102 does not directly measure it. The backend attempts a PPG-derived estimate only with at least 20 seconds of contiguous data at 50 Hz; otherwise the normalized value is `0` (unavailable).

## Normalized ingestion

`POST /ingest/vitals` accepts `patient_id`, `device_id`, timestamp, `heart_rate`, `spo2`, `respiratory_rate`, `ppg_samples`, `signal_quality`, and `source` (`simulator`, `dataset`, or `hardware`).

## Read APIs

| Method | Path | Description |
|---|---|---|
| `GET` | `/vitals/{patient_id}/latest` | Most recent stored reading with risk score and level |
| `GET` | `/vitals/{patient_id}/history?limit=60` | Historical time series; optional `window_minutes` |
| `GET` | `/alerts/{patient_id}?limit=30&unacknowledged_only=false` | Recent alerts |
| `POST` | `/alerts/{alert_id}/acknowledge` | Acknowledge alert |
| `GET` | `/patients` | Patient list |
| `GET` | `/patients/{patient_id}` | Patient details |
| `GET` | `/patients/{patient_id}/profile` | Patient and clinical context in one response |
| `GET` | `/patients/{patient_id}/clinical-history` | Medical history entries |
| `GET` | `/patients/{patient_id}/medications` | Medication records |
| `GET` | `/patients/{patient_id}/allergies` | Allergy records |
| `GET` | `/patients/{patient_id}/clinical-measurements` | Recorded clinical measurements (for example, blood pressure, temperature, glucose) |
| `GET` | `/patients/{patient_id}/labs` | Lab results and reference ranges |
| `GET` | `/patients/{patient_id}/events` | Previous synthetic/clinical events |

Clinical records are separate from sensor telemetry. Demo profiles and their clinical fields are explicitly marked `demo_data: true` and sourced as synthetic clinical records. Live `source` values for telemetry remain `hardware`, `simulator`, and `dataset`.

## Simulator control

- `GET /simulator/status`
- `POST /simulator/start`
- `POST /simulator/stop`
- `POST /simulator/scenario` with `{ "scenario": "hypoxemia", "patient_id": "PATIENT-001" }`

Scenario keys: `normal`, `hypoxemia`, `tachycardia`, `bradycardia`, `tachypnea`, `arrhythmia`, `sensor_disconnect`.

## WebSocket

Connect to `ws://localhost:8000/ws/vitals/{patient_id}`. The server sends `VITAL_UPDATE` packets containing `vital` (including `ppg_samples` and `source`), `risk` (`NORMAL` / `WATCH` / `HIGH_RISK`), and new `alerts`. The client may send `ping` and receives `pong`.

All API timestamps represent UTC instants. Legacy naive timestamps are treated as UTC on response; clients should render them in the viewer's local timezone.

## Response and validation

Hardware ingestion returns status, stored reading ID, risk score/level, and count of newly created alerts. Pydantic rejects missing or out-of-range required HR/SpO₂, malformed sample values, and unsupported source labels. Interactive OpenAPI documentation is available at `/docs`.
