import uuid
from decimal import Decimal
from datetime import datetime

from app.models.payment import Payment
from app.models.refund import Refund

from app.repositories.payment_repository import PaymentRepository
from app.repositories.fine_repository import FineRepository
from app.repositories.user_repository import UserRepository

from app.services.payment_gateway_service import PaymentGatewayService
from app.services.receipt_service import ReceiptService
from app.services.notification_service import NotificationService

from app.constants.payment_status import PaymentStatus
from app.constants.refund_status import RefundStatus
from app.constants.fine_status import FineStatus

from app.exceptions.payment_exceptions import *


class PaymentService:

    def __init__(self):

        self.payment_repository = PaymentRepository()

        self.fine_repository = FineRepository()

        self.user_repository = UserRepository()

        self.gateway = PaymentGatewayService()

        self.receipt_service = ReceiptService()

        self.notification_service = NotificationService()
        
    # ==========================================================
    # CREATE PAYMENT
    # ==========================================================

    def create_payment(self, user_id, data):

        fine = self.fine_repository.find_by_id(
            data["fine_id"]
        )

        if not fine:
            raise InvalidPaymentException(
                "Fine does not exist."
            )

        if fine.status == FineStatus.PAID:
            raise PaymentAlreadyCompletedException(
                "Fine has already been paid."
            )

        payment = Payment()

        payment.user_id = user_id
        payment.fine_id = fine.fine_id
        # Authoritative amount from backend database - never trust client amount
        payment.amount = Decimal(str(fine.amount))
        payment.gateway = data.get("gateway", "INTERNAL")
        payment.payment_method = data.get("payment_method", "CARD")

        payment.currency = "ZAR"

        payment.payment_reference = (
            f"PAY-{uuid.uuid4().hex[:12].upper()}"
        )

        payment.status = PaymentStatus.PENDING

        self.payment_repository.create(payment)

        gateway_response = self.gateway.create_payment(
            payment
        )

        return {

            "payment_reference": payment.payment_reference,

            "payment_url": gateway_response["payment_url"],

            "gateway_reference": gateway_response["gateway_reference"]

        }
    
    # ==========================================================
    # VERIFY PAYMENT
    # ==========================================================

    def verify_payment(self, payment_reference):

        payment = self.payment_repository.find_by_reference(
            payment_reference
        )

        if not payment:
            raise PaymentNotFoundException()

        if payment.status == PaymentStatus.PAID:

            return payment.to_dict()

        result = self.gateway.verify_payment(
            payment
        )

        if not result["success"]:

            payment.status = PaymentStatus.FAILED

            self.payment_repository.update(payment)

            raise PaymentGatewayException(
                "Payment verification failed."
            )

        payment.status = PaymentStatus.PAID

        payment.transaction_id = result["transaction_id"]

        payment.gateway_reference = result["gateway_reference"]

        payment.paid_at = datetime.utcnow()

        self.payment_repository.update(payment)

        fine = self.fine_repository.find_by_id(
            payment.fine_id
        )

        fine.status = FineStatus.PAID
        fine.paid_date = datetime.utcnow()

        self.fine_repository.update(fine)

        self.receipt_service.generate(payment)

        self.notification_service.payment_success(
            payment.user_id,
            payment
        )

        return payment.to_dict()  
    
    # ==========================================================
    # PAYMENT DETAILS
    # ==========================================================

    def payment(self, payment_id):

        payment = self.payment_repository.find_by_id(
            payment_id
        )

        if not payment:

            raise PaymentNotFoundException()

        return payment.to_dict()
    
    # ==========================================================
    # HISTORY
    # ==========================================================

    def history(self, user_id):

        payments = self.payment_repository.payment_history(
            user_id
        )

        return [

            payment.to_dict()

            for payment in payments

        ]
        
    # ==========================================================
    # RECEIPT
    # ==========================================================

    def receipt(self, payment_id):

        payment = self.payment_repository.find_by_id(
            payment_id
        )

        if not payment:
            raise PaymentNotFoundException()

        return self.receipt_service.download(
            payment
        )
        
    # ==========================================================
    # REFUND
    # ==========================================================

    def request_refund(self, payment_id, user_id, reason):

        payment = self.payment_repository.find_by_id(
            payment_id
        )

        if not payment:
            raise PaymentNotFoundException()

        if payment.user_id != user_id:

            raise RefundNotAllowedException(
                "You can only request a refund for your own payment."
            )

        if payment.status != PaymentStatus.PAID:

            raise PaymentNotRefundableException(
                "Only paid payments can be refunded."
            )

        if self.payment_repository.open_refund_for_payment(
            payment_id
        ):

            raise RefundAlreadyRequestedException(
                "An open refund request already exists for this payment."
            )

        refund = Refund()

        refund.payment_id = payment.payment_id

        refund.amount = payment.amount

        refund.reason = reason

        refund.status = RefundStatus.PENDING

        refund.refund_reference = (
            f"REF-{uuid.uuid4().hex[:10].upper()}"
        )

        self.payment_repository.create_refund(
            refund
        )

        return refund.to_dict()
    
    # ==========================================================
    # APPROVE REFUND
    # ==========================================================

    def approve_refund(self, refund_id, admin_id):

        refund = self.payment_repository.refund_by_id(
            refund_id
        )

        if not refund:

            raise RefundException()

        if refund.status != RefundStatus.PENDING:

            raise RefundAlreadyProcessedException()

        payment = self.payment_repository.find_by_id(
            refund.payment_id
        )

        self.gateway.refund(payment)

        refund.status = RefundStatus.COMPLETED

        refund.approved_by = admin_id

        refund.approved_date = datetime.utcnow()

        self.payment_repository.update_refund(
            refund
        )

        payment.status = PaymentStatus.REFUNDED

        self.payment_repository.update(payment)

        fine = self.fine_repository.find_by_id(payment.fine_id)
        if fine:
            fine.status = FineStatus.ISSUED
            fine.paid_date = None
            self.fine_repository.update(fine)

        return refund.to_dict()

    # ==========================================================
    # REJECT REFUND
    # ==========================================================

    def reject_refund(self, refund_id, admin_id, note=None):

        refund = self.payment_repository.refund_by_id(
            refund_id
        )

        if not refund:

            raise RefundException(
                "Refund request not found."
            )

        if refund.status != RefundStatus.PENDING:

            raise RefundAlreadyProcessedException(
                "Refund request has already been processed."
            )

        refund.status = RefundStatus.REJECTED

        refund.approved_by = admin_id

        refund.approved_date = datetime.utcnow()

        if note:

            refund.admin_note = note

        self.payment_repository.update_refund(
            refund
        )

        return refund.to_dict()

    # ==========================================================
    # LIST REFUNDS
    # ==========================================================

    def list_refunds(self, user_id, is_admin=False, status=None):

        if is_admin:

            refunds = self.payment_repository.refunds(status)

        else:

            refunds = self.payment_repository.refunds_for_user(
                user_id,
                status
            )

        return [self._refund_view(refund) for refund in refunds]

    @staticmethod
    def _refund_view(refund):

        data = refund.to_dict()

        payment = refund.payment

        if payment:

            data["payment_reference"] = payment.payment_reference

            data["fine_number"] = (
                payment.fine.fine_number if payment.fine else None
            )

            data["user_id"] = payment.user_id

            if payment.user:

                data["user_name"] = payment.user.full_name

                data["user_email"] = payment.user.email

        return data

    # ==========================================================
    # STATISTICS
    # ==========================================================

    def statistics(self):

        return self.payment_repository.statistics()
    
    
    # ==========================================================
    # SEARCH
    # ==========================================================

    def search(self, keyword):

        return [

            payment.to_dict()

            for payment in

            self.payment_repository.search(
                keyword
            )

        ]
        
    # ==========================================================
    # TOTAL PAID
    # ==========================================================

    def total_paid(self, user_id):

        return {

            "total_paid":

            self.payment_repository.total_paid(
                user_id
            ),

            "total_refunded":

            self.payment_repository.total_refunded(
                user_id
            )

        }
        
    
    