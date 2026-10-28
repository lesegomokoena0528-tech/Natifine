from marshmallow import Schema, fields, validate


class CreateUserSchema(Schema):

    first_name = fields.String(required=True)

    last_name = fields.String(required=True)

    email = fields.Email(required=True)

    phone = fields.String(required=True)

    id_number = fields.String(required=True)

    password = fields.String(
        required=True,
        validate=validate.Length(min=8)
    )

    role = fields.String(required=True)


class UpdateUserSchema(Schema):

    first_name = fields.String()

    last_name = fields.String()

    phone = fields.String()

    status = fields.String()

    role = fields.String()