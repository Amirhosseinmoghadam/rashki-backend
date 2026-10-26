from .base import AddressTestBase

class AddressPermissionTests(AddressTestBase):
    def test_other_users_address_is_not_accessible(self):
        address=self.make_address(user=self.other,is_default=True)
        client=self.authenticated_client()
        from django.urls import reverse
        detail=reverse("addresses_api_v1:address-detail",kwargs={"pk":address.pk})
        default=reverse("addresses_api_v1:address-set-default",kwargs={"pk":address.pk})
        self.assertEqual(client.get(detail).status_code,404)
        self.assertEqual(client.patch(detail,{"first_name":"نفوذ"},format="json").status_code,404)
        self.assertEqual(client.delete(detail).status_code,404)
        self.assertEqual(client.post(default).status_code,404)
        address.refresh_from_db()
        self.assertEqual(address.first_name,"علی")
