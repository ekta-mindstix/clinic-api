"""adding indices

Revision ID: dedeb6d32b44
Revises: c3d4e5f6g7h8
Create Date: 2026-03-01 00:15:00.000000
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "dedeb6d32b44"
down_revision = "c3d4e5f6g7h8"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_departments_name", "departments", ["name"], unique=True)
    op.create_index("ix_doctors_license_number", "doctors", ["license_number"], unique=True)


def downgrade():
    op.drop_index("ix_doctors_license_number", table_name="doctors")
    op.drop_index("ix_departments_name", table_name="departments")
    op.drop_index("ix_users_email", table_name="users")
