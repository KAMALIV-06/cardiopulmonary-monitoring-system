"""Copy the local SQLite backup into the current Alembic-managed PostgreSQL schema.

The SQLite file is opened read-only. All PostgreSQL inserts run in one transaction;
primary/unique conflicts are skipped, making successful runs safe to repeat.
Run from backend/ after `alembic upgrade head`.
"""
import asyncio
import datetime
import sqlite3
from pathlib import Path
from typing import Any

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import MetaData, Table, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import BACKEND_DIR, settings

SOURCE = BACKEND_DIR / "cardiopulmonary.db"
BATCH_SIZE = 250
TABLE_PLAN = (
    ("patients", "id", ("id", "name", "age", "gender", "medical_record_number", "baseline_notes", "created_at")),
    ("devices", "id", ("id", "device_type", "mac_address", "status", "last_seen")),
    ("vital_readings", "id", (
        "id", "patient_id", "device_id", "timestamp", "heart_rate", "spo2",
        "respiratory_rate", "ppg_samples_json", "legacy_ecg_samples_json",
        "signal_quality", "source", "risk_score", "risk_level",
    )),
    ("clinical_alerts", "id", (
        "id", "patient_id", "timestamp", "alert_type", "severity", "message",
        "trigger_value", "acknowledged",
    )),
)


def current_alembic_heads() -> list[str]:
    cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    return ScriptDirectory.from_config(cfg).get_heads()


def sqlite_rows(source: sqlite3.Connection, table: str) -> list[sqlite3.Row]:
    return source.execute(f'SELECT * FROM "{table}"').fetchall()


def parse_timestamp(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    result = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo:
        return result.astimezone(datetime.timezone.utc).replace(tzinfo=None)
    return result


def normalize_row(table: str, source_row: sqlite3.Row, target_columns: set[str]) -> dict[str, Any]:
    source_columns = set(source_row.keys())
    data: dict[str, Any] = {}
    for column in target_columns:
        if column in source_columns:
            data[column] = source_row[column]

    for date_column in ("created_at", "last_seen", "timestamp"):
        if date_column in data:
            data[date_column] = parse_timestamp(data[date_column])

    if table == "vital_readings":
        data["ppg_samples_json"] = source_row["ppg_samples_json"] if "ppg_samples_json" in source_columns else "[]"
        if "legacy_ecg_samples_json" in target_columns:
            if "legacy_ecg_samples_json" in source_columns:
                data["legacy_ecg_samples_json"] = source_row["legacy_ecg_samples_json"]
            elif "ecg_samples_json" in source_columns:
                data["legacy_ecg_samples_json"] = source_row["ecg_samples_json"]
            else:
                data["legacy_ecg_samples_json"] = None
    if table == "clinical_alerts" and "acknowledged" in data:
        data["acknowledged"] = bool(data["acknowledged"])
    return data


async def verify_target(conn) -> None:
    heads = current_alembic_heads()
    if len(heads) != 1:
        raise RuntimeError(f"Expected one Alembic head, found {heads}")
    revision = (await conn.execute(text("SELECT version_num FROM alembic_version"))).scalar_one_or_none()
    if revision != heads[0]:
        raise RuntimeError(f"PostgreSQL schema revision is {revision!r}, expected Alembic head {heads[0]!r}; run `alembic upgrade head`.")
    expected = {name for name, _, _ in TABLE_PLAN}
    present = set((await conn.execute(text(
        "SELECT table_name FROM information_schema.tables WHERE table_schema=current_schema()"
    ))).scalars())
    if not expected.issubset(present):
        raise RuntimeError(f"PostgreSQL schema is missing tables: {sorted(expected - present)}")


async def migrate() -> dict[str, dict[str, int]]:
    if not SOURCE.exists():
        raise FileNotFoundError(f"SQLite source not found: {SOURCE}")
    source = sqlite3.connect(SOURCE.resolve().as_uri() + "?mode=ro", uri=True)
    source.row_factory = sqlite3.Row
    engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
    stats = {table: {"attempted": 0, "inserted": 0, "skipped": 0, "failed": 0} for table, _, _ in TABLE_PLAN}
    all_rows: dict[str, list[sqlite3.Row]] = {}
    try:
        source_tables = {row[0] for row in source.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        required_tables = {table for table, _, _ in TABLE_PLAN}
        if not required_tables.issubset(source_tables):
            raise RuntimeError(f"SQLite backup is missing tables: {sorted(required_tables - source_tables)}")
        for table, _, _ in TABLE_PLAN:
            all_rows[table] = sqlite_rows(source, table)

        async with engine.begin() as conn:
            await verify_target(conn)
            def reflect(sync_conn):
                metadata = MetaData()
                metadata.reflect(bind=sync_conn)
                return metadata

            reflected = await conn.run_sync(reflect)
            for table_name, key, planned_columns in TABLE_PLAN:
                target = reflected.tables[table_name]
                target_columns = {column.name for column in target.columns}
                required_columns = set(planned_columns)
                if not required_columns.issubset(target_columns):
                    raise RuntimeError(f"PostgreSQL {table_name} is missing columns: {sorted(required_columns - target_columns)}")
                rows = all_rows[table_name]
                for start in range(0, len(rows), BATCH_SIZE):
                    batch = [normalize_row(table_name, row, target_columns) for row in rows[start:start + BATCH_SIZE]]
                    stats[table_name]["attempted"] += len(batch)
                    statement = (
                        pg_insert(target)
                        .values(batch)
                        .on_conflict_do_nothing()
                        .returning(target.c[key])
                    )
                    inserted_ids = (await conn.execute(statement)).scalars().all()
                    stats[table_name]["inserted"] += len(inserted_ids)
                    stats[table_name]["skipped"] += len(batch) - len(inserted_ids)

            for table in ("vital_readings", "clinical_alerts"):
                await conn.execute(text(
                    f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
                    f"COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM {table}"
                ))
        return stats
    except Exception as exc:
        # The engine.begin() context has rolled back every PostgreSQL insert.
        for table in stats:
            stats[table]["failed"] = stats[table]["attempted"]
            stats[table]["inserted"] = 0
            stats[table]["skipped"] = 0
        exc.migration_stats = stats
        raise
    finally:
        source.close()
        await engine.dispose()


async def main() -> None:
    try:
        stats = await migrate()
    except Exception as exc:
        print(f"Migration failed and PostgreSQL transaction rolled back: {type(exc).__name__}.")
        for table, counts in getattr(exc, "migration_stats", {}).items():
            print(f"{table}: inserted={counts['inserted']} skipped={counts['skipped']} failed={counts['failed']}")
        raise SystemExit(1) from exc
    print("SQLite backup was read-only; PostgreSQL transaction committed.")
    for table, counts in stats.items():
        print(f"{table}: inserted={counts['inserted']} skipped={counts['skipped']} failed={counts['failed']}")


if __name__ == "__main__":
    asyncio.run(main())
