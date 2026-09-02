import re
import unicodedata

from django.utils.text import slugify


# =========================================================
# Persian Character Normalization
# =========================================================


CHARACTER_TRANSLATION = str.maketrans(
    {
        # Arabic -> Persian
        "ي": "ی",
        "ى": "ی",
        "ك": "ک",

        # Persian digits -> English digits
        "۰": "0",
        "۱": "1",
        "۲": "2",
        "۳": "3",
        "۴": "4",
        "۵": "5",
        "۶": "6",
        "۷": "7",
        "۸": "8",
        "۹": "9",

        # Arabic digits -> English digits
        "٠": "0",
        "١": "1",
        "٢": "2",
        "٣": "3",
        "٤": "4",
        "٥": "5",
        "٦": "6",
        "٧": "7",
        "٨": "8",
        "٩": "9",
    }
)


ARABIC_DIACRITICS_REGEX = re.compile(
    r"[\u064B-\u065F\u0670\u06D6-\u06ED]"
)

MULTIPLE_HYPHENS_REGEX = re.compile(r"-{2,}")


# =========================================================
# Normalize Persian Text
# =========================================================


def normalize_persian_text(value):
    """
    Normalize Persian text before generating a slug.

    Examples:
        ي -> ی
        ك -> ک
        ۱۲۵ -> 125
        ZWNJ -> Space
    """

    if not value:
        return ""

    value = str(value).strip()

    # Unicode normalization
    value = unicodedata.normalize(
        "NFKC",
        value,
    )

    # Arabic/Persian character normalization
    value = value.translate(
        CHARACTER_TRANSLATION,
    )

    # Remove Arabic diacritics
    value = ARABIC_DIACRITICS_REGEX.sub(
        "",
        value,
    )

    # Replace Persian half-space with normal space
    value = value.replace(
        "\u200c",
        " ",
    )

    # Zero-width joiner
    value = value.replace(
        "\u200d",
        " ",
    )

    # Remove Tatweel
    value = value.replace(
        "ـ",
        "",
    )

    return value.strip()


# =========================================================
# Persian Slugify
# =========================================================


def persian_slugify(value):
    """
    Generate an SEO-friendly Persian slug.

    Example:
        'لنت ترمز هوندا ۱۲۵'
        ->
        'لنت-ترمز-هوندا-125'
    """

    value = normalize_persian_text(value)

    slug = slugify(
        value,
        allow_unicode=True,
    )

    # Google recommends hyphens instead of underscores
    slug = slug.replace(
        "_",
        "-",
    )

    # Remove duplicate hyphens
    slug = MULTIPLE_HYPHENS_REGEX.sub(
        "-",
        slug,
    )

    return slug.strip("-")


# =========================================================
# Unique Slug Generator
# =========================================================


def generate_unique_slug(
    instance,
    value,
    slug_field="slug",
):
    """
    Generate a unique SEO-friendly slug for a model instance.

    Example:
        لنت-ترمز
        لنت-ترمز-2
        لنت-ترمز-3
    """

    model_class = instance.__class__

    field = instance._meta.get_field(
        slug_field,
    )

    max_length = field.max_length or 255

    base_slug = persian_slugify(value)

    if not base_slug:
        base_slug = "item"

    # Respect database field max_length
    base_slug = base_slug[
        :max_length
    ].rstrip("-")

    queryset = model_class._default_manager.all()

    # When updating an existing object,
    # exclude itself from uniqueness check.
    if instance.pk:
        queryset = queryset.exclude(
            pk=instance.pk,
        )

    candidate = base_slug

    counter = 2

    while queryset.filter(
        **{
            slug_field: candidate,
        }
    ).exists():

        suffix = f"-{counter}"

        available_length = (
            max_length - len(suffix)
        )

        trimmed_slug = base_slug[
            :available_length
        ].rstrip("-")

        candidate = (
            f"{trimmed_slug}{suffix}"
        )

        counter += 1

    return candidate