"""Shared test data builders.

Each factory builds a saved-or-unsaved model with valid defaults. A test
overrides only the fields it cares about, so the test reads as its own
scenario. Karaoke models get their factories here when Milestone 2 adds them.
"""

import factory
from factory.django import DjangoModelFactory


class UserFactory(DjangoModelFactory):
    # String path, not the class: this module imports before Django's app
    # registry is ready, and a class reference would need it.
    class Meta:
        model = "auth.User"

    username = factory.Sequence(lambda n: f"singer{n}")
    email = factory.LazyAttribute(lambda user: f"{user.username}@example.test")
