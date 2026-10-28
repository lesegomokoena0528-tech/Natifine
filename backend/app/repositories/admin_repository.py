from datetime import datetime

from sqlalchemy import func

from app.config.database import db

from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.traffic_fine import TrafficFine
from app.models.payment import Payment
from app.models.dispute import Dispute
from app.models.notification import Notification


class AdminRepository:

    # =====================================================
    # USER MANAGEMENT
    # =====================================================

    def get_all_users(self):

        return User.query.order_by(
            User.first_name
        ).all()

    def get_user_by_id(self, user_id):

        return User.query.get(user_id)

    def search_users(self, keyword):

        keyword = f"%{keyword}%"

        return User.query.filter(

            (User.first_name.ilike(keyword)) |

            (User.last_name.ilike(keyword)) |

            (User.email.ilike(keyword)) |

            (User.id_number.ilike(keyword))

        ).all()

    def get_users_by_role(self, role):

        return User.query.filter_by(
            role=role
        ).all()

    def get_active_users(self):

        return User.query.filter_by(
            status="ACTIVE"
        ).all()

    def save_user(self, user):

        db.session.add(user)
        db.session.commit()

        return user

    def delete_user(self, user):

        Notification.query.filter_by(
            user_id=user.user_id
        ).delete(synchronize_session=False)

        db.session.delete(user)
        db.session.commit()

    def user_dependency_counts(self, user_id):

        return {
            "fines": TrafficFine.query.filter_by(
                officer_id=user_id
            ).count(),

            "payments": Payment.query.filter_by(
                user_id=user_id
            ).count(),

            "disputes": Dispute.query.filter(
                (Dispute.user_id == user_id) |
                (Dispute.reviewed_by == user_id)
            ).count()
        }

    # =====================================================
    # OFFICER MANAGEMENT
    # =====================================================

    def get_all_officers(self):

        return User.query.filter_by(
            role="OFFICER"
        ).all()

    def officer_count(self):

        return User.query.filter_by(
            role="OFFICER"
        ).count()

    # =====================================================
    # VEHICLES
    # =====================================================

    def total_vehicles(self):

        return Vehicle.query.count()

    def vehicles_with_unpaid_fines(self):

        return db.session.query(Vehicle).join(

            TrafficFine,

            Vehicle.vehicle_id == TrafficFine.vehicle_id

        ).filter(

            TrafficFine.status != "PAID"

        ).distinct().count()

    # =====================================================
    # TRAFFIC FINES
    # =====================================================

    def total_fines(self):

        return TrafficFine.query.count()

    def paid_fines(self):

        return TrafficFine.query.filter_by(
            status="PAID"
        ).count()

    def unpaid_fines(self):

        return TrafficFine.query.filter(

            TrafficFine.status.notin_(
                ["PAID", "CANCELLED"]
            )

        ).count()

    def overdue_fines(self):

        return TrafficFine.query.filter(

            TrafficFine.due_date < datetime.utcnow(),

            TrafficFine.status != "PAID"

        ).count()

    def disputed_fines(self):

        return TrafficFine.query.filter_by(
            status="DISPUTED"
        ).count()

    # =====================================================
    # PAYMENTS
    # =====================================================

    def total_payments(self):

        return Payment.query.count()

    def total_revenue(self):

        revenue = db.session.query(

            func.sum(Payment.amount)

        ).filter(

            Payment.status == "PAID"

        ).scalar()

        return revenue or 0

    def payments_today(self):

        today = datetime.utcnow().date()

        return Payment.query.filter(

            func.date(Payment.paid_at) == today

        ).count()

    def revenue_today(self):

        today = datetime.utcnow().date()

        revenue = db.session.query(

            func.sum(Payment.amount)

        ).filter(

            func.date(Payment.paid_at) == today

        ).scalar()

        return revenue or 0

    # =====================================================
    # DISPUTES
    # =====================================================

    def total_disputes(self):

        return Dispute.query.count()

    def pending_disputes(self):

        return Dispute.query.filter_by(
            status="PENDING"
        ).count()

    def approved_disputes(self):

        return Dispute.query.filter_by(
            status="APPROVED"
        ).count()

    def rejected_disputes(self):

        return Dispute.query.filter_by(
            status="REJECTED"
        ).count()

    # =====================================================
    # NOTIFICATIONS
    # =====================================================

    def total_notifications(self):

        return Notification.query.count()

    def notifications_by_channel(self, channel):

        return Notification.query.filter_by(
            channel=channel
        ).count()

    def failed_notifications(self):

        return Notification.query.filter_by(
            status="FAILED"
        ).count()

    # =====================================================
    # DASHBOARD
    # =====================================================

    def dashboard_statistics(self):

        return {

            "users": User.query.count(),

            "officers": self.officer_count(),

            "vehicles": self.total_vehicles(),

            "fines": self.total_fines(),

            "paid_fines": self.paid_fines(),

            "unpaid_fines": self.unpaid_fines(),

            "overdue_fines": self.overdue_fines(),

            "revenue": self.total_revenue(),

            "payments": self.total_payments(),

            "disputes": self.total_disputes(),

            "notifications": self.total_notifications()

        }