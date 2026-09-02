# =========================================================
# Motorcycle Brand Create
# =========================================================


MOTORCYCLE_BRAND_CREATE_EXAMPLE = {
    "name": "هوندا",
    "is_active": True,
}


# =========================================================
# Motorcycle Brand Update
# =========================================================


MOTORCYCLE_BRAND_UPDATE_EXAMPLE = {
    "name": "Honda",
    "is_active": True,
}


# =========================================================
# Motorcycle Brand Partial Update
# =========================================================


MOTORCYCLE_BRAND_PARTIAL_UPDATE_EXAMPLE = {
    "is_active": False,
}


# =========================================================
# Motorcycle Model Create
# =========================================================


MOTORCYCLE_MODEL_CREATE_EXAMPLE = {
    "brand": 1,
    "name": "CG 125",
    "production_start_year": 2010,
    "production_end_year": None,
    "engine_volume": 125,
    "description": (
        "مدل CG 125 مناسب انتخاب "
        "قطعات سازگار فروشگاه."
    ),
    "is_active": True,
}


# =========================================================
# Motorcycle Model Update
# =========================================================


MOTORCYCLE_MODEL_UPDATE_EXAMPLE = {
    "brand": 1,
    "name": "CG 125",
    "production_start_year": 2010,
    "production_end_year": None,
    "engine_volume": 125,
    "description": (
        "اطلاعات بروزرسانی‌شده "
        "مدل CG 125."
    ),
    "is_active": True,
}


# =========================================================
# Motorcycle Model Partial Update
# =========================================================


MOTORCYCLE_MODEL_PARTIAL_UPDATE_EXAMPLE = {
    "engine_volume": 125,
    "is_active": True,
}