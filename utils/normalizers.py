# =========================================================
# Digit Normalization
# =========================================================


DIGIT_TRANSLATION_TABLE = str.maketrans(
    "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
    "01234567890123456789",
)


def normalize_digits(value):
    """
    Convert Persian and Arabic digits
    to English ASCII digits.

    Example:

        ۰۹۱۲۳۴۵۶۷۸۹
        ->
        09123456789
    """

    if value is None:
        return value

    return str(value).translate(
        DIGIT_TRANSLATION_TABLE
    )


# =========================================================
# Single Line Text Normalization
# =========================================================


def normalize_single_line_text(value):
    """
    Normalize single-line text.

    - Strip leading/trailing whitespace
    - Collapse repeated whitespace

    Example:

        "  امیر   حسین  "
        ->
        "امیر حسین"
    """

    if value is None:
        return value

    return " ".join(
        str(value).strip().split()
    )