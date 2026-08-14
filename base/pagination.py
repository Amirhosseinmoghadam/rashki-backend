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


class GalleryPagination(DefaultPagination):
    """
    Pagination specifically for Gallery lists.
    Inherits the custom response structure from DefaultPagination
    but uses a page size of 12.
    """

    page_size = 12


class IssuePagination(DefaultPagination):
    """
    Pagination specifically for Issue lists.
    Inherits the custom response structure from DefaultPagination
    but uses a page size of 12.
    """

    page_size = 12


class IssueCommentPagination(DefaultPagination):
    """
    Pagination specifically for Issue Comment lists.
    Inherits the custom response structure from DefaultPagination
    but uses a page size of 30 (or adjust as needed).
    """

    page_size = 30


class InvestmentPagination(DefaultPagination):
    """
    Pagination specifically for Investment lists.
    Inherits the custom response structure from DefaultPagination
    but uses a page size of 12.
    """

    page_size = 12


class ApprovedParticipantsPagination(DefaultPagination):
    """
    Pagination specifically for the list of approved participants (Investors)
    within an investment project.
    Inherits the custom response structure from DefaultPagination.
    Sets a page size suitable for this list
    """

    page_size = 15
