# =========================================================
# Payment Start
# =========================================================


PAYMENT_START_ZARINPAL_EXAMPLE = {
    "order_number": (
        "RK-20260909-A84F123B"
    ),
    "provider": "zarinpal",
}


PAYMENT_START_TCART_EXAMPLE = {
    "order_number": (
        "RK-20260909-A84F123B"
    ),
    "provider": "tcart",
}


# =========================================================
# ZarinPal Callback
# =========================================================


ZARINPAL_CALLBACK_EXAMPLE = {
    "Authority": (
        "A00000000000000000000000000000000001"
    ),
    "Status": "OK",
}


# =========================================================
# Refund Create
# =========================================================


PAYMENT_REFUND_FULL_EXAMPLE = {
    "order_number": (
        "RK-20260909-A84F123B"
    ),
    "amount_toman": None,
    "reason": "customer_request",
    "description": (
        "لغو سفارش و بازپرداخت کامل مبلغ."
    ),
}


PAYMENT_REFUND_PARTIAL_EXAMPLE = {
    "order_number": (
        "RK-20260909-A84F123B"
    ),
    "amount_toman": 500000,
    "reason": "partial_refund",
    "description": (
        "بازپرداخت بخشی از مبلغ سفارش."
    ),
}