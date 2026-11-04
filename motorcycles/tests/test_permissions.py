from .base import MotorcycleTestBase


class MotorcyclePermissionTests(MotorcycleTestBase):
    def test_anonymous_can_list(self):
        self.assertEqual(self.call("brand", "list").status_code, 200)
        self.assertEqual(self.call("model", "list").status_code, 200)

    def test_anonymous_cannot_create(self):
        for kind in ("brand", "model"):
            with self.subTest(kind=kind):
                r = self.call(kind, "create", method="post", data={"name": "Blocked"})
                self.assertIn(r.status_code, (401, 403))

    def test_normal_user_cannot_create(self):
        for kind in ("brand", "model"):
            with self.subTest(kind=kind):
                r = self.call(kind, "create", method="post", data={"name": "Blocked"}, user=self.normal_user)
                self.assertEqual(r.status_code, 403)

    def test_normal_user_cannot_modify(self):
        for kind, pk in (("brand", self.brand.pk), ("model", self.model.pk)):
            for method, action in (("patch", "partial_update"), ("delete", "destroy")):
                with self.subTest(kind=kind, method=method):
                    r = self.call(kind, action, method=method, pk=pk, data={"name": "Blocked"}, user=self.normal_user)
                    self.assertEqual(r.status_code, 403)

    def test_admin_can_access_write_endpoint(self):
        r = self.call("brand", "create", method="post", data={"name": "Royal Enfield"}, user=self.admin_user)
        self.assertEqual(r.status_code, 201, r.data)
