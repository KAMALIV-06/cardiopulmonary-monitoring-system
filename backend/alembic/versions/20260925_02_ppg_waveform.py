"""Replace active waveform storage with PPG while preserving old samples.

Revision ID: 20260925_02
Revises: 20260925_01
"""
from alembic import op
import sqlalchemy as sa

revision = "20260925_02"
down_revision = "20260925_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "vital_readings",
        sa.Column("ppg_samples_json", sa.Text(), nullable=False, server_default="[]"),
    )
    op.alter_column("vital_readings", "ecg_samples_json", new_column_name="legacy_ecg_samples_json")
    op.alter_column("vital_readings", "legacy_ecg_samples_json", existing_type=sa.Text(), nullable=True)


def downgrade() -> None:
    raise RuntimeError("PPG waveform data cannot be removed safely; restore from backup instead of downgrading.")
