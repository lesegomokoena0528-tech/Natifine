from marshmallow import Schema, fields, validate


class PaymentCreateSchema(Schema):

    fine_id = fields.Integer(required=True)

    amount = fields.Decimal(
        required=True,
        places=2
    )

    gateway = fields.String(
        required=True,
        validate=validate.OneOf([
            "PAYFAST",
            "OZOW",
            "PEACH",
            "STRIPE",
            "PAYPAL",
            "INTERNAL"
        ])
    )

    payment_method = fields.String(
        required=True,
        validate=validate.OneOf([
            "CARD",
            "EFT",
            "PAYFAST",
            "OZOW",
            "PEACH",
            "PAYPAL",
            "CASH",
            "MOBILE"
        ])
    )


class PaymentVerificationSchema(Schema):

    payment_reference = fields.String(
        required=True
    )

    gateway_reference = fields.String(
        required=True
    )


class RefundRequestSchema(Schema):

    amount = fields.Decimal(
        required=True,
        places=2
    )

    reason = fields.String(
        required=True,
        validate=validate.Length(
            min=10,
            max=500
        )
    )