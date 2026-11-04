"""Reconcile TCart invoices when provider callback has not arrived."""
from django.core.management.base import BaseCommand
from django.utils import timezone
from payments.models import PaymentAttempt
from payments.services import process_payment_callback, PaymentValidationError


class Command(BaseCommand):
    help = "استعلام امن فاکتورهای TCart که هنوز موفق ثبت نشده‌اند"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=100)

    def handle(self, *args, **options):
        limit = min(max(options["limit"], 1), 1000)
        qs = (PaymentAttempt.objects.filter(
            provider=PaymentAttempt.Provider.TCART,
            status=PaymentAttempt.Status.PENDING,
        ).exclude(provider_reference="").order_by("created_at")[:limit])
        ids = list(qs.values_list("public_id", flat=True))
        errors = 0
        for public_id in ids:
            try:
                attempt = process_payment_callback(
                    public_id=public_id,
                    provider_key=PaymentAttempt.Provider.TCART,
                    callback_data={"source": "server_reconciliation"},
                )
                self.stdout.write(f"{public_id}: {attempt.status}")
            except PaymentValidationError as exc:
                errors += 1
                self.stderr.write(f"{public_id}: {exc}")
        self.stdout.write(f"checked={len(ids)}, errors={errors}")
