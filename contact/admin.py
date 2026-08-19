from django.contrib import admin

from .models import ContactRequest


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "first_name",
        "last_name",
        "phone_number",
        "subject_display",
        "is_read",
        "created_at",
    )

    list_filter = (
        "subject",
        "is_read",
        "created_at",
    )

    search_fields = (
        "first_name",
        "last_name",
        "phone_number",
        "description",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_editable = (
        "is_read",
    )

    ordering = (
        "-created_at",
    )

    date_hierarchy = "created_at"

    list_per_page = 25

    fieldsets = (
        (
            "اطلاعات مشتری",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "phone_number",
                ),
            },
        ),
        (
            "درخواست",
            {
                "fields": (
                    "subject",
                    "description",
                ),
            },
        ),
        (
            "وضعیت",
            {
                "fields": (
                    "is_read",
                ),
            },
        ),
        (
            "اطلاعات سیستم",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    @admin.display(
        description="موضوع درخواست",
        ordering="subject",
    )
    def subject_display(self, obj):
        return obj.get_subject_display()