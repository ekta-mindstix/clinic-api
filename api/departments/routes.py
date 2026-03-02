from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from api.core.constants import ADMIN_ROLE
from api.core.exceptions import ApiError
from api.core.rbac import roles_required
from api.departments.schemas import DepartmentCreateSchema, load_or_raise
from api.departments.services import DepartmentService


departments_bp = Blueprint("departments", __name__)


@departments_bp.post("")
@jwt_required()
@roles_required(ADMIN_ROLE)
def create_department():
    try:
        payload = request.get_json(silent=True) or {}
        valid_payload = load_or_raise(DepartmentCreateSchema(), payload)
        result = DepartmentService.create_department(**valid_payload)
        return jsonify(result), 201
    except ValueError as err:
        return jsonify({"error": str(err)}), 400
    except ApiError as err:
        return jsonify({"error": err.message}), err.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@departments_bp.get("")
@jwt_required()
@roles_required(ADMIN_ROLE)
def list_departments():
    try:
        result = DepartmentService.list_departments()
        return jsonify({"departments": result}), 200
    except ApiError as err:
        return jsonify({"error": err.message}), err.status_code
    except Exception:
        return jsonify({"error": "Internal server error"}), 500
