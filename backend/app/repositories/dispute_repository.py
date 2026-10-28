from datetime import datetime

from sqlalchemy import desc, func, or_
from sqlalchemy.orm import joinedload

from app.config.database import db

from app.models.dispute import Dispute
from app.models.dispute_document import DisputeDocument
from app.models.traffic_fine import TrafficFine

from app.constants.dispute_status import DisputeStatus


class DisputeRepository:

    # ==========================================================
    # CREATE DISPUTE
    # ==========================================================

    def create(self, dispute):

        db.session.add(dispute)
        db.session.commit()

        return dispute

    # ==========================================================
    # UPDATE DISPUTE
    # ==========================================================

    def update(self, dispute):

        dispute.updated_at = datetime.utcnow()

        db.session.commit()

        return dispute

    # ==========================================================
    # DELETE DISPUTE
    # ==========================================================

    def delete(self, dispute):

        db.session.delete(dispute)

        db.session.commit()

    # ==========================================================
    # FIND BY ID
    # ==========================================================

    def find_by_id(self, dispute_id):

        return (

            Dispute.query

            .options(

                joinedload(Dispute.documents),

                joinedload(Dispute.fine),

                joinedload(Dispute.citizen),

                joinedload(Dispute.reviewer)

            )

            .filter(

                Dispute.dispute_id == dispute_id

            )

            .first()

        )

    # ==========================================================
    # FIND ACTIVE DISPUTE FOR FINE
    # ==========================================================

    def active_dispute_for_fine(
            self,
            fine_id
    ):

        return (

            Dispute.query

            .filter(

                Dispute.fine_id == fine_id,

                Dispute.status.in_([

                    DisputeStatus.NEW,

                    DisputeStatus.PENDING,

                    DisputeStatus.UNDER_REVIEW,

                    DisputeStatus.MORE_INFORMATION_REQUIRED

                ])

            )

            .first()

        )

    # ==========================================================
    # USER DISPUTES
    # ==========================================================

    def user_disputes(
            self,
            user_id
    ):

        return (

            Dispute.query

            .filter(

                Dispute.user_id == user_id

            )

            .order_by(

                desc(Dispute.created_at)

            )

            .all()

        )

    # ==========================================================
    # FIND BY FINE
    # ==========================================================

    def disputes_by_fine(
            self,
            fine_id
    ):

        return (

            Dispute.query

            .filter(

                Dispute.fine_id == fine_id

            )

            .order_by(

                desc(Dispute.created_at)

            )

            .all()

        )

    # ==========================================================
    # PENDING REVIEW
    # ==========================================================

    def pending_reviews(self):

        return (

            Dispute.query

            .filter(

                Dispute.status.in_([

                    DisputeStatus.NEW,

                    DisputeStatus.PENDING,

                    DisputeStatus.UNDER_REVIEW

                ])

            )

            .order_by(

                Dispute.submitted_at

            )

            .all()

        )

    # ==========================================================
    # APPROVED
    # ==========================================================

    def approved_disputes(self):

        return (

            Dispute.query

            .filter(

                Dispute.status ==
                DisputeStatus.APPROVED

            )

            .all()

        )

    # ==========================================================
    # REJECTED
    # ==========================================================

    def rejected_disputes(self):

        return (

            Dispute.query

            .filter(

                Dispute.status ==
                DisputeStatus.REJECTED

            )

            .all()

        )

    # ==========================================================
    # CREATE DOCUMENT
    # ==========================================================

    def create_document(
            self,
            document
    ):

        db.session.add(document)

        db.session.commit()

        return document

    # ==========================================================
    # FIND DOCUMENT
    # ==========================================================

    def document(
            self,
            document_id
    ):

        return DisputeDocument.query.filter_by(

            document_id=document_id

        ).first()

    # ==========================================================
    # DISPUTE DOCUMENTS
    # ==========================================================

    def dispute_documents(
            self,
            dispute_id
    ):

        return (

            DisputeDocument.query

            .filter(

                DisputeDocument.dispute_id ==
                dispute_id

            )

            .order_by(

                DisputeDocument.uploaded_at

            )

            .all()

        )

    # ==========================================================
    # DELETE DOCUMENT
    # ==========================================================

    def delete_document(
            self,
            document
    ):

        db.session.delete(document)

        db.session.commit()

    # ==========================================================
    # SEARCH
    # ==========================================================

    def search(
            self,
            keyword
    ):

        keyword = f"%{keyword}%"

        return (

            Dispute.query

            .join(TrafficFine)

            .filter(

                or_(

                    Dispute.description.ilike(keyword),

                    Dispute.review_notes.ilike(keyword),

                    TrafficFine.fine_number.ilike(keyword)

                )

            )

            .order_by(

                desc(Dispute.created_at)

            )

            .all()

        )

    # ==========================================================
    # PAGINATION
    # ==========================================================

    def paginate(
            self,
            page,
            per_page
    ):

        return (

            Dispute.query

            .order_by(

                desc(Dispute.created_at)

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

    def statistics(self):

        return {

            "total":

                Dispute.query.count(),

            "pending":

                Dispute.query.filter(

                    Dispute.status.in_([

                        DisputeStatus.NEW,

                        DisputeStatus.PENDING,

                        DisputeStatus.UNDER_REVIEW

                    ])

                ).count(),

            "approved":

                Dispute.query.filter_by(

                    status=DisputeStatus.APPROVED

                ).count(),

            "rejected":

                Dispute.query.filter_by(

                    status=DisputeStatus.REJECTED

                ).count(),

            "closed":

                Dispute.query.filter_by(

                    status=DisputeStatus.CLOSED

                ).count()

        }

    # ==========================================================
    # MONTHLY STATISTICS
    # ==========================================================

    def monthly_statistics(self):

        return (

            db.session.query(

                func.year(Dispute.created_at),

                func.month(Dispute.created_at),

                func.count(Dispute.dispute_id)

            )

            .group_by(

                func.year(Dispute.created_at),

                func.month(Dispute.created_at)

            )

            .all()

        )

    # ==========================================================
    # EXISTS
    # ==========================================================

    def exists(
            self,
            dispute_id
    ):

        return (

            db.session.query(

                Dispute.dispute_id

            )

            .filter(

                Dispute.dispute_id == dispute_id

            )

            .first()

            is not None

        )

    # ==========================================================
    # COUNT USER DISPUTES
    # ==========================================================

    def user_total(
            self,
            user_id
    ):

        return (

            Dispute.query

            .filter(

                Dispute.user_id == user_id

            )

            .count()

        )