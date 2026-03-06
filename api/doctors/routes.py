import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from api.core.constants import ADMIN_ROLE, DOCTOR_ROLE
from api.core.exceptions import ApiError
from api.core.rbac import roles_required
from api.doctors.schemas import (
    DoctorAssignSchema,
    DoctorAvailabilityCreateSchema,
    DoctorAvailabilityUpdateSchema,
    DoctorCreateSchema,
    load_or_raise,
)
from api.doctors.services import DoctorService

logger = logging.getLogger(__name__)

doctors_bp = Blueprint("doctors", __name__)
doctor_availability_bp = Blueprint("doctor_availability", __name__)


def _success(data, status_code: int = 200):
    return jsonify({"success": True, "data": data}), status_code


def _error(message: str, status_code: int):
    return jsonify({"success": False, "error": message}), status_code


def _doctor_user_id_from_token() -> int:
    try:
        return int(get_jwt_identity())
    except (TypeError, ValueError) as err:
        raise ApiError("Invalid token identity", 401) from err


@doctors_bp.route("/doctors", methods=["POST"], strict_slashes=False)
@jwt_required()
@roles_required(ADMIN_ROLE)
def onboard_doctor():
    try:
        payload = request.get_json(silent=True) or {}
        valid_payload = load_or_raise(DoctorCreateSchema(), payload)
        result = DoctorService.onboard_doctor(**valid_payload)
        return _success(result, 201)
    except ValueError:
        return _error("Invalid request payload", 400)
    except ApiError as err:
        return _error(err.message, err.status_code)
    except Exception:
        logger.exception("Unexpected error in onboard_doctor endpoint")
        return _error("Internal server error", 500)


@doctors_bp.route("/departments/<int:department_id>/assign-doctor", methods=["POST"], strict_slashes=False)
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
        return _success(result, 200)
    except ValueError:
        return _error("Invalid request payload", 400)
    except ApiError as err:
        return _error(err.message, err.status_code)
    except Exception:
        logger.exception("Unexpected error in assign_doctor endpoint", extra={"department_id": department_id})
        return _error("Internal server error", 500)


@doctor_availability_bp.route("/availability", methods=["POST"], strict_slashes=False)
@jwt_required()
@roles_required(DOCTOR_ROLE)
def create_availability():
    try:
        payload = request.get_json(silent=True) or {}
        valid_payload = load_or_raise(DoctorAvailabilityCreateSchema(), payload)
        doctor_user_id = _doctor_user_id_from_token()
        result = DoctorService.create_availability(doctor_user_id=doctor_user_id, **valid_payload)
        return _success(result, 201)
    except ValueError:
        return _error("Invalid request payload", 400)
    except ApiError as err:
        return _error(err.message, err.status_code)
    except Exception:
        logger.exception("Unexpected error in create_availability endpoint")
        return _error("Internal server error", 500)


@doctor_availability_bp.route("/availability", methods=["GET"], strict_slashes=False)
@jwt_required()
@roles_required(DOCTOR_ROLE)
def list_my_availability():
    try:
        doctor_user_id = _doctor_user_id_from_token()
        result = DoctorService.list_my_availability(doctor_user_id=doctor_user_id)
        return _success(result, 200)
    except ApiError as err:
        return _error(err.message, err.status_code)
    except Exception:
        logger.exception("Unexpected error in list_my_availability endpoint")
        return _error("Internal server error", 500)


@doctor_availability_bp.route("/availability/<int:availability_id>", methods=["PUT"], strict_slashes=False)
@jwt_required()
@roles_required(DOCTOR_ROLE)
def update_availability(availability_id: int):
    try:
        payload = request.get_json(silent=True) or {}
        valid_payload = load_or_raise(DoctorAvailabilityUpdateSchema(), payload)
        if not valid_payload:
            return _error("At least one field is required", 400)

        doctor_user_id = _doctor_user_id_from_token()
        result = DoctorService.update_availability(
            doctor_user_id=doctor_user_id,
            availability_id=availability_id,
            payload=valid_payload,
        )
        return _success(result, 200)
    except ValueError:
        return _error("Invalid request payload", 400)
    except ApiError as err:
        return _error(err.message, err.status_code)
    except Exception:
        logger.exception("Unexpected error in update_availability endpoint")
        return _error("Internal server error", 500)


@doctor_availability_bp.route("/availability/<int:availability_id>", methods=["DELETE"], strict_slashes=False)
@jwt_required()
@roles_required(DOCTOR_ROLE)
def delete_availability(availability_id: int):
    try:
        doctor_user_id = _doctor_user_id_from_token()
        result = DoctorService.delete_availability(
            doctor_user_id=doctor_user_id,
            availability_id=availability_id,
        )
        return _success(result, 200)
    except ApiError as err:
        return _error(err.message, err.status_code)
    except Exception:
        logger.exception("Unexpected error in delete_availability endpoint")
        return _error("Internal server error", 500)
