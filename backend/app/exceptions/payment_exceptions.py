class PaymentException(Exception):
    """Base Payment Exception"""
    pass


class PaymentNotFoundException(PaymentException):
    pass


class PaymentAlreadyCompletedException(PaymentException):
    pass


class InvalidPaymentException(PaymentException):
    pass


class PaymentGatewayException(PaymentException):
    pass


class RefundException(PaymentException):
    pass


class RefundAlreadyProcessedException(PaymentException):
    pass


class RefundNotAllowedException(PaymentException):
    """Refund requested for a payment the caller does not own."""
    pass


class PaymentNotRefundableException(PaymentException):
    """Payment is not in a refundable (PAID) state."""
    pass


class RefundAlreadyRequestedException(PaymentException):
    """An open refund already exists for this payment."""
    pass