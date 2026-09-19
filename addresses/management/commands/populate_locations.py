from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Deprecated. Use sync_tipax_locations instead."
    )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING(
                (
                    "این Command قدیمی شده است.\n"
                    "برای دریافت شهر و استان از Tipax "
                    "از دستور زیر استفاده کنید:\n\n"
                    "python manage.py sync_tipax_locations"
                )
            )
        )
