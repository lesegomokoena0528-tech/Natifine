from flask import request

from marshmallow import ValidationError
from flask_jwt_extended import get_jwt_identity

from app.services.payment_service import PaymentService

from app.repositories.user_repository import UserRepository

from app.schemas.payment_schema import (
    PaymentCreateSchema,
    PaymentVerificationSchema,
    RefundRequestSchema
)

from app.exceptions.payment_exceptions import *

from app.utils.response import ApiResponse


service = PaymentService()

user_repository = UserRepository()


class PaymentController:

    # ==========================================================
    # CREATE PAYMENT
    # ==========================================================

    @staticmethod
    def create_payment():

        try:

            data = PaymentCreateSchema().load(
                request.get_json()
            )

            payment = service.create_payment(

                get_jwt_identity(),

                data

            )

            return ApiResponse.success(

                "Payment initiated successfully.",

                payment,

                201

            )

        except ValidationError as ex:

            return ApiResponse.error(

                ex.messages,

                400

            )

        except PaymentException as ex:

            return ApiResponse.error(

                str(ex),

                400

            )

        except Exception:

            return ApiResponse.error(

                "Internal server error.",

                500

            )

    # ==========================================================
    # VERIFY PAYMENT
    # ==========================================================

    @staticmethod
    def verify_payment():

        try:

            data = PaymentVerificationSchema().load(

                request.get_json()

            )

            payment = service.verify_payment(

                data["payment_reference"]

            )

            return ApiResponse.success(

                "Payment verified successfully.",

                payment

            )

        except ValidationError as ex:

            return ApiResponse.error(

                ex.messages,

                400

            )

        except PaymentException as ex:

            return ApiResponse.error(

                str(ex),

                400

            )

    # ==========================================================
    # PAYMENT DETAILS
    # ==========================================================

    @staticmethod
    def payment(payment_id):

        try:

            payment = service.payment(
                payment_id
            )

            return ApiResponse.success(

                "Payment retrieved successfully.",

                payment

            )

        except PaymentException as ex:

            return ApiResponse.error(

                str(ex),

                404

            )

    # ==========================================================
    # PAYMENT HISTORY
    # ==========================================================

    @staticmethod
    def history():

        try:

            history = service.history(

                get_jwt_identity()

            )

            return ApiResponse.success(

                "Payment history retrieved.",

                history

            )

        except PaymentException as ex:

            return ApiResponse.error(

                str(ex),

                400

            )

    # ==========================================================
    # DOWNLOAD RECEIPT
    # ==========================================================

    @staticmethod
    def receipt(payment_id):

        try:

            return service.receipt(
                payment_id
            )

        except PaymentException as ex:

            return ApiResponse.error(

                str(ex),

                404

            )

    # ==========================================================
    # REQUEST REFUND
    # ==========================================================

    @staticmethod
    def request_refund(payment_id):

        try:

            data = RefundRequestSchema().load(
                request.get_json()
            )

            refund = service.request_refund(

                payment_id,

                get_jwt_identity(),

                data["reason"]

            )

            return ApiResponse.success(

                "Refund request submitted.",

                refund,

                201

            )

        except ValidationError as ex:

            return ApiResponse.error(

                ex.messages,

                400

            )

        except RefundNotAllowedException as ex:

            return ApiResponse.error(

                str(ex),

                403

            )

        except RefundAlreadyRequestedException as ex:

            return ApiResponse.error(

                str(ex),

                409

            )

        except PaymentException as ex:

            return ApiResponse.error(

                str(ex),

                400

            )

    # ==========================================================
    # REJECT REFUND (ADMIN)
    # ==========================================================

    @staticmethod
    def reject_refund(refund_id):

        try:

            payload = request.get_json(silent=True) or {}

            note = payload.get("reason")

            if note is not None:

                note = str(note).strip()[:500] or None

            refund = service.reject_refund(

                refund_id,

                get_jwt_identity(),

                note

            )

            return ApiResponse.success(

                "Refund rejected.",

                refund

            )

        except PaymentException as ex:

            return ApiResponse.error(

                str(ex),

                400

            )

    # ==========================================================
    # APPROVE REFUND (ADMIN)
    # ==========================================================

    @staticmethod
    def approve_refund(refund_id):

        try:

            refund = service.approve_refund(

                refund_id,

                get_jwt_identity()

            )

            return ApiResponse.success(

                "Refund approved successfully.",

                refund

            )

        except PaymentException as ex:

            return ApiResponse.error(

                str(ex),

                400

            )

    # ==========================================================
    # LIST REFUNDS
    # ==========================================================

    @staticmethod
    def refunds():

        try:

            current = user_repository.find_by_id(
                get_jwt_identity()
            )

            is_admin = (
                current is not None and
                current.role.value == "ADMIN"
            )

            status = request.args.get("status") or None

            refunds = service.list_refunds(
                current.user_id,
                is_admin=is_admin,
                status=status
            )

            return ApiResponse.success(
                "Refunds retrieved.",
                refunds
            )

        except PaymentException as ex:

            return ApiResponse.error(
                str(ex),
                400
            )

    # ==========================================================
    # PAYMENT STATISTICS
    # ==========================================================

    @staticmethod
    def statistics():

        try:

            statistics = service.statistics()

            return ApiResponse.success(

                "Statistics retrieved.",

                statistics

            )

        except PaymentException as ex:

            return ApiResponse.error(

                str(ex),

                400

            )

    # ==========================================================
    # SEARCH PAYMENTS
    # ==========================================================

    @staticmethod
    def search():

        keyword = request.args.get(

            "keyword",

            ""

        )

        payments = service.search(
            keyword
        )

        return ApiResponse.success(

            "Search completed.",

            payments

        )

    # ==========================================================
    # TOTAL PAID
    # ==========================================================

    @staticmethod
    def total_paid():

        try:

            totals = service.total_paid(

                get_jwt_identity()

            )

            return ApiResponse.success(

                "Totals retrieved.",

                totals

            )

        except PaymentException as ex:

            return ApiResponse.error(

                str(ex),

                400

            )
            
