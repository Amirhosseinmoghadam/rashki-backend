from django.core.exceptions import ValidationError
from django.db import models

from utils.slug import generate_unique_slug
from utils.upload import upload_to
from utils.validators import validate_image


class Category(models.Model):

    name = models.CharField(
        max_length=150,
        verbose_name="نام دسته‌بندی",
    )

    slug = models.SlugField(
        max_length=180,
        unique=True,
        allow_unicode=True,
        blank=True,
        verbose_name="اسلاگ",
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="دسته والد",
    )

    image = models.ImageField(
        upload_to=upload_to,
        validators=[
            validate_image,
        ],
        blank=True,
        null=True,
        verbose_name="تصویر",
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات",
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ["name"]

    # =====================================================
    # Parent Validation
    # =====================================================

    def validate_parent_hierarchy(self):
        """
        Prevent circular category hierarchy.

        Invalid examples:

            A -> A

            A -> B -> C -> A
        """

        if not self.parent_id:
            return

        # -------------------------------------------------
        # Direct self-reference
        # -------------------------------------------------

        if (
            self.pk
            and self.parent_id == self.pk
        ):
            raise ValidationError(
                {
                    "parent": (
                        "یک دسته‌بندی نمی‌تواند "
                        "والد خودش باشد."
                    )
                }
            )

        # -------------------------------------------------
        # Circular hierarchy
        # -------------------------------------------------

        parent = self.parent

        visited = set()

        while parent is not None:

            if parent.pk in visited:
                raise ValidationError(
                    {
                        "parent": (
                            "ساختار دسته‌بندی "
                            "دارای حلقه است."
                        )
                    }
                )

            visited.add(parent.pk)

            if (
                self.pk
                and parent.pk == self.pk
            ):
                raise ValidationError(
                    {
                        "parent": (
                            "انتخاب این دسته والد "
                            "باعث ایجاد حلقه می‌شود."
                        )
                    }
                )

            parent = parent.parent

    # =====================================================
    # Save
    # =====================================================

    def save(
        self,
        *args,
        **kwargs,
    ):

        self.validate_parent_hierarchy()

        # Generate slug only once.
        #
        # Changing name later must NOT
        # automatically change the URL.
        if not self.slug:

            self.slug = generate_unique_slug(
                instance=self,
                value=self.name,
            )

        super().save(
            *args,
            **kwargs,
        )

    # =====================================================
    # String Representation
    # =====================================================

    def __str__(self):

        if self.parent:
            return (
                f"{self.parent} → "
                f"{self.name}"
            )

        return self.name