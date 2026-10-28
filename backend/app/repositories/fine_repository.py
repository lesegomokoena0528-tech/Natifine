from datetime import datetime
from sqlalchemy import or_, func

from app.models.traffic_fine import (
    TrafficFine,
    FineStatus
)

from app.models.vehicle import Vehicle

from app.repositories.base_repository import BaseRepository


class FineRepository(BaseRepository):

    def __init__(self):
        super().__init__(TrafficFine)

    # ==========================================================
    # FINDERS
    # ==========================================================

    def find_by_id(self, fine_id):
        return TrafficFine.query.get(fine_id)

    def find_by_fine_number(self, fine_number):
        return TrafficFine.query.filter(
            TrafficFine.fine_number == fine_number
        ).first()

    def find_by_vehicle(self, vehicle_id):
        return TrafficFine.query.filter_by(
            vehicle_id=vehicle_id
        ).all()

    def find_by_officer(self, officer_id):
        return TrafficFine.query.filter_by(
            officer_id=officer_id
        ).all()

    def find_by_status(self, status):
        return TrafficFine.query.filter(
            TrafficFine.status == status
        ).all()

    def find_by_owner(self, owner_id):
        return (
            TrafficFine.query
            .join(Vehicle)
            .filter(Vehicle.owner_id == owner_id)
            .all()
        )

    def find_open_fines(self):
        return TrafficFine.query.filter(
            TrafficFine.status.in_([
                FineStatus.ISSUED,
                FineStatus.DISPUTED,
                FineStatus.UNDER_REVIEW
            ])
        ).all()

    def find_paid_fines(self):
        return TrafficFine.query.filter(
            TrafficFine.status == FineStatus.PAID
        ).all()

    def find_overdue_fines(self):
        return TrafficFine.query.filter(
            TrafficFine.status == FineStatus.ISSUED,
            TrafficFine.due_date < datetime.utcnow()
        ).all()

    # ==========================================================
    # SEARCH
    # ==========================================================

    def search(self, keyword):

        keyword = f"%{keyword}%"

        return (
            TrafficFine.query
            .join(Vehicle)
            .filter(
                or_(
                    TrafficFine.fine_number.ilike(keyword),
                    TrafficFine.offence.ilike(keyword),
                    TrafficFine.location.ilike(keyword),
                    Vehicle.registration_number.ilike(keyword)
                )
            )
            .all()
        )

    # ==========================================================
    # VALIDATION
    # ==========================================================

    def exists_fine_number(self, fine_number):
        return self.find_by_fine_number(fine_number) is not None

    # ==========================================================
    # FILTERING
    # ==========================================================

    def filter(
        self,
        status=None,
        officer_id=None,
        vehicle_id=None,
        offence_code=None,
        start_date=None,
        end_date=None
    ):

        query = TrafficFine.query

        if status:
            query = query.filter(
                TrafficFine.status == status
            )

        if officer_id:
            query = query.filter(
                TrafficFine.officer_id == officer_id
            )

        if vehicle_id:
            query = query.filter(
                TrafficFine.vehicle_id == vehicle_id
            )

        if offence_code:
            query = query.filter(
                TrafficFine.offence_code == offence_code
            )

        if start_date:
            query = query.filter(
                TrafficFine.issue_date >= start_date
            )

        if end_date:
            query = query.filter(
                TrafficFine.issue_date <= end_date
            )

        return query.order_by(
            TrafficFine.issue_date.desc()
        ).all()

    # ==========================================================
    # PAGINATION
    # ==========================================================

    def paginate(
        self,
        page=1,
        per_page=20
    ):

        return (
            TrafficFine.query
            .order_by(TrafficFine.issue_date.desc())
            .paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
        )

    # ==========================================================
    # REPORTS
    # ==========================================================

    def count_all(self):
        return TrafficFine.query.count()

    def count_paid(self):
        return TrafficFine.query.filter(
            TrafficFine.status == FineStatus.PAID
        ).count()

    def count_unpaid(self):
        return TrafficFine.query.filter(
            TrafficFine.status != FineStatus.PAID
        ).count()

    def total_revenue(self):

        total = (
            TrafficFine.query
            .with_entities(
                func.sum(TrafficFine.amount)
            )
            .filter(
                TrafficFine.status == FineStatus.PAID
            )
            .scalar()
        )

        return total or 0

    # ==========================================================
    # DASHBOARD
    # ==========================================================

    def monthly_statistics(self):

        return (
            TrafficFine.query
            .with_entities(
                func.year(TrafficFine.issue_date),
                func.month(TrafficFine.issue_date),
                func.count(TrafficFine.fine_id)
            )
            .group_by(
                func.year(TrafficFine.issue_date),
                func.month(TrafficFine.issue_date)
            )
            .all()
        )

    def offence_statistics(self):

        return (
            TrafficFine.query
            .with_entities(
                TrafficFine.offence,
                func.count(TrafficFine.fine_id)
            )
            .group_by(
                TrafficFine.offence
            )
            .all()
        )

    def officer_statistics(self):

        return (
            TrafficFine.query
            .with_entities(
                TrafficFine.officer_id,
                func.count(TrafficFine.fine_id)
            )
            .group_by(
                TrafficFine.officer_id
            )
            .all()
        )

    # ==========================================================
    # RECENT
    # ==========================================================

    def recent(self, limit=10):

        return (
            TrafficFine.query
            .order_by(
                TrafficFine.created_at.desc()
            )
            .limit(limit)
            .all()
        )