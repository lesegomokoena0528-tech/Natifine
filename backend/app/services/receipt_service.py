import io
from datetime import datetime

from flask import send_file
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate

from app.repositories.fine_repository import FineRepository
from app.repositories.user_repository import UserRepository


class ReceiptService:

    def __init__(self):
        self.fine_repository = FineRepository()
        self.user_repository = UserRepository()

    def generate_receipt(
        self,
        payment,
        fine=None,
        user=None
    ):
        if not fine and payment.fine_id:
            fine = self.fine_repository.find_by_id(payment.fine_id)

        if not user and payment.user_id:
            user = self.user_repository.find_by_id(payment.user_id)

        filename = f"receipt_{payment.payment_id}.pdf"

        buffer = io.BytesIO()

        doc = SimpleDocTemplate(buffer)
        styles = getSampleStyleSheet()

        citizen_name = f"{user.first_name} {user.last_name}" if user else "Motorist"
        fine_number = fine.fine_number if fine else "N/A"
        payment_date_str = (
            payment.paid_at.strftime("%Y-%m-%d %H:%M:%S")
            if payment.paid_at
            else datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        )

        story = [
            Paragraph(
                "<b>NatiFine SA — Payment Receipt</b>",
                styles["Heading1"]
            ),
            Paragraph(
                f"<b>Receipt Number:</b> {payment.payment_id}",
                styles["BodyText"]
            ),
            Paragraph(
                f"<b>Payment Reference:</b> {payment.payment_reference}",
                styles["BodyText"]
            ),
            Paragraph(
                f"<b>Citizen:</b> {citizen_name}",
                styles["BodyText"]
            ),
            Paragraph(
                f"<b>Fine Number:</b> {fine_number}",
                styles["BodyText"]
            ),
            Paragraph(
                f"<b>Amount Paid:</b> ZAR {payment.amount:.2f}",
                styles["BodyText"]
            ),
            Paragraph(
                f"<b>Payment Date:</b> {payment_date_str}",
                styles["BodyText"]
            ),
            Paragraph(
                f"<b>Generated:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} (Simulated Academic System)",
                styles["BodyText"]
            )
        ]

        doc.build(story)

        return {
            "filename": filename,
            "data": buffer.getvalue(),
        }

    def download(self, payment):
        result = self.generate_receipt(payment)

        return send_file(
            io.BytesIO(result["data"]),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=result["filename"]
        )
