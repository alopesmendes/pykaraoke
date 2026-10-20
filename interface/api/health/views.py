from django.http import HttpRequest, JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def health(request: HttpRequest) -> JsonResponse:
    """Liveness probe for Render and the Docker HEALTHCHECK. Touches nothing."""
    return JsonResponse({"status": "ok"})
