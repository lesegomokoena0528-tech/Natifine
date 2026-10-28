from twilio.rest import Client

from app.config.sms import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_PHONE_NUMBER
)


import uuid


class SMSService:

    PROVIDER = "SIMULATED_SMS"

    def __init__(self):
        self.client = None
        if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
            try:
                self.client = Client(
                    TWILIO_ACCOUNT_SID,
                    TWILIO_AUTH_TOKEN
                )
            except Exception:
                self.client = None

    # ==========================================================
    # SEND GENERIC SMS
    # ==========================================================

    def send(self, notification):

        if self.client and TWILIO_PHONE_NUMBER:
            try:
                message = self.client.messages.create(
                    body=notification.message,
                    from_=TWILIO_PHONE_NUMBER,
                    to=notification.recipient
                )
                return {
                    "provider": "TWILIO",
                    "message_id": message.sid
                }
            except Exception:
                pass

        return {
            "provider": self.PROVIDER,
            "message_id": f"SIM-SMS-{uuid.uuid4().hex[:10].upper()}"
        }

    # ==========================================================
    # SEND CUSTOM MESSAGE
    # ==========================================================

    def send_message(

            self,

            phone,

            message

    ):

        if self.client and TWILIO_PHONE_NUMBER:
            try:
                sms = self.client.messages.create(
                    body=message,
                    from_=TWILIO_PHONE_NUMBER,
                    to=phone
                )
                return {
                    "provider": "TWILIO",
                    "message_id": sms.sid
                }
            except Exception:
                pass
        return {
            "provider": self.PROVIDER,
            "message_id": f"SIM-SMS-{uuid.uuid4().hex[:10].upper()}"
        }

    # ==========================================================
    # OTP
    # ==========================================================

    def send_otp(

            self,

            phone,

            otp

    ):

        message = (

            f"Your verification code is "

            f"{otp}. "

            "Do not share this code."

        )

        return self.send_message(

            phone,

            message

        )

    # ==========================================================
    # PAYMENT RECEIVED
    # ==========================================================

    def payment_received(

            self,

            user,

            payment

    ):

        message = (

            f"Payment received. "

            f"Reference: "

            f"{payment.payment_reference}"

        )

        return self.send_message(

            user.phone,

            message

        )

    # ==========================================================
    # FINE ISSUED
    # ==========================================================

    def fine_issued(

            self,

            user,

            fine

    ):

        message = (

            f"Traffic Fine "

            f"{fine.fine_number} "

            f"Amount: {fine.amount}"

        )

        return self.send_message(

            user.phone,

            message

        )

    # ==========================================================
    # PAYMENT REMINDER
    # ==========================================================

    def payment_reminder(

            self,

            user,

            fine

    ):

        message = (

            f"Reminder: "

            f"Fine "

            f"{fine.fine_number} "

            f"is due on "

            f"{fine.due_date:%d-%m-%Y}."

        )

        return self.send_message(

            user.phone,

            message

        )

    # ==========================================================
    # DISPUTE STATUS
    # ==========================================================

    def dispute_status(

            self,

            user,

            dispute

    ):

        message = (

            f"Your dispute "

            f"status is "

            f"{dispute.status}."

        )

        return self.send_message(

            user.phone,

            message

        )

    # ==========================================================
    # PASSWORD RESET
    # ==========================================================

    def password_reset(

            self,

            user,

            code

    ):

        message = (

            f"Password Reset Code: "

            f"{code}"

        )

        return self.send_message(

            user.phone,

            message

        )

    # ==========================================================
    # BULK SMS
    # ==========================================================

    def bulk_send(

            self,

            recipients,

            message

    ):

        responses = []

        for phone in recipients:

            responses.append(

                self.send_message(

                    phone,

                    message

                )

            )

        return responses