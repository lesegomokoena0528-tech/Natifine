from datetime import datetime

from app.config.database import db


class FineHistory(db.Model):

    __tablename__ = "fine_history"

    history_id = db.Column(
        db.BigInteger,
        primary_key=True,
        autoincrement=True
    )

    fine_id = db.Column(
        db.Integer,
        db.ForeignKey("traffic_fines.fine_id"),
        nullable=False,
        index=True
    )

    changed_by = db.Column(
    db.String(36),
    db.ForeignKey("users.user_id"),
    nullable=False
    )

    old_status = db.Column(
        db.String(50)
    )

    new_status = db.Column(
        db.String(50),
        nullable=False
    )

    reason = db.Column(
        db.Text
    )

    change_date = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    fine = db.relationship(
        "TrafficFine",
        back_populates="history"
    )

    user = db.relationship(
        "User"
    )

    def to_dict(self):

        return {

            "history_id": self.history_id,

            "fine_id": self.fine_id,

            "changed_by": self.changed_by,

            "old_status": self.old_status,

            "new_status": self.new_status,

            "reason": self.reason,

            "change_date": self.change_date.isoformat()

        }