from motorcycles.models import MotorcycleBrand, MotorcycleModel
from .base import MotorcycleTestBase


class MotorcycleViewTests(MotorcycleTestBase):
    def test_brand_list_public(self):
        r = self.call("brand", "list")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 2)

    def test_brand_list_excludes_inactive(self):
        self.other_brand.is_active = False
        self.other_brand.save(update_fields=["is_active"])
        self.assertEqual(self.call("brand", "list").data["count"], 1)

    def test_brand_detail_public(self):
        r = self.call("brand", "retrieve", pk=self.brand.pk)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["data"]["name"], "Honda")

    def test_brand_search(self):
        r = self.call("brand", "list", params={"search": "hond"})
        self.assertEqual(r.data["count"], 1)

    def test_inactive_brand_detail_404(self):
        self.brand.is_active = False
        self.brand.save(update_fields=["is_active"])
        self.assertEqual(self.call("brand", "retrieve", pk=self.brand.pk).status_code, 404)

    def test_model_list_public(self):
        r = self.call("model", "list")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 2)

    def test_model_detail_public(self):
        r = self.call("model", "retrieve", pk=self.model.pk)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["data"]["name"], "CBR 250")

    def test_inactive_model_hidden(self):
        self.model.is_active = False
        self.model.save(update_fields=["is_active"])
        self.assertEqual(self.call("model", "list").data["count"], 1)
        self.assertEqual(self.call("model", "retrieve", pk=self.model.pk).status_code, 404)

    def test_models_of_inactive_brand_hidden(self):
        self.brand.is_active = False
        self.brand.save(update_fields=["is_active"])
        self.assertEqual(self.call("model", "list").data["count"], 1)

    def test_model_brand_filter(self):
        r = self.call("model", "list", params={"brand": self.brand.pk})
        self.assertEqual(r.data["count"], 1)
        self.assertEqual(r.data["data"][0]["name"], "CBR 250")

    def test_model_engine_volume_filter(self):
        r = self.call("model", "list", params={"engine_volume": 125})
        self.assertEqual(r.data["count"], 1)

    def test_invalid_brand_filter_returns_empty(self):
        self.assertEqual(self.call("model", "list", params={"brand": "invalid"}).data["count"], 0)

    def test_invalid_engine_filter_returns_empty(self):
        self.assertEqual(self.call("model", "list", params={"engine_volume": "invalid"}).data["count"], 0)

    def test_model_search_name(self):
        self.assertEqual(self.call("model", "list", params={"search": "CBR"}).data["count"], 1)

    def test_model_search_brand(self):
        self.assertEqual(self.call("model", "list", params={"search": "Yamaha"}).data["count"], 1)

    def test_model_search_description(self):
        self.assertEqual(self.call("model", "list", params={"search": "sport"}).data["count"], 1)

    def test_admin_creates_brand(self):
        r = self.call("brand", "create", method="post", data={"name": "Suzuki"}, user=self.admin_user)
        self.assertEqual(r.status_code, 201, r.data)
        self.assertTrue(MotorcycleBrand.objects.filter(name="Suzuki").exists())

    def test_admin_updates_brand(self):
        r = self.call("brand", "partial_update", method="patch", pk=self.brand.pk, data={"name": "Honda Updated"}, user=self.admin_user)
        self.assertEqual(r.status_code, 200, r.data)
        self.brand.refresh_from_db()
        self.assertEqual(self.brand.name, "Honda Updated")

    def test_admin_creates_model(self):
        r = self.call("model", "create", method="post", data={"brand": self.brand.pk, "name": "CB 650"}, user=self.admin_user)
        self.assertEqual(r.status_code, 201, r.data)

    def test_admin_updates_model(self):
        r = self.call("model", "partial_update", method="patch", pk=self.model.pk, data={"engine_volume": 300}, user=self.admin_user)
        self.assertEqual(r.status_code, 200, r.data)
        self.model.refresh_from_db()
        self.assertEqual(self.model.engine_volume, 300)

    def test_admin_brand_delete_protected(self):
        r = self.call("brand", "destroy", method="delete", pk=self.brand.pk, user=self.admin_user)
        self.assertEqual(r.status_code, 409, r.data)

    def test_admin_deletes_unrelated_brand(self):
        new_brand = MotorcycleBrand.objects.create(name="Suzuki")
        r = self.call("brand", "destroy", method="delete", pk=new_brand.pk, user=self.admin_user)
        self.assertEqual(r.status_code, 200, r.data)

    def test_admin_deletes_model(self):
        r = self.call("model", "destroy", method="delete", pk=self.model.pk, user=self.admin_user)
        self.assertEqual(r.status_code, 200, r.data)
        self.assertFalse(MotorcycleModel.objects.filter(pk=self.model.pk).exists())
