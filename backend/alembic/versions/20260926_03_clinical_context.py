"""Add synthetic-demo clinical profile records and alert-to-reading links.

Revision ID: 20260926_03
Revises: 20260925_02
"""
from alembic import op
import sqlalchemy as sa

revision = "20260926_03"
down_revision = "20260925_02"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("patients", sa.Column("date_of_birth", sa.Date(), nullable=True))
    op.add_column("patients", sa.Column("height_cm", sa.Float(), nullable=True))
    op.add_column("patients", sa.Column("weight_kg", sa.Float(), nullable=True))
    op.add_column("patients", sa.Column("monitoring_status", sa.String(24), server_default="active", nullable=False))
    op.add_column("patients", sa.Column("demo_data", sa.Boolean(), server_default=sa.false(), nullable=False))
    op.add_column("clinical_alerts", sa.Column("vital_reading_id", sa.Integer(), nullable=True))
    op.create_index("ix_clinical_alerts_vital_reading_id", "clinical_alerts", ["vital_reading_id"])
    op.create_foreign_key(
        "fk_clinical_alerts_vital_reading_id_vital_readings",
        "clinical_alerts", "vital_readings", ["vital_reading_id"], ["id"], ondelete="SET NULL",
    )

    def common_columns():
        return [
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("patient_id", sa.String(64), sa.ForeignKey("patients.id", ondelete="CASCADE"), nullable=False),
        ]
    for table in ("medical_history", "medications", "allergies", "clinical_measurements", "lab_results", "patient_events"):
        op.create_table(table, *common_columns())
        op.create_index(f"ix_{table}_patient_id", table, ["patient_id"])

    op.add_column("medical_history", sa.Column("condition_name", sa.String(128), nullable=False))
    op.add_column("medical_history", sa.Column("diagnosis_date", sa.Date(), nullable=True))
    op.add_column("medical_history", sa.Column("status", sa.String(32), server_default="active", nullable=False))
    op.add_column("medical_history", sa.Column("notes", sa.Text(), nullable=True))

    op.add_column("medications", sa.Column("medication_name", sa.String(128), nullable=False))
    op.add_column("medications", sa.Column("dosage", sa.String(64), nullable=False))
    op.add_column("medications", sa.Column("frequency", sa.String(128), nullable=False))
    op.add_column("medications", sa.Column("start_date", sa.Date(), nullable=True))
    op.add_column("medications", sa.Column("end_date", sa.Date(), nullable=True))
    op.add_column("medications", sa.Column("notes", sa.Text(), nullable=True))

    op.add_column("allergies", sa.Column("allergen", sa.String(128), nullable=False))
    op.add_column("allergies", sa.Column("reaction", sa.String(128), nullable=False))
    op.add_column("allergies", sa.Column("severity", sa.String(24), nullable=False))
    op.add_column("allergies", sa.Column("notes", sa.Text(), nullable=True))

    op.add_column("clinical_measurements", sa.Column("measurement_type", sa.String(64), nullable=False))
    op.add_column("clinical_measurements", sa.Column("value", sa.Float(), nullable=False))
    op.add_column("clinical_measurements", sa.Column("unit", sa.String(32), nullable=False))
    op.add_column("clinical_measurements", sa.Column("measured_at", sa.DateTime(timezone=True), nullable=False))
    op.add_column("clinical_measurements", sa.Column("source", sa.String(32), server_default="CLINICAL_RECORD", nullable=False))
    op.add_column("clinical_measurements", sa.Column("notes", sa.Text(), nullable=True))

    op.add_column("lab_results", sa.Column("test_name", sa.String(128), nullable=False))
    op.add_column("lab_results", sa.Column("value", sa.Float(), nullable=False))
    op.add_column("lab_results", sa.Column("unit", sa.String(32), nullable=False))
    op.add_column("lab_results", sa.Column("reference_range", sa.String(64), nullable=True))
    op.add_column("lab_results", sa.Column("measured_at", sa.DateTime(timezone=True), nullable=False))
    op.add_column("lab_results", sa.Column("source", sa.String(32), server_default="CLINICAL_RECORD", nullable=False))
    op.add_column("lab_results", sa.Column("notes", sa.Text(), nullable=True))

    op.add_column("patient_events", sa.Column("event_type", sa.String(64), nullable=False))
    op.add_column("patient_events", sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False))
    op.add_column("patient_events", sa.Column("summary", sa.Text(), nullable=False))
    op.add_column("patient_events", sa.Column("source", sa.String(32), server_default="CLINICAL_RECORD", nullable=False))


def downgrade() -> None:
    raise RuntimeError("Clinical records and alert links are retained; restore from backup before removing these tables.")
