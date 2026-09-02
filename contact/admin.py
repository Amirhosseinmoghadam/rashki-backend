from django.contrib import admin

from .models import ContactRequest


# =========================================================
# Contact Request Admin
# =========================================================


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):

    # =====================================================
    # List
    # =====================================================

    list_display = (
        "id",
        "first_name",
        "last_name",
        "phone_number",
        "subject_display",
        "is_read",
        "created_at",
    )

    list_display_links = (
        "id",
        "first_name",
        "last_name",
    )

    # =====================================================
    # Filters
    # =====================================================

    list_filter = (
        "subject",
        "is_read",
        "created_at",
    )

    # =====================================================
    # Search
    # =====================================================

    search_fields = (
        "first_name",
        "last_name",
        "phone_number",
        "description",
    )

    # =====================================================
    # Ordering
    # =====================================================

    ordering = (
        "-created_at",
    )

    date_hierarchy = "created_at"

    list_per_page = 25

    # =====================================================
    # Editable Status
    # =====================================================

    list_editable = (
        "is_read",
    )

    # =====================================================
    # Read Only
    # =====================================================

    readonly_fields = (
        "first_name",
        "last_name",
        "phone_number",
        "subject",
        "description",
        "created_at",
        "updated_at",
    )

    # =====================================================
    # Actions
    # =====================================================

    actions = (
        "mark_as_read",
        "mark_as_unread",
    )

    # =====================================================
    # Fieldsets
    # =====================================================

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
                "classes": (
                    "collapse",
                ),
            },
        ),
    )

    # =====================================================
    # Subject Display
    # =====================================================

    @admin.display(
        description="موضوع درخواست",
        ordering="subject",
    )
    def subject_display(self, obj):

        return obj.get_subject_display()

    # =====================================================
    # Mark Read
    # =====================================================

    @admin.action(
        description=(
            "علامت‌گذاری به عنوان خوانده شده"
        )
    )
    def mark_as_read(
        self,
        request,
        queryset,
    ):

        queryset.update(
            is_read=True
        )

    # =====================================================
    # Mark Unread
    # =====================================================

    @admin.action(
        description=(
            "علامت‌گذاری به عنوان خوانده نشده"
        )
    )
    def mark_as_unread(
        self,
        request,
        queryset,
    ):

        queryset.update(
            is_read=False
        )

    # =====================================================
    # Disable Manual Creation
    # =====================================================

    def has_add_permission(
        self,
        request,
    ):

        return False