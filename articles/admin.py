from django.contrib import admin

from .models import Article, ArticleCategory

# =========================================================
# Article Category
# =========================================================


@admin.register(ArticleCategory)
class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "is_active",
    )

    list_filter = ("is_active",)

    search_fields = (
        "name",
        "slug",
        "description",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    list_editable = ("is_active",)

    ordering = ("name",)


# =========================================================
# Article
# =========================================================


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "category",
        "author",
        "status",
        "is_featured",
        "reading_time",
        "view_count",
        "published_at",
        "created_at",
    )

    list_filter = (
        "status",
        "is_featured",
        "category",
        "published_at",
        "created_at",
    )

    search_fields = (
        "title",
        "slug",
        "excerpt",
        "content",
        "seo_title",
        "meta_description",
        "author__username",
        "author__first_name",
        "author__last_name",
    )

    prepopulated_fields = {
        "slug": ("title",),
    }

    autocomplete_fields = (
        "category",
        "author",
        "products",
        "motorcycles",
    )

    readonly_fields = (
        "view_count",
        "created_at",
        "updated_at",
    )

    list_editable = (
        "status",
        "is_featured",
    )

    date_hierarchy = "published_at"

    ordering = (
        "-published_at",
        "-created_at",
    )

    fieldsets = (
        (
            "اطلاعات اصلی",
            {
                "fields": (
                    "title",
                    "slug",
                    "category",
                    "author",
                    "cover_image",
                )
            },
        ),
        (
            "محتوا",
            {
                "fields": (
                    "excerpt",
                    "content",
                )
            },
        ),
        (
            "ارتباطات",
            {
                "fields": (
                    "products",
                    "motorcycles",
                )
            },
        ),
        (
            "وضعیت انتشار",
            {
                "fields": (
                    "status",
                    "is_featured",
                    "published_at",
                )
            },
        ),
        (
            "اطلاعات مطالعه",
            {
                "fields": (
                    "reading_time",
                    "view_count",
                )
            },
        ),
        (
            "SEO",
            {
                "fields": (
                    "seo_title",
                    "meta_description",
                )
            },
        ),
        (
            "اطلاعات سیستم",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
