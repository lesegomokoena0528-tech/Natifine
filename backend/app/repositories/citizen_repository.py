from sqlalchemy import func, or_

from app.models.vehicle import Vehicle
from app.models.traffic_fine import TrafficFine, FineStatus
from app.models.payment import Payment
from app.models.dispute import Dispute
from app.models.notification import Notification


class CitizenRepository:

    # ==========================================================
    # DASHBOARD SUMMARY
    # ==========================================================

    def dashboard_summary(self, owner_id):

        total_fines = (
            TrafficFine.query
            .join(Vehicle)
            .filter(Vehicle.owner_id == owner_id)
            .count()
        )

        unpaid_fines = (
            TrafficFine.query
            .join(Vehicle)
            .filter(
                Vehicle.owner_id == owner_id,
                TrafficFine.status.in_([
                    FineStatus.ISSUED,
                    FineStatus.DISPUTED,
                    FineStatus.UNDER_REVIEW
                ])
            )
            .count()
        )

        paid_fines = (
            TrafficFine.query
            .join(Vehicle)
            .filter(
                Vehicle.owner_id == owner_id,
                TrafficFine.status == FineStatus.PAID
            )
            .count()
        )

        disputed_fines = (
            TrafficFine.query
            .join(Vehicle)
            .filter(
                Vehicle.owner_id == owner_id,
                TrafficFine.status == FineStatus.DISPUTED
            )
            .count()
        )

        outstanding_amount = (
            TrafficFine.query
            .with_entities(func.sum(TrafficFine.amount))
            .join(Vehicle)
            .filter(
                Vehicle.owner_id == owner_id,
                TrafficFine.status != FineStatus.PAID
            )
            .scalar()
        )

        paid_amount = (
            TrafficFine.query
            .with_entities(func.sum(TrafficFine.amount))
            .join(Vehicle)
            .filter(
                Vehicle.owner_id == owner_id,
                TrafficFine.status == FineStatus.PAID
            )
            .scalar()
        )

        return {
            "total_fines": total_fines,
            "unpaid_fines": unpaid_fines,
            "paid_fines": paid_fines,
            "disputed_fines": disputed_fines,
            "outstanding_amount": float(outstanding_amount or 0),
            "paid_amount": float(paid_amount or 0)
        }

    # ==========================================================
    # VEHICLES
    # ==========================================================

    def get_vehicles(self, owner_id):

        return (
            Vehicle.query
            .filter(
                Vehicle.owner_id == owner_id
            )
            .order_by(
                Vehicle.registration_number.asc()
            )
            .all()
        )

    # ==========================================================
    # FINES
    # ==========================================================

    def get_fines(self, owner_id):

        return (
            TrafficFine.query
            .join(Vehicle)
            .filter(
                Vehicle.owner_id == owner_id
            )
            .order_by(
                TrafficFine.issue_date.desc()
            )
            .all()
        )

    def get_fine(self, owner_id, fine_id):

        return (
            TrafficFine.query
            .join(Vehicle)
            .filter(
                Vehicle.owner_id == owner_id,
                TrafficFine.fine_id == fine_id
            )
            .first()
        )

    # ==========================================================
    # PAYMENTS
    # ==========================================================

    def get_payments(self, owner_id):

        return (
            Payment.query
            .join(TrafficFine)
            .join(Vehicle)
            .filter(
                Vehicle.owner_id == owner_id
            )
            .order_by(
                Payment.payment_date.desc()
            )
            .all()
        )

    # ==========================================================
    # DISPUTES
    # ==========================================================

    def get_disputes(self, owner_id):

        return (
            Dispute.query
            .join(TrafficFine)
            .join(Vehicle)
            .filter(
                Vehicle.owner_id == owner_id
            )
            .order_by(
                Dispute.dispute_id.desc()
            )
            .all()
        )

    # ==========================================================
    # NOTIFICATIONS
    # ==========================================================

    def get_notifications(self, user_id):

        return (
            Notification.query
            .filter(
                Notification.user_id == user_id
            )
            .order_by(
                Notification.sent_date.desc()
            )
            .all()
        )

    # ==========================================================
    # RECENT FINES
    # ==========================================================

    def recent_fines(self, owner_id, limit=5):

        return (
            TrafficFine.query
            .join(Vehicle)
            .filter(
                Vehicle.owner_id == owner_id
            )
            .order_by(
                TrafficFine.issue_date.desc()
            )
            .limit(limit)
            .all()
        )

    # ==========================================================
    # RECENT NOTIFICATIONS
    # ==========================================================

    def recent_notifications(self, user_id, limit=5):

        return (
            Notification.query
            .filter(
                Notification.user_id == user_id
            )
            .order_by(
                Notification.sent_date.desc()
            )
            .limit(limit)
            .all()
        )

    # ==========================================================
    # SEARCH FINES
    # ==========================================================

    def search_fines(self, owner_id, keyword):

        keyword = f"%{keyword}%"

        return (
            TrafficFine.query
            .join(Vehicle)
            .filter(
                Vehicle.owner_id == owner_id
            )
            .filter(
                or_(
                    TrafficFine.fine_number.ilike(keyword),
                    TrafficFine.offence.ilike(keyword),
                    TrafficFine.location.ilike(keyword),
                    Vehicle.registration_number.ilike(keyword)
                )
            )
            .order_by(
                TrafficFine.issue_date.desc()
            )
            .all()
        )

    # ==========================================================
    # FILTER FINES
    # ==========================================================

    def filter_fines(
        self,
        owner_id,
        status=None,
        start_date=None,
        end_date=None
    ):

        query = (
            TrafficFine.query
            .join(Vehicle)
            .filter(
                Vehicle.owner_id == owner_id
            )
        )

        if status:
            query = query.filter(
                TrafficFine.status == status
            )

        if start_date:
            query = query.filter(
                TrafficFine.issue_date >= start_date
            )

        if end_date:
            query = query.filter(
                TrafficFine.issue_date <= end_date
            )

        return (
            query
            .order_by(
                TrafficFine.issue_date.desc()
            )
            .all()
        )

    # ==========================================================
    # PAGINATION
    # ==========================================================

    def paginate_fines(
        self,
        owner_id,
        page=1,
        per_page=10
    ):

        return (
            TrafficFine.query
            .join(Vehicle)
            .filter(
                Vehicle.owner_id == owner_id
            )
            .order_by(
                TrafficFine.issue_date.desc()
            )
            .paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
        )

    # ==========================================================
    # STATISTICS
    # ==========================================================

    def statistics(self, owner_id):

        return {

            "vehicles":

                Vehicle.query.filter_by(
                    owner_id=owner_id
                ).count(),

            "payments":

                Payment.query
                .join(TrafficFine)
                .join(Vehicle)
                .filter(
                    Vehicle.owner_id == owner_id
                )
                .count(),

            "disputes":

                Dispute.query
                .join(TrafficFine)
                .join(Vehicle)
                .filter(
                    Vehicle.owner_id == owner_id
                )
                .count(),

            "notifications":

                Notification.query.filter_by(
                    user_id=owner_id
                ).count()

        }