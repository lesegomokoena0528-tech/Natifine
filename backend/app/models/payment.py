from datetime import datetime, UTC

from app.config.database import db

from app.constants.payment_status import PaymentStatus
from app.constants.payment_method import PaymentMethod
from app.constants.gateway import PaymentGateway


class Payment(db.Model):

    __tablename__ = "payments"

    payment_id = db.Column(
        db.Integer,
        primary_key=True
    )

    fine_id = db.Column(
        db.Integer,
        db.ForeignKey("traffic_fines.fine_id"),
        nullable=False,
        index=True
    )

    user_id = db.Column(
    db.String(36),
    db.ForeignKey("users.user_id"),
    nullable=False,
    index=True
    )

    gateway = db.Column(
        db.Enum(PaymentGateway),
        nullable=False
    )

    payment_method = db.Column(
        db.Enum(PaymentMethod),
        nullable=False
    )

    amount = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    currency = db.Column(
        db.String(3),
        nullable=False,
        default="ZAR"
    )

    payment_reference = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    gateway_reference = db.Column(
        db.String(150),
        unique=True
    )

    transaction_id = db.Column(
        db.String(150),
        unique=True
    )

    status = db.Column(
        db.Enum(PaymentStatus),
        nullable=False,
        default=PaymentStatus.PENDING
    )

    paid_at = db.Column(
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

    # Relationships
    fine = db.relationship(
        "TrafficFine",
        backref="payments",
        lazy=True
    )

    user = db.relationship(
        "User",
        backref="payments",
        lazy=True
    )

    refunds = db.relationship(
        "Refund",
        backref="payment",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def to_dict(self):

        return {

            "payment_id": self.payment_id,

            "fine_id": self.fine_id,

            "user_id": self.user_id,

            "gateway": self.gateway.value if hasattr(self.gateway, 'value') else str(self.gateway),

            "payment_method": self.payment_method.value if hasattr(self.payment_method, 'value') else str(self.payment_method),

            "amount": float(self.amount),

            "currency": self.currency,

            "payment_reference": self.payment_reference,

            "gateway_reference": self.gateway_reference,

            "transaction_id": self.transaction_id,

            "fine_number": self.fine.fine_number if self.fine else None,

            "status": self.status.value if hasattr(self.status, 'value') else str(self.status),

            "paid_at": self.paid_at.isoformat() if self.paid_at else None,

            "created_at": self.created_at.isoformat() if self.created_at else None,

            "updated_at": self.updated_at.isoformat() if self.updated_at else None

        }