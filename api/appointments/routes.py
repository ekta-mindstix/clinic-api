import logging

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from api.appointments.schemas import AppointmentCreateSchema, AppointmentUpdateSchema, load_or_raise
from api.appointments.services import AppointmentService
from api.core.constants import ADMIN_ROLE, MEMBER_ROLE
from api.core.exceptions import ApiError
from api.core.rbac import roles_required

logger = logging.getLogger(__name__)

appointments_bp = Blueprint("appointments", __name__)


def _success(data, status_code: int = 200):
    return jsonify({"success": True, "data": data}), status_code


def _error(message: str, status_code: int):
    return jsonify({"success": False, "error": message}), status_code


@appointments_bp.route("/", methods=["POST"], strict_slashes=False)
@jwt_required()
@roles_required(MEMBER_ROLE)
def book_appointment():
    try:
        payload = request.get_json(silent=True) or {}
        valid_payload = load_or_raise(AppointmentCreateSchema(), payload)
        member_user_id = int(get_jwt_identity())
        result = AppointmentService.book_appointment(member_user_id=member_user_id, **valid_payload)
        return _success(result, 201)
    except ValueError:
        return _error("Invalid request payload", 400)
    except ApiError as err:
        return _error(err.message, err.status_code)
    except Exception:
        logger.exception("Unexpected error in book_appointment endpoint")
        return _error("Internal server error", 500)


@appointments_bp.route("/<int:appointment_id>", methods=["PATCH"], strict_slashes=False)
@jwt_required()
@roles_required(MEMBER_ROLE)
def update_appointment(appointment_id: int):
    try:
        payload = request.get_json(silent=True) or {}
        valid_payload = load_or_raise(AppointmentUpdateSchema(), payload)
        if not valid_payload:
            return _error("At least one field is required", 400)

        member_user_id = int(get_jwt_identity())
        result = AppointmentService.update_appointment(
            member_user_id=member_user_id,
            appointment_id=appointment_id,
            payload=valid_payload,
        )
        return _success(result, 200)
    except ValueError:
        return _error("Invalid request payload", 400)
    except ApiError as err:
        return _error(err.message, err.status_code)
    except Exception:
        logger.exception("Unexpected error in update_appointment endpoint", extra={"appointment_id": appointment_id})
        return _error("Internal server error", 500)


@appointments_bp.route("/<int:appointment_id>", methods=["DELETE"], strict_slashes=False)
@jwt_required()
@roles_required(MEMBER_ROLE)
def delete_appointment(appointment_id: int):
    try:
        member_user_id = int(get_jwt_identity())
        result = AppointmentService.delete_appointment(
            member_user_id=member_user_id,
            appointment_id=appointment_id,
        )
        return _success(result, 200)
    except ApiError as err:
        return _error(err.message, err.status_code)
    except Exception:
        logger.exception("Unexpected error in delete_appointment endpoint", extra={"appointment_id": appointment_id})
        return _error("Internal server error", 500)


@appointments_bp.route("/", methods=["GET"], strict_slashes=False)
@jwt_required()
@roles_required(ADMIN_ROLE)
def list_appointments_for_admin():
    try:
        result = AppointmentService.list_all_appointments()
        return _success(result, 200)
    except ApiError as err:
        return _error(err.message, err.status_code)
    except Exception:
        logger.exception("Unexpected error in list_appointments_for_admin endpoint")
        return _error("Internal server error", 500)
