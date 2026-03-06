import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required

from api.auth.schemas import LoginSchema, RegisterSchema, load_or_raise
from api.auth.services import AuthService
from api.core.constants import DOCTOR_ROLE, MEMBER_ROLE
from api.core.exceptions import ApiError
from api.core.rbac import roles_required

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)


def _success(data, status_code: int = 200):
    return jsonify({"success": True, "data": data}), status_code


def _error(message: str, status_code: int):
    return jsonify({"success": False, "error": message}), status_code


@auth_bp.route("/register", methods=["POST"], strict_slashes=False)
def register():
    try:
        payload = request.get_json(silent=True) or {}
        valid_payload = load_or_raise(RegisterSchema(), payload)
        result = AuthService.register_member(**valid_payload)
        return _success(result, 201)
    except ValueError:
        return _error("Invalid request payload", 400)
    except ApiError as err:
        return _error(err.message, err.status_code)
    except Exception:
        logger.exception("Unexpected error in register endpoint")
        return _error("Internal server error", 500)


@auth_bp.route("/login", methods=["POST"], strict_slashes=False)
def login():
    try:
        payload = request.get_json(silent=True) or {}
        valid_payload = load_or_raise(LoginSchema(), payload)
        result = AuthService.login(**valid_payload)
        return _success(result, 200)
    except ValueError:
        return _error("Invalid request payload", 400)
    except ApiError as err:
        return _error(err.message, err.status_code)
    except Exception:
        logger.exception("Unexpected error in login endpoint")
        return _error("Internal server error", 500)


@auth_bp.route("/me", methods=["GET"], strict_slashes=False)
@jwt_required()
def current_user():
    try:
        claims = get_jwt()
        return _success({"email": claims.get("email"), "role": claims.get("role")}, 200)
    except Exception:
        logger.exception("Unexpected error in current_user endpoint")
        return _error("Internal server error", 500)


@auth_bp.route("/doctor/scope", methods=["GET"], strict_slashes=False)
@jwt_required()
@roles_required(DOCTOR_ROLE)
def doctor_scope():
    try:
        return _success({"message": "Doctor scope access granted"}, 200)
    except Exception:
        logger.exception("Unexpected error in doctor_scope endpoint")
        return _error("Internal server error", 500)


@auth_bp.route("/member/scope", methods=["GET"], strict_slashes=False)
@jwt_required()
@roles_required(MEMBER_ROLE)
def member_scope():
    try:
        return _success({"message": "Member scope access granted"}, 200)
    except Exception:
        logger.exception("Unexpected error in member_scope endpoint")
        return _error("Internal server error", 500)
