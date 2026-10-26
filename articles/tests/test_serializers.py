from articles.api.v1.serializers import (ArticleCategorySerializer, ArticleListSerializer, ArticleDetailSerializer, ArticleCreateUpdateSerializer)
from .base import ArticlesBase

class ArticleSerializerTests(ArticlesBase):
    def test_category_serialization(self):
        data=ArticleCategorySerializer(self.category).data
        self.assertEqual(data['name'], self.category.name)
        self.assertEqual(data['slug'], self.category.slug)
    def test_category_slug_is_read_only_in_serializer(self):
        ser=ArticleCategorySerializer(data={'name':'آموزش', 'slug':'training'})
        self.assertTrue(ser.is_valid(), ser.errors)
        self.assertNotIn('slug', ser.validated_data)
    def test_list_serializer_has_summary_fields(self):
        data=ArticleListSerializer(self.published).data
        self.assertEqual(data['category_name'],self.category.name)
        self.assertEqual(data['author'],self.author.pk)
        self.assertNotIn('content',data)
    def test_detail_serializer_has_content(self):
        data=ArticleDetailSerializer(self.published).data
        self.assertEqual(data['content'],'متن تعمیر')
        self.assertEqual(data['products'],[])
    def test_invalid_status_rejected(self):
        ser=ArticleCreateUpdateSerializer(data={'title':'عنوان','content':'متن','category':self.category.pk,'author':self.author.pk,'status':'unknown'})
        self.assertFalse(ser.is_valid())
        self.assertIn('status',ser.errors)
    def test_nonexistent_category_rejected(self):
        ser=ArticleCreateUpdateSerializer(data={'title':'عنوان','content':'متن','category':999999,'author':self.author.pk})
        self.assertFalse(ser.is_valid())
        self.assertIn('category',ser.errors)
    def test_slug_is_read_only_in_create_serializer(self):
        ser=ArticleCreateUpdateSerializer(data={'title':'جدید','slug':'user-value','content':'متن','category':self.category.pk,'author':self.author.pk})
        self.assertTrue(ser.is_valid(),ser.errors)
        self.assertNotIn('slug',ser.validated_data)
