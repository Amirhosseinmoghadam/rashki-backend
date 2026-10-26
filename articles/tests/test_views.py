from articles.models import Article
from .base import ArticlesBase

LIST='/api/v1/articles/articles/'
FEATURED='/api/v1/articles/articles/featured/'
CATEGORIES='/api/v1/articles/categories/'

class ArticleViewTests(ArticlesBase):
    def test_public_list_only_published(self):
        response=self.client.get(LIST)
        self.assertEqual(response.status_code,200)
        ids={a['id'] for a in response.data}
        self.assertIn(self.published.pk,ids)
        self.assertNotIn(self.draft.pk,ids)
    def test_filter_by_category(self):
        response=self.client.get(LIST,{'category':self.category.slug})
        self.assertEqual(response.status_code,200)
        self.assertIn(self.published.pk,{a['id'] for a in response.data})
    def test_filter_by_author(self):
        response=self.client.get(LIST,{'author':self.other.pk})
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.data),0)
    def test_search(self):
        response=self.client.get(LIST,{'search':'ترمز'})
        self.assertEqual(response.status_code,200)
        self.assertEqual([a['id'] for a in response.data],[self.published.pk])
    def test_featured_only_published(self):
        response=self.client.get(FEATURED)
        self.assertEqual(response.status_code,200)
        self.assertEqual([a['id'] for a in response.data],[self.published.pk])
    def test_detail_increments_published_views(self):
        old=self.published.view_count
        response=self.client.get(self.article_url(self.published))
        self.assertEqual(response.status_code,200)
        self.published.refresh_from_db()
        self.assertEqual(self.published.view_count,old+1)
    def test_draft_view_does_not_increment(self):
        response=self.client.get(self.article_url(self.draft))
        self.assertEqual(response.status_code,200)
        self.draft.refresh_from_db()
        self.assertEqual(self.draft.view_count,0)
    def test_missing_article_returns_404(self):
        self.assertEqual(self.client.get('/api/v1/articles/articles/999999/').status_code,404)
    def test_category_list_only_active(self):
        response=self.client.get(CATEGORIES)
        self.assertEqual(response.status_code,200)
        ids={x['id'] for x in response.data}
        self.assertIn(self.category.pk,ids)
        self.assertNotIn(self.inactive_category.pk,ids)
    def test_category_detail_retrieves_inactive(self):
        response=self.client.get(self.category_url(self.inactive_category))
        self.assertEqual(response.status_code,200)
