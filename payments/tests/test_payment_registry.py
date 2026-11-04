from django.test import SimpleTestCase
from payments.providers.base import PaymentProviderConfigurationError
from payments.providers.registry import get_payment_provider
from payments.providers.tcart import TCartProvider
from payments.providers.zarinpal import ZarinPalProvider
from payments.services import get_initial_provider_money, PaymentValidationError

class PaymentRegistryTests(SimpleTestCase):
    def test_zarinpal_factory(self):
        self.assertIsInstance(get_payment_provider('zarinpal'), ZarinPalProvider)

    def test_tcart_factory(self):
        self.assertIsInstance(get_payment_provider('tcart'), TCartProvider)

    def test_unknown_provider_raises(self):
        with self.assertRaises(PaymentProviderConfigurationError):
            get_payment_provider('made-up')

    def test_tcart_money_is_toman(self):
        self.assertEqual(get_initial_provider_money(provider='tcart', amount_toman=50000), (50000,'IRT'))

    def test_invalid_provider_money_rejected(self):
        with self.assertRaises(PaymentValidationError):
            get_initial_provider_money(provider='made-up', amount_toman=10000)
