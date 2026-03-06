from marshmallow import Schema, ValidationError, fields


class AppointmentCreateSchema(Schema):
    doctor_id = fields.Integer(required=True)
    appointment_at = fields.DateTime(required=True)
    notes = fields.String(required=False, allow_none=True)


class AppointmentUpdateSchema(Schema):
    appointment_at = fields.DateTime(required=False)
    notes = fields.String(required=False, allow_none=True)


def load_or_raise(schema: Schema, payload: dict) -> dict:
    try:
        return schema.load(payload)
    except ValidationError as err:
        raise ValueError(err.messages) from err
