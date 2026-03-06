from api.auth.models import User
from api.core.enum import RoleEnum
from api.core.extensions import db
from api.departments.models import Department
from api.doctors.models import Doctor


def seed_data() -> None:
    admin = User.query.filter_by(email="admin@clinic.local").first()
    if not admin:
        admin = User(
            email="admin@clinic.local",
            full_name="System Admin",
            role=RoleEnum.ADMIN,
        )
        admin.set_password("Admin@123")
        db.session.add(admin)

    member = User.query.filter_by(email="member@clinic.local").first()
    if not member:
        member = User(
            email="member@clinic.local",
            full_name="John Member",
            role=RoleEnum.MEMBER,
        )
        member.set_password("Member@123")
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
            role=RoleEnum.DOCTOR,
        )
        doctor_user.set_password("Doctor@123")
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
