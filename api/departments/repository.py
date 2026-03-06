from typing import Optional

from api.core.extensions import db
from api.departments.models import Department


class DepartmentRepository:
    @staticmethod
    def get_by_name(name: str) -> Optional[Department]:
        return Department.query.filter_by(name=name.strip()).first()

    @staticmethod
    def get_by_id(department_id: int) -> Optional[Department]:
        return db.session.get(Department, department_id)

    @staticmethod
    def list_all() -> list[Department]:
        return Department.query.order_by(Department.name.asc()).all()

    @staticmethod
    def create(department: Department) -> Department:
        db.session.add(department)
        db.session.commit()
        return department
