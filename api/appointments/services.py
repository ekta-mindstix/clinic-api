import logging

from api.appointments.models import Appointment
from api.appointments.repository import AppointmentRepository
from api.auth.models import User
from api.core.enum import RoleEnum
from api.core.exceptions import ApiError, ConflictError, NotFoundError
from api.core.extensions import db
from api.doctors.models import Doctor
from api.doctors.repository import DoctorAvailabilityRepository

logger = logging.getLogger(__name__)


class AppointmentService:
    @staticmethod
    def book_appointment(member_user_id: int, doctor_id: int, appointment_at, notes: str | None = None) -> dict:
        member = db.session.get(User, member_user_id)
        if not member:
            raise NotFoundError("Member not found")

        if member.role != RoleEnum.MEMBER:
            raise ApiError("Only members can book appointments", 403)

        doctor = db.session.get(Doctor, doctor_id)
        if not doctor:
            raise NotFoundError("Doctor not found")

        slot = DoctorAvailabilityRepository.find_covering_slot(doctor_id=doctor_id, appointment_at=appointment_at)
        if not slot:
            raise ApiError("Appointment time is outside doctor's availability", 400)

        if AppointmentRepository.exists_for_doctor_and_time(doctor_id=doctor_id, appointment_at=appointment_at):
            raise ConflictError("Selected time is already booked for this doctor")

        appointment = Appointment(
            doctor_id=doctor_id,
            member_id=member_user_id,
            appointment_at=appointment_at,
            notes=notes,
        )
        AppointmentRepository.create(appointment)
        logger.info(
            "Appointment booked",
            extra={"appointment_id": appointment.id, "doctor_id": doctor_id, "member_id": member_user_id},
        )
        return AppointmentService._appointment_to_dict(appointment)

    @staticmethod
    def update_appointment(member_user_id: int, appointment_id: int, payload: dict) -> dict:
        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundError("Appointment not found")

        if appointment.member_id != member_user_id:
            raise ApiError("Forbidden", 403)

        new_appointment_at = payload.get("appointment_at", appointment.appointment_at)
        new_notes = payload.get("notes", appointment.notes)

        if new_appointment_at != appointment.appointment_at:
            slot = DoctorAvailabilityRepository.find_covering_slot(
                doctor_id=appointment.doctor_id,
                appointment_at=new_appointment_at,
            )
            if not slot:
                raise ApiError("Appointment time is outside doctor's availability", 400)

            if AppointmentRepository.exists_for_doctor_and_time_excluding(
                doctor_id=appointment.doctor_id,
                appointment_at=new_appointment_at,
                exclude_appointment_id=appointment.id,
            ):
                raise ConflictError("Selected time is already booked for this doctor")

        appointment.appointment_at = new_appointment_at
        appointment.notes = new_notes
        AppointmentRepository.save()
        logger.info(
            "Appointment updated",
            extra={"appointment_id": appointment.id, "member_id": member_user_id},
        )
        return AppointmentService._appointment_to_dict(appointment)

    @staticmethod
    def delete_appointment(member_user_id: int, appointment_id: int) -> dict:
        appointment = AppointmentRepository.get_by_id(appointment_id)
        if not appointment:
            raise NotFoundError("Appointment not found")

        if appointment.member_id != member_user_id:
            raise ApiError("Forbidden", 403)

        deleted_id = appointment.id
        AppointmentRepository.delete(appointment)
        logger.info("Appointment deleted", extra={"appointment_id": deleted_id, "member_id": member_user_id})
        return {"id": deleted_id, "deleted": True}

    @staticmethod
    def list_all_appointments() -> list[dict]:
        appointments = AppointmentRepository.list_all()
        return [AppointmentService._appointment_to_dict(item) for item in appointments]

    @staticmethod
    def _appointment_to_dict(appointment: Appointment) -> dict:
        return {
            "id": appointment.id,
            "doctor_id": appointment.doctor_id,
            "member_id": appointment.member_id,
            "appointment_at": appointment.appointment_at.isoformat(),
            "notes": appointment.notes,
        }
