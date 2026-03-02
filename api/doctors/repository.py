from typing import Optional

from api.core.extensions import db
from api.doctors.models import Doctor


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
