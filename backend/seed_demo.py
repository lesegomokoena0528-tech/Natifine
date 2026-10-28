"""
NatiFine SA - demo data seeder.

Ensures the database schema exists (the Alembic migrations are the source of
truth via `flask db upgrade`; this script also calls `db.create_all()` as a
safety net) and inserts fully fictional South African demonstration data
covering every role and every major workflow.

Run from the backend folder:

    python seed_demo.py

All names, ID numbers, phone numbers, vehicles and amounts are fictitious.
Safe to run repeatedly: it will not duplicate records that already exist.
"""

from datetime import datetime, timedelta

from app.factory import create_app
from app.config.database import db

from app.models.user import User, UserRole, UserStatus
from app.models.vehicle import Vehicle, VehicleType, VehicleStatus
from app.models.traffic_fine import TrafficFine, FineStatus, OffenceSeverity
from app.models.payment import Payment
from app.models.dispute import Dispute
from app.models.notification import Notification
from app.models.fine_history import FineHistory
from app.models.notification_template import NotificationTemplate

from app.constants.payment_status import PaymentStatus
from app.constants.payment_method import PaymentMethod
from app.constants.gateway import PaymentGateway
from app.constants.dispute_status import DisputeStatus
from app.constants.notification_channel import NotificationChannel
from app.constants.notification_status import NotificationStatus
from app.constants.notification_type import NotificationType


app = create_app()


def ensure_user(
    id_number,
    first_name,
    last_name,
    email,
    phone,
    password,
    role
):
    existing = User.query.filter_by(email=email).first()
    if existing:
        return existing
    user = User(
        id_number=id_number,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        role=role,
        status=UserStatus.ACTIVE
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    return user


def ensure_vehicle(
    registration_number,
    owner,
    make,
    model,
    year,
    color,
    vin,
    engine_number,
    vehicle_type=VehicleType.CAR
):
    existing = Vehicle.query.filter_by(
        registration_number=registration_number
    ).first()
    if existing:
        return existing
    vehicle = Vehicle(
        registration_number=registration_number,
        owner_id=owner.user_id,
        make=make,
        model=model,
        year=year,
        color=color,
        vin=vin,
        engine_number=engine_number,
        vehicle_type=vehicle_type,
        status=VehicleStatus.ACTIVE
    )
    db.session.add(vehicle)
    db.session.flush()
    return vehicle


def add_fine(
    fine_number,
    vehicle,
    officer,
    offence_code,
    offence,
    severity,
    amount,
    location,
    status,
    issue_days_ago,
    due_in_days,
    evidence,
    remarks=None,
    paid=False
):
    existing = TrafficFine.query.filter_by(
        fine_number=fine_number
    ).first()
    if existing:
        return existing

    issue_date = datetime.utcnow() - timedelta(days=issue_days_ago)
    due_date = issue_date + timedelta(days=due_in_days)

    fine = TrafficFine(
        fine_number=fine_number,
        vehicle_id=vehicle.vehicle_id,
        officer_id=officer.user_id,
        offence_code=offence_code,
        offence=offence,
        severity=severity,
        amount=amount,
        location=location,
        evidence_photo=evidence,
        remarks=remarks,
        status=status,
        issue_date=issue_date,
        due_date=due_date,
        paid_date=issue_date + timedelta(days=3) if paid else None
    )
    db.session.add(fine)
    db.session.flush()

    db.session.add(FineHistory(
        fine_id=fine.fine_id,
        changed_by=officer.user_id,
        old_status=None,
        new_status=FineStatus.ISSUED.value,
        reason="Fine issued",
        change_date=issue_date
    ))
    return fine


def add_payment(fine, user, method, gateway, days_ago):
    existing = Payment.query.filter_by(
        payment_reference=f"PAY-DEMO-{fine.fine_number}"
    ).first()
    if existing:
        return existing
    payment = Payment(
        fine_id=fine.fine_id,
        user_id=user.user_id,
        gateway=gateway,
        payment_method=method,
        amount=fine.amount,
        currency="ZAR",
        payment_reference=f"PAY-DEMO-{fine.fine_number}",
        gateway_reference=f"GW-DEMO-{fine.fine_number}",
        transaction_id=f"TXN-DEMO-{fine.fine_number}",
        status=PaymentStatus.PAID,
        paid_at=datetime.utcnow() - timedelta(days=days_ago)
    )
    db.session.add(payment)
    db.session.flush()
    return payment


def add_dispute(fine, user, reviewer, description, status, days_ago, notes=None):
    existing = Dispute.query.filter_by(fine_id=fine.fine_id).first()
    if existing:
        return existing
    reviewed = status in (
        DisputeStatus.APPROVED,
        DisputeStatus.REJECTED,
        DisputeStatus.MORE_INFORMATION_REQUIRED
    )
    dispute = Dispute(
        fine_id=fine.fine_id,
        user_id=user.user_id,
        description=description,
        status=status,
        submitted_at=datetime.utcnow() - timedelta(days=days_ago),
        reviewed_by=reviewer.user_id if reviewed else None,
        reviewed_at=datetime.utcnow() - timedelta(days=max(days_ago - 2, 0)) if reviewed else None,
        review_notes=notes
    )
    db.session.add(dispute)
    db.session.flush()
    return dispute


def add_notification(user, title, message, channel, ntype, status, days_ago):
    existing = Notification.query.filter_by(
        user_id=user.user_id,
        title=title
    ).first()
    if existing:
        return existing
    notification = Notification(
        user_id=user.user_id,
        title=title,
        message=message,
        channel=channel,
        type=ntype,
        status=status,
        recipient=user.phone or user.email,
        provider="SIMULATED",
        sent_date=datetime.utcnow() - timedelta(days=days_ago)
    )
    db.session.add(notification)
    db.session.flush()
    return notification


def seed_templates():
    templates = [
        (
            "FINE_DUE",
            NotificationChannel.SMS,
            "Traffic Fine Due Soon",
            "Dear {first_name}, your fine {fine_number} of ZAR {amount} is due on {due_date}. Please settle online."
        ),
        (
            "OVERDUE_FINE",
            NotificationChannel.SMS,
            "Overdue Traffic Fine",
            "Dear {first_name}, your fine {fine_number} of ZAR {amount} is overdue. Please settle to avoid further penalties."
        )
    ]
    for name, channel, subject, body in templates:
        if not NotificationTemplate.query.filter_by(name=name).first():
            db.session.add(NotificationTemplate(
                name=name,
                channel=channel,
                subject=subject,
                body=body,
                active=True
            ))


def main():
    with app.app_context():
        db.create_all()
        print("Schema ensured.")

        admin = ensure_user(
            "8001015009087", "System", "Administrator",
            "admin@natifine.gov.za", "0711111111",
            "Admin@123", UserRole.ADMIN
        )
        officer = ensure_user(
            "8505055009086", "Nyiko", "Mlambo",
            "officer@natifine.gov.za", "0722222222",
            "Officer@123", UserRole.OFFICER
        )
        officer2 = ensure_user(
            "8707075009088", "Thandi", "Nkosi",
            "thandi.nkosi@natifine.gov.za", "0733333333",
            "Officer@123", UserRole.OFFICER
        )

        sipho = ensure_user(
            "9202205012083", "Sipho", "Dlamini",
            "citizen@natifine.co.za", "0821234567",
            "Citizen@123", UserRole.CITIZEN
        )
        lerato = ensure_user(
            "9101155013084", "Lerato", "Mahlangu",
            "lerato@natifine.co.za", "0732345678",
            "Citizen@123", UserRole.CITIZEN
        )
        johan = ensure_user(
            "8803155012085", "Johan", "van der Merwe",
            "johan@natifine.co.za", "0843456789",
            "Citizen@123", UserRole.CITIZEN
        )

        v_sipho1 = ensure_vehicle(
            "CA123456", sipho, "Volkswagen", "Polo",
            2019, "White", "WVWZZZ1KZAW123456", "ENG-SIP-001"
        )
        v_sipho2 = ensure_vehicle(
            "GP456789", sipho, "Toyota", "Hilux",
            2021, "Silver", "AHTFR22G10K456789", "ENG-SIP-002",
            VehicleType.TRUCK
        )
        v_lerato = ensure_vehicle(
            "GP987654", lerato, "Hyundai", "i20",
            2020, "Blue", "KMHCT41C7AU987654", "ENG-LER-001"
        )
        v_johan = ensure_vehicle(
            "ZN456789", johan, "Ford", "Ranger",
            2018, "Grey", "MNCBBBB0JWW456789", "ENG-JOH-001"
        )

        staff = [officer, officer2]

        # ---- Sipho: one unpaid due soon, one overdue, one paid, one disputed
        f1 = add_fine(
            "NF-2026-000001", v_sipho1, staff[0],
            "SPD-112", "Exceeding the speed limit in a 60km/h zone",
            OffenceSeverity.HIGH, 1500.00,
            "Jan Smuts Avenue, Randburg", FineStatus.ISSUED,
            issue_days_ago=5, due_in_days=25,
            evidence="/assets/images/evidence-2.svg"
        )
        f2 = add_fine(
            "NF-2026-000002", v_sipho1, staff[1],
            "PARK-015", "Parking in a no-stopping zone",
            OffenceSeverity.LOW, 500.00,
            "Church Street, Pretoria CBD", FineStatus.ISSUED,
            issue_days_ago=45, due_in_days=30,
            evidence="/assets/images/evidence-3.svg"
        )
        f3 = add_fine(
            "NF-2026-000003", v_sipho2, staff[0],
            "SIG-021", "Disregarding a red traffic signal",
            OffenceSeverity.CRITICAL, 2500.00,
            "N1 Highway, Midrand", FineStatus.PAID,
            issue_days_ago=60, due_in_days=30,
            evidence="/assets/images/evidence-1.svg", paid=True
        )
        add_payment(f3, sipho, PaymentMethod.CARD, PaymentGateway.INTERNAL, 50)

        f4 = add_fine(
            "NF-2026-000004", v_sipho2, staff[1],
            "LIC-004", "Operating a vehicle with an expired licence disc",
            OffenceSeverity.MEDIUM, 1000.00,
            "Beyers Naude Drive, Johannesburg", FineStatus.DISPUTED,
            issue_days_ago=20, due_in_days=10,
            evidence="/assets/images/evidence-1.svg"
        )
        add_dispute(
            f4, sipho, None,
            "The licence disc was renewed at the Randburg licensing office two days before the notice was issued. I have attached the renewal receipt as supporting evidence.",
            DisputeStatus.PENDING, 12
        )

        # ---- Lerato: unpaid + approved dispute (fine cancelled)
        f5 = add_fine(
            "NF-2026-000005", v_lerato, staff[0],
            "SPD-108", "Exceeding the speed limit in an 80km/h zone",
            OffenceSeverity.MEDIUM, 1200.00,
            "Soweto Highway, Johannesburg", FineStatus.ISSUED,
            issue_days_ago=10, due_in_days=20,
            evidence="/assets/images/evidence-2.svg"
        )
        f6 = add_fine(
            "NF-2026-000006", v_lerato, staff[1],
            "LIC-004", "Operating a vehicle with an expired licence disc",
            OffenceSeverity.MEDIUM, 800.00,
            "Voortrekker Road, Krugersdorp", FineStatus.CANCELLED,
            issue_days_ago=40, due_in_days=30,
            evidence="/assets/images/evidence-1.svg"
        )
        add_dispute(
            f6, lerato, officer,
            "The vehicle was sold and the licence disc belonged to the previous owner. Transfer of ownership forms are attached.",
            DisputeStatus.APPROVED, 35,
            notes="Transfer documents verified. Fine cancelled."
        )

        # ---- Johan: overdue unpaid + rejected dispute
        f7 = add_fine(
            "NF-2026-000007", v_johan, staff[0],
            "SIG-021", "Disregarding a red traffic signal",
            OffenceSeverity.CRITICAL, 2500.00,
            "Kruger Gate Road, Nelspruit", FineStatus.ISSUED,
            issue_days_ago=75, due_in_days=30,
            evidence="/assets/images/evidence-1.svg"
        )
        f8 = add_fine(
            "NF-2026-000008", v_johan, staff[1],
            "PARK-015", "Parking in a no-stopping zone",
            OffenceSeverity.LOW, 500.00,
            "Samora Machel Avenue, Witbank", FineStatus.REJECTED_DISPUTE,
            issue_days_ago=30, due_in_days=30,
            evidence="/assets/images/evidence-3.svg"
        )
        add_dispute(
            f8, johan, officer,
            "I was only stopped for a few minutes and there were no clear signs indicating the restriction in that area.",
            DisputeStatus.REJECTED, 25,
            notes="Signage confirmed present by issuing officer. Fine upheld."
        )

        # ---- Notifications
        add_notification(
            sipho, "Traffic Fine Issued: NF-2026-000001",
            "Dear Sipho, a traffic fine (NF-2026-000001) of ZAR 1500.00 was issued for "
            "speeding at Jan Smuts Avenue, Randburg. Please view or settle online.",
            NotificationChannel.SMS, NotificationType.FINE_ISSUED,
            NotificationStatus.SENT, 5
        )
        add_notification(
            sipho, "Payment Successful: PAY-DEMO-NF-2026-000003",
            "Dear Sipho, payment of ZAR 2500.00 was received for NF-2026-000003. "
            "Your fine is now marked as Paid.",
            NotificationChannel.SMS, NotificationType.PAYMENT_RECEIVED,
            NotificationStatus.SENT, 50
        )
        add_notification(
            sipho, "Dispute Submitted: #1",
            "Dear Sipho, your dispute for fine NF-2026-000004 has been received and is "
            "currently under review by an adjudication officer.",
            NotificationChannel.EMAIL, NotificationType.DISPUTE_SUBMITTED,
            NotificationStatus.SENT, 12
        )
        add_notification(
            sipho, "Urgent Reminder: Fine NF-2026-000002 Outstanding",
            "Dear Sipho, your traffic fine NF-2026-000002 of ZAR 500.00 is outstanding. "
            "Please settle or submit a dispute to avoid late penalties.",
            NotificationChannel.SMS, NotificationType.FINE_DUE,
            NotificationStatus.SENT, 15
        )
        add_notification(
            lerato, "Dispute Decision: Upheld (Fine Dismissed)",
            "Dear Lerato, your dispute was reviewed. Decision: Upheld. "
            "Notes: Transfer documents verified. Fine cancelled.",
            NotificationChannel.SMS, NotificationType.DISPUTE_APPROVED,
            NotificationStatus.SENT, 33
        )
        add_notification(
            johan, "Traffic Fine Issued: NF-2026-000007",
            "Dear Johan, a traffic fine (NF-2026-000007) of ZAR 2500.00 was issued for "
            "disregarding a red signal at Nelspruit.",
            NotificationChannel.SMS, NotificationType.FINE_ISSUED,
            NotificationStatus.SENT, 75
        )

        seed_templates()

        db.session.commit()

        print("Demo data seeded successfully.")
        print("------------------------------------------")
        print("Admin    : admin@natifine.gov.za / Admin@123")
        print("Officer  : officer@natifine.gov.za / Officer@123")
        print("Citizen  : citizen@natifine.co.za / Citizen@123")
        print("Citizen  : lerato@natifine.co.za / Citizen@123")
        print("Citizen  : johan@natifine.co.za / Citizen@123")
        print("------------------------------------------")


if __name__ == "__main__":
    main()
