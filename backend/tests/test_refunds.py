"""
==========================================================
NatiFine Backend

Refund Endpoint Integration Tests

Covers the refund wiring between:
    - payment_routes.py
    - payment_controller.py
    - payment_service.py
    - payment_repository.py

Flow: request -> list (citizen/admin) -> approve (admin)
==========================================================
"""

from datetime import datetime, timedelta

import pytest

from flask_jwt_extended import create_access_token

from app.config.database import db
from app.models.user import User
from app.models.user import UserRole
from app.models.user import UserStatus
from app.models.vehicle import Vehicle
from app.models.vehicle import VehicleType
from app.models.vehicle import VehicleStatus
from app.models.traffic_fine import TrafficFine
from app.models.traffic_fine import FineStatus
from app.models.traffic_fine import OffenceSeverity
from app.models.payment import Payment
from app.constants.payment_status import PaymentStatus
from app.constants.payment_method import PaymentMethod
from app.constants.gateway import PaymentGateway


class TestRefunds:

    @pytest.fixture(autouse=True)
    def setup(self, app):

        self.app = app

        with app.app_context():

            db.session.query(Payment).delete()
            db.session.query(TrafficFine).delete()
            db.session.query(Vehicle).delete()
            db.session.query(User).delete()

            db.session.commit()

            self.citizen = self._user(
                "9901015009087", "John", "Smith",
                "john@test.com", "0712345678", UserRole.CITIZEN
            )

            self.admin = self._user(
                "8801015009087", "Ada", "Admin",
                "ada@test.com", "0723456789", UserRole.ADMIN
            )

            self.officer = self._user(
                "7701015009087", "Oscar", "Officer",
                "oscar@test.com", "0734567890", UserRole.OFFICER
            )

            self.other = self._user(
                "6601015009087", "Mia", "Mokoena",
                "mia@test.com", "0745678901", UserRole.CITIZEN
            )

            vehicle = Vehicle(
                registration_number="CA 123 456",
                owner_id=self.citizen.user_id,
                make="Toyota",
                model="Corolla",
                year=2020,
                vin="1HGCM82633A004352",
                vehicle_type=VehicleType.CAR,
                status=VehicleStatus.ACTIVE
            )

            db.session.add(vehicle)
            db.session.commit()

            fine = TrafficFine(
                fine_number="FINE-0001",
                vehicle_id=vehicle.vehicle_id,
                officer_id=self.officer.user_id,
                offence_code="SPD-001",
                offence="Speeding",
                severity=OffenceSeverity.MEDIUM,
                amount=1500.00,
                location="Cape Town CBD",
                issue_date=datetime.utcnow(),
                due_date=datetime.utcnow() + timedelta(days=30),
                status=FineStatus.PAID
            )

            db.session.add(fine)
            db.session.commit()

            payment = Payment(
                fine_id=fine.fine_id,
                user_id=self.citizen.user_id,
                gateway=PaymentGateway.INTERNAL,
                payment_method=PaymentMethod.CARD,
                amount=1500.00,
                currency="ZAR",
                payment_reference="PAY-TEST0001",
                status=PaymentStatus.PAID,
                paid_at=datetime.utcnow()
            )

            db.session.add(payment)

            pending = Payment(
                fine_id=fine.fine_id,
                user_id=self.citizen.user_id,
                gateway=PaymentGateway.INTERNAL,
                payment_method=PaymentMethod.CARD,
                amount=1500.00,
                currency="ZAR",
                payment_reference="PAY-TEST0002",
                status=PaymentStatus.PENDING
            )

            db.session.add(pending)
            db.session.commit()

            self.fine_id = fine.fine_id
            self.payment_id = payment.payment_id
            self.pending_payment_id = pending.payment_id

    # -----------------------------------------------------

    def _user(self, id_number, first, last, email, phone, role):

        user = User(
            id_number=id_number,
            first_name=first,
            last_name=last,
            email=email,
            phone=phone,
            role=role,
            status=UserStatus.ACTIVE
        )

        user.set_password("Password@123")

        db.session.add(user)
        db.session.commit()

        return user

    # -----------------------------------------------------

    def _token(self, user):

        with self.app.app_context():

            return create_access_token(
                identity=str(user.user_id),
                additional_claims={
                    "role": user.role.value,
                    "email": user.email
                }
            )

    def _auth(self, user):

        return {"Authorization": f"Bearer {self._token(user)}"}

    # -----------------------------------------------------
    # REQUEST
    # -----------------------------------------------------

    def test_citizen_can_request_refund(self, client):

        response = client.post(
            f"/api/v1/payments/{self.payment_id}/refund",
            headers=self._auth(self.citizen),
            json={"amount": 1500.00, "reason": "Duplicate payment made in error"}
        )

        assert response.status_code == 201

        body = response.get_json()

        assert body["success"] is True

        assert body["data"]["status"] == "PENDING"

        assert body["data"]["refund_reference"].startswith("REF-")

    # -----------------------------------------------------

    def test_refund_requires_reason(self, client):

        response = client.post(
            f"/api/v1/payments/{self.payment_id}/refund",
            headers=self._auth(self.citizen),
            json={"amount": 1500.00, "reason": "short"}
        )

        assert response.status_code == 400

    # -----------------------------------------------------

    def test_admin_cannot_request_refund(self, client):

        response = client.post(
            f"/api/v1/payments/{self.payment_id}/refund",
            headers=self._auth(self.admin),
            json={"amount": 1500.00, "reason": "Duplicate payment made in error"}
        )

        assert response.status_code == 403

    # -----------------------------------------------------
    # LIST
    # -----------------------------------------------------

    def test_citizen_lists_own_refunds_with_view_fields(self, client):

        client.post(
            f"/api/v1/payments/{self.payment_id}/refund",
            headers=self._auth(self.citizen),
            json={"amount": 1500.00, "reason": "Duplicate payment made in error"}
        )

        response = client.get(
            "/api/v1/payments/refunds",
            headers=self._auth(self.citizen)
        )

        assert response.status_code == 200

        data = response.get_json()["data"]

        assert len(data) == 1

        assert data[0]["payment_reference"] == "PAY-TEST0001"

        assert data[0]["fine_number"] == "FINE-0001"

        assert data[0]["user_name"] == "John Smith"

    # -----------------------------------------------------

    def test_status_filter(self, client):

        client.post(
            f"/api/v1/payments/{self.payment_id}/refund",
            headers=self._auth(self.citizen),
            json={"amount": 1500.00, "reason": "Duplicate payment made in error"}
        )

        pending = client.get(
            "/api/v1/payments/refunds?status=PENDING",
            headers=self._auth(self.admin)
        )

        completed = client.get(
            "/api/v1/payments/refunds?status=COMPLETED",
            headers=self._auth(self.admin)
        )

        assert len(pending.get_json()["data"]) == 1

        assert len(completed.get_json()["data"]) == 0

    # -----------------------------------------------------

    def test_officer_cannot_list_refunds(self, client):

        response = client.get(
            "/api/v1/payments/refunds",
            headers=self._auth(self.officer)
        )

        assert response.status_code == 403

    # -----------------------------------------------------
    # APPROVE
    # -----------------------------------------------------

    def test_admin_approves_refund(self, client):

        created = client.post(
            f"/api/v1/payments/{self.payment_id}/refund",
            headers=self._auth(self.citizen),
            json={"amount": 1500.00, "reason": "Duplicate payment made in error"}
        ).get_json()["data"]

        refund_id = created["refund_id"]

        response = client.patch(
            f"/api/v1/payments/refunds/{refund_id}/approve",
            headers=self._auth(self.admin),
            json={}
        )

        assert response.status_code == 200

        data = response.get_json()["data"]

        assert data["status"] == "COMPLETED"

        assert data["approved_by"] == self.admin.user_id

        assert data["approved_date"] is not None

        with self.app.app_context():

            payment = db.session.get(Payment, self.payment_id)

            fine = db.session.get(TrafficFine, self.fine_id)

            assert payment.status == PaymentStatus.REFUNDED

            assert fine.status == FineStatus.ISSUED

    # -----------------------------------------------------

    def test_citizen_cannot_approve_refund(self, client):

        created = client.post(
            f"/api/v1/payments/{self.payment_id}/refund",
            headers=self._auth(self.citizen),
            json={"amount": 1500.00, "reason": "Duplicate payment made in error"}
        ).get_json()["data"]

        response = client.patch(
            f"/api/v1/payments/refunds/{created['refund_id']}/approve",
            headers=self._auth(self.citizen),
            json={}
        )

        assert response.status_code == 403

    # -----------------------------------------------------

    def test_cannot_approve_twice(self, client):

        created = client.post(
            f"/api/v1/payments/{self.payment_id}/refund",
            headers=self._auth(self.citizen),
            json={"amount": 1500.00, "reason": "Duplicate payment made in error"}
        ).get_json()["data"]

        url = f"/api/v1/payments/refunds/{created['refund_id']}/approve"

        client.patch(url, headers=self._auth(self.admin), json={})

        response = client.patch(url, headers=self._auth(self.admin), json={})

        assert response.status_code == 400

    # -----------------------------------------------------

    def test_approve_unknown_refund(self, client):

        response = client.patch(
            "/api/v1/payments/refunds/999999/approve",
            headers=self._auth(self.admin),
            json={}
        )

        assert response.status_code == 400

    # -----------------------------------------------------
    # REJECT
    # -----------------------------------------------------

    def test_admin_rejects_refund_with_note(self, client):

        created = client.post(
            f"/api/v1/payments/{self.payment_id}/refund",
            headers=self._auth(self.citizen),
            json={"amount": 1500.00, "reason": "Duplicate payment made in error"}
        ).get_json()["data"]

        response = client.patch(
            f"/api/v1/payments/refunds/{created['refund_id']}/reject",
            headers=self._auth(self.admin),
            json={"reason": "Payment already reconciled"}
        )

        assert response.status_code == 200

        data = response.get_json()["data"]

        assert data["status"] == "REJECTED"

        assert data["admin_note"] == "Payment already reconciled"

        assert data["approved_by"] == self.admin.user_id

        with self.app.app_context():

            payment = db.session.get(Payment, self.payment_id)

            fine = db.session.get(TrafficFine, self.fine_id)

            assert payment.status == PaymentStatus.PAID

            assert fine.status == FineStatus.PAID

    # -----------------------------------------------------

    def test_citizen_cannot_reject_refund(self, client):

        created = client.post(
            f"/api/v1/payments/{self.payment_id}/refund",
            headers=self._auth(self.citizen),
            json={"amount": 1500.00, "reason": "Duplicate payment made in error"}
        ).get_json()["data"]

        response = client.patch(
            f"/api/v1/payments/refunds/{created['refund_id']}/reject",
            headers=self._auth(self.citizen),
            json={}
        )

        assert response.status_code == 403

    # -----------------------------------------------------

    def test_cannot_reject_twice(self, client):

        created = client.post(
            f"/api/v1/payments/{self.payment_id}/refund",
            headers=self._auth(self.citizen),
            json={"amount": 1500.00, "reason": "Duplicate payment made in error"}
        ).get_json()["data"]

        url = f"/api/v1/payments/refunds/{created['refund_id']}/reject"

        client.patch(url, headers=self._auth(self.admin), json={})

        response = client.patch(url, headers=self._auth(self.admin), json={})

        assert response.status_code == 400

    # -----------------------------------------------------

    def test_rejected_refund_allows_new_request(self, client):

        created = client.post(
            f"/api/v1/payments/{self.payment_id}/refund",
            headers=self._auth(self.citizen),
            json={"amount": 1500.00, "reason": "Duplicate payment made in error"}
        ).get_json()["data"]

        client.patch(
            f"/api/v1/payments/refunds/{created['refund_id']}/reject",
            headers=self._auth(self.admin),
            json={}
        )

        response = client.post(
            f"/api/v1/payments/{self.payment_id}/refund",
            headers=self._auth(self.citizen),
            json={"amount": 1500.00, "reason": "Re-requesting after rejection"}
        )

        assert response.status_code == 201

    # -----------------------------------------------------
    # REQUEST VALIDATION
    # -----------------------------------------------------

    def test_cannot_refund_someone_elses_payment(self, client):

        response = client.post(
            f"/api/v1/payments/{self.payment_id}/refund",
            headers=self._auth(self.other),
            json={"amount": 1500.00, "reason": "Trying another users payment"}
        )

        assert response.status_code == 403

    # -----------------------------------------------------

    def test_cannot_refund_unpaid_payment(self, client):

        response = client.post(
            f"/api/v1/payments/{self.pending_payment_id}/refund",
            headers=self._auth(self.citizen),
            json={"amount": 1500.00, "reason": "Refund on an unpaid transaction"}
        )

        assert response.status_code == 400

    # -----------------------------------------------------

    def test_cannot_open_duplicate_refund(self, client):

        payload = {"amount": 1500.00, "reason": "Duplicate payment made in error"}

        client.post(
            f"/api/v1/payments/{self.payment_id}/refund",
            headers=self._auth(self.citizen),
            json=payload
        )

        response = client.post(
            f"/api/v1/payments/{self.payment_id}/refund",
            headers=self._auth(self.citizen),
            json=payload
        )

        assert response.status_code == 409

    # -----------------------------------------------------

    def test_refund_requires_auth(self, client):

        response = client.get("/api/v1/payments/refunds")

        assert response.status_code == 401

    # -----------------------------------------------------
    # TOTALS
    # -----------------------------------------------------

    def test_totals_include_completed_refund(self, client):

        created = client.post(
            f"/api/v1/payments/{self.payment_id}/refund",
            headers=self._auth(self.citizen),
            json={"amount": 1500.00, "reason": "Duplicate payment made in error"}
        ).get_json()["data"]

        client.patch(
            f"/api/v1/payments/refunds/{created['refund_id']}/approve",
            headers=self._auth(self.admin),
            json={}
        )

        response = client.get(
            "/api/v1/payments/totals",
            headers=self._auth(self.citizen)
        )

        assert response.status_code == 200

        data = response.get_json()["data"]

        assert data["total_refunded"] == 1500.00
