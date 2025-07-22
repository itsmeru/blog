from rest_framework.renderers import JSONRenderer


class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context["response"]
        status_code = response.status_code
        context_data = getattr(response, "context", {}) or {}
        message = context_data.get("message", "ok")
        errors = context_data.get("errors", None)

        # 判斷請求是否成功
        success = renderer_context.get("success", 200 <= status_code < 300)

        response_data = {
            "success": success,
            "message": message,
            "data": data,
        }
        if errors is not None:
            response_data["errors"] = errors
            response_data["data"] = context_data.get("data")

        return super().render(response_data, accepted_media_type, renderer_context)
