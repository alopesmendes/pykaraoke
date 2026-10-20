"""The OpenAPI schema, Swagger UI and the temporary ping endpoint.

All three answer only while ENABLE_API_DOCS is on. Each test sets the flag
through the `settings` fixture, which is checked per request.
"""

import pytest
from django.test import Client


def test_schema_lists_the_ping_endpoint(client: Client, settings) -> None:
    settings.ENABLE_API_DOCS = True

    response = client.get("/api/schema/", secure=True)

    assert response.status_code == 200
    assert "/api/ping/" in response.content.decode()


def test_swagger_ui_is_served(client: Client, settings) -> None:
    settings.ENABLE_API_DOCS = True

    response = client.get("/api/docs/", secure=True)

    assert response.status_code == 200


def test_ping_answers_when_docs_are_on(client: Client, settings) -> None:
    settings.ENABLE_API_DOCS = True

    response = client.get("/api/ping/", secure=True)

    assert response.status_code == 200
    assert response.json() == {"status": "pong"}


@pytest.mark.parametrize("path", ["/api/schema/", "/api/docs/", "/api/ping/"])
def test_routes_are_hidden_when_docs_are_off(client: Client, settings, path: str) -> None:
    settings.ENABLE_API_DOCS = False

    response = client.get(path, secure=True)

    assert response.status_code == 404
