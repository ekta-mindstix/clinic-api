from api.core.enum import RoleEnum
from api.core.extensions import db
from api.models.base import TimestampMixin


class User(TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    full_name = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=RoleEnum.MEMBER.value)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    doctor_profile = db.relationship("Doctor", back_populates="user", uselist=False)
