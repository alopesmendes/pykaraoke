from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from interface.api.guards import api_docs_only
from interface.api.ping.serializers import PingSerializer


class PingView(APIView):
    """Temporary endpoint so the OpenAPI schema has a path. Remove with the first real endpoint."""

    permission_classes = [AllowAny]

    @extend_schema(responses=PingSerializer)
    def get(self, request: Request) -> Response:
        return Response({"status": "pong"})


ping = api_docs_only(PingView.as_view())
