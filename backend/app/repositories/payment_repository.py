from datetime import datetime
from sqlalchemy import desc, func

from app.config.database import db

from app.models.payment import Payment
from app.models.refund import Refund
from app.models.traffic_fine import TrafficFine
from app.models.user import User

from app.constants.payment_status import PaymentStatus
from app.constants.refund_status import RefundStatus


class PaymentRepository:

    # ==========================================================
    # CREATE PAYMENT
    # ==========================================================

    def create(self, payment):

        db.session.add(payment)
        db.session.commit()

        return payment

    # ==========================================================
    # UPDATE PAYMENT
    # ==========================================================

    def update(self, payment):

        payment.updated_at = datetime.utcnow()

        db.session.commit()

        return payment

    # ==========================================================
    # DELETE PAYMENT
    # ==========================================================

    def delete(self, payment):

        db.session.delete(payment)

        db.session.commit()

    # ==========================================================
    # FIND PAYMENT BY ID
    # ==========================================================

    def find_by_id(self, payment_id):

        return Payment.query.filter_by(
            payment_id=payment_id
        ).first()

    # ==========================================================
    # FIND BY PAYMENT REFERENCE
    # ==========================================================

    def find_by_reference(self, payment_reference):

        return Payment.query.filter_by(
            payment_reference=payment_reference
        ).first()

    # ==========================================================
    # FIND BY GATEWAY REFERENCE
    # ==========================================================

    def find_by_gateway_reference(
            self,
            gateway_reference
    ):

        return Payment.query.filter_by(
            gateway_reference=gateway_reference
        ).first()

    # ==========================================================
    # FIND TRANSACTION ID
    # ==========================================================

    def find_by_transaction_id(
            self,
            transaction_id
    ):

        return Payment.query.filter_by(
            transaction_id=transaction_id
        ).first()

    # ==========================================================
    # USER PAYMENT HISTORY
    # ==========================================================

    def payment_history(
            self,
            user_id
    ):

        return (

            Payment.query

            .filter(
                Payment.user_id == user_id
            )

            .order_by(
                desc(Payment.created_at)
            )

            .all()

        )

    # ==========================================================
    # FINE PAYMENTS
    # ==========================================================

    def fine_payments(
            self,
            fine_id
    ):

        return (

            Payment.query

            .filter(
                Payment.fine_id == fine_id
            )

            .order_by(
                desc(Payment.created_at)
            )

            .all()

        )

    # ==========================================================
    # SUCCESSFUL PAYMENTS
    # ==========================================================

    def successful_payments(self):

        return (

            Payment.query

            .filter(
                Payment.status == PaymentStatus.PAID
            )

            .order_by(
                desc(Payment.paid_at)
            )

            .all()

        )

    # ==========================================================
    # PENDING PAYMENTS
    # ==========================================================

    def pending_payments(self):

        return (

            Payment.query

            .filter(
                Payment.status == PaymentStatus.PENDING
            )

            .order_by(
                Payment.created_at
            )

            .all()

        )

    # ==========================================================
    # FAILED PAYMENTS
    # ==========================================================

    def failed_payments(self):

        return (

            Payment.query

            .filter(
                Payment.status == PaymentStatus.FAILED
            )

            .all()

        )

    # ==========================================================
    # CREATE REFUND
    # ==========================================================

    def create_refund(
            self,
            refund
    ):

        db.session.add(refund)

        db.session.commit()

        return refund

    # ==========================================================
    # UPDATE REFUND
    # ==========================================================

    def update_refund(
            self,
            refund
    ):

        db.session.commit()

        return refund

    # ==========================================================
    # FIND REFUND
    # ==========================================================

    def refund_by_id(
            self,
            refund_id
    ):

        return Refund.query.filter_by(

            refund_id=refund_id

        ).first()

    # ==========================================================
    # PAYMENT REFUNDS
    # ==========================================================

    def payment_refunds(
            self,
            payment_id
    ):

        return (

            Refund.query

            .filter(
                Refund.payment_id == payment_id
            )

            .order_by(
                desc(Refund.created_at)
            )

            .all()

        )

    # ==========================================================
    # OPEN REFUND FOR PAYMENT
    # ==========================================================

    def open_refund_for_payment(
            self,
            payment_id
    ):

        return (
            Refund.query
            .filter(
                Refund.payment_id == payment_id,
                Refund.status.in_([
                    RefundStatus.PENDING,
                    RefundStatus.APPROVED,
                    RefundStatus.PROCESSING,
                    RefundStatus.COMPLETED
                ])
            )
            .first()
        )

    # ==========================================================
    # PENDING REFUNDS
    # ==========================================================

    def pending_refunds(self):

        return (

            Refund.query

            .filter(
                Refund.status == RefundStatus.PENDING
            )

            .all()

        )

    # ==========================================================
    # ALL REFUNDS (ADMIN)
    # ==========================================================

    def refunds(
            self,
            status=None
    ):

        query = Refund.query

        if status:

            query = query.filter(
                Refund.status == RefundStatus[status.upper()]
            )

        return (
            query
            .order_by(desc(Refund.created_at))
            .all()
        )

    # ==========================================================
    # USER REFUNDS
    # ==========================================================

    def refunds_for_user(
            self,
            user_id,
            status=None
    ):

        query = (
            Refund.query
            .join(
                Payment,
                Refund.payment_id == Payment.payment_id
            )
            .filter(
                Payment.user_id == user_id
            )
        )

        if status:

            query = query.filter(
                Refund.status == RefundStatus[status.upper()]
            )

        return (
            query
            .order_by(desc(Refund.created_at))
            .all()
        )

    # ==========================================================
    # PAYMENT EXISTS
    # ==========================================================

    def exists(
            self,
            payment_reference
    ):

        return (

            db.session.query(

                Payment.payment_id

            )

            .filter(

                Payment.payment_reference ==
                payment_reference

            )

            .first()

            is not None

        )

    # ==========================================================
    # USER TOTAL PAYMENTS
    # ==========================================================

    def total_paid(
            self,
            user_id
    ):

        amount = (

            db.session.query(

                func.sum(Payment.amount)

            )

            .filter(

                Payment.user_id == user_id,

                Payment.status == PaymentStatus.PAID

            )

            .scalar()

        )

        return float(amount or 0)

    # ==========================================================
    # TOTAL REFUNDED
    # ==========================================================

    def total_refunded(
            self,
            user_id
    ):

        amount = (

            db.session.query(

                func.sum(Refund.amount)

            )

            .join(
                Payment,
                Refund.payment_id ==
                Payment.payment_id
            )

            .filter(

                Payment.user_id == user_id,

                Refund.status ==
                RefundStatus.COMPLETED

            )

            .scalar()

        )

        return float(amount or 0)

    # ==========================================================
    # PAGINATED HISTORY
    # ==========================================================

    def paginate_history(
            self,
            user_id,
            page,
            per_page
    ):

        return (

            Payment.query

            .filter(
                Payment.user_id == user_id
            )

            .order_by(
                desc(Payment.created_at)
            )

            .paginate(

                page=page,

                per_page=per_page,

                error_out=False

            )

        )

    # ==========================================================
    # SEARCH PAYMENT
    # ==========================================================

    def search(
            self,
            keyword
    ):

        keyword = f"%{keyword}%"

        return (

            Payment.query

            .filter(

                Payment.payment_reference.ilike(keyword)

                |

                Payment.gateway_reference.ilike(keyword)

                |

                Payment.transaction_id.ilike(keyword)

            )

            .order_by(
                desc(Payment.created_at)
            )

            .all()

        )

    # ==========================================================
    # DAILY REVENUE
    # ==========================================================

    def daily_revenue(self):

        return (

            db.session.query(

                func.date(Payment.paid_at),

                func.sum(Payment.amount)

            )

            .filter(

                Payment.status ==
                PaymentStatus.PAID

            )

            .group_by(

                func.date(Payment.paid_at)

            )

            .all()

        )

    # ==========================================================
    # PAYMENT STATISTICS
    # ==========================================================

    def statistics(self):

        return {

            "payments":

                Payment.query.count(),

            "successful":

                Payment.query.filter_by(
                    status=PaymentStatus.PAID
                ).count(),

            "pending":

                Payment.query.filter_by(
                    status=PaymentStatus.PENDING
                ).count(),

            "failed":

                Payment.query.filter_by(
                    status=PaymentStatus.FAILED
                ).count(),

            "refunds":

                Refund.query.count()

        }