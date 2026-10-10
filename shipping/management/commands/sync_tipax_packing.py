from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from shipping.tipax_packing import (
    TipaxPackingSyncError,
    sync_tipax_packing,
)


class Command(BaseCommand):
    help = (
        "Sync Tipax packing options "
        "and validate packing reference data."
    )

    def handle(
        self,
        *args,
        **options,
    ):
        self.stdout.write(
            (
                "در حال دریافت و Sync کردن "
                "Packing Reference Data از Tipax..."
            )
        )

        try:
            stats = (
                sync_tipax_packing()
            )

        except TipaxPackingSyncError as exc:
            raise CommandError(
                str(exc)
            ) from exc

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Sync Tipax Packing تمام شد."
            )
        )

        self.stdout.write(
            (
                "Raw packing options: "
                f"{stats['raw_packing_options']}"
            )
        )

        self.stdout.write(
            (
                "Valid packing options: "
                f"{stats['valid_packing_options']}"
            )
        )

        self.stdout.write(
            (
                "Invalid packing options: "
                f"{stats['invalid_packing_options']}"
            )
        )

        self.stdout.write(
            (
                "Created: "
                f"{stats['created']}"
            )
        )

        self.stdout.write(
            (
                "Updated: "
                f"{stats['updated']}"
            )
        )

        self.stdout.write(
            (
                "Deactivated: "
                f"{stats['deactivated']}"
            )
        )

        self.stdout.write(
            (
                "Detected cartons: "
                f"{stats['cartons']}"
            )
        )

        content = stats[
            "package_content"
        ]

        parcel = stats[
            "parcel_type"
        ]

        self.stdout.write("")

        self.stdout.write(
            (
                "Package content: "
                f"{content.get('id')} - "
                f"{content.get('title')}"
            )
        )

        self.stdout.write(
            (
                "Parcel type: "
                f"{parcel.get('id')} - "
                f"{parcel.get('title')}"
            )
        )