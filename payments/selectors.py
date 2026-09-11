from .models import PaymentAttempt


# =========================================================
# Payment QuerySet
# =========================================================


def get_payment_attempt_queryset():

    return (
        PaymentAttempt.objects
        .select_related(
            "order",
            "order__user",
        )
    )


# =========================================================
# User Attempts
# =========================================================


def get_user_payment_attempts(
    user,
):

    return (
        get_payment_attempt_queryset()
        .filter(
            order__user=user
        )
        .order_by(
            "-created_at"
        )
    )