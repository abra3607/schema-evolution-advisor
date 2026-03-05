"""Drop legacy tables and columns

Revision ID: abc003
Revises: abc002
Create Date: 2024-03-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "abc003"
down_revision = "abc002"


def upgrade():
    op.drop_column("users", "bio")
    op.drop_table("legacy_sessions")


def downgrade():
    op.create_table(
        "legacy_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("token", sa.String(255)),
    )
    op.add_column("users", sa.Column("bio", sa.Text(), nullable=True))
