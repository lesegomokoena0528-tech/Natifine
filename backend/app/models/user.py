from enum import Enum

from datetime import datetime, UTC

from app.config.database import db

import bcrypt

import uuid


class UserRole(Enum):
    ADMIN = "ADMIN"
    OFFICER = "OFFICER"
    CITIZEN = "CITIZEN"


class UserStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    LOCKED = "LOCKED"


class User(db.Model):

    __tablename__ = "users"

    user_id = db.Column(
    db.String(36),
    primary_key=True,
    default=lambda: str(uuid.uuid4()))

    id_number = db.Column(
        db.String(13),
        nullable=False,
        unique=True
    )

    first_name = db.Column(
        db.String(100),
        nullable=False
    )

    last_name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(150),
        nullable=False,
        unique=True
    )

    phone = db.Column(
        db.String(20),
        unique=True
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.Enum(UserRole),
        nullable=False,
        default=UserRole.CITIZEN
    )

    status = db.Column(
        db.Enum(UserStatus),
        nullable=False,
        default=UserStatus.ACTIVE
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
    
    # -------------------------
# Relationships
# -------------------------

    vehicles = db.relationship(
        "Vehicle",
        back_populates="owner",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )

    # -------------------------
    # Password Methods
    # -------------------------

    def set_password(self, raw_password):

        salt = bcrypt.gensalt()

        self.password = bcrypt.hashpw(
            raw_password.encode("utf-8"),
            salt
        ).decode("utf-8")

    def check_password(self, raw_password):

        return bcrypt.checkpw(
            raw_password.encode("utf-8"),
            self.password.encode("utf-8")
        )

    # -------------------------

    @property
    def full_name(self):

        return f"{self.first_name} {self.last_name}"

    # -------------------------

    def is_admin(self):

        return self.role == UserRole.ADMIN

    def is_officer(self):

        return self.role == UserRole.OFFICER

    def is_citizen(self):

        return self.role == UserRole.CITIZEN

    # -------------------------

    def is_active(self):

        return self.status == UserStatus.ACTIVE

    # -------------------------

    def to_dict(self):

        return {

            "user_id": self.user_id,

            "id_number": self.id_number,

            "first_name": self.first_name,

            "last_name": self.last_name,

            "full_name": self.full_name,

            "email": self.email,

            "phone": self.phone,

            "role": self.role.value,

            "status": self.status.value,

            "created_at": self.created_at.isoformat() if self.created_at else None,

            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }