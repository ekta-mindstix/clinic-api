import pytest

from api.auth.models import User
from api.auth.repository import AuthRepository


def test_create_user_repository(app):
    user = User(
        email="repo-auth@test.local",
        full_name="Repo Auth",
        password_hash="hashed",
        role="Member",
    )

    created = AuthRepository.create_user(user)

    assert created.id is not None


def test_get_user_by_email_repository(app):
    user = User(
        email="findme@test.local",
        full_name="Find Me",
        password_hash="hashed",
        role="Member",
    )
    AuthRepository.create_user(user)

    found = AuthRepository.get_user_by_email("findme@test.local")

    assert found is not None
    assert found.email == "findme@test.local"


def test_get_user_by_email_not_found_repository(app):
    found = AuthRepository.get_user_by_email("missing@test.local")

    assert found is None
