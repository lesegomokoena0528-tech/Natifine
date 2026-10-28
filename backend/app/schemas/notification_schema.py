from marshmallow import Schema, fields, validate


class NotificationSchema(Schema):

    user_id = fields.UUID(required=True)

    channel = fields.String(required=True)
    
    recipient = fields.String(
    required=True,
    validate=validate.Length(min=5, max=255)
    )

    type = fields.String(required=True)

    title = fields.String(
        required=True,
        validate=validate.Length(max=255)
    )

    message = fields.String(
        required=True,
        validate=validate.Length(min=1)
    )


class TemplateNotificationSchema(Schema):

    template = fields.String(required=True)

    user_id = fields.UUID(required=True)

    variables = fields.Dict(
        keys=fields.String(),
        values=fields.Raw(),
        load_default=dict
    )


class NotificationPreferenceSchema(Schema):

    email = fields.Boolean()

    sms = fields.Boolean()

    whatsapp = fields.Boolean()


class MarkAsReadSchema(Schema):

    notification_id = fields.Integer(required=True)