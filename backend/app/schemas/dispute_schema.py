from marshmallow import (
    Schema,
    fields,
    validate
)


class CreateDisputeSchema(Schema):

    fine_id = fields.Integer(
        required=True
    )

    description = fields.String(

        required=True,

        validate=validate.Length(
            min=20,
            max=3000
        )
    )


class ReviewDisputeSchema(Schema):

    review_notes = fields.String(

        required=True,

        validate=validate.Length(
            min=10,
            max=2000
        )
    )


class UploadDocumentSchema(Schema):

    file = fields.Raw(
        required=True
    )


class RequestMoreInformationSchema(Schema):

    message = fields.String(

        required=True,

        validate=validate.Length(
            min=10,
            max=2000
        )
    )