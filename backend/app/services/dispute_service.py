import os
import uuid
from datetime import datetime

from app.models.dispute import Dispute
from app.models.dispute_document import DisputeDocument

from app.repositories.dispute_repository import DisputeRepository
from app.repositories.fine_repository import FineRepository
from app.repositories.user_repository import UserRepository

from app.services.upload_service import UploadService
from app.services.notification_service import NotificationService

from app.constants.dispute_status import DisputeStatus
from app.constants.fine_status import FineStatus

from app.exceptions.dispute_exceptions import *


class DisputeService:

    def __init__(self):

        self.repository = DisputeRepository()

        self.fine_repository = FineRepository()

        self.user_repository = UserRepository()

        self.upload_service = UploadService()

        self.notification_service = NotificationService()
    
    # ==========================================================
    # SUBMIT DISPUTE
    # ==========================================================

    def submit_dispute(
            self,
            user_id,
            data
    ):

        fine = self.fine_repository.find_by_id(
            data["fine_id"]
        )

        if not fine:

            raise InvalidDisputeException(
                "Traffic fine does not exist."
            )

        # Fine belongs to vehicle; verify vehicle owner
        owner_id = fine.vehicle.owner_id if fine.vehicle else getattr(fine, "owner_id", None)
        if owner_id != user_id:

            raise InvalidDisputeException(
                "You may only dispute your own traffic fines."
            )

        existing = self.repository.active_dispute_for_fine(
            fine.fine_id
        )

        if existing:

            raise DuplicateDisputeException(
                "An active dispute already exists."
            )

        dispute = Dispute()

        dispute.fine_id = fine.fine_id

        dispute.user_id = user_id

        dispute.description = data["description"]

        dispute.status = DisputeStatus.PENDING

        dispute.submitted_at = datetime.utcnow()

        self.repository.create(dispute)

        fine.status = FineStatus.DISPUTED
        self.fine_repository.update(fine)

        self.notification_service.dispute_created(
            user_id,
            dispute
        )

        return dispute.to_dict()
    
    # ==========================================================
    # UPLOAD DOCUMENT
    # ==========================================================

    def upload_document(
            self,
            dispute_id,
            uploaded_file
    ):

        dispute = self.repository.find_by_id(
            dispute_id
        )

        if not dispute:

            raise DisputeNotFoundException()

        file_information = self.upload_service.upload(
            uploaded_file,
            "disputes"
        )

        document = DisputeDocument()

        document.dispute_id = dispute.dispute_id

        document.file_name = file_information["file_name"]

        document.original_name = file_information["original_name"]

        document.mime_type = file_information["mime_type"]

        document.file_size = file_information["size"]

        document.storage_path = file_information["path"]

        self.repository.create_document(
            document
        )

        return document.to_dict()
    
    # ==========================================================
    # USER DISPUTES
    # ==========================================================

    def user_disputes(
            self,
            user_id
    ):

        disputes = self.repository.user_disputes(
            user_id
        )

        return [

            dispute.to_dict()

            for dispute in disputes

        ]
        
    # ==========================================================
    # DETAILS
    # ==========================================================

    def dispute(
            self,
            dispute_id
    ):

        dispute = self.repository.find_by_id(
            dispute_id
        )

        if not dispute:

            raise DisputeNotFoundException()

        return dispute.to_dict()
    
    # ==========================================================
    # PENDING REVIEWS
    # ==========================================================

    def pending_reviews(self):

        return [

            dispute.to_dict()

            for dispute

            in self.repository.pending_reviews()

        ]
        
        
    # ==========================================================
    # APPROVE
    # ==========================================================

    def approve(
            self,
            dispute_id,
            reviewer_id,
            notes
    ):

        dispute = self.repository.find_by_id(
            dispute_id
        )

        if not dispute:

            raise DisputeNotFoundException()

        dispute.status = DisputeStatus.APPROVED

        dispute.reviewed_by = reviewer_id

        dispute.review_notes = notes

        dispute.reviewed_at = datetime.utcnow()

        self.repository.update(dispute)

        fine = self.fine_repository.find_by_id(
            dispute.fine_id
        )

        fine.status = FineStatus.CANCELLED

        self.fine_repository.update(fine)

        self.notification_service.dispute_approved(

            dispute.user_id,

            dispute

        )

        return dispute.to_dict()
    
    # ==========================================================
    # REJECT
    # ==========================================================

    def reject(
            self,
            dispute_id,
            reviewer_id,
            notes
    ):

        dispute = self.repository.find_by_id(
            dispute_id
        )

        if not dispute:

            raise DisputeNotFoundException()

        dispute.status = DisputeStatus.REJECTED

        dispute.reviewed_by = reviewer_id

        dispute.review_notes = notes

        dispute.reviewed_at = datetime.utcnow()

        self.repository.update(dispute)

        self.notification_service.dispute_rejected(

            dispute.user_id,

            dispute

        )

        return dispute.to_dict()
    
    # ==========================================================
    # REQUEST INFORMATION
    # ==========================================================

    def request_information(
            self,
            dispute_id,
            reviewer_id,
            message
    ):

        dispute = self.repository.find_by_id(
            dispute_id
        )

        if not dispute:

            raise DisputeNotFoundException()

        dispute.status = (
            DisputeStatus.MORE_INFORMATION_REQUIRED
        )

        dispute.reviewed_by = reviewer_id

        dispute.review_notes = message

        dispute.reviewed_at = datetime.utcnow()

        self.repository.update(dispute)

        self.notification_service.more_information(

            dispute.user_id,

            dispute

        )

        return dispute.to_dict()
    
    # ==========================================================
    # DASHBOARD
    # ==========================================================

    def statistics(self):

        return self.repository.statistics()
    
    # ==========================================================
    # SEARCH
    # ==========================================================

    def search(
            self,
            keyword
    ):

        disputes = self.repository.search(
            keyword
        )

        return [

            dispute.to_dict()

            for dispute in disputes

        ]
        
    