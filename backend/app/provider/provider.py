from flask import Blueprint, request

from app.services.notification_service import NotificationService

bp = Blueprint(
    "notification_webhook",
    __name__
)

service = NotificationService()


@bp.route(
    "/webhooks/twilio",
    methods=["POST"]
)
def twilio():

    data = request.form

    message_id = data.get("MessageSid")

    status = data.get("MessageStatus")

    service.update_provider_status(

        message_id,

        status

    )

    return "", 200