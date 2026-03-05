"""Alter column types and drop index

Revision ID: abc002
Revises: abc001
Create Date: 2024-02-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "abc002"
down_revision = "abc001"


def upgrade():
    op.alter_column("users", "name", type_=sa.Text(), existing_type=sa.String(100))
    op.drop_index("ix_users_email", table_name="users")
    op.add_column("users", sa.Column("age", sa.Integer(), nullable=False))


def downgrade():
    op.drop_column("users", "age")
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.alter_column("users", "name", type_=sa.String(100), existing_type=sa.Text())
