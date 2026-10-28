from enum import Enum


class NotificationStatus(Enum):

    PENDING = "PENDING"

    QUEUED = "QUEUED"

    SENDING = "SENDING"

    SENT = "SENT"

    DELIVERED = "DELIVERED"

    READ = "READ"

    FAILED = "FAILED"

    CANCELLED = "CANCELLED"