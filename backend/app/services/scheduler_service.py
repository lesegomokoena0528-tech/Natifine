from datetime import datetime, timedelta

from app.repositories.fine_repository import FineRepository
from app.repositories.notification_repository import NotificationRepository

from app.services.notification_service import NotificationService


class SchedulerService:

    def __init__(self):

        self.fine_repository = FineRepository()

        self.notification_service = NotificationService()

        self.notification_repository = NotificationRepository()

    # =====================================================
    # DAILY PAYMENT REMINDERS
    # =====================================================

    def send_due_reminders(self):

        fines = self.fine_repository.find_due_within_days(3)

        count = 0

        for fine in fines:

            self.notification_service.send_from_template(

                "FINE_DUE",

                fine.vehicle.owner,

                {

                    "fine_number": fine.fine_number,

                    "amount": fine.amount,

                    "due_date": fine.due_date.strftime("%d-%m-%Y")

                }

            )

            count += 1

        return count

    # =====================================================
    # OVERDUE REMINDERS
    # =====================================================

    def send_overdue_notifications(self):

        fines = self.fine_repository.find_overdue()

        count = 0

        for fine in fines:

            self.notification_service.send_from_template(

                "OVERDUE_FINE",

                fine.vehicle.owner,

                {

                    "fine_number": fine.fine_number,

                    "amount": fine.amount

                }

            )

            count += 1

        return count

    # =====================================================
    # RETRY FAILED
    # =====================================================

    def retry_failed_notifications(self):

        return self.notification_service.retry_failed()

    # =====================================================
    # CLEANUP
    # =====================================================

    def cleanup_old_notifications(self):

        cutoff = datetime.utcnow() - timedelta(days=365)

        notifications = self.notification_repository.find_before(cutoff)

        deleted = 0

        for notification in notifications:

            self.notification_repository.delete(notification)

            deleted += 1

        return deleted

    # =====================================================
    # MONTHLY REPORT
    # =====================================================

    def generate_monthly_statistics(self):

        return self.notification_repository.statistics()

    # =====================================================
    # WEEKLY REPORT
    # =====================================================

    def weekly_summary(self):

        return {

            "generated": datetime.utcnow(),

            "statistics": self.notification_repository.statistics()

        }