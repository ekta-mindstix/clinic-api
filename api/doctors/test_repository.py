from api.auth.models import User
from api.core.enum import RoleEnum
from api.core.extensions import db
from api.core.security import hash_password
from api.doctors.models import Doctor
from api.doctors.repository import DoctorRepository


def test_create_doctor_repository(app):
    user = User(
        email="repo-doctor@test.local",
        full_name="Repo Doctor",
        password_hash=hash_password("Pass@123"),
        role=RoleEnum.DOCTOR.value,
    )
    db.session.add(user)
    db.session.commit()

    doctor = Doctor(user_id=user.id, license_number="LIC-REPO-1", specialty="Cardiology")
    created = DoctorRepository.create(doctor)

    assert created.id is not None


def test_get_by_id_repository(app):
    user = User(
        email="repo-doctor-id@test.local",
        full_name="Repo Doctor ID",
        password_hash=hash_password("Pass@123"),
        role=RoleEnum.DOCTOR.value,
    )
    db.session.add(user)
    db.session.commit()

    created = DoctorRepository.create(Doctor(user_id=user.id, license_number="LIC-REPO-2", specialty="Neuro"))
    found = DoctorRepository.get_by_id(created.id)

    assert found is not None
    assert found.id == created.id


def test_get_by_license_repository(app):
    user = User(
        email="repo-doctor-license@test.local",
        full_name="Repo Doctor License",
        password_hash=hash_password("Pass@123"),
        role=RoleEnum.DOCTOR.value,
    )
    db.session.add(user)
    db.session.commit()

    DoctorRepository.create(Doctor(user_id=user.id, license_number="LIC-REPO-3", specialty="Ortho"))
    found = DoctorRepository.get_by_license("LIC-REPO-3")

    assert found is not None
    assert found.license_number == "LIC-REPO-3"
