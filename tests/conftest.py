"""Fixtures every test can use without importing them.

pytest-django already provides `db`, `client`, `admin_client` and `rf`.
This file adds the project's own: a saved member and a client logged in as them.
"""

import pytest
from django.test import Client
from factories import UserFactory


@pytest.fixture
def member(db) -> object:
    """A regular, non-staff user saved to the test database."""
    return UserFactory()


@pytest.fixture
def member_client(client: Client, member) -> Client:
    client.force_login(member)
    return client
