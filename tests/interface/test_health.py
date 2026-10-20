"""GET /health/ answers 200 without a database or a logged-in user.

No `db` mark on purpose: pytest-django blocks database access in unmarked
tests, so any query made by the health view fails this test.
"""

from django.test import Client


def test_health_returns_ok_for_an_anonymous_client(client: Client) -> None:
    response = client.get("/health/")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
