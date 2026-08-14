import requests
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from payments.models import Payment

HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
}


# ============================================================
# 1️⃣ Request – ایجاد پرداخت
# ============================================================
def request_payment(order, request):
    callback_url = request.build_absolute_uri(reverse("payments:verify"))

    data = {
        "merchant_id": settings.ZARINPAL_CONFIG["MERCHANT"],
        "amount": order.total_price * 10,  # تومان ➜ ریال
        "callback_url": callback_url,
        "description": f"پرداخت سفارش #{order.id}",
        "metadata": {
            "email": order.user.email,
        },
    }

    response = requests.post(
        settings.ZARINPAL_CONFIG["REQUEST_URL"],
        json=data,
        headers=HEADERS,
        timeout=15,
    )

    result = response.json()

    if result.get("data") and result["data"].get("authority"):
        payment = Payment.objects.create(
            user=order.user,
            order=order,
            amount=order.total_price,
            authority=result["data"]["authority"],
            status=Payment.PaymentStatus.PENDING,
        )

        return {
            "success": True,
            "payment_url": settings.ZARINPAL_CONFIG["STARTPAY_URL"].format(
                authority=payment.authority
            ),
        }

    return {"success": False, "error": result.get("errors")}


# ============================================================
# 2️⃣ Verify – تأیید پرداخت
# ============================================================
def verify_payment(authority):
    payment = Payment.objects.filter(authority=authority).first()
    if not payment:
        return {"success": False, "message": "پرداخت یافت نشد"}

    data = {
        "merchant_id": settings.ZARINPAL_CONFIG["MERCHANT"],
        "amount": payment.amount * 10,
        "authority": authority,
    }

    response = requests.post(
        settings.ZARINPAL_CONFIG["VERIFY_URL"],
        json=data,
        headers=HEADERS,
        timeout=15,
    )

    result = response.json()

    if result.get("data") and result["data"]["code"] == 100:
        payment.status = Payment.PaymentStatus.SUCCESS
        payment.ref_id = result["data"]["ref_id"]
        payment.card_pan = result["data"].get("card_pan")
        payment.card_hash = result["data"].get("card_hash")
        payment.save(update_fields=["status", "ref_id", "card_pan", "card_hash"])

        return {"success": True, "ref_id": payment.ref_id}

    payment.status = Payment.PaymentStatus.FAILED
    payment.save(update_fields=["status"])
    return {"success": False, "error": result}


# ============================================================
# 3️⃣ Inquiry – استعلام پرداخت
# ============================================================
def inquiry_payment(authority):
    data = {
        "merchant_id": settings.ZARINPAL_CONFIG["MERCHANT"],
        "authority": authority,
    }

    response = requests.post(
        settings.ZARINPAL_CONFIG["INQUIRY_URL"],
        json=data,
        headers=HEADERS,
        timeout=15,
    )

    return response.json()


# ============================================================
# 4️⃣ Unverified – پرداخت‌های تأیید نشده
# ============================================================
def unverified_payments():
    data = {
        "merchant_id": settings.ZARINPAL_CONFIG["MERCHANT"],
    }

    response = requests.post(
        settings.ZARINPAL_CONFIG["UNVERIFIED_URL"],
        json=data,
        headers=HEADERS,
        timeout=15,
    )

    return response.json()


# ============================================================
# 5️⃣ Reverse – لغو تراکنش
# ============================================================
def reverse_payment(authority):
    data = {
        "merchant_id": settings.ZARINPAL_CONFIG["MERCHANT"],
        "authority": authority,
    }

    response = requests.post(
        settings.ZARINPAL_CONFIG["REVERSE_URL"],
        json=data,
        headers=HEADERS,
        timeout=15,
    )

    return response.json()


# ============================================================
# 6️⃣ Refund – بازگشت وجه
# ============================================================
def refund_payment(authority, amount=None):
    data = {
        "merchant_id": settings.ZARINPAL_CONFIG["MERCHANT"],
        "authority": authority,
    }

    if amount:
        data["amount"] = amount * 10  # تومان ➜ ریال

    response = requests.post(
        settings.ZARINPAL_CONFIG["REFUND_URL"],
        json=data,
        headers=HEADERS,
        timeout=15,
    )

    return response.json()


# ============================================================
# 7️⃣ Transaction List – لیست تراکنش‌ها
# ============================================================
def transaction_list(from_date=None, to_date=None):
    data = {
        "merchant_id": settings.ZARINPAL_CONFIG["MERCHANT"],
    }

    if from_date:
        data["from_date"] = from_date
    if to_date:
        data["to_date"] = to_date

    response = requests.post(
        settings.ZARINPAL_CONFIG["TRANSACTION_URL"],
        json=data,
        headers=HEADERS,
        timeout=15,
    )

    return response.json()
