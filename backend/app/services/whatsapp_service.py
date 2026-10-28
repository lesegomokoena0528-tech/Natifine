import requests

from app.config.whatsapp import (
    WHATSAPP_API_URL,
    WHATSAPP_PHONE_NUMBER_ID,
    WHATSAPP_ACCESS_TOKEN,
)


import uuid


class WhatsAppService:
    PROVIDER = "SIMULATED_WHATSAPP"

    def __init__(self):
        self.url = (
            f"{WHATSAPP_API_URL}/"
            f"{WHATSAPP_PHONE_NUMBER_ID}"
            "/messages"
        ) if WHATSAPP_API_URL and WHATSAPP_PHONE_NUMBER_ID else None

        self.headers = {
            "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        } if WHATSAPP_ACCESS_TOKEN else {}

    # =====================================================
    # GENERIC SEND
    # =====================================================
    def send(self, notification):
        if self.url and self.headers:
            try:
                payload = {
                    "messaging_product": "whatsapp",
                    "to": notification.recipient,
                    "type": "text",
                    "text": {
                        "body": notification.message,
                    },
                }

                response = requests.post(
                    self.url,
                    headers=self.headers,
                    json=payload,
                    timeout=5,
                )
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "provider": "META_WHATSAPP",
                        "message_id": result["messages"][0]["id"],
                    }
            except Exception:
                pass

        return {
            "provider": self.PROVIDER,
            "message_id": f"SIM-WA-{uuid.uuid4().hex[:10].upper()}",
        }

    # =====================================================
    # CUSTOM MESSAGE
    # =====================================================
    def send_message(self, phone, message):
        notification = type(
            "Notification",
            (),
            {
                "recipient": phone,
                "message": message,
            },
        )()

        return self.send(notification)

    # =====================================================
    # OTP
    # =====================================================
    def send_otp(self, phone, otp):
        text = (
            f"Your verification code is "
            f"{otp}.\n"
            "Do not share it."
        )

        return self.send_message(phone, text)

    # =====================================================
    # PAYMENT RECEIVED
    # =====================================================
    def payment_received(self, user, payment):
        text = (
            f"Payment received.\n"
            f"Reference: "
            f"{payment.payment_reference}"
        )

        return self.send_message(user.phone, text)

    # =====================================================
    # FINE ISSUED
    # =====================================================
    def fine_issued(self, user, fine):
        text = (
            f"Traffic Fine Issued\n\n"
            f"Fine Number: "
            f"{fine.fine_number}\n"
            f"Amount: ${fine.amount}\n"
            f"Due Date: "
            f"{fine.due_date}"
        )

        return self.send_message(user.phone, text)

    # =====================================================
    # PAYMENT REMINDER
    # =====================================================
    def payment_reminder(self, user, fine):
        text = (
            f"Reminder\n\n"
            f"Your fine "
            f"{fine.fine_number}"
            f" is due "
            f"{fine.due_date:%d-%m-%Y}"
        )

        return self.send_message(user.phone, text)

    # =====================================================
    # DISPUTE STATUS
    # =====================================================
    def dispute_status(self, user, dispute):
        text = (
            f"Dispute Update\n\n"
            f"Status: "
            f"{dispute.status}"
        )

        return self.send_message(user.phone, text)

    # =====================================================
    # DISPUTE STATUS
    # =====================================================
    def _post(self, payload):
        try:
            response = requests.post(
                self.url,
                headers=self.headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            return {
                "provider": "META_WHATSAPP",
                "message_id": result["messages"][0]["id"],
            }
        except Exception:
            return {
                "provider": self.PROVIDER,
                "message_id": f"SIM-WA-{uuid.uuid4().hex[:10].upper()}",
            }

    def send_template(self, phone, template_name, language="en_US"):
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language,
                },
            },
        }

        return self._post(payload)

    # =====================================================
    # Send PDF Receipt
    # =====================================================
    def send_document(self, phone, document_url, filename):
        payload = {
            "messaging_product": "whatsapp",
            "to": phone,
            "type": "document",
            "document": {
                "link": document_url,
                "filename": filename,
            },
        }

        response = requests.post(
            self.url,
            headers=self.headers,
            json=payload,
            timeout=30,
        )

        response.raise_for_status()

        result = response.json()

        return {
            "provider": self.PROVIDER,
            "message_id": result["messages"][0]["id"],
        }