from api.appointments.models import Appointment
from api.core.extensions import db


class AppointmentRepository:
    @staticmethod
    def create(appointment: Appointment) -> Appointment:
        db.session.add(appointment)
        db.session.commit()
        return appointment

    @staticmethod
    def get_by_id(appointment_id: int) -> Appointment | None:
        return db.session.get(Appointment, appointment_id)

    @staticmethod
    def exists_for_doctor_and_time(doctor_id: int, appointment_at) -> bool:
        return (
            Appointment.query.filter(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_at == appointment_at,
            ).first()
            is not None
        )

    @staticmethod
    def exists_for_doctor_and_time_excluding(doctor_id: int, appointment_at, exclude_appointment_id: int) -> bool:
        return (
            Appointment.query.filter(
                Appointment.doctor_id == doctor_id,
                Appointment.appointment_at == appointment_at,
                Appointment.id != exclude_appointment_id,
            ).first()
            is not None
        )

    @staticmethod
    def list_all() -> list[Appointment]:
        return Appointment.query.order_by(Appointment.appointment_at.desc()).all()

    @staticmethod
    def save() -> None:
        db.session.commit()

    @staticmethod
    def delete(appointment: Appointment) -> None:
        db.session.delete(appointment)
        db.session.commit()
