"""Initial schema before the PPG waveform transition.

Revision ID: 20260925_01
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "20260925_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "patients",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("gender", sa.String(16), nullable=False),
        sa.Column("medical_record_number", sa.String(64), nullable=True),
        sa.Column("baseline_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_patients_id", "patients", ["id"])
    op.create_index("ix_patients_medical_record_number", "patients", ["medical_record_number"], unique=True)

    op.create_table(
        "devices",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("device_type", sa.String(32), server_default="simulator", nullable=True),
        sa.Column("mac_address", sa.String(32), nullable=True),
        sa.Column("status", sa.String(16), server_default="active", nullable=True),
        sa.Column("last_seen", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_devices_id", "devices", ["id"])

    op.create_table(
        "vital_readings",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("patient_id", sa.String(64), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("device_id", sa.String(64), sa.ForeignKey("devices.id"), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.Column("heart_rate", sa.Float(), nullable=False),
        sa.Column("spo2", sa.Float(), nullable=False),
        sa.Column("respiratory_rate", sa.Float(), nullable=False),
        sa.Column("ecg_samples_json", sa.Text(), nullable=False),
        sa.Column("signal_quality", sa.Float(), nullable=False),
        sa.Column("source", sa.String(32), nullable=False),
        sa.Column("risk_score", sa.Float(), server_default="0.0", nullable=True),
        sa.Column("risk_level", sa.String(16), server_default="NORMAL", nullable=True),
    )
    op.create_index("ix_vital_readings_patient_id", "vital_readings", ["patient_id"])
    op.create_index("ix_vital_readings_timestamp", "vital_readings", ["timestamp"])
    op.create_index("idx_patient_timestamp", "vital_readings", ["patient_id", "timestamp"])

    op.create_table(
        "clinical_alerts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("patient_id", sa.String(64), sa.ForeignKey("patients.id"), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.Column("alert_type", sa.String(64), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False),
        sa.Column("message", sa.String(256), nullable=False),
        sa.Column("trigger_value", sa.Float(), nullable=True),
        sa.Column("acknowledged", sa.Boolean(), server_default=sa.false(), nullable=True),
    )
    op.create_index("ix_clinical_alerts_patient_id", "clinical_alerts", ["patient_id"])
    op.create_index("ix_clinical_alerts_timestamp", "clinical_alerts", ["timestamp"])
    op.create_index("idx_alert_patient_ack", "clinical_alerts", ["patient_id", "acknowledged"])


def downgrade() -> None:
    raise RuntimeError("Initial schema tables contain application data and will not be dropped by downgrade.")
