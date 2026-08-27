from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAdminUser
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .serializers import (
    ArticleCategorySerializer,
    ArticleListSerializer,
    ArticleDetailSerializer,
    ArticleCreateUpdateSerializer,
)
from articles.models import ArticleCategory, Article
from .openapi.responses import (
    article_category_list_response,
    article_category_detail_response,
    article_category_create_response,
    article_list_response,
    article_detail_response,
    article_create_response,
    common_error_response,
    validation_error_response,
)
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse


class ArticleCategoryListView(APIView):
    """
    List all article categories or create a new category.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary="List Article Categories",
        description="Get a list of all article categories",
        responses={
            200: article_category_list_response,
            401: common_error_response,
        },
        tags=['Articles - Categories']
    )
    def get(self, request):
        categories = ArticleCategory.objects.filter(is_active=True)
        serializer = ArticleCategorySerializer(categories, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Create Article Category",
        description="Create a new article category",
        request=ArticleCategorySerializer,
        responses={
            201: article_category_create_response,
            400: validation_error_response,
            401: common_error_response,
        },
        tags=['Articles - Categories']
    )
    def post(self, request):
        if not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to create categories."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ArticleCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArticleCategoryDetailView(APIView):
    """
    Retrieve, update or delete an article category.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary="Get Article Category",
        description="Get details of a specific article category",
        responses={
            200: article_category_detail_response,
            404: common_error_response,
        },
        tags=['Articles - Categories']
    )
    def get(self, request, pk):
        category = get_object_or_404(ArticleCategory, pk=pk)
        serializer = ArticleCategorySerializer(category)
        return Response(serializer.data)

    @extend_schema(
        summary="Update Article Category",
        description="Update an existing article category",
        request=ArticleCategorySerializer,
        responses={
            200: article_category_detail_response,
            400: validation_error_response,
            404: common_error_response,
        },
        tags=['Articles - Categories']
    )
    def put(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to update categories."},
                status=status.HTTP_403_FORBIDDEN
            )

        category = get_object_or_404(ArticleCategory, pk=pk)
        serializer = ArticleCategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete Article Category",
        description="Delete an article category",
        responses={
            204: None,
            404: common_error_response,
        },
        tags=['Articles - Categories']
    )
    def delete(self, request, pk):
        if not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to delete categories."},
                status=status.HTTP_403_FORBIDDEN
            )

        category = get_object_or_404(ArticleCategory, pk=pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ArticleListView(APIView):
    """
    List all articles or create a new article.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary="List Articles",
        description="Get a list of all published articles with optional filtering",
        parameters=[
            OpenApiParameter(
                name='category',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Filter by category slug'
            ),
            OpenApiParameter(
                name='author',
                type=int,
                location=OpenApiParameter.QUERY,
                description='Filter by author ID'
            ),
            OpenApiParameter(
                name='is_featured',
                type=bool,
                location=OpenApiParameter.QUERY,
                description='Filter featured articles'
            ),
            OpenApiParameter(
                name='search',
                type=str,
                location=OpenApiParameter.QUERY,
                description='Search in title, content, and excerpt'
            ),
        ],
        responses={
            200: article_list_response,
        },
        tags=['Articles']
    )
    def get(self, request):
        articles = Article.objects.select_related('category', 'author').filter(
            status=Article.Status.PUBLISHED
        )

        # Optional filtering
        category_slug = request.query_params.get('category')
        if category_slug:
            articles = articles.filter(category__slug=category_slug)

        author_id = request.query_params.get('author')
        if author_id:
            articles = articles.filter(author_id=author_id)

        is_featured = request.query_params.get('is_featured')
        if is_featured:
            articles = articles.filter(is_featured=True)

        search = request.query_params.get('search')
        if search:
            articles = articles.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(excerpt__icontains=search)
            )

        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Create Article",
        description="Create a new article (requires authentication)",
        request=ArticleCreateUpdateSerializer,
        responses={
            201: article_create_response,
            400: validation_error_response,
            401: common_error_response,
        },
        tags=['Articles']
    )
    def post(self, request):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        serializer = ArticleCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            # Set author from request user if not provided
            if 'author' not in request.data:
                serializer.validated_data['author'] = request.user

            # Handle products and motorcycles
            products_data = request.data.get('products', [])
            motorcycles_data = request.data.get('motorcycles', [])

            article = serializer.save()

            if products_data:
                article.products.set(products_data)
            if motorcycles_data:
                article.motorcycles.set(motorcycles_data)

            return Response(
                ArticleDetailSerializer(article).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArticleDetailView(APIView):
    """
    Retrieve, update or delete an article.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary="Get Article",
        description="Get details of a specific article by ID or slug",
        responses={
            200: article_detail_response,
            404: common_error_response,
        },
        tags=['Articles']
    )
    def get(self, request, identifier):
        # Try to get by ID first, then by slug
        try:
            article = Article.objects.select_related(
                'category', 'author'
            ).prefetch_related(
                'products', 'motorcycles'
            ).get(Q(id=identifier) | Q(slug=identifier))
        except Article.DoesNotExist:
            return Response(
                {"detail": "Article not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Increment view count for published articles
        if article.status == Article.Status.PUBLISHED:
            article.view_count += 1
            article.save(update_fields=['view_count'])

        serializer = ArticleDetailSerializer(article)
        return Response(serializer.data)

    @extend_schema(
        summary="Update Article",
        description="Update an existing article",
        request=ArticleCreateUpdateSerializer,
        responses={
            200: article_detail_response,
            400: validation_error_response,
            404: common_error_response,
        },
        tags=['Articles']
    )
    def put(self, request, identifier):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            article = Article.objects.get(Q(id=identifier) | Q(slug=identifier))
        except Article.DoesNotExist:
            return Response(
                {"detail": "Article not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check permissions
        if article.author != request.user and not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to update this article."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ArticleCreateUpdateSerializer(article, data=request.data)
        if serializer.is_valid():
            article = serializer.save()

            # Handle products and motorcycles
            products_data = request.data.get('products', [])
            motorcycles_data = request.data.get('motorcycles', [])

            if products_data:
                article.products.set(products_data)
            if motorcycles_data:
                article.motorcycles.set(motorcycles_data)

            return Response(ArticleDetailSerializer(article).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Delete Article",
        description="Delete an article",
        responses={
            204: None,
            404: common_error_response,
        },
        tags=['Articles']
    )
    def delete(self, request, identifier):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            article = Article.objects.get(Q(id=identifier) | Q(slug=identifier))
        except Article.DoesNotExist:
            return Response(
                {"detail": "Article not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check permissions
        if article.author != request.user and not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to delete this article."},
                status=status.HTTP_403_FORBIDDEN
            )

        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FeaturedArticleListView(APIView):
    """
    List featured articles.
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        summary="List Featured Articles",
        description="Get a list of featured articles",
        responses={
            200: article_list_response,
        },
        tags=['Articles']
    )
    def get(self, request):
        articles = Article.objects.select_related(
            'category', 'author'
        ).filter(
            status=Article.Status.PUBLISHED,
            is_featured=True
        )
        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data)