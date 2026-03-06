import logging

from api.auth.models import User
from api.auth.repository import AuthRepository
from api.core.enum import RoleEnum
from api.core.exceptions import ApiError, ConflictError, NotFoundError
from api.core.extensions import db
from api.departments.repository import DepartmentRepository
from api.doctors.models import Doctor, DoctorAvailability
from api.doctors.repository import DoctorAvailabilityRepository, DoctorRepository

logger = logging.getLogger(__name__)


class DoctorService:
    @staticmethod
    def onboard_doctor(
        email: str,
        full_name: str,
        password: str,
        license_number: str,
        specialty: str | None = None,
    ) -> dict:
        normalized_email = email.strip().lower()
        normalized_license = license_number.strip()

        if AuthRepository.get_user_by_email(normalized_email):
            logger.warning("Duplicate doctor onboarding email", extra={"email": normalized_email})
            raise ConflictError("Email is already registered")

        if DoctorRepository.get_by_license(normalized_license):
            logger.warning("Duplicate doctor license", extra={"license_number": normalized_license})
            raise ConflictError("License number already exists")

        try:
            user = User(
                email=normalized_email,
                full_name=full_name.strip(),
                role=RoleEnum.DOCTOR,
            )
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

            doctor = Doctor(
                user_id=user.id,
                license_number=normalized_license,
                specialty=specialty,
            )
            db.session.add(doctor)
            db.session.commit()
            logger.info(
                "Doctor onboarded",
                extra={"doctor_id": doctor.id, "user_id": user.id, "email": user.email},
            )
        except Exception:
            db.session.rollback()
            logger.exception("Doctor onboarding failed", extra={"email": normalized_email})
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
            logger.warning("Assign failed: doctor not found", extra={"doctor_id": doctor_id, "department_id": department_id})
            raise NotFoundError("Doctor not found")

        department = DepartmentRepository.get_by_id(department_id)
        if not department:
            logger.warning("Assign failed: department not found", extra={"doctor_id": doctor_id, "department_id": department_id})
            raise NotFoundError("Department not found")

        if department in doctor.departments:
            logger.warning(
                "Assign failed: duplicate assignment",
                extra={"doctor_id": doctor_id, "department_id": department_id},
            )
            raise ConflictError("Doctor is already assigned to this department")

        doctor.departments.append(department)
        DoctorRepository.save()
        logger.info("Doctor assigned to department", extra={"doctor_id": doctor.id, "department_id": department.id})

        return {
            "doctor_id": doctor.id,
            "department_id": department.id,
            "department_name": department.name,
        }

    @staticmethod
    def create_availability(doctor_user_id: int, start_at, end_at) -> dict:
        if start_at >= end_at:
            raise ApiError("start_at must be before end_at", 400)

        doctor = DoctorService._get_doctor_by_user_id(doctor_user_id)

        overlapping = DoctorAvailabilityRepository.find_overlapping(
            doctor_id=doctor.id,
            start_at=start_at,
            end_at=end_at,
        )
        if overlapping:
            raise ConflictError("Availability slot overlaps with an existing slot")

        availability = DoctorAvailability(doctor_id=doctor.id, start_at=start_at, end_at=end_at)
        DoctorAvailabilityRepository.create(availability)
        logger.info(
            "Doctor availability created",
            extra={"doctor_id": doctor.id, "availability_id": availability.id},
        )
        return DoctorService._availability_to_dict(availability)

    @staticmethod
    def update_availability(doctor_user_id: int, availability_id: int, payload: dict) -> dict:
        availability = DoctorAvailabilityRepository.get_by_id(availability_id)
        if not availability:
            raise NotFoundError("Availability slot not found")

        doctor = DoctorService._get_doctor_by_user_id(doctor_user_id)
        if availability.doctor_id != doctor.id:
            raise ApiError("Forbidden", 403)

        new_start = payload.get("start_at", availability.start_at)
        new_end = payload.get("end_at", availability.end_at)

        if new_start >= new_end:
            raise ApiError("start_at must be before end_at", 400)

        overlapping = DoctorAvailabilityRepository.find_overlapping(
            doctor_id=doctor.id,
            start_at=new_start,
            end_at=new_end,
            exclude_availability_id=availability.id,
        )
        if overlapping:
            raise ConflictError("Availability slot overlaps with an existing slot")

        availability.start_at = new_start
        availability.end_at = new_end
        DoctorRepository.save()
        logger.info(
            "Doctor availability updated",
            extra={"doctor_id": doctor.id, "availability_id": availability.id},
        )
        return DoctorService._availability_to_dict(availability)

    @staticmethod
    def list_my_availability(doctor_user_id: int) -> list[dict]:
        doctor = DoctorService._get_doctor_by_user_id(doctor_user_id)
        slots = DoctorAvailabilityRepository.list_by_doctor_id(doctor.id)
        return [DoctorService._availability_to_dict(slot) for slot in slots]

    @staticmethod
    def delete_availability(doctor_user_id: int, availability_id: int) -> dict:
        availability = DoctorAvailabilityRepository.get_by_id(availability_id)
        if not availability:
            raise NotFoundError("Availability slot not found")

        doctor = DoctorService._get_doctor_by_user_id(doctor_user_id)
        if availability.doctor_id != doctor.id:
            raise ApiError("Forbidden", 403)

        deleted_id = availability.id
        DoctorAvailabilityRepository.delete(availability)
        logger.info("Doctor availability deleted", extra={"doctor_id": doctor.id, "availability_id": deleted_id})
        return {"id": deleted_id, "deleted": True}

    @staticmethod
    def _get_doctor_by_user_id(doctor_user_id: int) -> Doctor:
        doctor = Doctor.query.filter_by(user_id=doctor_user_id).first()
        if not doctor:
            raise NotFoundError("Doctor profile not found")
        return doctor

    @staticmethod
    def _availability_to_dict(availability: DoctorAvailability) -> dict:
        return {
            "id": availability.id,
            "doctor_id": availability.doctor_id,
            "start_at": availability.start_at.isoformat(),
            "end_at": availability.end_at.isoformat(),
        }
