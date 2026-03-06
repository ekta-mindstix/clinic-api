from werkzeug.security import check_password_hash, generate_password_hash

from api.core.enum import RoleEnum
from api.core.extensions import db
from api.models.base import TimestampMixin


class User(TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.Enum(
            RoleEnum,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
            native_enum=False,
        ),
        nullable=False,
        default=RoleEnum.MEMBER,
    )
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    doctor_profile = db.relationship("Doctor", back_populates="user", uselist=False)
    appointments = db.relationship("Appointment", back_populates="member", lazy="selectin")

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    def __repr__(self) -> str:
        return f"<User id={self.id} email='{self.email}' role='{self.role.value}'>"
