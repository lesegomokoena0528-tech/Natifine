import os

from flask import current_app
from flask_mail import Message
from flask import render_template

from app.config.mail import mail


class EmailService:

    PROVIDER = "SMTP"

    # ==========================================================
    # SEND EMAIL
    # ==========================================================

    def send(self, notification):

        message = Message(

            subject=notification.title,

            recipients=[notification.recipient]

        )

        message.body = notification.message

        message.html = render_template(

            "email/base.html",

            title=notification.title,

            message=notification.message

        )

        mail.send(message)

        return {

            "provider": self.PROVIDER,

            "message_id": None

        }

    # ==========================================================
    # SEND HTML TEMPLATE
    # ==========================================================

    def send_template(

            self,

            recipient,

            subject,

            template,

            **context

    ):

        message = Message(

            subject=subject,

            recipients=[recipient]

        )

        message.html = render_template(

            template,

            **context

        )

        mail.send(message)

        return {

            "provider": self.PROVIDER,

            "message_id": None

        }

    # ==========================================================
    # SEND RECEIPT
    # ==========================================================

    def send_receipt(

            self,

            recipient,

            receipt_path,

            payment

    ):

        message = Message(

            subject="Payment Receipt",

            recipients=[recipient]

        )

        message.html = render_template(

            "email/payment_receipt.html",

            payment=payment

        )

        with open(receipt_path, "rb") as attachment:

            message.attach(

                filename=os.path.basename(receipt_path),

                content_type="application/pdf",

                data=attachment.read()

            )

        mail.send(message)

        return {

            "provider": self.PROVIDER,

            "message_id": None

        }

    # ==========================================================
    # WELCOME EMAIL
    # ==========================================================

    def welcome(

            self,

            user

    ):

        return self.send_template(

            user.email,

            "Welcome",

            "email/welcome.html",

            user=user

        )

    # ==========================================================
    # PASSWORD RESET
    # ==========================================================

    def password_reset(

            self,

            user,

            reset_link

    ):

        return self.send_template(

            user.email,

            "Reset Your Password",

            "email/password_reset.html",

            user=user,

            reset_link=reset_link

        )

    # ==========================================================
    # FINE ISSUED
    # ==========================================================

    def fine_issued(

            self,

            user,

            fine

    ):

        return self.send_template(

            user.email,

            "Traffic Fine Issued",

            "email/fine_issued.html",

            user=user,

            fine=fine

        )

    # ==========================================================
    # DISPUTE STATUS
    # ==========================================================

    def dispute_status(

            self,

            user,

            dispute

    ):

        return self.send_template(

            user.email,

            "Dispute Update",

            "email/dispute_status.html",

            user=user,

            dispute=dispute

        )