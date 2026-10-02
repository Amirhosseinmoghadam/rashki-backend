from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from shipping.tipax_locations import (
    TipaxLocationSyncError,
    sync_tipax_locations,
)


class Command(BaseCommand):
    help = (
        "Sync Tipax provinces and cities "
        "with local location tables."
    )

    def handle(
        self,
        *args,
        **options,
    ):
        self.stdout.write(
            "Syncing Tipax locations..."
        )

        try:
            stats = (
                sync_tipax_locations()
            )

        except TipaxLocationSyncError as exc:
            raise CommandError(
                str(exc)
            ) from exc

        self.stdout.write(
            self.style.SUCCESS(
                (
                    "Tipax locations synced successfully.\n"
                    f"Provinces: {stats['provinces']}\n"
                    f"Cities: {stats['cities']}\n"
                    f"Province maps: "
                    f"{stats['province_maps']}\n"
                    f"City maps: "
                    f"{stats['city_maps']}\n"
                    f"Skipped cities: "
                    f"{stats['skipped_cities']}"
                )
            )
        )