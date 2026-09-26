# Database Schema and Migrations

PostgreSQL is required for the application. SQLAlchemy async models define metadata; Alembic is the only schema lifecycle tool. FastAPI startup verifies PostgreSQL connectivity only and never imports Alembic or creates/alters tables.

## Current entities

- **patients:** ID, name, age, gender, medical record number, baseline notes, creation timestamp.
- **devices:** ID, type/source, optional MAC, status, last seen.
- **vital_readings:** primary ID, patient/device foreign keys, timestamp, HR, SpO₂, RR, `ppg_samples_json`, signal quality, source, risk score, risk level, and nullable `legacy_ecg_samples_json` archive.
- **clinical_alerts:** primary ID, patient foreign key, timestamp, alert type, severity, message, trigger value, acknowledged flag.
- **medical_history, medications, allergies, clinical_measurements, lab_results, patient_events:** additive patient-linked clinical context. Demo cohort rows are synthetic and explicitly marked on the patient.

New telemetry uses PPG. Legacy waveform values are preserved as legacy data only, never interpreted as PPG. The relationships and patient/timestamp and patient/acknowledgement indexes are created by Alembic.

## Alembic revisions

- `20260925_01`: initial schema matching the pre-PPG deployment (including the old waveform column).
- `20260925_02`: add `ppg_samples_json`, rename the old waveform column to `legacy_ecg_samples_json`, and make the legacy field nullable.
- `20260926_03` (**head**): add patient demographics/status fields, clinical context tables, and an optional link from alerts to the triggering vital reading. Existing patient, device, vital, and alert rows are retained.

Fresh database:

```powershell
cd backend
alembic upgrade head
```

To populate the patient-centric screens with eight synthetic-only records after migration:

```powershell
python scripts/seed_demo_dataset.py
```

The seed command is idempotent and does not overwrite existing patient IDs.

For an existing original schema created before Alembic, first verify that its tables and old waveform column match revision 01, then adopt and upgrade:

```powershell
alembic stamp 20260925_01
alembic upgrade head
```

If the temporary PPG SQL migration has already been applied, verify that both `ppg_samples_json` and `legacy_ecg_samples_json` exist, then stamp `20260925_02`. Do not stamp an uninspected schema. Downgrading is intentionally blocked because removing PPG data would be destructive.

## Copy local SQLite data

The existing `backend/cardiopulmonary.db` backup is opened read-only. After PostgreSQL is configured and migrated to Alembic head:

```powershell
cd backend
python scripts/migrate_sqlite_to_postgresql.py
```

The script copies patients, devices, readings, and alerts in foreign-key order in one transaction. It preserves timestamps and IDs when unique, skips conflicts so reruns do not duplicate rows, maps old ECG JSON to the legacy archive, and initializes missing PPG JSON to `[]`. A failure rolls back all PostgreSQL inserts. The SQLite file is not changed.

## Configuration

Set `DATABASE_URL` through `backend/.env` or the process environment:

```env
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DATABASE
```

There is no SQLite fallback. Never commit secrets. See [`deployment.md`](deployment.md) for development/production configuration and deployment steps.
