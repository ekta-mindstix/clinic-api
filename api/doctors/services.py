from api.auth.models import User
from api.auth.repository import AuthRepository
from api.core.enum import RoleEnum
from api.core.exceptions import ConflictError, NotFoundError
from api.core.extensions import db
from api.core.security import hash_password
from api.departments.repository import DepartmentRepository
from api.doctors.models import Doctor
from api.doctors.repository import DoctorRepository


class DoctorService:
    @staticmethod
    def onboard_doctor(
        email: str,
        full_name: str,
        password: str,
        license_number: str,
        specialty: str | None = None,
    ) -> dict:
        if AuthRepository.get_user_by_email(email):
            raise ConflictError("Email is already registered")

        if DoctorRepository.get_by_license(license_number):
            raise ConflictError("License number already exists")

        try:
            user = User(
                email=email.strip().lower(),
                full_name=full_name.strip(),
                password_hash=hash_password(password),
                role=RoleEnum.DOCTOR.value,
            )
            db.session.add(user)
            db.session.flush()

            doctor = Doctor(
                user_id=user.id,
                license_number=license_number.strip(),
                specialty=specialty,
            )
            db.session.add(doctor)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise

        return {
            "doctor_id": doctor.id,
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "license_number": doctor.license_number,
            "specialty": doctor.specialty,
        }

    @staticmethod
    def assign_doctor_to_department(doctor_id: int, department_id: int) -> dict:
        doctor = DoctorRepository.get_by_id(doctor_id)
        if not doctor:
            raise NotFoundError("Doctor not found")

        department = DepartmentRepository.get_by_id(department_id)
        if not department:
            raise NotFoundError("Department not found")

        if department in doctor.departments:
            raise ConflictError("Doctor is already assigned to this department")

        doctor.departments.append(department)
        DoctorRepository.save()

        return {
            "doctor_id": doctor.id,
            "department_id": department.id,
            "department_name": department.name,
        }
