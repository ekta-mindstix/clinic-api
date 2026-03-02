from flask import Flask, jsonify

from api.auth.routes import auth_bp
from api.core.config import Settings
from api.core.exceptions import register_error_handlers
from api.core.extensions import db, jwt, migrate
from api.departments.routes import departments_bp
from api.doctors.routes import doctors_bp


def create_app(config_object: type[Settings] = Settings) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Import model modules explicitly so SQLAlchemy metadata is registered.
    from api.auth import models as _auth_models  # noqa: F401
    from api.departments import models as _departments_models  # noqa: F401
    from api.doctors import models as _doctors_models  # noqa: F401

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(departments_bp, url_prefix="/admin/departments")
    app.register_blueprint(doctors_bp, url_prefix="/admin")

    register_error_handlers(app)
    register_jwt_handlers()

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    return app


def register_jwt_handlers() -> None:
    @jwt.unauthorized_loader
    def unauthorized(_reason: str):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401

    @jwt.invalid_token_loader
    def invalid(_reason: str):
        return jsonify({"error": "Invalid token"}), 401

    @jwt.expired_token_loader
    def expired(_jwt_header, _jwt_payload):
        return jsonify({"error": "Token has expired"}), 401
