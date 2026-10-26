from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from articles.models import Article, ArticleCategory

class ArticlesBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.author = User.objects.create_user(phone_number="09120000011")
        cls.other = User.objects.create_user(phone_number="09120000012")
        cls.staff = User.objects.create_user(phone_number="09120000013")
        cls.staff.is_staff = True
        cls.staff.save(update_fields=["is_staff"])
        cls.category = ArticleCategory.objects.create(name="راهنمای تعمیر", slug="repair-guide")
        cls.inactive_category = ArticleCategory.objects.create(name="قدیمی", slug="old-guides", is_active=False)
        cls.published = Article.objects.create(title="راهنمای ترمز", slug="brake-guide", content="متن تعمیر", category=cls.category, author=cls.author, status=Article.Status.PUBLISHED, is_featured=True)
        cls.draft = Article.objects.create(title="پیش نویس", slug="secret-draft", content="متن منتشر نشده", category=cls.category, author=cls.author, status=Article.Status.DRAFT)
    def setUp(self):
        self.client = APIClient()
    def login(self, user):
        self.client.force_authenticate(user=user)
    @staticmethod
    def article_url(article):
        return f"/api/v1/articles/articles/{article.pk}/"
    @staticmethod
    def category_url(category):
        return f"/api/v1/articles/categories/{category.pk}/"
