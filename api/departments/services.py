from api.core.exceptions import ConflictError
from api.departments.models import Department
from api.departments.repository import DepartmentRepository


class DepartmentService:
    @staticmethod
    def create_department(name: str, description: str | None = None) -> dict:
        if DepartmentRepository.get_by_name(name):
            raise ConflictError("Department already exists")

        department = Department(name=name.strip(), description=description)
        DepartmentRepository.create(department)

        return {
            "id": department.id,
            "name": department.name,
            "description": department.description,
        }

    @staticmethod
    def list_departments() -> list[dict]:
        departments = DepartmentRepository.list_all()
        return [
            {
                "id": item.id,
                "name": item.name,
                "description": item.description,
                "doctor_count": len(item.doctors),
            }
            for item in departments
        ]
