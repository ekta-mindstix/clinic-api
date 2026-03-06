import pytest

from api.core.exceptions import ConflictError
from api.departments.services import DepartmentService


def test_create_department_service(app):
    result = DepartmentService.create_department("Service Department", "Service Desc")

    assert result["name"] == "Service Department"
    assert result["description"] == "Service Desc"


def test_create_department_duplicate_service(app):
    DepartmentService.create_department("Duplicate Department", "Desc")

    with pytest.raises(ConflictError):
        DepartmentService.create_department("Duplicate Department", "Desc 2")


def test_list_departments_service(app):
    DepartmentService.create_department("Gamma", "G")
    DepartmentService.create_department("Beta", "B")

    records = DepartmentService.list_departments()

    assert [item["name"] for item in records] == ["Beta", "Gamma"]
    assert all(item["doctor_count"] == 0 for item in records)
