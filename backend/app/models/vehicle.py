from enum import Enum
from datetime import datetime, UTC

from app.config.database import db


class VehicleType(Enum):
    CAR = "CAR"
    TRUCK = "TRUCK"
    BUS = "BUS"
    MOTORCYCLE = "MOTORCYCLE"
    TAXI = "TAXI"
    OTHER = "OTHER"


class VehicleStatus(Enum):
    ACTIVE = "ACTIVE"
    SOLD = "SOLD"
    SCRAPPED = "SCRAPPED"
    STOLEN = "STOLEN"


class Vehicle(db.Model):

    __tablename__ = "vehicles"

    vehicle_id = db.Column(
        db.BigInteger,
        primary_key=True,
        autoincrement=True
    )

    registration_number = db.Column(
        db.String(20),
        nullable=False,
        unique=True,
        index=True
    )

    owner_id = db.Column(
    db.String(36),
    db.ForeignKey("users.user_id"),
    nullable=False,
    index=True
    )

    make = db.Column(
        db.String(100),
        nullable=False
    )

    model = db.Column(
        db.String(100),
        nullable=False
    )

    year = db.Column(
        db.Integer,
        nullable=False
    )

    color = db.Column(
        db.String(50)
    )

    vin = db.Column(
        db.String(17),
        unique=True,
        nullable=False
    )

    engine_number = db.Column(
        db.String(50),
        unique=True
    )

    vehicle_type = db.Column(
        db.Enum(VehicleType),
        default=VehicleType.CAR,
        nullable=False
    )

    status = db.Column(
        db.Enum(VehicleStatus),
        default=VehicleStatus.ACTIVE,
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

    # -------------------------
    # Relationships
    # -------------------------

    owner = db.relationship(
    "User",
    back_populates="vehicles"
    )

    # -------------------------
    # Helper Methods
    # -------------------------

    @property
    def full_name(self):
        return f"{self.make} {self.model}"

    def is_active(self):
        return self.status == VehicleStatus.ACTIVE

    def is_stolen(self):
        return self.status == VehicleStatus.STOLEN

    def to_dict(self):

        return {

            "vehicle_id": self.vehicle_id,

            "registration_number": self.registration_number,

            "owner_id": self.owner_id,

            "make": self.make,

            "model": self.model,

            "year": self.year,

            "color": self.color,

            "vin": self.vin,

            "engine_number": self.engine_number,

            "vehicle_type": self.vehicle_type.value if hasattr(self.vehicle_type, 'value') else str(self.vehicle_type),

            "status": self.status.value if hasattr(self.status, 'value') else str(self.status),

            "created_at": self.created_at.isoformat() if self.created_at else None,

            "updated_at": self.updated_at.isoformat() if self.updated_at else None

        }