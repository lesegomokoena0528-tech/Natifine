from marshmallow import Schema
from marshmallow import fields
from marshmallow import validate


class FineRegistrationSchema(Schema):

    vehicle_id = fields.Integer(required=True)

    offence_code = fields.String(
        required=True,
        validate=validate.Length(max=20)
    )

    offence = fields.String(
        required=True,
        validate=validate.Length(max=255)
    )

    severity = fields.String(required=True)

    amount = fields.Decimal(
        required=True,
        places=2,
        as_string=True
    )

    location = fields.String(
        required=True
    )

    latitude = fields.Decimal(
        places=7,
        required=False,
        allow_none=True
    )

    longitude = fields.Decimal(
        places=7,
        required=False,
        allow_none=True
    )

    remarks = fields.String(
        allow_none=True
    )


class FineUpdateSchema(Schema):

    offence = fields.String()

    amount = fields.Decimal(
        places=2,
        as_string=True
    )

    location = fields.String()

    remarks = fields.String()

    severity = fields.String()

    status = fields.String()


class FineStatusSchema(Schema):

    status = fields.String(required=True)

    reason = fields.String(required=True)


class FineResponseSchema(Schema):

    fine_id = fields.Integer()

    fine_number = fields.String()

    vehicle_id = fields.Integer()

    officer_id = fields.Integer()

    offence_code = fields.String()

    offence = fields.String()

    severity = fields.String()

    amount = fields.Decimal(as_string=True)

    location = fields.String()

    latitude = fields.Decimal(as_string=True)

    longitude = fields.Decimal(as_string=True)

    evidence_photo = fields.String()

    issue_date = fields.DateTime()

    due_date = fields.DateTime()

    paid_date = fields.DateTime(allow_none=True)

    remarks = fields.String()

    status = fields.String()

    created_at = fields.DateTime()

    updated_at = fields.DateTime()