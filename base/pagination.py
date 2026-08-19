from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class DefaultPagination(PageNumberPagination):
    """
    Default pagination class for the project with a custom response structure.
    Default page size: 20.
    """

    page_size = 20

    def get_paginated_response(self, data):
        """Returns the custom response format."""
        return Response(
            {
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "total_objects": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "current_page_number": self.page.number,
                "results": data,
            }
        )


class ArticlePagination(DefaultPagination):
    """
    Pagination specifically for Article lists.
    Inherits the custom response structure from DefaultPagination
    but uses a page size of 12.
    """

    page_size = 12


