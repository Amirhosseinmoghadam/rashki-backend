import json

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
        "Sync Tipax states/cities, "
        "local locations and provider mappings."
    )

    def handle(
        self,
        *args,
        **options,
    ):
        self.stdout.write(
            "در حال دریافت و Sync "
            "کردن Locations از Tipax..."
        )

        try:
            stats = (
                sync_tipax_locations()
            )

        except TipaxLocationSyncError as exc:
            raise CommandError(
                str(exc)
            ) from exc

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Sync Tipax Locations تمام شد."
            )
        )

        self.stdout.write(
            (
                f"Raw states: "
                f"{stats['raw_states']}"
            )
        )

        self.stdout.write(
            (
                f"Raw cities: "
                f"{stats['raw_cities']}"
            )
        )

        self.stdout.write(
            (
                f"Valid states: "
                f"{stats['valid_states']}"
            )
        )

        self.stdout.write(
            (
                f"Invalid states: "
                f"{stats['invalid_states']}"
            )
        )

        self.stdout.write(
            (
                f"Valid cities: "
                f"{stats['valid_cities']}"
            )
        )

        self.stdout.write(
            (
                f"Invalid cities: "
                f"{stats['invalid_cities']}"
            )
        )

        self.stdout.write(
            (
                f"Cities with unknown state: "
                f"{stats['unknown_state_cities']}"
            )
        )

        self.stdout.write("")

        self.stdout.write(
            (
                f"Local Province created: "
                f"{stats['province_created']}"
            )
        )

        self.stdout.write(
            (
                f"Local Province existing: "
                f"{stats['province_existing']}"
            )
        )

        self.stdout.write(
            (
                f"Local City created: "
                f"{stats['city_created']}"
            )
        )

        self.stdout.write(
            (
                f"Local City existing: "
                f"{stats['city_existing']}"
            )
        )

        self.stdout.write("")

        self.stdout.write(
            (
                "Provider Province created: "
                f"{stats['provider_province_created']}"
            )
        )

        self.stdout.write(
            (
                "Provider Province updated: "
                f"{stats['provider_province_updated']}"
            )
        )

        self.stdout.write(
            (
                "Provider City created: "
                f"{stats['provider_city_created']}"
            )
        )

        self.stdout.write(
            (
                "Provider City updated: "
                f"{stats['provider_city_updated']}"
            )
        )

        self.stdout.write("")

        self.stdout.write(
            (
                "Province Map created: "
                f"{stats['province_map_created']}"
            )
        )

        self.stdout.write(
            (
                "Province Map updated: "
                f"{stats['province_map_updated']}"
            )
        )

        self.stdout.write(
            (
                "City Map created: "
                f"{stats['city_map_created']}"
            )
        )

        self.stdout.write(
            (
                "City Map updated: "
                f"{stats['city_map_updated']}"
            )
        )

        skipped = (
            stats[
                "skipped_cities"
            ]
        )

        if skipped:
            self.stdout.write("")
            self.stdout.write(
                "نمونه Cityهای Skip شده:"
            )

            self.stdout.write(
                json.dumps(
                    skipped,
                    ensure_ascii=False,
                    indent=2,
                    default=str,
                )
            )