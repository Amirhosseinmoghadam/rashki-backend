import warnings

from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError

from PIL import (
    Image,
    UnidentifiedImageError,
)


# =========================================================
# Image Format Mapping
# =========================================================


IMAGE_EXTENSION_FORMAT_MAP = {
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".png": "PNG",
    ".webp": "WEBP",
}


# =========================================================
# Image Validator
# =========================================================


def validate_image(file):
    """
    Validate uploaded image.

    Checks:
        - File size
        - File extension
        - Real image content
        - Real image format
        - Extension / format consistency
        - Maximum pixel count
    """

    if not file:
        return file

    # =====================================================
    # 1. File Size
    # =====================================================

    max_size = getattr(
        settings,
        "MAX_IMAGE_UPLOAD_SIZE",
        10 * 1024 * 1024,
    )

    if file.size > max_size:
        max_size_mb = max_size / (
            1024 * 1024
        )

        raise ValidationError(
            f"حجم تصویر نباید بیشتر از "
            f"{max_size_mb:g} مگابایت باشد."
        )

    # =====================================================
    # 2. Extension
    # =====================================================

    extension = (
        Path(file.name)
        .suffix
        .lower()
    )

    allowed_extensions = {
        str(ext).lower()
        for ext in getattr(
            settings,
            "ALLOWED_IMAGE_EXTENSIONS",
            {
                ".jpg",
                ".jpeg",
                ".png",
                ".webp",
            },
        )
    }

    if extension not in allowed_extensions:

        allowed = ", ".join(
            ext.replace(".", "").upper()
            for ext in sorted(
                allowed_extensions
            )
        )

        raise ValidationError(
            f"فرمت تصویر مجاز نیست. "
            f"فرمت‌های مجاز: {allowed}"
        )

    # =====================================================
    # 3. Allowed Real Formats
    # =====================================================

    allowed_formats = {
        str(image_format).upper()
        for image_format in getattr(
            settings,
            "ALLOWED_IMAGE_FORMATS",
            {
                "JPEG",
                "PNG",
                "WEBP",
            },
        )
    }

    # =====================================================
    # 4. Maximum Pixel Count
    # =====================================================

    max_pixels = getattr(
        settings,
        "MAX_IMAGE_PIXEL_COUNT",
        40_000_000,
    )

    # =====================================================
    # 5. Validate Real Image
    # =====================================================

    try:

        file.seek(0)

        with warnings.catch_warnings():

            warnings.simplefilter(
                "error",
                Image.DecompressionBombWarning,
            )

            image = Image.open(file)

            actual_format = (
                image.format or ""
            ).upper()

            width, height = image.size

            # ---------------------------------------------
            # Real format
            # ---------------------------------------------

            if actual_format not in allowed_formats:
                raise ValidationError(
                    "فرمت واقعی تصویر مجاز نیست."
                )

            # ---------------------------------------------
            # Extension must match real format
            # ---------------------------------------------

            expected_format = (
                IMAGE_EXTENSION_FORMAT_MAP.get(
                    extension
                )
            )

            if (
                expected_format
                and actual_format
                != expected_format
            ):
                raise ValidationError(
                    "پسوند فایل با فرمت واقعی "
                    "تصویر مطابقت ندارد."
                )

            # ---------------------------------------------
            # Pixel count
            # ---------------------------------------------

            pixel_count = (
                width * height
            )

            if pixel_count > max_pixels:
                raise ValidationError(
                    "ابعاد تصویر بیش از حد مجاز است."
                )

            # ---------------------------------------------
            # Verify image structure
            # ---------------------------------------------

            image.verify()

    except ValidationError:
        raise

    except (
        UnidentifiedImageError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
        OSError,
        ValueError,
    ):
        raise ValidationError(
            "فایل آپلود شده یک تصویر معتبر نیست."
        )

    finally:

        try:
            file.seek(0)
        except (AttributeError, OSError):
            pass

    return file