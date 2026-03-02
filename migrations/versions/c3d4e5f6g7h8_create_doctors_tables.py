"""create doctors tables

Revision ID: c3d4e5f6g7h8
Revises: b1c2d3e4f5g6
Create Date: 2026-03-01 00:10:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "c3d4e5f6g7h8"
down_revision = "b1c2d3e4f5g6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "doctors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("license_number", sa.String(length=120), nullable=False),
        sa.Column("specialty", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("license_number"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_table(
        "doctor_departments",
        sa.Column("doctor_id", sa.Integer(), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["doctor_id"], ["doctors.id"]),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"]),
        sa.PrimaryKeyConstraint("doctor_id", "department_id"),
    )


def downgrade():
    op.drop_table("doctor_departments")
    op.drop_table("doctors")
