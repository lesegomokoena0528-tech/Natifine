from datetime import datetime, UTC

from app.config.database import db

from app.constants.notification_channel import NotificationChannel
from app.constants.notification_status import NotificationStatus
from app.constants.notification_type import NotificationType


class Notification(db.Model):

    __tablename__ = "notifications"

    notification_id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
    db.String(36),
    db.ForeignKey("users.user_id"),
    nullable=False,
    index=True
    )

    title = db.Column(
        db.String(255),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    channel = db.Column(
        db.Enum(NotificationChannel),
        nullable=False
    )

    type = db.Column(
        db.Enum(NotificationType),
        nullable=False
    )

    status = db.Column(
        db.Enum(NotificationStatus),
        default=NotificationStatus.PENDING,
        nullable=False
    )

    recipient = db.Column(
        db.String(255),
        nullable=False
    )

    provider = db.Column(
        db.String(100)
    )

    provider_message_id = db.Column(
        db.String(255)
    )

    retry_count = db.Column(
        db.Integer,
        default=0
    )

    error_message = db.Column(
        db.Text
    )

    sent_date = db.Column(
        db.DateTime
    )

    delivered_date = db.Column(
        db.DateTime
    )

    read_date = db.Column(
        db.DateTime
    )

    created_at = db.Column(
            db.DateTime,
            default=lambda: datetime.now(UTC)
    )
    
    updated_at = db.Column(
            db.DateTime,
            default=lambda: datetime.now(UTC),
            onupdate=lambda: datetime.now(UTC)
    )

    user = db.relationship(
        "User",
        backref="notifications",
        lazy=True
    )

    def to_dict(self):

        return {

            "notification_id": self.notification_id,

            "user_id": self.user_id,

            "title": self.title,

            "message": self.message,

            "channel": self.channel.value if hasattr(self.channel, 'value') else str(self.channel),

            "type": self.type.value if hasattr(self.type, 'value') else str(self.type),

            "status": self.status.value if hasattr(self.status, 'value') else str(self.status),

            "recipient": self.recipient,

            "provider": self.provider,

            "provider_message_id": self.provider_message_id,

            "retry_count": self.retry_count,

            "error_message": self.error_message,

            "sent_date": self.sent_date.isoformat() if self.sent_date else None,

            "delivered_date": self.delivered_date.isoformat() if self.delivered_date else None,

            "read_date": self.read_date.isoformat() if self.read_date else None,

            "created_at": self.created_at.isoformat() if self.created_at else None,

            "updated_at": self.updated_at.isoformat() if self.updated_at else None

        }