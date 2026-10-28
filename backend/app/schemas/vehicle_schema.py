from datetime import datetime

from marshmallow import Schema
from marshmallow import fields
from marshmallow import validate
from marshmallow import validates
from marshmallow import ValidationError


class VehicleRegistrationSchema(Schema):

    registration_number = fields.String(
        required=True,
        validate=validate.Length(
            min=3,
            max=20
        )
    )

    owner_id = fields.UUID(required=False, allow_none=True)

    make = fields.String(
        required=True,
        validate=validate.Length(max=100)
    )

    model = fields.String(
        required=True,
        validate=validate.Length(max=100)
    )

    year = fields.Integer(required=True)

    color = fields.String()

    vin = fields.String(
        required=True,
        validate=validate.Length(equal=17)
    )

    engine_number = fields.String()

    vehicle_type = fields.String(required=True)

    @validates("year")
    def validate_year(self, value, **kwargs):
        current_year = datetime.now().year

        if value < 1900:
            raise ValidationError(
                "Invalid manufacturing year."
            )

        if value > current_year + 1:
            raise ValidationError(
                "Manufacturing year cannot be in the future."
            )


class VehicleUpdateSchema(Schema):

    make = fields.String()

    model = fields.String()

    color = fields.String()

    year = fields.Integer()

    vehicle_type = fields.String()

    status = fields.String()


class VehicleResponseSchema(Schema):

    vehicle_id = fields.Integer()

    registration_number = fields.String()

    make = fields.String()

    model = fields.String()

    year = fields.Integer()

    color = fields.String()

    vin = fields.String()

    engine_number = fields.String()

    vehicle_type = fields.String()

    status = fields.String()

    created_at = fields.DateTime()

    updated_at = fields.DateTime()