from api.departments.models import Department
from api.departments.repository import DepartmentRepository


def test_create_department_repository(app):
    department = Department(name="Repo Department", description="Repo Desc")

    created = DepartmentRepository.create(department)

    assert created.id is not None


def test_get_by_name_repository(app):
    DepartmentRepository.create(Department(name="Cardiology", description="Heart"))

    found = DepartmentRepository.get_by_name("Cardiology")

    assert found is not None
    assert found.name == "Cardiology"


def test_get_by_id_repository(app):
    created = DepartmentRepository.create(Department(name="Neurology", description="Brain"))

    found = DepartmentRepository.get_by_id(created.id)

    assert found is not None
    assert found.id == created.id


def test_list_all_repository_sorted(app):
    DepartmentRepository.create(Department(name="Zeta", description="Z"))
    DepartmentRepository.create(Department(name="Alpha", description="A"))

    records = DepartmentRepository.list_all()

    assert [item.name for item in records] == ["Alpha", "Zeta"]
