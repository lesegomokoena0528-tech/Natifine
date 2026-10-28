import uuid
from decimal import Decimal


class PaymentGatewayService:
    """
    Simulation payment gateway abstraction for NatiFine SA academic prototype.
    Supports simulated PayFast, Ozow, Card, and Instant EFT transactions.
    """

    PROVIDER = "MOCK_GATEWAY"

    def create_payment(self, payment):
        """
        Creates a simulated payment checkout session.
        """
        gateway_ref = f"GW-{uuid.uuid4().hex[:10].upper()}"
        return {
            "success": True,
            "provider": self.PROVIDER,
            "gateway_reference": gateway_ref,
            "payment_reference": payment.payment_reference,
            "payment_url": f"/payments/simulate/{payment.payment_reference}"
        }

    def process_payment(
        self,
        amount: Decimal,
        payment_method: str,
        reference: str,
        payer=None
    ):
        """
        Processes simulated payment transaction.
        """
        return {
            "success": True,
            "provider": self.PROVIDER,
            "transaction_id": f"TXN-{uuid.uuid4().hex[:12].upper()}",
            "payment_reference": reference,
            "gateway_reference": f"GW-{uuid.uuid4().hex[:10].upper()}",
            "amount": float(amount),
            "payment_method": payment_method,
            "status": "SUCCESS"
        }

    def verify_payment(self, payment_or_ref):
        """
        Verifies payment status with simulated gateway.
        """
        txn_id = getattr(payment_or_ref, "transaction_id", None) or f"TXN-{uuid.uuid4().hex[:12].upper()}"
        gw_ref = getattr(payment_or_ref, "gateway_reference", None) or f"GW-{uuid.uuid4().hex[:10].upper()}"

        return {
            "success": True,
            "transaction_id": txn_id,
            "gateway_reference": gw_ref,
            "status": "SUCCESS"
        }

    def refund(self, payment):
        """
        Processes refund on the simulated gateway.
        """
        return {
            "success": True,
            "transaction_id": payment.transaction_id or f"TXN-{uuid.uuid4().hex[:12].upper()}",
            "status": "REFUNDED"
        }

    def refund_payment(
        self,
        transaction_id: str,
        amount: Decimal
    ):
        return {
            "success": True,
            "transaction_id": transaction_id,
            "refund_amount": float(amount),
            "status": "REFUNDED"
        }