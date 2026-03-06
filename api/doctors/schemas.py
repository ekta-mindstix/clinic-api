from marshmallow import Schema, ValidationError, fields


class DoctorCreateSchema(Schema):
    email = fields.Email(required=True)
    full_name = fields.String(required=True)
    password = fields.String(required=True)
    license_number = fields.String(required=True)
    specialty = fields.String(required=False, allow_none=True)


class DoctorAssignSchema(Schema):
    doctor_id = fields.Integer(required=True)


class DoctorAvailabilityCreateSchema(Schema):
    start_at = fields.DateTime(required=True)
    end_at = fields.DateTime(required=True)


class DoctorAvailabilityUpdateSchema(Schema):
    start_at = fields.DateTime(required=False)
    end_at = fields.DateTime(required=False)


def load_or_raise(schema: Schema, payload: dict) -> dict:
    try:
        return schema.load(payload)
    except ValidationError as err:
        raise ValueError(err.messages) from err
