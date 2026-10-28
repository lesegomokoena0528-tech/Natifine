from enum import Enum


class PaymentGateway(Enum):

    PAYFAST = "PAYFAST"

    OZOW = "OZOW"

    PEACH = "PEACH"

    STRIPE = "STRIPE"

    PAYPAL = "PAYPAL"

    INTERNAL = "INTERNAL"