from marshmallow import Schema, ValidationError, fields


class DepartmentCreateSchema(Schema):
    name = fields.String(required=True)
    description = fields.String(required=False, allow_none=True)


def load_or_raise(schema: Schema, payload: dict) -> dict:
    try:
        return schema.load(payload)
    except ValidationError as err:
        raise ValueError(err.messages) from err
