from datetime import datetime, timedelta
from uuid import uuid4

from app.config.database import db

from app.models.user import UserRole
from app.models.traffic_fine import (
    TrafficFine,
    FineStatus,
    OffenceSeverity
)

from app.models.fine_history import FineHistory

from app.repositories.fine_repository import FineRepository
from app.repositories.fine_history_repository import FineHistoryRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.repositories.user_repository import UserRepository

from app.exceptions.fine_exceptions import *

from app.services.sms_service import SMSService
from app.services.email_service import EmailService
from app.services.whatsapp_service import WhatsAppService
from app.services.notification_service import NotificationService


class FineService:

    def __init__(self):

        self.repository = FineRepository()

        self.history_repository = FineHistoryRepository()

        self.vehicle_repository = VehicleRepository()

        self.user_repository = UserRepository()

        self.sms = SMSService()

        self.email = EmailService()

        self.whatsapp = WhatsAppService()

        self.notification_service = NotificationService()
        
    # ======================================================
    # ISSUE FINE
    # ======================================================

    def issue_fine(self, data, officer_id):

        officer = self.user_repository.find_by_id(
            officer_id
        )

        if not officer:
            raise InvalidOfficerException()

        if officer.role not in [
            UserRole.ADMIN,
            UserRole.OFFICER
        ]:
            raise InvalidOfficerException(
                "User cannot issue fines."
            )

        vehicle = self.vehicle_repository.find_by_id(
            data["vehicle_id"]
        )

        if not vehicle:
            raise InvalidVehicleException()

        duplicate = self.repository.filter(
            vehicle_id=data["vehicle_id"],
            offence_code=data["offence_code"],
            status=FineStatus.ISSUED
        )

        if duplicate:
            raise DuplicateFineException(
                "Active fine already exists."
            )

        fine = TrafficFine()

        fine.fine_number = self.generate_fine_number()

        fine.vehicle_id = vehicle.vehicle_id

        fine.officer_id = officer.user_id

        fine.offence_code = data["offence_code"]

        fine.offence = data["offence"]

        fine.severity = OffenceSeverity[
            data["severity"].upper()
        ]

        fine.amount = data["amount"]

        fine.location = data["location"]

        fine.latitude = data.get("latitude")

        fine.longitude = data.get("longitude")

        fine.remarks = data.get("remarks")

        fine.status = FineStatus.ISSUED

        fine.issue_date = datetime.utcnow()

        fine.due_date = self.calculate_due_date()

        db.session.add(fine)

        db.session.commit()

        self.record_history(
            fine,
            officer.user_id,
            None,
            FineStatus.ISSUED,
            "Fine Issued"
        )

        owner = vehicle.owner

        if owner:
            try:
                self.notification_service.fine_issued(owner.user_id, fine)
            except Exception:
                pass

        return fine
    
    # ======================================================
    # GENERATE FINE NUMBER
    # ======================================================
    
    def generate_fine_number(self):

        year = datetime.utcnow().year

        count = self.repository.count_all() + 1

        return f"NF-{year}-{count:06d}"
    
    # ======================================================
    # FINE DUE DATE
    # ======================================================
    
    def calculate_due_date(self):

        return datetime.utcnow() + timedelta(days=30)
    
    # ======================================================
    # HISTORY RECORDING
    # ======================================================
    
    def record_history(

        self,

        fine,

        changed_by,

        old_status,

        new_status,

        reason

    ):

        history = FineHistory()

        history.fine_id = fine.fine_id

        history.changed_by = changed_by

        history.old_status = (
            old_status.value if old_status else None
        )

        history.new_status = new_status.value

        history.reason = reason

        db.session.add(history)

        db.session.commit()
        
    # ======================================================
    # UPDATE FINE
    # ======================================================
    
    def update_fine(self, fine_id, data):

        fine = self.repository.find_by_id(
            fine_id
        )

        if not fine:
            raise FineNotFoundException()

        if fine.status == FineStatus.PAID:
            raise FineAlreadyPaidException()

        for field in [
            "offence",
            "location",
            "remarks",
            "amount"
        ]:

            if field in data:
                setattr(
                    fine,
                    field,
                    data[field]
                )

        db.session.commit()

        return fine
    
    
    # ======================================================
    # CANCEL FINE
    # ======================================================
    
    def cancel_fine(

        self,

        fine_id,

        officer_id,

        reason

    ):

        fine = self.repository.find_by_id(
            fine_id
        )

        if not fine:
            raise FineNotFoundException()

        if fine.status == FineStatus.CANCELLED:
            raise FineAlreadyCancelledException()

        old = fine.status

        fine.status = FineStatus.CANCELLED

        db.session.commit()

        self.record_history(
            fine,
            officer_id,
            old,
            FineStatus.CANCELLED,
            reason
        )

        return fine
    
    # ======================================================
    # CHANGE FINE STATUS
    # ======================================================
    
    def change_status(

        self,

        fine_id,

        officer_id,

        status,

        reason

    ):

        fine = self.repository.find_by_id(
            fine_id
        )

        if not fine:
            raise FineNotFoundException()

        old = fine.status

        fine.status = FineStatus[
            status.upper()
        ]

        if fine.status == FineStatus.PAID:
            fine.paid_date = datetime.utcnow()

        db.session.commit()

        self.record_history(
            fine,
            officer_id,
            old,
            fine.status,
            reason
        )

        return fine
    
    
    # ======================================================
    # SEARCH FINE
    # ======================================================
    
    def search(self, keyword):

        return self.repository.search(
            keyword
        )
    
    # ======================================================
    # CITIZEN FINE
    # ======================================================
    
    def citizen_fines(self, owner_id):

        return self.repository.find_by_owner(
            owner_id
        )
    
    # ======================================================
    # STATISTICS FINE
    # ======================================================
    
    def statistics(self):

        return {

            "total":

                self.repository.count_all(),

            "paid":

                self.repository.count_paid(),

            "unpaid":

                self.repository.count_unpaid(),

            "revenue":

                float(
                    self.repository.total_revenue()
                )

        }
    
    # ======================================================
    # HISTORY FINE
    # ======================================================
    
    def history(self, fine_id):

        return self.history_repository.find_by_fine(
            fine_id
        )