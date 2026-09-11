ORDER_CREATE_EXAMPLE = {
    "address_id": 12,
    "shipping_method_id": 1,
    "accept_terms": True,
    "customer_note": (
        "لطفاً قبل از ارسال تماس بگیرید."
    ),
}
# =========================================================
# Order Cancellation
# =========================================================


OrderCancellationRequestExample = {
    "reason": "customer_request",
    "description": (
        "مشتری درخواست لغو سفارش را ثبت کرده است."
    ),
}