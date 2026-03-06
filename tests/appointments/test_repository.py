from datetime import datetime, timedelta

from api.appointments.models import Appointment
from api.appointments.repository import AppointmentRepository
from api.auth.models import User
from api.core.enum import RoleEnum
from api.core.extensions import db
from api.doctors.models import Doctor, DoctorAvailability
from api.doctors.repository import DoctorAvailabilityRepository


def _create_doctor(email: str, license_number: str) -> Doctor:
    user = User(email=email, full_name="Doctor Test", role=RoleEnum.DOCTOR)
    user.set_password("Pass@123")
    db.session.add(user)
    db.session.flush()

    doctor = Doctor(user_id=user.id, license_number=license_number, specialty="General")
    db.session.add(doctor)
    db.session.commit()
    return doctor


def _create_member(email: str) -> User:
    member = User(email=email, full_name="Member Test", role=RoleEnum.MEMBER)
    member.set_password("Pass@123")
    db.session.add(member)
    db.session.commit()
    return member


def test_doctor_availability_repository_overlap_and_covering_slot(app):
    doctor = _create_doctor("doctor-repo@test.local", "LIC-APT-REPO-1")

    start = datetime.now().replace(second=0, microsecond=0)
    end = start + timedelta(hours=2)
    availability = DoctorAvailability(doctor_id=doctor.id, start_at=start, end_at=end)
    DoctorAvailabilityRepository.create(availability)

    overlapping = DoctorAvailabilityRepository.find_overlapping(
        doctor_id=doctor.id,
        start_at=start + timedelta(minutes=30),
        end_at=end + timedelta(minutes=30),
    )
    assert overlapping is not None

    covering = DoctorAvailabilityRepository.find_covering_slot(doctor_id=doctor.id, appointment_at=start + timedelta(hours=1))
    assert covering is not None
    assert covering.id == availability.id


def test_appointment_repository_exists_for_doctor_and_time(app):
    doctor = _create_doctor("doctor-appoint-repo@test.local", "LIC-APT-REPO-2")
    member = _create_member("member-appoint-repo@test.local")

    at = datetime.now().replace(second=0, microsecond=0) + timedelta(days=1)
    appointment = Appointment(doctor_id=doctor.id, member_id=member.id, appointment_at=at)
    AppointmentRepository.create(appointment)

    assert AppointmentRepository.exists_for_doctor_and_time(doctor.id, at) is True
    assert AppointmentRepository.exists_for_doctor_and_time(doctor.id, at + timedelta(minutes=30)) is False
