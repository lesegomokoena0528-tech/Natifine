from datetime import datetime, timedelta
from collections import defaultdict

from app.repositories.admin_repository import AdminRepository
from app.repositories.fine_repository import FineRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.dispute_repository import DisputeRepository


class ReportService:

    def __init__(self):

        self.admin_repository = AdminRepository()

        self.fine_repository = FineRepository()

        self.payment_repository = PaymentRepository()

        self.dispute_repository = DisputeRepository()

    # ==========================================================
    # DASHBOARD REPORT
    # ==========================================================

    def dashboard_report(self):

        return self.admin_repository.dashboard_statistics()

    # ==========================================================
    # REVENUE REPORT
    # ==========================================================

    def revenue_report(self):

        return {

            "total_revenue":

                self.admin_repository.total_revenue(),

            "payments_today":

                self.admin_repository.payments_today(),

            "revenue_today":

                self.admin_repository.revenue_today(),

            "total_payments":

                self.admin_repository.total_payments()

        }

    # ==========================================================
    # FINE REPORT
    # ==========================================================

    def fine_report(self):

        return {

            "total_fines":

                self.admin_repository.total_fines(),

            "paid":

                self.admin_repository.paid_fines(),

            "unpaid":

                self.admin_repository.unpaid_fines(),

            "overdue":

                self.admin_repository.overdue_fines(),

            "disputed":

                self.admin_repository.disputed_fines()

        }

    # ==========================================================
    # USER REPORT
    # ==========================================================

    def user_report(self):

        users = self.admin_repository.get_all_users()

        return {

            "total_users": len(users),

            "active":

                len(

                    [

                        u for u in users

                        if u.status == "ACTIVE"

                    ]

                ),

            "suspended":

                len(

                    [

                        u for u in users

                        if u.status == "SUSPENDED"

                    ]

                ),

            "administrators":

                len(

                    [

                        u for u in users

                        if u.role == "ADMIN"

                    ]

                ),

            "officers":

                len(

                    [

                        u for u in users

                        if u.role == "OFFICER"

                    ]

                ),

            "citizens":

                len(

                    [

                        u for u in users

                        if u.role == "CITIZEN"

                    ]

                )

        }

    # ==========================================================
    # VEHICLE REPORT
    # ==========================================================

    def vehicle_report(self):

        return {

            "registered":

                self.admin_repository.total_vehicles(),

            "with_unpaid_fines":

                self.admin_repository.vehicles_with_unpaid_fines()

        }

    # ==========================================================
    # DISPUTE REPORT
    # ==========================================================

    def dispute_report(self):

        return {

            "total":

                self.admin_repository.total_disputes(),

            "pending":

                self.admin_repository.pending_disputes(),

            "approved":

                self.admin_repository.approved_disputes(),

            "rejected":

                self.admin_repository.rejected_disputes()

        }

    # ==========================================================
    # NOTIFICATION REPORT
    # ==========================================================

    def notification_report(self):

        return {

            "total":

                self.admin_repository.total_notifications(),

            "email":

                self.admin_repository.notifications_by_channel(

                    "EMAIL"

                ),

            "sms":

                self.admin_repository.notifications_by_channel(

                    "SMS"

                ),

            "whatsapp":

                self.admin_repository.notifications_by_channel(

                    "WHATSAPP"

                ),

            "failed":

                self.admin_repository.failed_notifications()

        }

    # ==========================================================
    # SYSTEM REPORT
    # ==========================================================

    def full_system_report(self):

        return {

            "generated":

                datetime.utcnow().isoformat(),

            "dashboard":

                self.dashboard_report(),

            "revenue":

                self.revenue_report(),

            "users":

                self.user_report(),

            "vehicles":

                self.vehicle_report(),

            "fines":

                self.fine_report(),

            "disputes":

                self.dispute_report(),

            "notifications":

                self.notification_report()

        }

    # ==========================================================
    # OFFENCE ANALYTICS
    # ==========================================================

    def offence_statistics(self):

        fines = self.fine_repository.find_all()

        report = defaultdict(int)

        for fine in fines:

            report[fine.offence] += 1

        return dict(report)

    # ==========================================================
    # MONTHLY REVENUE
    # ==========================================================

    def monthly_revenue(self):

        payments = self.payment_repository.find_all()

        report = defaultdict(float)

        for payment in payments:

            month = payment.payment_date.strftime("%Y-%m")

            report[month] += float(payment.amount)

        return dict(report)

    # ==========================================================
    # OFFICER PERFORMANCE
    # ==========================================================

    def officer_performance(self):

        fines = self.fine_repository.find_all()

        performance = defaultdict(int)

        for fine in fines:

            performance[fine.officer_id] += 1

        return dict(performance)