from typing import Optional

from api.core.extensions import db
from api.doctors.models import Doctor, DoctorAvailability


class DoctorRepository:
    @staticmethod
    def get_by_id(doctor_id: int) -> Optional[Doctor]:
        return db.session.get(Doctor, doctor_id)

    @staticmethod
    def get_by_license(license_number: str) -> Optional[Doctor]:
        return Doctor.query.filter_by(license_number=license_number).first()

    @staticmethod
    def create(doctor: Doctor) -> Doctor:
        db.session.add(doctor)
        db.session.commit()
        return doctor

    @staticmethod
    def save() -> None:
        db.session.commit()


class DoctorAvailabilityRepository:
    @staticmethod
    def create(availability: DoctorAvailability) -> DoctorAvailability:
        db.session.add(availability)
        db.session.commit()
        return availability

    @staticmethod
    def get_by_id(availability_id: int) -> DoctorAvailability | None:
        return db.session.get(DoctorAvailability, availability_id)

    @staticmethod
    def list_by_doctor_id(doctor_id: int) -> list[DoctorAvailability]:
        return (
            DoctorAvailability.query.filter(DoctorAvailability.doctor_id == doctor_id)
            .order_by(DoctorAvailability.start_at.asc())
            .all()
        )

    @staticmethod
    def find_overlapping(
        doctor_id: int,
        start_at,
        end_at,
        exclude_availability_id: int | None = None,
    ) -> DoctorAvailability | None:
        query = DoctorAvailability.query.filter(
            DoctorAvailability.doctor_id == doctor_id,
            DoctorAvailability.start_at < end_at,
            DoctorAvailability.end_at > start_at,
        )
        if exclude_availability_id is not None:
            query = query.filter(DoctorAvailability.id != exclude_availability_id)
        return query.first()

    @staticmethod
    def find_covering_slot(doctor_id: int, appointment_at) -> DoctorAvailability | None:
        return (
            DoctorAvailability.query.filter(
                DoctorAvailability.doctor_id == doctor_id,
                DoctorAvailability.start_at <= appointment_at,
                DoctorAvailability.end_at > appointment_at,
            )
            .order_by(DoctorAvailability.start_at.asc())
            .first()
        )

    @staticmethod
    def delete(availability: DoctorAvailability) -> None:
        db.session.delete(availability)
        db.session.commit()
