from datetime import datetime, UTC

from app.config.database import db

from app.constants.refund_status import RefundStatus


class Refund(db.Model):

    __tablename__ = "refunds"

    refund_id = db.Column(
        db.Integer,
        primary_key=True
    )

    payment_id = db.Column(
        db.Integer,
        db.ForeignKey("payments.payment_id"),
        nullable=False,
        index=True
    )

    amount = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    reason = db.Column(
        db.Text,
        nullable=False
    )

    refund_reference = db.Column(
        db.String(100),
        unique=True
    )

    status = db.Column(
        db.Enum(RefundStatus),
        default=RefundStatus.PENDING,
        nullable=False
    )

    approved_by = db.Column(
    db.String(36),
    db.ForeignKey("users.user_id"),
    nullable=True,
    index=True
    )

    approved_date = db.Column(
        db.DateTime,
        nullable=True
    )

    admin_note = db.Column(
        db.Text,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(UTC)
    )

    def to_dict(self):

        return {

            "refund_id": self.refund_id,

            "payment_id": self.payment_id,

            "amount": float(self.amount),

            "reason": self.reason,

            "refund_reference": self.refund_reference,

            "status": self.status.value if hasattr(self.status, 'value') else str(self.status),

            "approved_by": self.approved_by,

            "approved_date": self.approved_date.isoformat() if self.approved_date else None,

            "admin_note": self.admin_note,

            "created_at": self.created_at.isoformat() if self.created_at else None

        }