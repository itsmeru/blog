from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = "size"
    page_query_param = "page"
    max_page_size = 100
    page_size = 10

    def get_paginated_response(self, data):
        return Response(
            {
                "success": True,
                "message": "查詢成功",
                "pagination": {
                    "count": self.page.paginator.count,
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "data": data,
            }
        )
