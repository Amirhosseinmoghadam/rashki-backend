import json

from django.core.management.base import (
    BaseCommand,
)

from shipping.providers.tipax_client import (
    TipaxAPIError,
    TipaxClient,
)


class Command(BaseCommand):

    help = (
        "Fetch Tipax reference data such as "
        "packing, package content, parcel and "
        "payment types."
    )

    def handle(
        self,
        *args,
        **options,
    ):

        client = TipaxClient()

        endpoints = {

            "PackContentRates": (
                client.get_pack_content_rates
            ),

            "PackingPrices": (
                client.get_packing_prices
            ),

            "ParcelTypes": (
                client.get_parcel_types
            ),

            "PaymentTypes": (
                client.get_payment_types
            ),

            "Cities": (
                client.get_cities
            ),
        }

        for title, function in (
            endpoints.items()
        ):

            self.stdout.write(
                "\n"
                +
                "=" * 60
            )

            self.stdout.write(
                title
            )

            self.stdout.write(
                "=" * 60
            )

            try:

                data = function()

            except TipaxAPIError as exc:

                self.stderr.write(
                    self.style.ERROR(
                        str(exc)
                    )
                )

                continue

            self.stdout.write(
                json.dumps(
                    data,
                    ensure_ascii=False,
                    indent=2,
                    default=str,
                )
            )