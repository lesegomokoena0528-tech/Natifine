from datetime import datetime, UTC

from app.config.database import db
from app.constants.dispute_status import DisputeStatus


class Dispute(db.Model):

    __tablename__ = "disputes"

    dispute_id = db.Column(
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

    description = db.Column(
        db.Text,
        nullable=False
    )

    status = db.Column(
        db.Enum(DisputeStatus),
        nullable=False,
        default=DisputeStatus.NEW
    )

    submitted_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    reviewed_by = db.Column(
    db.String(36),
    db.ForeignKey("users.user_id"),
    nullable=True
    )

    reviewed_at = db.Column(
        db.DateTime
    )

    review_notes = db.Column(
        db.Text
    )

    created_at = db.Column(
            db.DateTime,
            default=lambda: datetime.now(UTC)
    )

    updated_at = db.Column(
            db.DateTime,
            default=lambda: datetime.now(UTC)
    )

    # Relationships

    fine = db.relationship(
        "TrafficFine",
        backref="disputes",
        lazy=True
    )

    citizen = db.relationship(
        "User",
        foreign_keys=[user_id],
        lazy=True
    )

    reviewer = db.relationship(
        "User",
        foreign_keys=[reviewed_by],
        lazy=True
    )

    documents = db.relationship(
        "DisputeDocument",
        backref="dispute",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def to_dict(self):

        return {

            "dispute_id": self.dispute_id,

            "fine_id": self.fine_id,

            "user_id": self.user_id,

            "fine_number": self.fine.fine_number if self.fine else None,

            "citizen_name": self.citizen.full_name if self.citizen else None,

            "reviewer_name": self.reviewer.full_name if self.reviewer else None,

            "description": self.description,

            "status": self.status.value if hasattr(self.status, 'value') else str(self.status),

            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,

            "reviewed_by": self.reviewed_by,

            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,

            "review_notes": self.review_notes,

            "created_at": self.created_at.isoformat() if self.created_at else None,

            "updated_at": self.updated_at.isoformat() if self.updated_at else None

        }