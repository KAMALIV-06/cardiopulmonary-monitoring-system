# Deployment and Environment Configuration

The application requires PostgreSQL. FastAPI startup verifies connectivity only; it does not import Alembic, inspect revisions, or create schema. Deployments must run Alembic before starting the web service.

## Backend environment

Copy `backend/.env.example` to `backend/.env` for local development, or provide the values through the deployment platform's secret/environment manager. Do not commit `.env` or credentials.

| Variable | Purpose |
|---|---|
| `APP_ENV` | `development`, `production`, or `test`; production rejects localhost/wildcard CORS origins |
| `DATABASE_URL` | Required PostgreSQL async URL, `postgresql+asyncpg://...`; SQLite is rejected |
| `CORS_ORIGINS` | JSON array of exact frontend origins; used for REST CORS and WebSocket Origin validation |
| `AUTO_START_SIMULATOR` | `true` for a demo without hardware; usually `false` when relying on live hardware in production |
| `PROJECT_NAME` | FastAPI service title |
| `API_V1_STR` | REST API prefix, default `/api/v1` |
| `DEFAULT_PATIENT_ID` | Default telemetry patient identifier |
| `DEFAULT_DEVICE_ID` | Default device identifier |

Example production values (substitute actual deployment origins/URL privately):

```env
APP_ENV=production
DATABASE_URL=postgresql+asyncpg://APP_USER:APP_PASSWORD@DB_HOST:5432/cardiopulmonary
CORS_ORIGINS=["https://monitor.example.com"]
AUTO_START_SIMULATOR=false
```

Use a managed secret store for `DATABASE_URL`; do not paste a real URL into docs or source control. Restrict PostgreSQL network access to the backend service. Back up the database before schema changes.

## Schema and SQLite copy

Fresh PostgreSQL database:

```powershell
cd backend
alembic upgrade head
alembic current
alembic heads
```

Existing unversioned database with the original pre-PPG schema: inspect the tables/columns first, then adopt the matching baseline and upgrade:

```powershell
cd backend
alembic stamp 20260925_01
alembic upgrade head
```

If the temporary PPG SQL change was already applied, verify `ppg_samples_json` and `legacy_ecg_samples_json` then stamp `20260925_02`. Do not stamp a database whose schema has not been inspected. `downgrade` is blocked because dropping PPG data is unsafe.

To import the unchanged local SQLite backup, run after the schema is at head:

```powershell
cd backend
python scripts/migrate_sqlite_to_postgresql.py
```

The copy is transactional and repeatable. It preserves unique IDs/timestamps, skips conflicts, retains old waveform JSON in the legacy column, and prints inserted/skipped/failed row counts. The SQLite file is read-only throughout.

## Backend deployment

Install `backend/requirements.txt`, configure environment variables, then run migrations as a release step. Start FastAPI behind a process manager/reverse proxy, for example:

```powershell
cd backend
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Terminate TLS at the proxy or use a TLS-capable platform. Configure the proxy for WebSocket upgrades on `/ws/vitals/` and preserve long-lived connections. Ensure its public origin appears exactly in `CORS_ORIGINS`.

## Frontend deployment

Set these Vite variables at build time (see `frontend/.env.example`):

| Variable | Example | Purpose |
|---|---|---|
| `VITE_API_BASE_URL` | `https://api.example.com/api/v1` | REST API base |
| `VITE_WS_BASE_URL` | `wss://api.example.com` | WebSocket origin; TLS deployments must use `wss` |

Then run `npm ci` and `npm run build` from `frontend/`, and serve `dist/` through the chosen static hosting provider. These values are compiled into the bundle; rebuild after changing them.

## ESP8266 deployment

Set `WIFI_SSID`, `WIFI_PASSWORD`, `API_BASE_URL`, `API_ROOT_CA_PEM`, `PATIENT_ID`, and `DEVICE_ID` in the firmware before compiling. `API_BASE_URL` is the deployed FastAPI origin only; firmware appends `/api/v1/ingest/hardware`. For HTTPS, configure the server's public root CA so the TLS certificate is verified. The firmware contains no PostgreSQL URL or credentials.

## Local development

For local UI work, use `APP_ENV=development`, a local PostgreSQL `DATABASE_URL`, `CORS_ORIGINS=["http://localhost:5173"]`, and `AUTO_START_SIMULATOR=true`. Alembic still must be run before FastAPI. The SQLite file is a backup/import source, not an application fallback.
