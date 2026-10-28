from datetime import datetime, UTC

from app.config.database import db

from app.constants.notification_channel import NotificationChannel


class NotificationTemplate(db.Model):

    __tablename__ = "notification_templates"

    template_id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    channel = db.Column(
        db.Enum(NotificationChannel),
        nullable=False
    )

    subject = db.Column(
        db.String(255)
    )

    body = db.Column(
        db.Text,
        nullable=False
    )

    active = db.Column(
        db.Boolean,
        default=True
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

    def to_dict(self):

        return {

            "template_id": self.template_id,

            "name": self.name,

            "channel": self.channel.value,

            "subject": self.subject,

            "body": self.body,

            "active": self.active,

            "created_at": self.created_at,

            "updated_at": self.updated_at

        }