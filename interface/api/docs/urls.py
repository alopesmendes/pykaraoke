from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from interface.api.guards import api_docs_only

urlpatterns = [
    path("api/schema/", api_docs_only(SpectacularAPIView.as_view()), name="schema"),
    path(
        "api/docs/",
        api_docs_only(SpectacularSwaggerView.as_view(url_name="schema")),
        name="swagger-ui",
    ),
]
