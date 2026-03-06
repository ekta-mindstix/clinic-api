"""create appointment tables

Revision ID: 9a8b7c6d5e4f
Revises: dedeb6d32b44
Create Date: 2026-03-06 00:30:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "9a8b7c6d5e4f"
down_revision = "dedeb6d32b44"
branch_labels = None
depends_on = None


def _index_exists(inspector, table_name: str, index_name: str) -> bool:
    return any(idx.get("name") == index_name for idx in inspector.get_indexes(table_name))


def _unique_exists(inspector, table_name: str, constraint_name: str) -> bool:
    return any(uc.get("name") == constraint_name for uc in inspector.get_unique_constraints(table_name))


def _table_columns(inspector, table_name: str) -> set[str]:
    return {column["name"] for column in inspector.get_columns(table_name)}


def _create_doctor_availabilities_table() -> None:
    op.create_table(
        "doctor_availabilities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("doctor_id", sa.Integer(), nullable=False),
        sa.Column("start_at", sa.DateTime(), nullable=False),
        sa.Column("end_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["doctor_id"], ["doctors.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def _create_appointments_table() -> None:
    op.create_table(
        "appointments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("doctor_id", sa.Integer(), nullable=False),
        sa.Column("member_id", sa.Integer(), nullable=False),
        sa.Column("appointment_at", sa.DateTime(), nullable=False),
        sa.Column("notes", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["doctor_id"], ["doctors.id"]),
        sa.ForeignKeyConstraint(["member_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("doctor_id", "appointment_at", name="uq_doctor_appointment_at"),
    )


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("doctor_availabilities"):
        _create_doctor_availabilities_table()
        inspector = sa.inspect(bind)

    if not _index_exists(inspector, "doctor_availabilities", "ix_doctor_availabilities_doctor_id"):
        op.create_index("ix_doctor_availabilities_doctor_id", "doctor_availabilities", ["doctor_id"], unique=False)

    if inspector.has_table("appointments"):
        columns = _table_columns(inspector, "appointments")
        required = {"doctor_id", "member_id", "appointment_at"}

        if not required.issubset(columns):
            legacy_name = "appointments_legacy_9a8b7c6d5e4f"
            if not inspector.has_table(legacy_name):
                op.rename_table("appointments", legacy_name)
                inspector = sa.inspect(bind)
            else:
                # If legacy table already exists from a prior failed attempt,
                # drop the broken appointments table and recreate cleanly.
                op.drop_table("appointments")
                inspector = sa.inspect(bind)

    if not inspector.has_table("appointments"):
        _create_appointments_table()
        inspector = sa.inspect(bind)

    if not _unique_exists(inspector, "appointments", "uq_doctor_appointment_at"):
        columns = _table_columns(inspector, "appointments")
        if {"doctor_id", "appointment_at"}.issubset(columns):
            op.create_unique_constraint("uq_doctor_appointment_at", "appointments", ["doctor_id", "appointment_at"])
            inspector = sa.inspect(bind)

    if not _index_exists(inspector, "appointments", "ix_appointments_doctor_id"):
        if "doctor_id" in _table_columns(inspector, "appointments"):
            op.create_index("ix_appointments_doctor_id", "appointments", ["doctor_id"], unique=False)
            inspector = sa.inspect(bind)

    if not _index_exists(inspector, "appointments", "ix_appointments_member_id"):
        if "member_id" in _table_columns(inspector, "appointments"):
            op.create_index("ix_appointments_member_id", "appointments", ["member_id"], unique=False)


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table("appointments"):
        if _index_exists(inspector, "appointments", "ix_appointments_member_id"):
            op.drop_index("ix_appointments_member_id", table_name="appointments")
        if _index_exists(inspector, "appointments", "ix_appointments_doctor_id"):
            op.drop_index("ix_appointments_doctor_id", table_name="appointments")
        op.drop_table("appointments")

    inspector = sa.inspect(bind)
    if inspector.has_table("doctor_availabilities"):
        if _index_exists(inspector, "doctor_availabilities", "ix_doctor_availabilities_doctor_id"):
            op.drop_index("ix_doctor_availabilities_doctor_id", table_name="doctor_availabilities")
        op.drop_table("doctor_availabilities")
