from api.core.extensions import db
from api.models.base import TimestampMixin


class Department(TimestampMixin, db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    doctors = db.relationship(
        "Doctor",
        secondary="doctor_departments",
        back_populates="departments",
        lazy="selectin",
    )
