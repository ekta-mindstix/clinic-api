from marshmallow import Schema, ValidationError, fields


class RegisterSchema(Schema):
    email = fields.Email(required=True)
    full_name = fields.String(required=True)
    password = fields.String(required=True)


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


def load_or_raise(schema: Schema, payload: dict) -> dict:
    try:
        return schema.load(payload)
    except ValidationError as err:
        raise ValueError(err.messages) from err
