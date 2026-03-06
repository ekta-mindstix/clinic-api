import logging

from api.auth.models import User
from api.auth.repository import AuthRepository
from api.core.enum import RoleEnum
from api.core.exceptions import ConflictError, UnauthorizedError
from api.core.security import generate_token

logger = logging.getLogger(__name__)


class AuthService:
    @staticmethod
    def register_member(email: str, full_name: str, password: str) -> dict:
        normalized_email = email.strip().lower()

        if AuthRepository.get_user_by_email(normalized_email):
            logger.warning("Duplicate registration attempt", extra={"email": normalized_email})
            raise ConflictError("Email is already registered")

        user = User(
            email=normalized_email,
            full_name=full_name.strip(),
            role=RoleEnum.MEMBER,
        )
        user.set_password(password)
        AuthRepository.create_user(user)

        logger.info("Member registered", extra={"user_id": user.id, "email": user.email})

        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
        }

    @staticmethod
    def login(email: str, password: str) -> dict:
        normalized_email = email.strip().lower()
        user = AuthRepository.get_user_by_email(normalized_email)
        if not user or not user.check_password(password):
            logger.warning("Invalid login attempt", extra={"email": normalized_email})
            raise UnauthorizedError("Invalid credentials")

        token = generate_token(user.id, user.email, user.role)
        logger.info("User logged in", extra={"user_id": user.id, "email": user.email, "role": user.role.value})
        return {
            "access_token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
            },
        }
