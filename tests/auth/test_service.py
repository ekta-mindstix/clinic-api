import pytest

from api.auth.services import AuthService
from api.core.enum import RoleEnum
from api.core.exceptions import ConflictError, UnauthorizedError


def test_register_member_service(app):
    result = AuthService.register_member("service-auth@test.local", "Service Auth", "Pass@123")

    assert result["email"] == "service-auth@test.local"
    assert result["role"] == RoleEnum.MEMBER.value


def test_register_member_duplicate_service(app):
    AuthService.register_member("dup-auth@test.local", "User 1", "Pass@123")

    with pytest.raises(ConflictError):
        AuthService.register_member("dup-auth@test.local", "User 2", "Pass@123")


def test_login_service_success(app):
    AuthService.register_member("login-auth@test.local", "Login User", "Pass@123")

    result = AuthService.login("login-auth@test.local", "Pass@123")

    assert "access_token" in result
    assert result["user"]["email"] == "login-auth@test.local"


def test_login_service_invalid_password(app):
    AuthService.register_member("invalid-auth@test.local", "Invalid User", "Pass@123")

    with pytest.raises(UnauthorizedError):
        AuthService.login("invalid-auth@test.local", "Wrong@123")
