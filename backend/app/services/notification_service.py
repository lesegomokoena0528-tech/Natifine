from app.models.notification import Notification

from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository

from app.services.email_service import EmailService
from app.services.sms_service import SMSService
from app.services.whatsapp_service import WhatsAppService
from app.services.notification_dispatcher import NotificationDispatcher

from app.constants.notification_channel import NotificationChannel
from app.constants.notification_status import NotificationStatus
from app.constants.notification_type import NotificationType

from app.exceptions.notification_exceptions import (
    NotificationNotFoundException,
    NotificationChannelException,
    NotificationDeliveryException,
    TemplateNotFoundException
)


class NotificationService:

    def __init__(self):

        self.repository = NotificationRepository()

        self.user_repository = UserRepository()

        self.dispatcher = NotificationDispatcher()

        self.email_service = EmailService()

        self.sms_service = SMSService()

        self.whatsapp_service = WhatsAppService()

    # =====================================================
    # CREATE
    # =====================================================

    def create_notification(
        self,
        user_id,
        title,
        message,
        channel,
        notification_type,
        recipient
    ):

        notification = Notification()

        notification.user_id = user_id
        notification.title = title
        notification.message = message
        notification.channel = channel
        notification.type = notification_type
        notification.status = NotificationStatus.PENDING
        notification.recipient = recipient

        return self.repository.create(notification)

    # =====================================================
    # QUEUE
    # =====================================================

    def queue_notification(self, notification):

        notification.status = NotificationStatus.QUEUED

        self.repository.update(notification)

        self.dispatcher.queue(notification.notification_id)

        return notification

    # =====================================================
    # SEND
    # =====================================================

    def send_notification(self, notification_id):

        notification = self.repository.find_by_id(notification_id)

        if notification is None:
            raise NotificationNotFoundException()

        notification.status = NotificationStatus.SENDING

        self.repository.update(notification)

        try:

            if notification.channel == NotificationChannel.EMAIL:

                result = self.email_service.send(notification)

            elif notification.channel == NotificationChannel.SMS:

                result = self.sms_service.send(notification)

            elif notification.channel == NotificationChannel.WHATSAPP:

                result = self.whatsapp_service.send(notification)

            else:

                raise NotificationChannelException()

            notification.provider = result.get("provider")

            notification.provider_message_id = result.get("message_id")

            self.repository.mark_sent(notification)

            return notification

        except Exception as ex:

            self.repository.mark_failed(
                notification,
                str(ex)
            )

            raise NotificationDeliveryException(str(ex))

    # =====================================================
    # TEMPLATE
    # =====================================================

    def send_from_template(
        self,
        template_name,
        user,
        variables
    ):

        template = self.repository.template_by_name(template_name)

        if template is None:

            raise TemplateNotFoundException()

        subject = template.subject

        body = template.body

        for key, value in variables.items():

            placeholder = "{{" + key + "}}"

            body = body.replace(
                placeholder,
                str(value)
            )

            if subject:

                subject = subject.replace(
                    placeholder,
                    str(value)
                )

        notification = self.create_notification(

            user.user_id,

            subject or template.name,

            body,

            template.channel,

            NotificationType.SYSTEM_NOTIFICATION,

            self._recipient(
                user,
                template.channel
            )
        )

        return self.queue_notification(notification)

    # =====================================================
    # RETRY FAILED
    # =====================================================

    def retry_failed(self):

        notifications = self.repository.retry_queue()

        count = 0

        for notification in notifications:

            self.queue_notification(notification)

            count += 1

        return {

            "retried": count

        }

    # =====================================================
    # MARK DELIVERED
    # =====================================================

    def mark_delivered(self, notification_id):

        notification = self.repository.find_by_id(notification_id)

        if notification is None:

            raise NotificationNotFoundException()

        self.repository.mark_delivered(notification)

        return notification.to_dict()

    # =====================================================
    # MARK READ
    # =====================================================

    def mark_read(self, notification_id):

        notification = self.repository.find_by_id(notification_id)

        if notification is None:

            raise NotificationNotFoundException()

        self.repository.mark_read(notification)

        return notification.to_dict()

    # =====================================================
    # USER HISTORY
    # =====================================================

    def user_notifications(self, user_id):

        return [

            notification.to_dict()

            for notification

            in self.repository.user_notifications(user_id)

        ]

    # =====================================================
    # BUSINESS WORKFLOW NOTIFICATIONS
    # =====================================================

    def fine_issued(self, user_id, fine):
        user = self.user_repository.find_by_id(user_id)
        if not user:
            return None
        title = f"Traffic Fine Issued: {fine.fine_number}"
        message = (
            f"Dear {user.first_name}, a traffic fine ({fine.fine_number}) of ZAR {float(fine.amount):.2f} "
            f"was issued for offence '{fine.offence}' at {fine.location}. Please view or settle online."
        )
        notification = self.create_notification(
            user_id=user.user_id,
            title=title,
            message=message,
            channel=NotificationChannel.SMS,
            notification_type=NotificationType.FINE_ISSUED,
            recipient=user.phone or user.email
        )
        return self.send_notification(notification.notification_id)

    def payment_success(self, user_id, payment):
        user = self.user_repository.find_by_id(user_id)
        if not user:
            return None
        title = f"Payment Successful: {payment.payment_reference}"
        message = (
            f"Dear {user.first_name}, payment of ZAR {float(payment.amount):.2f} was received for "
            f"reference {payment.payment_reference}. Your fine record is now marked as Paid."
        )
        notification = self.create_notification(
            user_id=user.user_id,
            title=title,
            message=message,
            channel=NotificationChannel.SMS,
            notification_type=NotificationType.PAYMENT_RECEIVED,
            recipient=user.phone or user.email
        )
        return self.send_notification(notification.notification_id)

    def dispute_created(self, user_id, dispute):
        user = self.user_repository.find_by_id(user_id)
        if not user:
            return None
        title = f"Dispute Submitted: #{dispute.dispute_id if hasattr(dispute, 'dispute_id') else ''}"
        fine_id = getattr(dispute, 'fine_id', '')
        message = (
            f"Dear {user.first_name}, your dispute for fine ID {fine_id} has been received "
            f"and is currently Under Review by an adjudication officer."
        )
        notification = self.create_notification(
            user_id=user.user_id,
            title=title,
            message=message,
            channel=NotificationChannel.EMAIL,
            notification_type=NotificationType.DISPUTE_SUBMITTED,
            recipient=user.email or user.phone
        )
        return self.send_notification(notification.notification_id)

    def dispute_decision(self, user_id, dispute):
        user = self.user_repository.find_by_id(user_id)
        if not user:
            return None
        status_val = dispute.status.value if hasattr(dispute.status, 'value') else str(dispute.status)
        is_upheld = "UPHELD" in status_val or "APPROVED" in status_val
        status_text = "Upheld (Fine Dismissed)" if is_upheld else "Rejected"
        title = f"Dispute Decision: {status_text}"
        notes = getattr(dispute, 'review_notes', '') or 'No additional notes'
        message = (
            f"Dear {user.first_name}, your dispute #{getattr(dispute, 'dispute_id', '')} was reviewed. "
            f"Decision: {status_text}. Notes: {notes}."
        )
        notif_type = NotificationType.DISPUTE_APPROVED if is_upheld else NotificationType.DISPUTE_REJECTED
        notification = self.create_notification(
            user_id=user.user_id,
            title=title,
            message=message,
            channel=NotificationChannel.SMS,
            notification_type=notif_type,
            recipient=user.phone or user.email
        )
        return self.send_notification(notification.notification_id)

    def dispute_approved(self, user_id, dispute):
        return self.dispute_decision(user_id, dispute)

    def dispute_rejected(self, user_id, dispute):
        return self.dispute_decision(user_id, dispute)

    def more_information(self, user_id, dispute):
        user = self.user_repository.find_by_id(user_id)
        if not user:
            return None
        notes = getattr(dispute, 'review_notes', '') or 'Please provide further details.'
        title = f"More Information Required: Dispute #{getattr(dispute, 'dispute_id', '')}"
        message = (
            f"Dear {user.first_name}, additional information is required for your dispute "
            f"#{getattr(dispute, 'dispute_id', '')} on fine ID {getattr(dispute, 'fine_id', '')}. "
            f"Officer notes: {notes}. Please update your submission."
        )
        notification = self.create_notification(
            user_id=user.user_id,
            title=title,
            message=message,
            channel=NotificationChannel.EMAIL,
            notification_type=NotificationType.MORE_INFORMATION_REQUIRED,
            recipient=user.email or user.phone
        )
        return self.send_notification(notification.notification_id)

    def reminder(self, user_id, fine):
        user = self.user_repository.find_by_id(user_id)
        if not user:
            return None
        title = f"Urgent Reminder: Fine {fine.fine_number} Outstanding"
        message = (
            f"Dear {user.first_name}, your traffic fine {fine.fine_number} of ZAR {float(fine.amount):.2f} "
            f"is outstanding. Please settle or submit a dispute to avoid late penalties."
        )
        notification = self.create_notification(
            user_id=user.user_id,
            title=title,
            message=message,
            channel=NotificationChannel.SMS,
            notification_type=NotificationType.FINE_DUE,
            recipient=user.phone or user.email
        )
        return self.send_notification(notification.notification_id)

    def send_welcome_email(self, user):
        if not user:
            return None
        title = "Welcome to NatiFine SA"
        message = (
            f"Dear {user.first_name}, welcome to NatiFine SA. "
            f"Your account has been created successfully. "
            f"You can now sign in to view and manage your traffic fines online."
        )
        notification = self.create_notification(
            user_id=user.user_id,
            title=title,
            message=message,
            channel=NotificationChannel.EMAIL,
            notification_type=NotificationType.WELCOME,
            recipient=user.email or user.phone
        )
        return self.send_notification(notification.notification_id)

    def password_reset(self, user, temporary_password):
        if not user:
            return None
        title = "Your NatiFine SA Password Has Been Reset"
        message = (
            f"Dear {user.first_name}, an administrator has reset your password. "
            f"Your temporary password is: {temporary_password}. "
            f"Please sign in and change it immediately."
        )
        notification = self.create_notification(
            user_id=user.user_id,
            title=title,
            message=message,
            channel=NotificationChannel.EMAIL,
            notification_type=NotificationType.PASSWORD_RESET,
            recipient=user.email or user.phone
        )
        return self.send_notification(notification.notification_id)

    # =====================================================
    # DASHBOARD
    # =====================================================

    def statistics(self):

        return {

            "overall": self.repository.statistics(),

            "channels": self.repository.channel_statistics(),

            "monthly": self.repository.monthly_statistics()

        }

    # =====================================================
    # PRIVATE
    # =====================================================

    @staticmethod
    def _recipient(user, channel):

        if channel == NotificationChannel.EMAIL:

            return user.email

        if channel in (
            NotificationChannel.SMS,
            NotificationChannel.WHATSAPP
        ):

            return user.phone

        raise NotificationChannelException()