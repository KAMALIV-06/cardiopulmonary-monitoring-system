# Cardiopulmonary Monitoring and Early Risk Detection

An Imagine Cup prototype for live cardiopulmonary telemetry. It keeps the existing FastAPI, SQLAlchemy, PostgreSQL, WebSocket, React, alerts, risk analyzer, dataset adapter, and simulator architecture while targeting an **ESP8266 + MAX30102 PPG sensor** for hardware input. There is no ECG sensor in the final hardware path.

The risk engine is a transparent, rule-based baseline, not trained AI and not a medical diagnosis. MAX30102 supplies optical PPG data and device-calculated heart rate/SpO₂. Respiratory rate is not directly measured by MAX30102: the backend estimates it only from at least 20 seconds of PPG; shorter windows yield `0` (unavailable), displayed as `--`.

## Architecture and data flow

```text
ESP8266 + MAX30102 ─┐
Simulator ──────────┼─> Source adapter ─> normalized VitalData (PPG)
Recorded dataset ──┘                         │
                                             ▼
                                   FastAPI validation / PPG SQI
                                             │
                              rule-based risk scoring and alerts
                                             │
                              SQLAlchemy -> PostgreSQL persistence
                                             │
                                   patient WebSocket broadcast
                                             │
                              React dashboard / historical charts
```

All sources use the same contract: `patient_id`, `device_id`, `timestamp`, `heart_rate`, `spo2`, `respiratory_rate`, `ppg_samples`, `signal_quality`, and `source` (`hardware`, `simulator`, or `dataset`). The hardware adapter only converts payloads; it does not access the database. The ESP8266 posts to FastAPI and never connects to PostgreSQL.

Valid hardware data receives a 15 second live-source lease for its patient. Simulator publications for that patient are suppressed while packets continue arriving. If the hardware stops transmitting, simulator telemetry can resume after the lease expires. The React client receives new values over the existing WebSocket without refresh.

## Physiological simulator

The simulator remains enabled for development and starts with the backend. It generates synthetic pulse-shaped PPG windows and scenario vital values at two updates per second. Scenarios include normal, hypoxemia, tachycardia, bradycardia, tachypnea, arrhythmia-like pulse variability, and sensor disconnect. These values are generated demo data, not patient measurements.

## Database and migration

PostgreSQL is required by the application. Set `DATABASE_URL` in `backend/.env` or the process environment; startup checks database connectivity and fails if PostgreSQL is unavailable. Schema migrations are an explicit deployment step using Alembic; startup does not import Alembic, inspect revisions, or create tables.

The repository includes a previously used `backend/cardiopulmonary.db` SQLite file. It remains untouched. It currently contains 1 patient, 4 devices, 10,443 vital readings, and 19 alerts. To preserve these records in PostgreSQL:

1. Configure a PostgreSQL URL and create the target database.
2. For a fresh database run `alembic upgrade head` from `backend/`. For an existing old application schema, inspect it first, then `alembic stamp 20260925_01` followed by `alembic upgrade head`. If the temporary PPG SQL migration was already applied, stamp `20260925_02` after confirming its schema.
3. Run `python scripts/migrate_sqlite_to_postgresql.py` from `backend/`. It requires the Alembic head, reads SQLite read-only, copies all four tables in one PostgreSQL transaction, preserves IDs/timestamps, and skips duplicates. Old ECG samples are copied to `legacy_ecg_samples_json`; PPG samples remain PPG or default to `[]`. It never modifies the SQLite backup.

The migration prints inserted, skipped, and failed counts for each table. Any error rolls back the whole PostgreSQL copy. The source SQLite file remains available as a backup.

### Synthetic patient cohort

After applying migrations, run `python scripts/seed_demo_dataset.py` from `backend/` to insert eight clearly marked synthetic demo profiles with medical history, medications, allergies, clinical measurements, lab results, events, historical dataset readings, and selected historical alerts. The script is idempotent and leaves existing patient IDs unchanged. All clinical context is marked as synthetic demo data and must not be represented as real patient information.

## Run locally (PowerShell)

Backend:

```powershell
cd "C:\Users\Kamali V\Desktop\cardiopulmonary\backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# Apply schema before starting FastAPI.
alembic upgrade head
# Optional: add the synthetic demo cohort for multi-patient screens.
python scripts/seed_demo_dataset.py
uvicorn app.main:app --reload --port 8000
```

Frontend in a second terminal:

```powershell
cd "C:\Users\Kamali V\Desktop\cardiopulmonary\frontend"
npm install
npm run dev
```

Open `http://localhost:5173`; FastAPI's interactive API docs are at `http://localhost:8000/docs`.

## API

Base URL: `http://localhost:8000/api/v1`

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/ingest/hardware` | ESP8266/MAX30102 payload to shared pipeline |
| `POST` | `/ingest/vitals` | Ingest normalized `VitalData` |
| `GET` | `/vitals/{patient_id}/latest` | Latest stored reading and risk fields |
| `GET` | `/vitals/{patient_id}/history` | Historical readings for charts |
| `GET` | `/alerts/{patient_id}` | Recent alerts |
| `POST` | `/alerts/{alert_id}/acknowledge` | Acknowledge an alert |
| `GET/POST` | `/simulator/status`, `/simulator/scenario` | Simulator status and scenario control |
| `POST` | `/simulator/start`, `/simulator/stop` | Start/stop simulator |
| `WS` | `/ws/vitals/{patient_id}` | Live normalized readings, risk and alerts |

Example hardware payload:

```json
{
  "patient_id": "PATIENT-001",
  "device_id": "ESP8266-MAX30102-01",
  "heart_rate": 78,
  "spo2": 97,
  "signal_quality": 0.82,
  "ppg_samples": [0.02, 0.14, 0.41, 0.18, 0.03]
}
```

`timestamp` is optional and defaults to backend time. For PPG-derived respiratory-rate estimation, send at least 1,000 samples at 50 Hz. A short window is accepted, but the estimate is unavailable (`0`) until sufficient sample history is provided.

## Dashboard screens

- **Overview / Live Monitoring:** live PPG waveform, heart rate, SpO₂, estimated respiratory rate, signal quality, risk score/level, alerts, and historical trends.
- **Patients:** current demo patient and monitoring state.
- **Trends:** saved vital history.
- **Alerts:** recent alerts and acknowledgement actions.
- **Devices:** active source, device ID, connection freshness, last seen time, and test controls.
- **Settings:** simulator and fake hardware controls plus local service information.

The UI currently uses the fixed demo patient ID `PATIENT-001`. The fake hardware modal is for development only and has explicit demo input controls; it is not a sensor substitute.

## Hardware setup

Firmware is in [`hardware/esp8266/max30102_monitor.ino`](hardware/esp8266/max30102_monitor.ino). It uses the SparkFun MAX3010x Arduino library (which supports MAX30102) and its bundled heart-rate/SpO₂ example algorithm, ESP8266 Arduino core, and ArduinoJson. Configure Wi-Fi and the backend LAN URL before flashing. Proposed I²C wiring is ESP8266 D2 (SDA) and D1 (SCL); check the exact board and sensor breakout voltage requirements. See [`docs/hardware_esp8266_guide.md`](docs/hardware_esp8266_guide.md).

Firmware sends a rolling 20 second PPG history and device-calculated heart rate/SpO₂ to FastAPI over HTTP. The 20 second buffer permits the backend's conservative PPG modulation estimate. Signal quality sent by firmware is a simple optical contact/pulsatility heuristic, not a validated clinical SQI.

## Project structure

```text
backend/app/       FastAPI routes, Pydantic schemas, SQLAlchemy models, services
backend/alembic/   Versioned PostgreSQL schema migrations
backend/scripts/   Transactional SQLite to PostgreSQL data copy
frontend/src/      React dashboard, PPG canvas, WebSocket hook, REST client
hardware/esp8266/  MAX30102 firmware
simulator/         Synthetic PPG data and scenarios
docs/              Architecture, API, database, hardware documentation
```

Deployment configuration and exact Alembic commands are in [`docs/deployment.md`](docs/deployment.md).

## Current limitations

- The dataset adapter normalizes caller-supplied records; there is no bundled PhysioNet/MIT-BIH dataset loader or replay UI.
- PPG respiratory-rate estimate is intentionally unavailable unless sufficient contiguous sample data is supplied. The current simulator sends only short windows and supplies its own simulated RR.
- Hardware firmware and physical sensor wiring have not been compiled or bench-tested on an ESP8266/MAX30102 board in this workspace.
- Historical ECG samples from older databases are retained only as legacy archive data. They are never exposed as PPG or used for new live processing.
- The baseline risk thresholds and optical SQI heuristic are prototypes, not clinically validated tools.
