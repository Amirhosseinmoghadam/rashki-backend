from django.test import SimpleTestCase
from django.urls import reverse, resolve
from shipping.api.v1.serializers import ShippingMethodSerializer, ShippingRateRuleSerializer
from shipping.api.v1.views import ShippingQuoteAPIView, ShippingMethodViewSet, ShippingRateRuleViewSet
from shipping.models import ShippingMethod, ShippingRateRule
from shipping.providers.base import ProviderQuote, ShippingProviderError, ShippingRateNotFoundError
from shipping.services import ShippingQuote


class ShippingContractTests(SimpleTestCase):
    def test_method_serializer_fields(self):
        fields = ShippingMethodSerializer().fields
        for name in ("code", "name", "provider", "calculation_mode", "is_active"):
            with self.subTest(field=name):
                self.assertIn(name, fields)

    def test_rate_serializer_fields(self):
        fields = ShippingRateRuleSerializer().fields
        for name in ("method_id", "destination_scope", "min_weight_grams", "base_price_toman"):
            with self.subTest(field=name):
                self.assertIn(name, fields)

    def test_serializer_method_relation_is_writable_by_id(self):
        self.assertTrue(ShippingRateRuleSerializer().fields["method_id"].write_only)

    def test_method_serializer_id_read_only(self):
        self.assertTrue(ShippingMethodSerializer().fields["id"].read_only)

    def test_shipping_quote_url(self):
        url = reverse("shipping_api_v1:shipping-quotes")
        self.assertEqual(resolve(url).func.view_class, ShippingQuoteAPIView)

    def test_method_list_url(self):
        url = reverse("shipping_api_v1:shipping-method-list")
        self.assertEqual(resolve(url).func.cls, ShippingMethodViewSet)

    def test_rate_list_url(self):
        url = reverse("shipping_api_v1:shipping-rate-rule-list")
        self.assertEqual(resolve(url).func.cls, ShippingRateRuleViewSet)

    def test_provider_quote_data_contract(self):
        quote = ProviderQuote(amount_toman=10000, provider_data={"source": "manual"})
        self.assertEqual(quote.amount_toman, 10000)

    def test_shipping_quote_unavailable_contract(self):
        quote = ShippingQuote(method=None, amount_toman=None, weight_grams=200,
                              is_available=False, unavailable_reason="unavailable")
        self.assertIsNone(quote.amount_toman)

    def test_provider_exception_inheritance(self):
        self.assertTrue(issubclass(ShippingRateNotFoundError, ShippingProviderError))

    def test_provider_enum_contains_tipax_and_post(self):
        self.assertNotEqual(ShippingMethod.Provider.TIPAX, ShippingMethod.Provider.POST)

    def test_rate_rule_scopes_present(self):
        self.assertTrue(ShippingRateRule.DestinationScope.CITY)
        self.assertTrue(ShippingRateRule.DestinationScope.PROVINCE)
        self.assertTrue(ShippingRateRule.DestinationScope.NATIONWIDE)
