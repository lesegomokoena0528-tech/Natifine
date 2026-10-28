from flask import request

from marshmallow import ValidationError
from flask_jwt_extended import get_jwt_identity

from app.services.dispute_service import DisputeService

from app.schemas.dispute_schema import (
    CreateDisputeSchema,
    ReviewDisputeSchema,
    RequestMoreInformationSchema
)

from app.exceptions.dispute_exceptions import *

from app.utils.response import ApiResponse


service = DisputeService()


class DisputeController:

    # ==========================================================
    # SUBMIT DISPUTE
    # ==========================================================

    @staticmethod
    def submit():

        try:

            data = CreateDisputeSchema().load(
                request.get_json()
            )

            dispute = service.submit_dispute(

                get_jwt_identity(),

                data

            )

            return ApiResponse.success(

                "Dispute submitted successfully.",

                dispute,

                201

            )

        except ValidationError as ex:

            return ApiResponse.error(

                ex.messages,

                400

            )

        except DisputeException as ex:

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
    # UPLOAD DOCUMENT
    # ==========================================================

    @staticmethod
    def upload_document(dispute_id):

        try:

            if "file" not in request.files:

                return ApiResponse.error(

                    "No file uploaded.",

                    400

                )

            document = service.upload_document(

                dispute_id,

                request.files["file"]

            )

            return ApiResponse.success(

                "Document uploaded successfully.",

                document,

                201

            )

        except DisputeException as ex:

            return ApiResponse.error(

                str(ex),

                400

            )

        except Exception:

            return ApiResponse.error(

                "File upload failed.",

                500

            )

    # ==========================================================
    # MY DISPUTES
    # ==========================================================

    @staticmethod
    def my_disputes():

        try:

            disputes = service.user_disputes(

                get_jwt_identity()

            )

            return ApiResponse.success(

                "Disputes retrieved successfully.",

                disputes

            )

        except DisputeException as ex:

            return ApiResponse.error(

                str(ex),

                400

            )

    # ==========================================================
    # DISPUTE DETAILS
    # ==========================================================

    @staticmethod
    def details(dispute_id):

        try:

            dispute = service.dispute(dispute_id)

            return ApiResponse.success(

                "Dispute retrieved successfully.",

                dispute

            )

        except DisputeException as ex:

            return ApiResponse.error(

                str(ex),

                404

            )

    # ==========================================================
    # PENDING REVIEWS
    # ==========================================================

    @staticmethod
    def pending():

        try:

            disputes = service.pending_reviews()

            return ApiResponse.success(

                "Pending disputes retrieved.",

                disputes

            )

        except DisputeException as ex:

            return ApiResponse.error(

                str(ex),

                400

            )

    # ==========================================================
    # APPROVE DISPUTE
    # ==========================================================

    @staticmethod
    def approve(dispute_id):

        try:

            data = ReviewDisputeSchema().load(

                request.get_json()

            )

            dispute = service.approve(

                dispute_id,

                get_jwt_identity(),

                data["review_notes"]

            )

            return ApiResponse.success(

                "Dispute approved successfully.",

                dispute

            )

        except ValidationError as ex:

            return ApiResponse.error(

                ex.messages,

                400

            )

        except DisputeException as ex:

            return ApiResponse.error(

                str(ex),

                400

            )

    # ==========================================================
    # REJECT DISPUTE
    # ==========================================================

    @staticmethod
    def reject(dispute_id):

        try:

            data = ReviewDisputeSchema().load(

                request.get_json()

            )

            dispute = service.reject(

                dispute_id,

                get_jwt_identity(),

                data["review_notes"]

            )

            return ApiResponse.success(

                "Dispute rejected successfully.",

                dispute

            )

        except ValidationError as ex:

            return ApiResponse.error(

                ex.messages,

                400

            )

        except DisputeException as ex:

            return ApiResponse.error(

                str(ex),

                400

            )

    # ==========================================================
    # REQUEST MORE INFORMATION
    # ==========================================================

    @staticmethod
    def request_information(dispute_id):

        try:

            data = RequestMoreInformationSchema().load(

                request.get_json()

            )

            dispute = service.request_information(

                dispute_id,

                get_jwt_identity(),

                data["message"]

            )

            return ApiResponse.success(

                "Information request sent.",

                dispute

            )

        except ValidationError as ex:

            return ApiResponse.error(

                ex.messages,

                400

            )

        except DisputeException as ex:

            return ApiResponse.error(

                str(ex),

                400

            )

    # ==========================================================
    # SEARCH DISPUTES
    # ==========================================================

    @staticmethod
    def search():

        try:

            keyword = request.args.get(

                "keyword",

                ""

            )

            disputes = service.search(keyword)

            return ApiResponse.success(

                "Search completed.",

                disputes

            )

        except DisputeException as ex:

            return ApiResponse.error(

                str(ex),

                400

            )

    # ==========================================================
    # STATISTICS
    # ==========================================================

    @staticmethod
    def statistics():

        try:

            stats = service.statistics()

            return ApiResponse.success(

                "Statistics retrieved.",

                stats

            )

        except DisputeException as ex:

            return ApiResponse.error(

                str(ex),

                400

            )