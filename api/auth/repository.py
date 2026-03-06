from typing import Optional

from api.auth.models import User
from api.core.extensions import db


class AuthRepository:
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        return User.query.filter_by(email=email.lower()).first()

    @staticmethod
    def create_user(user: User) -> User:
        db.session.add(user)
        db.session.commit()
        return user
