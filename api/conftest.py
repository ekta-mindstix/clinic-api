import pytest

from api import create_app
from api.auth.models import User
from api.core.enum import RoleEnum
from api.core.extensions import db
from api.core.security import hash_password


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
    def _make_user(email: str, role: str = RoleEnum.MEMBER.value, full_name: str = "Test User", password: str = "Pass@123") -> User:
        user = User(
            email=email.lower(),
            full_name=full_name,
            password_hash=hash_password(password),
            role=role,
        )
        db.session.add(user)
        db.session.commit()
        return user

    return _make_user
