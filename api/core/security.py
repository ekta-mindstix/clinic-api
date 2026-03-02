from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash


def hash_password(raw_password: str) -> str:
    return generate_password_hash(raw_password)


def verify_password(password_hash: str, raw_password: str) -> bool:
    return check_password_hash(password_hash, raw_password)


def generate_token(user_id: int, email: str, role: str) -> str:
    return create_access_token(
        identity=str(user_id),
        additional_claims={"email": email, "role": role},
    )
