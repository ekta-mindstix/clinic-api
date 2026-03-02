from api.auth.models import User
from api.auth.repository import AuthRepository
from api.core.enum import RoleEnum
from api.core.exceptions import ConflictError, UnauthorizedError
from api.core.security import generate_token, hash_password, verify_password


class AuthService:
    @staticmethod
    def register_member(email: str, full_name: str, password: str) -> dict:
        normalized_email = email.strip().lower()

        if AuthRepository.get_user_by_email(normalized_email):
            raise ConflictError("Email is already registered")

        user = User(
            email=normalized_email,
            full_name=full_name.strip(),
            password_hash=hash_password(password),
            role=RoleEnum.MEMBER.value,
        )
        AuthRepository.create_user(user)

        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
        }

    @staticmethod
    def login(email: str, password: str) -> dict:
        user = AuthRepository.get_user_by_email(email.strip().lower())
        if not user or not verify_password(user.password_hash, password):
            raise UnauthorizedError("Invalid credentials")

        token = generate_token(user.id, user.email, user.role)
        return {
            "access_token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
            },
        }
