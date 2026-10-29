from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

from app.services.receipt_service import ReceiptService


def test_receipt_download_generates_pdf_without_blob(app):
    service = ReceiptService()
    payment = SimpleNamespace(
        payment_id=6,
        fine_id=12,
        user_id="citizen-id",
        payment_reference="PAY-TEST-6",
        amount=Decimal("125.00"),
        paid_at=datetime(2026, 10, 29, 12, 0, 0),
    )
    fine = SimpleNamespace(fine_number="NF-TEST-12")
    user = SimpleNamespace(first_name="Demo", last_name="Citizen")
    service.fine_repository.find_by_id = lambda _fine_id: fine
    service.user_repository.find_by_id = lambda _user_id: user

    with app.test_request_context():
        response = service.download(payment)

    assert response.mimetype == "application/pdf"
    assert response.headers["Content-Disposition"] == (
        "attachment; filename=receipt_6.pdf"
    )
    response.direct_passthrough = False
    assert response.get_data().startswith(b"%PDF-")
