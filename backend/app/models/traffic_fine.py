from enum import Enum
from datetime import datetime, UTC

from app.config.database import db


class FineStatus(Enum):
    DRAFT = "DRAFT"
    ISSUED = "ISSUED"
    PAID = "PAID"
    DISPUTED = "DISPUTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED_DISPUTE = "APPROVED_DISPUTE"
    REJECTED_DISPUTE = "REJECTED_DISPUTE"
    CANCELLED = "CANCELLED"
    CLOSED = "CLOSED"


class OffenceSeverity(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TrafficFine(db.Model):

    __tablename__ = "traffic_fines"

    fine_id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    fine_number = db.Column(
        db.String(30),
        unique=True,
        nullable=False,
        index=True
    )

    vehicle_id = db.Column(
        db.BigInteger,
        db.ForeignKey("vehicles.vehicle_id"),
        nullable=False,
        index=True
    )

    officer_id = db.Column(
    db.String(36),
    db.ForeignKey("users.user_id"),
    nullable=False,
    index=True
    )

    offence_code = db.Column(
        db.String(20),
        nullable=False
    )

    offence = db.Column(
        db.String(255),
        nullable=False
    )

    severity = db.Column(
        db.Enum(OffenceSeverity),
        nullable=False
    )

    amount = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )

    location = db.Column(
        db.String(255),
        nullable=False
    )

    latitude = db.Column(
        db.Numeric(10, 7)
    )

    longitude = db.Column(
        db.Numeric(10, 7)
    )

    evidence_photo = db.Column(
        db.String(255)
    )

    issue_date = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    due_date = db.Column(
        db.DateTime,
        nullable=False
    )

    paid_date = db.Column(
        db.DateTime
    )

    remarks = db.Column(
        db.Text
    )

    status = db.Column(
        db.Enum(FineStatus),
        default=FineStatus.ISSUED,
        nullable=False
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

    # --------------------------------------
    # Relationships
    # --------------------------------------

    vehicle = db.relationship(
        "Vehicle",
        backref="traffic_fines"
    )

    officer = db.relationship(
        "User",
        foreign_keys=[officer_id]
    )

    history = db.relationship(
        "FineHistory",
        back_populates="fine",
        cascade="all, delete-orphan",
        lazy=True
    )

    # --------------------------------------
    # Helpers
    # --------------------------------------

    @property
    def owner_id(self):
        return self.vehicle.owner_id if self.vehicle else None

    @property
    def is_paid(self):
        return self.status == FineStatus.PAID

    @property
    def is_disputed(self):
        return self.status == FineStatus.DISPUTED

    @property
    def is_open(self):
        return self.status in [
            FineStatus.ISSUED,
            FineStatus.DISPUTED,
            FineStatus.UNDER_REVIEW
        ]

    def to_dict(self):

        return {

            "fine_id": self.fine_id,

            "fine_number": self.fine_number,

            "vehicle_id": self.vehicle_id,

            "registration_number": self.vehicle.registration_number if self.vehicle else None,

            "vehicle_make": self.vehicle.make if self.vehicle else None,

            "vehicle_model": self.vehicle.model if self.vehicle else None,

            "owner_id": self.vehicle.owner_id if self.vehicle else None,

            "owner_name": self.vehicle.owner.full_name if self.vehicle and self.vehicle.owner else None,

            "owner_id_number": self.vehicle.owner.id_number if self.vehicle and self.vehicle.owner else None,

            "officer_id": self.officer_id,

            "officer_name": self.officer.full_name if self.officer else None,

            "offence_code": self.offence_code,

            "offence": self.offence,

            "severity": self.severity.value,

            "amount": float(self.amount),

            "location": self.location,

            "latitude": float(self.latitude) if self.latitude else None,

            "longitude": float(self.longitude) if self.longitude else None,

            "evidence_photo": self.evidence_photo,

            "issue_date": self.issue_date.isoformat() if self.issue_date else None,

            "due_date": self.due_date.isoformat() if self.due_date else None,

            "paid_date": self.paid_date.isoformat() if self.paid_date else None,

            "remarks": self.remarks,

            "status": self.status.value,

            "created_at": self.created_at.isoformat() if self.created_at else None,

            "updated_at": self.updated_at.isoformat() if self.updated_at else None

        }