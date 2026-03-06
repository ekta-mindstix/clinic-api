import pytest
from flask_jwt_extended import create_access_token

from api import create_app
from api.auth.models import User
from api.core.enum import RoleEnum
from api.core.extensions import db


class TestSettings:
    TESTING = True
    SECRET_KEY = "test-secret"
    JWT_SECRET_KEY = "test-jwt-secret"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


@pytest.fixture()
def app():
    app = create_app(TestSettings)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def make_user(app):
    def _make_user(
        email: str,
        role: RoleEnum = RoleEnum.MEMBER,
        full_name: str = "Test User",
        password: str = "Pass@123",
    ) -> User:
        user = User(
            email=email.lower(),
            full_name=full_name,
            role=role,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    return _make_user


@pytest.fixture()
def role_tokens(app, make_user):
    admin = make_user("admin@test.local", RoleEnum.ADMIN, full_name="Admin User")
    doctor = make_user("doctor@test.local", RoleEnum.DOCTOR, full_name="Doctor User")
    member = make_user("member@test.local", RoleEnum.MEMBER, full_name="Member User")

    with app.app_context():
        admin_token = create_access_token(
            identity=str(admin.id),
            additional_claims={"email": admin.email, "role": admin.role.value},
        )
        doctor_token = create_access_token(
            identity=str(doctor.id),
            additional_claims={"email": doctor.email, "role": doctor.role.value},
        )
        member_token = create_access_token(
            identity=str(member.id),
            additional_claims={"email": member.email, "role": member.role.value},
        )

    return {
        "admin": admin_token,
        "doctor": doctor_token,
        "member": member_token,
    }
