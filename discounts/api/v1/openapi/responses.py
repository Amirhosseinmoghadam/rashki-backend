DiscountValidateSuccess = {
    "success": True,
    "message": "کد تخفیف معتبر است.",
    "data": {
        "code": "OFF20",
        "discount_type": "percentage",
        "scope": "all",
        "subtotal_toman": 2000000,
        "eligible_subtotal_toman": 2000000,
        "discount_amount_toman": 300000,
        "final_subtotal_toman": 1700000,
        "start_at": "2026-09-04T12:00:00Z",
        "end_at": "2026-10-04T12:00:00Z",
    },
}


DiscountInvalidCode = {
    "success": False,
    "message": "کد تخفیف معتبر نیست.",
    "errors": None,
}


DiscountExpired = {
    "success": False,
    "message": "این کد تخفیف منقضی شده است.",
    "errors": None,
}


DiscountMinimumOrder = {
    "success": False,
    "message": (
        "حداقل مبلغ سفارش برای استفاده "
        "از این کد 1,000,000 تومان است."
    ),
    "errors": None,
}


DiscountUsageLimitReached = {
    "success": False,
    "message": (
        "ظرفیت استفاده از این "
        "کد تخفیف به پایان رسیده است."
    ),
    "errors": None,
}


DiscountUserLimitReached = {
    "success": False,
    "message": (
        "شما به حداکثر تعداد "
        "استفاده از این کد رسیده‌اید."
    ),
    "errors": None,
}


DiscountNoEligibleProduct = {
    "success": False,
    "message": (
        "هیچ‌یک از محصولات سبد "
        "مشمول این کد تخفیف نیستند."
    ),
    "errors": None,
}


DiscountDeleteSuccess = {
    "success": True,
    "message": "کد تخفیف با موفقیت حذف شد.",
    "data": None,
}


DiscountDeleteProtected = {
    "success": False,
    "message": (
        "این کد دارای سابقه استفاده است "
        "و قابل حذف نیست. آن را غیرفعال کنید."
    ),
    "errors": None,
}


AuthenticationRequired = {
    "detail": (
        "Authentication credentials "
        "were not provided."
    )
}


PermissionDenied = {
    "detail": (
        "You do not have permission "
        "to perform this action."
    )
}