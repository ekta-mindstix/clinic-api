from api.core.extensions import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
