import unittest
from django.db import IntegrityError
from articles.models import Article
from .base import ArticlesBase

class KnownIssueRegressionTests(ArticlesBase):
    @unittest.expectedFailure
    def test_category_creation_generates_a_slug(self):
        # Existing serializer ignores slug but model has a required unique slug.
        self.login(self.staff)
        response=self.client.post('/api/v1/articles/categories/',{'name':'تعمیر موتور'},format='json')
        self.assertEqual(response.status_code,201)
        self.assertTrue(response.data['slug'])
    @unittest.expectedFailure
    def test_draft_is_not_publicly_accessible_by_id(self):
        # Existing detail view does not filter by published status.
        response=self.client.get(self.article_url(self.draft))
        self.assertEqual(response.status_code,404)
    @unittest.expectedFailure
    def test_new_article_receives_nonempty_unique_slug(self):
        # Existing create serializer ignores slug; two creations may collide.
        self.login(self.author)
        response=self.client.post('/api/v1/articles/articles/', {'title':'First unique title','content':'body','category':self.category.pk}, format='json')
        self.assertEqual(response.status_code,201)
        self.assertTrue(Article.objects.get(pk=response.data['id']).slug)
