from django.test import SimpleTestCase,override_settings
from django.core.cache import caches
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request
from rest_framework.exceptions import Throttled
from contact.throttles import ContactRequestThrottle
from contact.api.v1.views import ContactRequestCreateAPIView


class ContactThrottleTests(SimpleTestCase):
    def test_scope(self):
        self.assertEqual(ContactRequestThrottle.scope,"contact")

    @override_settings(REST_FRAMEWORK={"DEFAULT_THROTTLE_RATES":{"contact":"2/min"}})
    def test_limit_blocks_third_request(self):
        # Initialize a fresh throttle with an isolated in-memory cache.
        from django.core.cache.backends.locmem import LocMemCache
        factory=APIRequestFactory()
        class IsolatedThrottle(ContactRequestThrottle):
            cache=LocMemCache("contact-test",{})
        throttle=IsolatedThrottle()
        throttle.THROTTLE_RATES={"contact":"2/min"}
        throttle.rate="2/min"
        throttle.num_requests,throttle.duration=throttle.parse_rate(throttle.rate)
        request=Request(factory.post("/api/v1/contact/",{},format="json",REMOTE_ADDR="198.51.100.10"))
        view=ContactRequestCreateAPIView()
        self.assertTrue(throttle.allow_request(request,view))
        self.assertTrue(throttle.allow_request(request,view))
        self.assertFalse(throttle.allow_request(request,view))
        self.assertGreater(throttle.wait(),0)
