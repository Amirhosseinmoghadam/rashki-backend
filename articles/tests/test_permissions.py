from .base import ArticlesBase

class ArticlePermissionsTests(ArticlesBase):
    def test_anonymous_cannot_create_article(self):
        result=self.client.post('/api/v1/articles/articles/',{'title':'x'},format='json')
        self.assertIn(result.status_code,(401,403))
    def test_anonymous_cannot_create_category(self):
        result=self.client.post('/api/v1/articles/categories/',{'name':'new'},format='json')
        self.assertIn(result.status_code,(401,403))
    def test_nonstaff_cannot_create_category(self):
        self.login(self.author)
        result=self.client.post('/api/v1/articles/categories/',{'name':'new'},format='json')
        self.assertEqual(result.status_code,403)
    def test_nonstaff_cannot_update_category(self):
        self.login(self.author)
        result=self.client.put(self.category_url(self.category),{'name':'changed'},format='json')
        self.assertEqual(result.status_code,403)
    def test_nonstaff_cannot_delete_category(self):
        self.login(self.author)
        self.assertEqual(self.client.delete(self.category_url(self.category)).status_code,403)
    def test_other_user_cannot_update_article(self):
        self.login(self.other)
        result=self.client.put(self.article_url(self.published),{'title':'hijack'},format='json')
        self.assertEqual(result.status_code,403)
    def test_other_user_cannot_delete_article(self):
        self.login(self.other)
        self.assertEqual(self.client.delete(self.article_url(self.published)).status_code,403)
    def test_author_can_delete_own_draft(self):
        self.login(self.author)
        self.assertEqual(self.client.delete(self.article_url(self.draft)).status_code,204)
    def test_staff_can_delete_other_author_draft(self):
        self.login(self.staff)
        self.assertEqual(self.client.delete(self.article_url(self.draft)).status_code,204)
