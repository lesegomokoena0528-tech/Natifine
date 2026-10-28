from datetime import datetime

from sqlalchemy import desc, func, or_
from sqlalchemy.orm import joinedload

from app.config.database import db

from app.models.notification import Notification
from app.models.notification_template import NotificationTemplate

from app.constants.notification_status import NotificationStatus
from app.constants.notification_channel import NotificationChannel
from app.constants.notification_type import NotificationType


class NotificationRepository:

    # ==========================================================
    # CREATE
    # ==========================================================

    def create(self, notification):

        db.session.add(notification)
        db.session.commit()

        return notification

    # ==========================================================
    # UPDATE
    # ==========================================================

    def update(self, notification):

        notification.updated_at = datetime.utcnow()

        db.session.commit()

        return notification

    # ==========================================================
    # DELETE
    # ==========================================================

    def delete(self, notification):

        db.session.delete(notification)
        db.session.commit()

    # ==========================================================
    # FIND BY ID
    # ==========================================================

    def find_by_id(self, notification_id):

        return (

            Notification.query

            .options(

                joinedload(Notification.user)

            )

            .filter(

                Notification.notification_id == notification_id

            )

            .first()

        )

    # ==========================================================
    # USER NOTIFICATIONS
    # ==========================================================

    def user_notifications(
            self,
            user_id
    ):

        return (

            Notification.query

            .filter(

                Notification.user_id == user_id

            )

            .order_by(

                desc(Notification.created_at)

            )

            .all()

        )

    # ==========================================================
    # UNREAD
    # ==========================================================

    def unread_notifications(
            self,
            user_id
    ):

        return (

            Notification.query

            .filter(

                Notification.user_id == user_id,

                Notification.status != NotificationStatus.READ

            )

            .order_by(

                desc(Notification.created_at)

            )

            .all()

        )

    # ==========================================================
    # PENDING QUEUE
    # ==========================================================

    def pending_notifications(self):

        return (

            Notification.query

            .filter(

                Notification.status.in_([

                    NotificationStatus.PENDING,

                    NotificationStatus.QUEUED

                ])

            )

            .order_by(

                Notification.created_at

            )

            .all()

        )

    # ==========================================================
    # FAILED
    # ==========================================================

    def failed_notifications(self):

        return (

            Notification.query

            .filter(

                Notification.status ==
                NotificationStatus.FAILED

            )

            .order_by(

                Notification.created_at

            )

            .all()

        )

    # ==========================================================
    # READY FOR RETRY
    # ==========================================================

    def retry_queue(
            self,
            max_attempts=5
    ):

        return (

            Notification.query

            .filter(

                Notification.status ==
                NotificationStatus.FAILED,

                Notification.retry_count < max_attempts

            )

            .all()

        )

    # ==========================================================
    # MARK AS SENT
    # ==========================================================

    def mark_sent(
            self,
            notification
    ):

        notification.status = NotificationStatus.SENT

        notification.sent_date = datetime.utcnow()

        self.update(notification)

    # ==========================================================
    # MARK DELIVERED
    # ==========================================================

    def mark_delivered(
            self,
            notification
    ):

        notification.status = NotificationStatus.DELIVERED

        notification.delivered_date = datetime.utcnow()

        self.update(notification)

    # ==========================================================
    # MARK READ
    # ==========================================================

    def mark_read(
            self,
            notification
    ):

        notification.status = NotificationStatus.READ

        notification.read_date = datetime.utcnow()

        self.update(notification)

    # ==========================================================
    # MARK FAILED
    # ==========================================================

    def mark_failed(
            self,
            notification,
            message
    ):

        notification.status = NotificationStatus.FAILED

        notification.retry_count += 1

        notification.error_message = message

        self.update(notification)

    # ==========================================================
    # SEARCH
    # ==========================================================

    def search(
            self,
            keyword
    ):

        keyword = f"%{keyword}%"

        return (

            Notification.query

            .filter(

                or_(

                    Notification.title.ilike(keyword),

                    Notification.message.ilike(keyword),

                    Notification.recipient.ilike(keyword)

                )

            )

            .order_by(

                desc(Notification.created_at)

            )

            .all()

        )

    # ==========================================================
    # PAGINATION
    # ==========================================================

    def paginate(
            self,
            page,
            per_page
    ):

        return (

            Notification.query

            .order_by(

                desc(Notification.created_at)

            )

            .paginate(

                page=page,

                per_page=per_page,

                error_out=False

            )

        )

    # ==========================================================
    # CREATE TEMPLATE
    # ==========================================================

    def create_template(
            self,
            template
    ):

        db.session.add(template)

        db.session.commit()

        return template

    # ==========================================================
    # TEMPLATE BY NAME
    # ==========================================================

    def template_by_name(
            self,
            name
    ):

        return NotificationTemplate.query.filter(

            NotificationTemplate.name == name,

            NotificationTemplate.active == True

        ).first()

    # ==========================================================
    # TEMPLATE BY ID
    # ==========================================================

    def template_by_id(
            self,
            template_id
    ):

        return NotificationTemplate.query.filter_by(

            template_id=template_id

        ).first()

    # ==========================================================
    # ALL TEMPLATES
    # ==========================================================

    def templates(self):

        return (

            NotificationTemplate.query

            .order_by(

                NotificationTemplate.name

            )

            .all()

        )

    # ==========================================================
    # UPDATE TEMPLATE
    # ==========================================================

    def update_template(
            self,
            template
    ):

        template.updated_at = datetime.utcnow()

        db.session.commit()

        return template

    # ==========================================================
    # DELETE TEMPLATE
    # ==========================================================

    def delete_template(
            self,
            template
    ):

        db.session.delete(template)

        db.session.commit()

    # ==========================================================
    # STATISTICS
    # ==========================================================

    def statistics(self):

        return {

            "total":

                Notification.query.count(),

            "pending":

                Notification.query.filter_by(

                    status=NotificationStatus.PENDING

                ).count(),

            "queued":

                Notification.query.filter_by(

                    status=NotificationStatus.QUEUED

                ).count(),

            "sent":

                Notification.query.filter_by(

                    status=NotificationStatus.SENT

                ).count(),

            "delivered":

                Notification.query.filter_by(

                    status=NotificationStatus.DELIVERED

                ).count(),

            "failed":

                Notification.query.filter_by(

                    status=NotificationStatus.FAILED

                ).count(),

            "read":

                Notification.query.filter_by(

                    status=NotificationStatus.READ

                ).count()
        }

    # ==========================================================
    # CHANNEL STATISTICS
    # ==========================================================

    def channel_statistics(self):

        return (

            db.session.query(

                Notification.channel,

                func.count(Notification.notification_id)

            )

            .group_by(

                Notification.channel

            )

            .all()

        )

    # ==========================================================
    # MONTHLY STATISTICS
    # ==========================================================

    def monthly_statistics(self):

        return (

            db.session.query(

                func.year(Notification.created_at),

                func.month(Notification.created_at),

                func.count(Notification.notification_id)

            )

            .group_by(

                func.year(Notification.created_at),

                func.month(Notification.created_at)

            )

            .all()

        )

    # ==========================================================
    # EXISTS
    # ==========================================================

    def exists(
            self,
            notification_id
    ):

        return (

            db.session.query(

                Notification.notification_id

            )

            .filter(

                Notification.notification_id == notification_id

            )

            .first()

            is not None

        )