from datetime import datetime, timedelta

import pytest

from api.appointments.services import AppointmentService
from api.auth.models import User
from api.core.enum import RoleEnum
from api.core.exceptions import ApiError, ConflictError
from api.core.extensions import db
from api.doctors.models import Doctor
from api.doctors.services import DoctorService


def _create_doctor(email: str, license_number: str) -> tuple[User, Doctor]:
    user = User(email=email, full_name="Doctor Test", role=RoleEnum.DOCTOR)
    user.set_password("Pass@123")
    db.session.add(user)
    db.session.flush()

    doctor = Doctor(user_id=user.id, license_number=license_number, specialty="General")
    db.session.add(doctor)
    db.session.commit()
    return user, doctor


def _create_member(email: str) -> User:
    member = User(email=email, full_name="Member Test", role=RoleEnum.MEMBER)
    member.set_password("Pass@123")
    db.session.add(member)
    db.session.commit()
    return member


def test_create_availability_and_prevent_overlap(app):
    doctor_user, _doctor = _create_doctor("doctor-service@test.local", "LIC-APT-SVC-1")
    start = datetime.now().replace(second=0, microsecond=0) + timedelta(days=1)
    end = start + timedelta(hours=2)

    created = DoctorService.create_availability(doctor_user.id, start, end)
    assert created["doctor_id"] == _doctor.id

    with pytest.raises(ConflictError):
        DoctorService.create_availability(doctor_user.id, start + timedelta(minutes=30), end + timedelta(minutes=30))


def test_book_appointment_success_and_prevent_same_doctor_same_time(app):
    doctor_user, doctor = _create_doctor("doctor-book@test.local", "LIC-APT-SVC-2")
    member = _create_member("member-book@test.local")

    start = datetime.now().replace(second=0, microsecond=0) + timedelta(days=1)
    end = start + timedelta(hours=2)
    DoctorService.create_availability(doctor_user.id, start, end)

    appointment_at = start + timedelta(minutes=30)
    booked = AppointmentService.book_appointment(member.id, doctor.id, appointment_at, notes="First")
    assert booked["doctor_id"] == doctor.id

    with pytest.raises(ConflictError):
        AppointmentService.book_appointment(member.id, doctor.id, appointment_at, notes="Duplicate")


def test_same_time_different_doctors_is_allowed(app):
    doctor_user_1, doctor_1 = _create_doctor("doctor-a@test.local", "LIC-APT-SVC-3")
    doctor_user_2, doctor_2 = _create_doctor("doctor-b@test.local", "LIC-APT-SVC-4")
    member = _create_member("member-same-time@test.local")

    start = datetime.now().replace(second=0, microsecond=0) + timedelta(days=1)
    end = start + timedelta(hours=3)
    DoctorService.create_availability(doctor_user_1.id, start, end)
    DoctorService.create_availability(doctor_user_2.id, start, end)

    appointment_at = start + timedelta(minutes=45)
    first = AppointmentService.book_appointment(member.id, doctor_1.id, appointment_at)
    second = AppointmentService.book_appointment(member.id, doctor_2.id, appointment_at)

    assert first["doctor_id"] == doctor_1.id
    assert second["doctor_id"] == doctor_2.id


def test_member_cannot_book_outside_availability(app):
    doctor_user, doctor = _create_doctor("doctor-outside@test.local", "LIC-APT-SVC-5")
    member = _create_member("member-outside@test.local")

    start = datetime.now().replace(second=0, microsecond=0) + timedelta(days=1)
    end = start + timedelta(hours=1)
    DoctorService.create_availability(doctor_user.id, start, end)

    with pytest.raises(ApiError):
        AppointmentService.book_appointment(member.id, doctor.id, end + timedelta(minutes=5))


def test_update_appointment_reschedule(app):
    doctor_user, doctor = _create_doctor("doctor-update@test.local", "LIC-APT-SVC-6")
    member = _create_member("member-update@test.local")

    start = datetime.now().replace(second=0, microsecond=0) + timedelta(days=1)
    end = start + timedelta(hours=2)
    DoctorService.create_availability(doctor_user.id, start, end)

    booked = AppointmentService.book_appointment(member.id, doctor.id, start + timedelta(minutes=15), notes="old")
    updated = AppointmentService.update_appointment(
        member_user_id=member.id,
        appointment_id=booked["id"],
        payload={"appointment_at": start + timedelta(minutes=45), "notes": "updated"},
    )
    assert updated["notes"] == "updated"


def test_delete_appointment(app):
    doctor_user, doctor = _create_doctor("doctor-delete@test.local", "LIC-APT-SVC-7")
    member = _create_member("member-delete@test.local")

    start = datetime.now().replace(second=0, microsecond=0) + timedelta(days=1)
    end = start + timedelta(hours=2)
    DoctorService.create_availability(doctor_user.id, start, end)

    booked = AppointmentService.book_appointment(member.id, doctor.id, start + timedelta(minutes=20), notes="to delete")
    deleted = AppointmentService.delete_appointment(member_user_id=member.id, appointment_id=booked["id"])

    assert deleted["deleted"] is True

    with pytest.raises(ApiError):
        AppointmentService.delete_appointment(member_user_id=member.id, appointment_id=booked["id"])
