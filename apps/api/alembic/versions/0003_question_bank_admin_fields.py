"""add admin question bank fields

Revision ID: 0003_question_bank_admin_fields
Revises: 0002_assessment_engine_phase1
Create Date: 2026-04-14
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0003_question_bank_admin_fields"
down_revision = "0002_assessment_engine_phase1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "question_bank",
        sa.Column("active_in_scoring", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.add_column("question_bank", sa.Column("experiment_tag", sa.String(), nullable=True))
    op.add_column("question_bank", sa.Column("experiment_mode", sa.String(), nullable=True))
    op.add_column(
        "question_bank",
        sa.Column("boundary_metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("question_bank", "boundary_metadata_json")
    op.drop_column("question_bank", "experiment_mode")
    op.drop_column("question_bank", "experiment_tag")
    op.drop_column("question_bank", "active_in_scoring")
