import logging

from api.core.exceptions import ConflictError
from api.departments.models import Department
from api.departments.repository import DepartmentRepository

logger = logging.getLogger(__name__)


class DepartmentService:
    @staticmethod
    def create_department(name: str, description: str | None = None) -> dict:
        normalized_name = (name or "").strip()

        if DepartmentRepository.get_by_name(normalized_name):
            logger.warning("Duplicate department creation attempt", extra={"department_name": normalized_name})
            raise ConflictError("Department already exists")

        department = Department(name=normalized_name, description=description)
        DepartmentRepository.create(department)

        logger.info(
            "Department created",
            extra={"department_id": department.id, "department_name": department.name},
        )

        return {
            "id": department.id,
            "name": department.name,
            "description": department.description,
        }

    @staticmethod
    def list_departments() -> list[dict]:
        departments = DepartmentRepository.list_all()
        logger.info("Departments listed", extra={"count": len(departments)})
        return [
            {
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "doctor_count": len(item.doctors),
            }
            for item in departments
        ]
