from pathlib import Path
from uuid import uuid4

from django.utils import timezone

from utils.slug import persian_slugify


def upload_to(instance, filename):
    """
    Generate a clean and unique upload path.

    Example:

    categories/category/2026/09/
        لنت-ترمز-هوندا-125-a31f82c4d910.webp
    """

    # =====================================================
    # App / Model
    # =====================================================

    app_name = instance._meta.app_label
    model_name = instance._meta.model_name

    # =====================================================
    # Extension
    # =====================================================

    extension = Path(filename).suffix.lower()

    # =====================================================
    # SEO-friendly filename
    # =====================================================

    source_name = (
        getattr(instance, "slug", None)
        or getattr(instance, "name", None)
        or Path(filename).stem
    )

    filename_stem = persian_slugify(
        source_name
    )

    if not filename_stem:
        filename_stem = "image"

    filename_stem = filename_stem[:80].rstrip("-")

    # =====================================================
    # Unique suffix
    # =====================================================

    unique_suffix = uuid4().hex[:12]

    final_filename = (
        f"{filename_stem}-"
        f"{unique_suffix}"
        f"{extension}"
    )

    # =====================================================
    # Date based directory
    # =====================================================

    now = timezone.now()

    return (
        f"{app_name}/"
        f"{model_name}/"
        f"{now:%Y}/"
        f"{now:%m}/"
        f"{final_filename}"
    )