from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity

from app.services.notification_service import NotificationService

from app.repositories.user_repository import UserRepository

from app.schemas.notification_schema import (
    NotificationSchema,
    TemplateNotificationSchema
)

from app.utils.response import success_response, error_response


class NotificationController:

    def __init__(self):

        self.service = NotificationService()

        self.user_repository = UserRepository()

        self.notification_schema = NotificationSchema()

        self.template_schema = TemplateNotificationSchema()

    # =====================================================
    # SEND NOTIFICATION
    # =====================================================

    def send_notification(self):

        try:

            data = self.notification_schema.load(

                request.get_json()

            )

            notification = self.service.create_notification(

                user_id=str(data["user_id"]),

                title=data["title"],

                message=data["message"],

                channel=data["channel"],

                notification_type=data["type"],

                recipient=data["recipient"]

            )

            self.service.queue_notification(notification)

            return success_response(

                "Notification queued successfully",

                notification.to_dict(),

                201

            )

        except Exception as ex:

            return error_response(

                str(ex),

                400

            )

    # =====================================================
    # SEND TEMPLATE
    # =====================================================

    def send_template(self):

        try:

            data = self.template_schema.load(

                request.get_json()

            )

            user = self.user_repository.find_by_id(
                str(data["user_id"])
            )

            if user is None:

                return error_response(
                    "Recipient user not found",
                    404
                )

            result = self.service.send_from_template(

                template_name=data["template"],

                user=user,

                variables=data.get("variables") or {}

            )

            return success_response(

                "Template queued",

                result.to_dict()

            )

        except Exception as ex:

            return error_response(

                str(ex),

                400

            )

    # =====================================================
    # LIST TEMPLATES
    # =====================================================

    def templates(self):

        try:

            templates = self.service.repository.templates()

            return success_response(

                "Templates retrieved",

                [template.to_dict() for template in templates]

            )

        except Exception as ex:

            return error_response(

                str(ex),

                400

            )

    # =====================================================
    # USER NOTIFICATIONS
    # =====================================================

    def my_notifications(self):

        try:

            user_id = get_jwt_identity()

            notifications = self.service.user_notifications(

                user_id

            )

            return success_response(

                "Notifications retrieved",

                notifications

            )

        except Exception as ex:

            return error_response(

                str(ex),

                400

            )

    # =====================================================
    # MARK READ
    # =====================================================

    def mark_read(self, notification_id):

        try:

            notification = self.service.mark_read(

                notification_id

            )

            return success_response(

                "Notification marked as read",

                notification

            )

        except Exception as ex:

            return error_response(

                str(ex),

                400

            )

    # =====================================================
    # MARK DELIVERED
    # =====================================================

    def mark_delivered(self, notification_id):

        try:

            notification = self.service.mark_delivered(

                notification_id

            )

            return success_response(

                "Delivery updated",

                notification

            )

        except Exception as ex:

            return error_response(

                str(ex),

                400

            )

    # =====================================================
    # RETRY FAILED
    # =====================================================

    def retry_failed(self):

        try:

            result = self.service.retry_failed()

            return success_response(

                "Retry completed",

                result

            )

        except Exception as ex:

            return error_response(

                str(ex),

                400

            )

    # =====================================================
    # DASHBOARD STATISTICS
    # =====================================================

    def statistics(self):

        try:

            return success_response(

                "Statistics retrieved",

                self.service.statistics()

            )

        except Exception as ex:

            return error_response(

                str(ex),

                400

            )

    # =====================================================
    # GET NOTIFICATION
    # =====================================================

    def get_notification(self, notification_id):

        try:

            notification = self.service.repository.find_by_id(

                notification_id

            )

            if notification is None:

                return error_response(

                    "Notification not found",

                    404

                )

            return success_response(

                "Notification retrieved",

                notification.to_dict()

            )

        except Exception as ex:

            return error_response(

                str(ex),

                400

            )

    # =====================================================
    # DELETE NOTIFICATION
    # =====================================================

    def delete_notification(self, notification_id):

        try:

            notification = self.service.repository.find_by_id(

                notification_id

            )

            if notification is None:

                return error_response(

                    "Notification not found",

                    404

                )

            self.service.repository.delete(

                notification

            )

            return success_response(

                "Notification deleted"

            )

        except Exception as ex:

            return error_response(

                str(ex),

                400

            )