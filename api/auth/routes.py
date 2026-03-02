from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required

from api.auth.schemas import LoginSchema, RegisterSchema, load_or_raise
from api.core.constants import DOCTOR_ROLE, MEMBER_ROLE
from api.auth.services import AuthService
from api.core.exceptions import ApiError
from api.core.rbac import roles_required


auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    try:
        payload = request.get_json(silent=True) or {}
        valid_payload = load_or_raise(RegisterSchema(), payload)
        result = AuthService.register_member(**valid_payload)
        return jsonify(result), 201
    except ValueError as err:
        return jsonify({"error": str(err)}), 400
    except ApiError as err:
        return jsonify({"error": err.message}), err.status_code
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.post("/login")
def login():
    try:
        payload = request.get_json(silent=True) or {}
        valid_payload = load_or_raise(LoginSchema(), payload)
        result = AuthService.login(**valid_payload)
        return jsonify(result), 200
    except ValueError as err:
        return jsonify({"error": str(err)}), 400
    except ApiError as err:
        return jsonify({"error": err.message}), err.status_code
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.get("/me")
@jwt_required()
def current_user():
    try:
        claims = get_jwt()
        return jsonify(
            {
                "email": claims.get("email"),
                "role": claims.get("role"),
            }
        ), 200
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.get("/doctor/scope")
@jwt_required()
@roles_required(DOCTOR_ROLE)
def doctor_scope():
    try:
        return jsonify({"message": "Doctor scope access granted"}), 200
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@auth_bp.get("/member/scope")
@jwt_required()
@roles_required(MEMBER_ROLE)
def member_scope():
    try:
        return jsonify({"message": "Member scope access granted"}), 200
    except Exception:
        return jsonify({"error": "Internal server error"}), 500
