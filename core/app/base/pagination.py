from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "success": {"type": "boolean", "default": True},
                "message": {"type": "string", "default": "ok"},
                "data": {
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer", "example": 123},
                        "next": {
                            "type": ["string", "null"],
                            "format": "uri",
                            "example": None,
                        },
                        "previous": {
                            "type": ["string", "null"],
                            "format": "uri",
                            "example": None,
                        },
                        "results": schema,
                    },
                },
            },
            "required": ["success", "message", "data"],
        }
