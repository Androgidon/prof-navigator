"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma}
Create Date: ${create_date}
"""
\n+from alembic import op
import sqlalchemy as sa
\n+\n+def upgrade() -> None:
    pass
\n+\n+def downgrade() -> None:
    pass
