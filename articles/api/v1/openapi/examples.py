"""
OpenAPI Examples for Articles API
"""

# Article Category Examples
article_category_example = {
    "id": 1,
    "name": "تکنولوژی",
    "slug": "technology",
    "description": "مقالات مربوط به تکنولوژی و نوآوری‌های روز دنیا",
    "is_active": True,
}

article_category_list_example = [
    article_category_example,
    {
        "id": 2,
        "name": "آموزش",
        "slug": "education",
        "description": "مقالات آموزشی و راهنماها",
        "is_active": True,
    },
    {
        "id": 3,
        "name": "اخبار",
        "slug": "news",
        "description": "آخرین اخبار و رویدادها",
        "is_active": True,
    },
]


# Article Examples
article_list_example = [
    {
        "id": 1,
        "title": "راهنمای کامل خرید موتورسیکلت",
        "slug": "complete-guide-to-buying-motorcycle",
        "excerpt": "در این مقاله به بررسی نکات مهم هنگام خرید موتورسیکلت می‌پردازیم",
        "cover_image": "https://example.com/media/articles/motorcycle-guide.jpg",
        "category": 1,
        "category_name": "آموزش",
        "author": 1,
        "author_name": "admin",
        "status": "published",
        "is_featured": True,
        "reading_time": 10,
        "view_count": 1500,
        "published_at": "2024-01-15T10:00:00Z",
        "created_at": "2024-01-14T08:00:00Z",
    },
    {
        "id": 2,
        "title": "بررسی جدیدترین مدل‌های موتورسیکلت ۲۰۲۴",
        "slug": "review-newest-motorcycle-models-2024",
        "excerpt": "مروری بر بهترین موتورسیکلت‌های عرضه شده در سال ۲۰۲۴",
        "cover_image": "https://example.com/media/articles/motorcycle-2024.jpg",
        "category": 2,
        "category_name": "اخبار",
        "author": 1,
        "author_name": "admin",
        "status": "published",
        "is_featured": False,
        "reading_time": 8,
        "view_count": 890,
        "published_at": "2024-01-10T14:00:00Z",
        "created_at": "2024-01-09T12:00:00Z",
    },
]

article_detail_example = {
    "id": 1,
    "title": "راهنمای کامل خرید موتورسیکلت",
    "slug": "complete-guide-to-buying-motorcycle",
    "excerpt": "در این مقاله به بررسی نکات مهم هنگام خرید موتورسیکلت می‌پردازیم",
    "content": """
        <p>خرید موتورسیکلت یکی از تصمیمات مهم برای علاقه‌مندان به دنیای دوچرخ است...</p>
        <h2>نکات مهم هنگام خرید</h2>
        <ul>
            <li>بررسی فنی موتورسیکلت</li>
            <li>بررسی مدارک و سند</li>
            <li>تست رانندگی</li>
        </ul>
    """,
    "cover_image": "https://example.com/media/articles/motorcycle-guide.jpg",
    "category": 1,
    "category_name": "آموزش",
    "author": 1,
    "author_name": "admin",
    "products": [1, 2, 3],
    "motorcycles": [1, 2],
    "status": "published",
    "is_featured": True,
    "reading_time": 10,
    "view_count": 1500,
    "seo_title": "راهنمای خرید موتورسیکلت - نکات کلیدی",
    "meta_description": "آموزش کامل خرید موتورسیکلت با بررسی تمام نکات فنی و قانونی",
    "published_at": "2024-01-15T10:00:00Z",
    "created_at": "2024-01-14T08:00:00Z",
    "updated_at": "2024-01-16T09:00:00Z",
}

article_create_example = {
    "title": "عنوان مقاله جدید",
    "excerpt": "خلاصه‌ای کوتاه از مقاله",
    "content": "محتوای کامل مقاله...",
    "category": 1,
    "author": 1,
    "products": [1, 2],
    "motorcycles": [1],
    "status": "draft",
    "is_featured": False,
    "reading_time": 5,
    "seo_title": "عنوان سئو",
    "meta_description": "توضیحات متا برای سئو",
}
