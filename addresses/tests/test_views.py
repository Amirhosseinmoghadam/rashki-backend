from django.urls import reverse
from rest_framework import status
from .base import AddressTestBase

class AddressAPITests(AddressTestBase):
    def url(self,name,**kwargs):
        return reverse("addresses_api_v1:"+name,kwargs=kwargs or None)

    def test_public_provinces_and_filtered_cities(self):
        client=self.client
        provinces=client.get(self.url("province-list"))
        self.assertEqual(provinces.status_code,status.HTTP_200_OK)
        self.assertEqual(len(provinces.data["data"]),2)
        cities=client.get(self.url("city-list-by-province",province_id=self.province.pk))
        self.assertEqual(cities.status_code,status.HTTP_200_OK)
        self.assertEqual([x["id"] for x in cities.data["data"]],[self.city.pk])

    def test_authentication_required_for_address_list(self):
        self.assertIn(self.client.get(self.url("address-list-create")).status_code,(401,403))

    def test_create_and_list_only_own_addresses(self):
        client=self.authenticated_client()
        response=client.post(self.url("address-list-create"),self.payload(),format="json")
        self.assertEqual(response.status_code,201,response.data)
        self.assertTrue(response.data["data"]["is_default"])
        self.make_address(user=self.other)
        listing=client.get(self.url("address-list-create"))
        self.assertEqual(listing.status_code,200)
        self.assertEqual(len(listing.data["data"]),1)

    def test_create_rejects_mismatched_city(self):
        response=self.authenticated_client().post(self.url("address-list-create"),self.payload(city=self.other_city.pk),format="json")
        self.assertEqual(response.status_code,400)

    def test_detail_patch_and_delete(self):
        addr=self.make_address(is_default=True)
        client=self.authenticated_client()
        url=self.url("address-detail",pk=addr.pk)
        self.assertEqual(client.get(url).status_code,200)
        response=client.patch(url,{"first_name":"رضا"},format="json")
        self.assertEqual(response.status_code,200,response.data)
        addr.refresh_from_db()
        self.assertEqual(addr.first_name,"رضا")
        self.assertEqual(client.delete(url).status_code,200)
        self.assertFalse(type(addr).objects.filter(pk=addr.pk).exists())

    def test_set_default_switches_addresses(self):
        first=self.make_address(is_default=True)
        second=self.make_address()
        response=self.authenticated_client().post(self.url("address-set-default",pk=second.pk))
        self.assertEqual(response.status_code,200,response.data)
        first.refresh_from_db();second.refresh_from_db()
        self.assertFalse(first.is_default)
        self.assertTrue(second.is_default)

    def test_default_address_cannot_be_unset_using_patch(self):
        addr=self.make_address(is_default=True)
        response=self.authenticated_client().patch(self.url("address-detail",pk=addr.pk),{"is_default":False},format="json")
        self.assertEqual(response.status_code,400,response.data)
