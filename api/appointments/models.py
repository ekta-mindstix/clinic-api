from api.core.extensions import db
from api.models.base import TimestampMixin


class Appointment(TimestampMixin, db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False, index=True)
    member_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    appointment_at = db.Column(db.DateTime, nullable=False)
    notes = db.Column(db.String(255), nullable=True)

    doctor = db.relationship("Doctor", back_populates="appointments")
    member = db.relationship("User", back_populates="appointments")

    __table_args__ = (
        db.UniqueConstraint("doctor_id", "appointment_at", name="uq_doctor_appointment_at"),
    )

    def __repr__(self) -> str:
        return f"<Appointment id={self.id} doctor_id={self.doctor_id} member_id={self.member_id} at='{self.appointment_at}'>"
