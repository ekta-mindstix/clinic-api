import pytest

from api.core.exceptions import ConflictError, NotFoundError
from api.departments.services import DepartmentService
from api.doctors.services import DoctorService


def test_onboard_doctor_service(app):
    result = DoctorService.onboard_doctor(
        email="service-doctor@test.local",
        full_name="Service Doctor",
        password="Pass@123",
        license_number="LIC-SVC-1",
        specialty="ENT",
    )

    assert result["email"] == "service-doctor@test.local"
    assert result["license_number"] == "LIC-SVC-1"


def test_onboard_doctor_duplicate_email_service(app):
    DoctorService.onboard_doctor(
        email="duplicate-doctor@test.local",
        full_name="Doctor One",
        password="Pass@123",
        license_number="LIC-SVC-2",
    )

    with pytest.raises(ConflictError):
        DoctorService.onboard_doctor(
            email="duplicate-doctor@test.local",
            full_name="Doctor Two",
            password="Pass@123",
            license_number="LIC-SVC-3",
        )


def test_assign_doctor_to_department_service(app):
    department = DepartmentService.create_department("Service Assign", "Assign Desc")
    doctor = DoctorService.onboard_doctor(
        email="assign-doctor@test.local",
        full_name="Assign Doctor",
        password="Pass@123",
        license_number="LIC-SVC-4",
    )

    result = DoctorService.assign_doctor_to_department(
        doctor_id=doctor["doctor_id"],
        department_id=department["id"],
    )

    assert result["department_name"] == "Service Assign"


def test_assign_doctor_not_found_service(app):
    department = DepartmentService.create_department("NF Department", "Desc")

    with pytest.raises(NotFoundError):
        DoctorService.assign_doctor_to_department(doctor_id=99999, department_id=department["id"])
