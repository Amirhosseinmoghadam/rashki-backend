from django.db.models.deletion import ProtectedError
from django.db import IntegrityError, transaction
from articles.models import Article, ArticleCategory
from .base import ArticlesBase

class ArticleModelsTests(ArticlesBase):
    def test_category_string(self):
        self.assertEqual(str(self.category), self.category.name)
    def test_article_string(self):
        self.assertEqual(str(self.published), self.published.title)
    def test_article_defaults(self):
        article = Article.objects.create(title="تازه", slug="new-article", content="محتوا", category=self.category, author=self.author)
        self.assertEqual(article.status, Article.Status.DRAFT)
        self.assertFalse(article.is_featured)
        self.assertEqual(article.reading_time, 1)
        self.assertEqual(article.view_count, 0)
    def test_slugs_are_unique(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Article.objects.create(title="تکراری", slug=self.published.slug, content="متن", category=self.category, author=self.author)
    def test_category_slug_is_unique(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ArticleCategory.objects.create(name="نام دیگر", slug=self.category.slug)
    def test_category_is_protected_from_deletion(self):
        with self.assertRaises(ProtectedError):
            self.category.delete()
    def test_author_is_protected_from_deletion(self):
        with self.assertRaises(ProtectedError):
            self.author.delete()
    def test_article_timestamps(self):
        self.assertIsNotNone(self.published.created_at)
        self.assertIsNotNone(self.published.updated_at)
    def test_article_m2m_empty_by_default(self):
        self.assertEqual(self.published.products.count(), 0)
        self.assertEqual(self.published.motorcycles.count(), 0)
