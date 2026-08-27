from django.urls import path
from .views import (
    ArticleCategoryListView,
    ArticleCategoryDetailView,
    ArticleListView,
    ArticleDetailView,
    FeaturedArticleListView,
)

app_name = 'articles'

urlpatterns = [
    # Article Category URLs
    path('categories/', ArticleCategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', ArticleCategoryDetailView.as_view(), name='category-detail'),

    # Article URLs
    path('articles/', ArticleListView.as_view(), name='article-list'),
    path('articles/featured/', FeaturedArticleListView.as_view(), name='article-featured'),
    path('articles/<str:identifier>/', ArticleDetailView.as_view(), name='article-detail'),
]