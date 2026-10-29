from types import SimpleNamespace

from app.models.user import UserRole, UserStatus
from app.services.report_service import ReportService


def test_user_report_counts_enum_roles_and_supported_statuses():
    service = ReportService()
    service.admin_repository.get_all_users = lambda: [
        SimpleNamespace(role=UserRole.ADMIN, status=UserStatus.ACTIVE),
        SimpleNamespace(role=UserRole.OFFICER, status=UserStatus.ACTIVE),
        SimpleNamespace(role=UserRole.OFFICER, status=UserStatus.LOCKED),
        SimpleNamespace(role=UserRole.CITIZEN, status=UserStatus.ACTIVE),
        SimpleNamespace(role=UserRole.CITIZEN, status=UserStatus.INACTIVE),
        SimpleNamespace(role=UserRole.CITIZEN, status=UserStatus.ACTIVE),
    ]

    report = service.user_report()

    assert report == {
        "total_users": 6,
        "active": 4,
        "inactive": 1,
        "locked": 1,
        "administrators": 1,
        "officers": 2,
        "citizens": 3,
    }
