"""
Custom pagination classes for FlowPilot AI.
"""
from rest_framework.pagination import PageNumberPagination, CursorPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination with page size of 50.
    Allows client to set page size up to 100.
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        """Return paginated response with metadata."""
        return Response({
            'success': True,
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page_size': self.page_size,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })


class LargeResultsSetPagination(PageNumberPagination):
    """
    Pagination for large result sets with page size of 100.
    Allows client to set page size up to 500.
    """
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 500

    def get_paginated_response(self, data):
        """Return paginated response with metadata."""
        return Response({
            'success': True,
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page_size': self.page_size,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })


class ExecutionLogsPagination(CursorPagination):
    """
    Cursor-based pagination for execution logs.
    More efficient for large datasets with time-based ordering.
    """
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 500
    ordering = '-created_at'

    def get_paginated_response(self, data):
        """Return paginated response with metadata."""
        return Response({
            'success': True,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })
