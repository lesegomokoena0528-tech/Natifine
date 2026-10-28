import re

from marshmallow import Schema

from marshmallow import fields

from marshmallow import validate


SA_ID_NUMBER_RE = re.compile(r"^\d{13}$")

SA_PHONE_RE = re.compile(r"^(?:\+27|0)\d{9}$")


class RegisterSchema(Schema):

    id_number = fields.String(
        required=True,
        validate=validate.Regexp(
            SA_ID_NUMBER_RE,
            error="ID number must be exactly 13 digits."
        )
    )

    first_name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100)
    )

    last_name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100)
    )

    email = fields.Email(
        required=True,
        validate=validate.Length(max=150)
    )

    phone = fields.String(
        required=True,
        validate=validate.Regexp(
            SA_PHONE_RE,
            error="Enter a valid South African cellphone number, e.g. 0821234567."
        )
    )

    password = fields.String(
        required=True,
        validate=validate.Length(min=8)
    )


class LoginSchema(Schema):

    email = fields.Email(required=True)

    password = fields.String(required=True)


class UserResponseSchema(Schema):

    user_id = fields.UUID()

    id_number = fields.String()

    first_name = fields.String()

    last_name = fields.String()

    email = fields.Email()

    phone = fields.String()

    role = fields.String()

    status = fields.String()

    created_at = fields.DateTime()
