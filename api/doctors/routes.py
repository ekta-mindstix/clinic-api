from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from api.core.constants import ADMIN_ROLE
from api.core.exceptions import ApiError
from api.core.rbac import roles_required
from api.doctors.schemas import DoctorAssignSchema, DoctorCreateSchema, load_or_raise
from api.doctors.services import DoctorService


doctors_bp = Blueprint("doctors", __name__)


@doctors_bp.post("/doctors")
@jwt_required()
@roles_required(ADMIN_ROLE)
def onboard_doctor():
    try:
        payload = request.get_json(silent=True) or {}
        valid_payload = load_or_raise(DoctorCreateSchema(), payload)
        result = DoctorService.onboard_doctor(**valid_payload)
        return jsonify(result), 201
    except ValueError as err:
        return jsonify({"error": str(err)}), 400
    except ApiError as err:
        return jsonify({"error": err.message}), err.status_code
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@doctors_bp.post("/departments/<int:department_id>/assign-doctor")
@jwt_required()
@roles_required(ADMIN_ROLE)
def assign_doctor(department_id: int):
    try:
        payload = request.get_json(silent=True) or {}
        valid_payload = load_or_raise(DoctorAssignSchema(), payload)
        result = DoctorService.assign_doctor_to_department(
            doctor_id=valid_payload["doctor_id"],
            department_id=department_id,
        )
        return jsonify(result), 200
    except ValueError as err:
        return jsonify({"error": str(err)}), 400
    except ApiError as err:
        return jsonify({"error": err.message}), err.status_code
    except Exception:
        return jsonify({"error": "Internal server error"}), 500
