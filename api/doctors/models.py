from api.core.extensions import db
from api.models.base import TimestampMixin


doctor_departments = db.Table(
    "doctor_departments",
    db.Column("doctor_id", db.Integer, db.ForeignKey("doctors.id"), primary_key=True),
    db.Column("department_id", db.Integer, db.ForeignKey("departments.id"), primary_key=True),
)


class Doctor(TimestampMixin, db.Model):
    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    license_number = db.Column(db.String(120), nullable=False, unique=True)
    specialty = db.Column(db.String(120), nullable=True)

    user = db.relationship("User", back_populates="doctor_profile")
    departments = db.relationship(
        "Department",
        secondary=doctor_departments,
        back_populates="doctors",
        lazy="selectin",
    )
