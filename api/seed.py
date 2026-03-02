from api.auth.models import User
from api.core.enum import RoleEnum
from api.core.extensions import db
from api.core.security import hash_password
from api.departments.models import Department
from api.doctors.models import Doctor


def seed_data() -> None:
    admin = User.query.filter_by(email="admin@clinic.local").first()
    if not admin:
        admin = User(
            email="admin@clinic.local",
            full_name="System Admin",
            password_hash=hash_password("Admin@123"),
            role=RoleEnum.ADMIN.value,
        )
        db.session.add(admin)

    member = User.query.filter_by(email="member@clinic.local").first()
    if not member:
        member = User(
            email="member@clinic.local",
            full_name="John Member",
            password_hash=hash_password("Member@123"),
            role=RoleEnum.MEMBER.value,
        )
        db.session.add(member)

    cardio = Department.query.filter_by(name="Cardiology").first()
    if not cardio:
        cardio = Department(name="Cardiology", description="Heart and vascular care")
        db.session.add(cardio)

    doctor_user = User.query.filter_by(email="doctor@clinic.local").first()
    if not doctor_user:
        doctor_user = User(
            email="doctor@clinic.local",
            full_name="Dr. Alice Carter",
            password_hash=hash_password("Doctor@123"),
            role=RoleEnum.DOCTOR.value,
        )
        db.session.add(doctor_user)
        db.session.flush()

        doctor = Doctor(
            user_id=doctor_user.id,
            license_number="LIC-10001",
            specialty="Cardiology",
        )
        db.session.add(doctor)
        db.session.flush()
        doctor.departments.append(cardio)

    db.session.commit()
