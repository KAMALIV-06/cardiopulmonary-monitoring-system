# Architecture

## Hardware target and invariant

Final physical source: **MAX30102 PPG sensor + ESP8266 + Li-ion battery**. The MAX30102 provides red/infrared optical signals used for PPG, heart rate, and SpO₂ estimates. It does not directly measure respiratory rate. No ECG/AD8232 hardware is part of this target.

The existing application structure remains:

```text
ESP8266/MAX30102 ─┐
Simulator ────────┼─> Source adapters ─> VitalData
Recorded dataset ┘                       │
                                         ▼
                              FastAPI ingest/validation
                                         │
                           PPG filtering and signal quality
                                         │
                             rule-based risk and alerts
                                         │
                            SQLAlchemy / PostgreSQL
                                         │
                              WebSocket telemetry
                                         │
                                React dashboard
```

`VitalData` is the hardware-independent contract: patient/device identifiers, timestamp, heart rate, SpO₂, respiratory-rate value, PPG samples, signal quality, and source. The hardware adapter contains no database or UI logic. The device only posts to FastAPI; it does not connect to PostgreSQL.

## Hardware packet and normalization

`POST /api/v1/ingest/hardware` accepts patient/device identifiers, optional timestamp, a PPG sample window (or raw IR samples), heart rate, SpO₂, and optional signal quality. `HardwareAdapter` normalizes this payload and sets `source="hardware"`. The backend derives respiratory rate from PPG only when at least 20 seconds of samples are available at the assumed 50 Hz; otherwise it sets `0` to mean unavailable. MAX30102 is not described as a direct respiration sensor.

The simulator adapter and dataset adapter produce the same normalized contract. Dataset support is an adapter only; no dataset importer or replay controller is included.

## Ingestion pipeline

1. FastAPI validates the normalized schema.
2. PPG samples are centered/smoothed for quality assessment. A bounded amplitude-spread heuristic estimates SQI; it is not clinically validated.
3. A rule-based risk analyzer evaluates HR, SpO₂, RR, and SQI, returning `risk_score`, `risk_level` (`NORMAL`, `WATCH`, `HIGH_RISK`), confidence, factors, and recommendations.
4. SQLAlchemy writes the vital, patient/device records, risk result, and any generated alerts.
5. The WebSocket manager sends `VITAL_UPDATE` with vital, risk, and new alerts to subscribers for that patient.
6. React updates current values and appends PPG samples to its waveform buffer without a page refresh.

## Simulator and source arbitration

The simulator remains enabled for development and produces synthetic PPG pulse windows and vitals. Valid hardware packets renew a 15 second lease for the same patient. During the lease, simulator telemetry for that patient is not published. If packets cease, the lease expires and the simulator resumes. The source is carried in every normalized reading and displayed by the dashboard.

## Persistence and migrations

SQLAlchemy async models represent `patients`, `devices`, `vital_readings`, and `clinical_alerts`. PostgreSQL is required. Alembic owns schema creation and upgrades; FastAPI startup checks the database and current revision but never calls `create_all()`.

Old SQLite records are not automatically copied or deleted. `backend/scripts/migrate_sqlite_to_postgresql.py` reads the existing SQLite database in read-only mode and copies records to Alembic-managed PostgreSQL in one transaction. It preserves IDs/timestamps and archives old waveform JSON separately; old data is not interpreted as PPG.

## Signal and risk scope

PPG filtering and SQI are lightweight prototype operations. Respiratory rate estimation uses the dominant respiratory-band modulation in an adequately long PPG envelope. HRV/QRS/Pan-Tompkins processing is not part of the PPG live path. Risk outputs are a transparent early warning baseline, not a trained AI classifier or diagnosis.
