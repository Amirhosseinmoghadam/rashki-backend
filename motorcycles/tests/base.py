from types import SimpleNamespace
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from motorcycles.models import MotorcycleBrand, MotorcycleModel
from motorcycles.api.v1.views import MotorcycleBrandViewSet, MotorcycleModelViewSet


class MotorcycleTestBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.brand = MotorcycleBrand.objects.create(name="Honda")
        cls.other_brand = MotorcycleBrand.objects.create(name="Yamaha")
        cls.model = MotorcycleModel.objects.create(
            brand=cls.brand, name="CBR 250", engine_volume=250,
            production_start_year=2018, production_end_year=2024,
            description="Sport bike",
        )
        cls.other_model = MotorcycleModel.objects.create(
            brand=cls.other_brand, name="MT 125", engine_volume=125,
        )

    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin_user = SimpleNamespace(is_authenticated=True, is_staff=True, is_active=True)
        self.normal_user = SimpleNamespace(is_authenticated=True, is_staff=False, is_active=True)

    def call(self, kind, action, method="get", pk=None, data=None, params=None, user=None):
        viewset = MotorcycleBrandViewSet if kind == "brand" else MotorcycleModelViewSet
        path = "/api/v1/motorcycles/" + ("motorcycle-brands/" if kind == "brand" else "motorcycles/")
        if pk is not None:
            path += f"{pk}/"
        req = getattr(self.factory, method)(path, data=data or {}, format="json", **({"QUERY_STRING": "&".join(f"{k}={v}" for k, v in params.items())} if params else {}))
        if user is not None:
            force_authenticate(req, user=user)
        response = viewset.as_view({method: action})(req, **({"pk": str(pk)} if pk is not None else {}))
        response.render()
        return response
