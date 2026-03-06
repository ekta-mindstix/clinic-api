from api.core.extensions import db
from api.models.base import TimestampMixin


doctor_departments = db.Table(
    "doctor_departments",
    db.Column("doctor_id", db.Integer, db.ForeignKey("doctors.id"), primary_key=True),
    db.Column("department_id", db.Integer, db.ForeignKey("departments.id"), primary_key=True),
)


class DoctorAvailability(TimestampMixin, db.Model):
    __tablename__ = "doctor_availabilities"

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False, index=True)
    start_at = db.Column(db.DateTime, nullable=False)
    end_at = db.Column(db.DateTime, nullable=False)

    doctor = db.relationship("Doctor", back_populates="availabilities")

    def __repr__(self) -> str:
        return f"<DoctorAvailability id={self.id} doctor_id={self.doctor_id} start_at='{self.start_at}' end_at='{self.end_at}'>"


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
    availabilities = db.relationship("DoctorAvailability", back_populates="doctor", lazy="selectin")
    appointments = db.relationship("Appointment", back_populates="doctor", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Doctor id={self.id} user_id={self.user_id} license='{self.license_number}'>"
