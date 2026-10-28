from datetime import datetime, UTC

from app.config.database import db


class AuditLog(db.Model):

    __tablename__ = "audit_logs"

    audit_id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.String(36),
        nullable=False,
        index=True
    )

    username = db.Column(
        db.String(150),
        nullable=False
    )

    role = db.Column(
        db.String(30),
        nullable=False
    )

    action = db.Column(
        db.String(100),
        nullable=False,
        index=True
    )

    entity = db.Column(
        db.String(100),
        nullable=False
    )

    entity_id = db.Column(
        db.String(100)
    )

    description = db.Column(
        db.Text
    )

    ip_address = db.Column(
        db.String(50)
    )

    request_method = db.Column(
        db.String(10)
    )

    endpoint = db.Column(
        db.String(255)
    )

    status_code = db.Column(
        db.Integer
    )

    old_value = db.Column(
        db.JSON
    )

    new_value = db.Column(
        db.JSON
    )

    correlation_id = db.Column(
        db.String(100),
        unique=True,
        index=True
    )

    created_at = db.Column(
            db.DateTime,
            default=lambda: datetime.now(UTC)
    )
    

    def to_dict(self):

        return {

            "audit_id": self.audit_id,

            "user_id": self.user_id,

            "username": self.username,

            "role": self.role,

            "action": self.action,

            "entity": self.entity,

            "entity_id": self.entity_id,

            "description": self.description,

            "ip_address": self.ip_address,

            "request_method": self.request_method,

            "endpoint": self.endpoint,

            "status_code": self.status_code,

            "old_value": self.old_value,

            "new_value": self.new_value,

            "correlation_id": self.correlation_id,

            "created_at": self.created_at.isoformat()

        }