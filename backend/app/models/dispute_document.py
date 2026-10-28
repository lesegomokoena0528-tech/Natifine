from datetime import UTC, datetime

from app.config.database import db


class DisputeDocument(db.Model):

    __tablename__ = "dispute_documents"

    document_id = db.Column(
        db.Integer,
        primary_key=True
    )

    dispute_id = db.Column(
        db.Integer,
        db.ForeignKey("disputes.dispute_id"),
        nullable=False,
        index=True
    )

    file_name = db.Column(
        db.String(255),
        nullable=False,
        unique=True
    )

    original_name = db.Column(
        db.String(255),
        nullable=False
    )

    mime_type = db.Column(
        db.String(100),
        nullable=False
    )

    file_size = db.Column(
        db.BigInteger,
        nullable=False
    )

    storage_path = db.Column(
        db.String(500),
        nullable=False
    )

    uploaded_at = db.Column(
            db.DateTime,
            default=lambda: datetime.now(UTC)
    )

    def to_dict(self):

        return {

            "document_id": self.document_id,

            "dispute_id": self.dispute_id,

            "file_name": self.file_name,

            "original_name": self.original_name,

            "mime_type": self.mime_type,

            "file_size": self.file_size,

            "storage_path": self.storage_path,

            "uploaded_at": self.uploaded_at

        }