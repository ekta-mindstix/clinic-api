from flask_jwt_extended import create_access_token

from api.core.enum import RoleEnum


def generate_token(user_id: int, email: str, role: str | RoleEnum) -> str:
    role_value = role.value if isinstance(role, RoleEnum) else role
    return create_access_token(
        identity=str(user_id),
        additional_claims={"email": email, "role": role_value},
    )
