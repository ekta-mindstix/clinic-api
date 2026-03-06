import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from api.core.constants import ADMIN_ROLE
from api.core.exceptions import ApiError
from api.core.rbac import roles_required
from api.departments.schemas import DepartmentCreateSchema, load_or_raise
from api.departments.services import DepartmentService

logger = logging.getLogger(__name__)

departments_bp = Blueprint("departments", __name__)


def _success(data, status_code: int = 200):
    return jsonify({"success": True, "data": data}), status_code


def _error(message: str, status_code: int):
    return jsonify({"success": False, "error": message}), status_code


@departments_bp.route("/", methods=["POST"], strict_slashes=False)
@jwt_required()
@roles_required(ADMIN_ROLE)
def create_department():
    try:
        payload = request.get_json(silent=True) or {}
        valid_payload = load_or_raise(DepartmentCreateSchema(), payload)
        result = DepartmentService.create_department(**valid_payload)
        return _success(result, 201)
    except ValueError as err:
        return _error("Invalid request payload", 400)
    except ApiError as err:
        return _error(err.message, err.status_code)
    except Exception:
        logger.exception("Unexpected error in create_department endpoint")
        return _error("Internal server error", 500)


@departments_bp.route("/", methods=["GET"], strict_slashes=False)
@jwt_required()
@roles_required(ADMIN_ROLE)
def list_departments():
    try:
        result = DepartmentService.list_departments()
        return _success(result, 200)
    except ApiError as err:
        return _error(err.message, err.status_code)
    except Exception:
        logger.exception("Unexpected error in list_departments endpoint")
        return _error("Internal server error", 500)
