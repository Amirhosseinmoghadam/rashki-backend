"""
ابزار تست ترمینالی سرویس زرین‌پال
=================================

با اجرای این فایل، یک منوی ترمینالی نمایش داده می‌شود.

مثلاً:

    python test_zarinpal.py

سپس:

    1. ایجاد درخواست پرداخت
    2. ساخت URL از Authority
    3. Verify پرداخت
    4. Inquiry
    5. تراکنش‌های Verify نشده
    6. Reverse
    7. Refund
    8. لیست تراکنش‌ها
    9. محاسبه کارمزد
    0. خروج
"""

import os
import pprint
import django

# ============================================================
# تنظیم Django
# ============================================================

# ------------------------------------------------------------
# این مقدار را با مسیر واقعی settings پروژه خودت عوض کن.
#
# مثلاً اگر ساختار پروژه:
#
# project/
# ├── config/
# │   ├── settings.py
# │   └── urls.py
# ├── payments/
# └── manage.py
#
# باید بنویسی:
#
# DJANGO_SETTINGS_MODULE = "config.settings"
# ------------------------------------------------------------
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "core.settings",
)

django.setup()

# ============================================================
# Import سرویس
# ============================================================

from utils.zarinpal import (
    ZarinPalService,
    ZarinPalServiceError,
)

# ============================================================
# ساخت Client
# ============================================================

try:

    zarinpal = ZarinPalService()

except Exception as exc:

    print("\n❌ خطا در ساخت سرویس زرین‌پال:")
    print(exc)

    raise SystemExit(1)


# ============================================================
# تابع نمایش خروجی
# ============================================================


def print_result(result):
    """
    خروجی Dictionary مربوط به SDK را به صورت خوانا چاپ می‌کند.
    """

    print("\n")
    print("=" * 70)
    print("نتیجه:")
    print("=" * 70)

    pprint.pprint(
        result,
        sort_dicts=False,
        width=120,
    )

    print("=" * 70)


# ============================================================
# 1. ایجاد درخواست پرداخت
# ============================================================


def test_create_payment():
    """
    تست ایجاد Payment.

    توجه:
    این متد واقعاً به زرین‌پال درخواست ارسال می‌کند.
    """

    print("\n")
    print("🔵 ایجاد درخواست پرداخت")

    amount = int(input("مبلغ را وارد کنید: "))

    description = input("توضیحات پرداخت: ")

    callback_url = input("Callback URL: ")

    mobile = input("شماره موبایل (اختیاری): ").strip()

    email = input("ایمیل (اختیاری): ").strip()

    currency = input("Currency [IRR/IRT] (اختیاری): ").strip().upper()

    if not currency:
        currency = None

    if not mobile:
        mobile = None

    if not email:
        email = None

    try:

        result = zarinpal.create_payment_and_get_url(
            amount=amount,
            callback_url=callback_url,
            description=description,
            mobile=mobile,
            email=email,
            currency=currency,
        )

        print_result(result)

        print("\n✅ Authority:")
        print(result["authority"])

        print("\n🌐 Payment URL:")
        print(result["payment_url"])

        print("\n⚠️ این URL را می‌توانی در مرورگر باز کنی.")

    except ZarinPalServiceError as exc:

        print("\n❌ خطای زرین‌پال:")
        print(exc)


# ============================================================
# 2. ساخت Payment URL
# ============================================================


def test_payment_url():
    """
    اگر Authority قبلاً داری،
    بدون ایجاد تراکنش جدید URL پرداخت را بساز.
    """

    print("\n")
    print("🔵 ساخت Payment URL")

    authority = input("Authority: ").strip()

    try:

        url = zarinpal.get_payment_url(authority)

        print("\n🌐 Payment URL:")
        print(url)

    except ZarinPalServiceError as exc:

        print("\n❌ خطا:")
        print(exc)


# ============================================================
# 3. Verify
# ============================================================


def test_verify():
    """
    Verify یک پرداخت.

    توجه بسیار مهم:

    در پروژه واقعی amount باید از دیتابیس خوانده شود.

    اینجا برای تست دستی از کاربر می‌گیریم.
    """

    print("\n")
    print("🟢 Verify Payment")

    authority = input("Authority: ").strip()

    amount = int(input("مبلغ تراکنش: "))

    try:

        result = zarinpal.verify_payment(
            authority=authority,
            amount=amount,
        )

        print_result(result)

        print("\n🔍 آیا Verify موفق بود؟")

        if zarinpal.is_verified(result):

            print("✅ بله")

            print("\nRef ID:")

            print(zarinpal.get_ref_id(result))

        else:

            print("❌ خیر")

    except ZarinPalServiceError as exc:

        print("\n❌ خطا:")
        print(exc)


# ============================================================
# 4. Inquiry
# ============================================================


def test_inquiry():
    """
    استعلام تراکنش.
    """

    print("\n")
    print("🔎 Inquiry Payment")

    authority = input("Authority: ").strip()

    try:

        result = zarinpal.inquire_payment(authority)

        print_result(result)

    except ZarinPalServiceError as exc:

        print("\n❌ خطا:")
        print(exc)


# ============================================================
# 5. Unverified
# ============================================================


def test_unverified():
    """
    دریافت تراکنش‌های Verify نشده.
    """

    print("\n")
    print("🟡 Unverified Payments")

    try:

        result = zarinpal.get_unverified_payments()

        print_result(result)

    except ZarinPalServiceError as exc:

        print("\n❌ خطا:")
        print(exc)


# ============================================================
# 6. Reverse
# ============================================================


def test_reverse():
    """
    Reverse تراکنش.
    """

    print("\n")
    print("🔴 Reverse Payment")

    authority = input("Authority: ").strip()

    confirmation = input("آیا مطمئن هستید؟ [y/N]: ").strip().lower()

    if confirmation != "y":

        print("\n❌ عملیات لغو شد.")

        return

    try:

        result = zarinpal.reverse_payment(authority)

        print_result(result)

    except ZarinPalServiceError as exc:

        print("\n❌ خطا:")
        print(exc)


# ============================================================
# 7. Refund
# ============================================================


def test_refund():
    """
    Refund تراکنش.
    """

    print("\n")
    print("💰 Refund Payment")

    session_id = input("Session ID: ").strip()

    amount = int(input("مبلغ Refund: "))

    description = input("توضیحات: ").strip()

    method = input("Method [CARD/PAYA]: ").strip().upper()

    reason = input("Reason: ").strip()

    confirmation = input("\n⚠️ آیا مطمئن هستید؟ [y/N]: ").strip().lower()

    if confirmation != "y":

        print("\n❌ عملیات لغو شد.")

        return

    try:

        result = zarinpal.refund_payment(
            session_id=session_id,
            amount=amount,
            description=description,
            method=method,
            reason=reason,
        )

        print_result(result)

    except ZarinPalServiceError as exc:

        print("\n❌ خطا:")
        print(exc)


# ============================================================
# 8. Transactions List
# ============================================================


def test_transactions():
    """
    دریافت لیست تراکنش‌ها.
    """

    print("\n")
    print("📋 Transactions List")

    terminal_id = input("Terminal ID: ").strip()

    filter_status = (
        input("Filter [PAID/VERIFIED/TRASH/ACTIVE/REFUNDED] " "(اختیاری): ")
        .strip()
        .upper()
    )

    offset_input = input("Offset (خالی = بدون مقدار): ").strip()

    limit_input = input("Limit (خالی = بدون مقدار): ").strip()

    filter_status = filter_status if filter_status else None

    offset = int(offset_input) if offset_input else None

    limit = int(limit_input) if limit_input else None

    try:

        result = zarinpal.list_transactions(
            terminal_id=terminal_id,
            filter_status=filter_status,
            offset=offset,
            limit=limit,
        )

        print_result(result)

    except ZarinPalServiceError as exc:

        print("\n❌ خطا:")
        print(exc)


# ============================================================
# 9. Fee Calculation
# ============================================================


def test_fee():
    """
    محاسبه کارمزد.
    """

    print("\n")
    print("🧮 محاسبه کارمزد")

    amount = int(input("مبلغ: "))

    currency = input("Currency [IRR/IRT]: ").strip().upper()

    try:

        result = zarinpal.calculate_fee(
            amount=amount,
            currency=currency,
        )

        print_result(result)

    except ZarinPalServiceError as exc:

        print("\n❌ خطا:")
        print(exc)


# ============================================================
# نمایش منو
# ============================================================


def show_menu():
    """
    نمایش منوی اصلی.
    """

    print("\n")

    print("=" * 70)

    print("        ZARINPAL SERVICE TEST CONSOLE")

    print("=" * 70)

    print("1. ایجاد درخواست پرداخت")

    print("2. ساخت Payment URL از Authority")

    print("3. Verify Payment")

    print("4. Inquiry Payment")

    print("5. دریافت Unverified Payments")

    print("6. Reverse Payment")

    print("7. Refund Payment")

    print("8. دریافت لیست تراکنش‌ها")

    print("9. محاسبه کارمزد")

    print("0. خروج")

    print("=" * 70)


# ============================================================
# Main
# ============================================================


def main():

    while True:

        show_menu()

        choice = input("\nانتخاب شما: ").strip()

        try:

            if choice == "1":

                test_create_payment()

            elif choice == "2":

                test_payment_url()

            elif choice == "3":

                test_verify()

            elif choice == "4":

                test_inquiry()

            elif choice == "5":

                test_unverified()

            elif choice == "6":

                test_reverse()

            elif choice == "7":

                test_refund()

            elif choice == "8":

                test_transactions()

            elif choice == "9":

                test_fee()

            elif choice == "0":

                print("\n👋 خروج از برنامه...")

                break

            else:

                print("\n❌ گزینه نامعتبر است.")

        except ValueError:

            print("\n❌ مقدار عددی نامعتبر است.")

        except KeyboardInterrupt:

            print("\n\n👋 برنامه متوقف شد.")

            break

        except Exception as exc:

            print("\n❌ خطای غیرمنتظره:")

            print(exc)


# ============================================================
# اجرای برنامه
# ============================================================

if __name__ == "__main__":

    main()
