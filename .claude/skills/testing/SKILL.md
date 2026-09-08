---
name: testing
description: Test conventions for pykaraoke — pytest-django, fixtures vs factory-boy, what is worth testing in an MTV app, and coverage rules. Use when writing or reviewing a test, when a test is flaky or slow, when deciding what to cover for a new feature, or when asked "do I need a test for this?".
---

# Testing (pykaraoke)

`pytest` + `pytest-django` + `factory-boy`. No `unittest.TestCase`, no `django.test.TestCase`
subclassing — plain functions and fixtures.

## Layout

```
tests/
  conftest.py              # shared fixtures
  factories.py             # factory-boy factories, one per model
  test_smoke.py            # settings load, system checks pass
  karaoke/
    test_models.py         # constraints, properties, custom QuerySets
    test_forms.py          # validation rules, error messages
    test_services.py       # business rules — the densest file
    test_views.py          # status codes, redirects, template used, auth gating
```

Mirror the source tree. One test module per source module.

## Naming

`test_<unit>_<condition>_<expected>`:

```python
def test_reserve_seat_when_event_full_puts_participant_on_waiting_list(): ...
def test_sign_up_form_rejects_pseudo_shorter_than_two_chars(): ...
def test_overview_view_with_invalid_token_returns_404(): ...
```

The name is the spec. If you cannot name it this way, you do not know what you are testing.

## Fixtures vs factories

- **factory-boy** builds model instances. One factory per model in `tests/factories.py`,
  `Sequence` for unique fields, `SubFactory` for FKs, traits for variants.
- **pytest fixtures** wire the scenario (a client, a logged-in participant, a full event).
- Never call `Model.objects.create(...)` directly in a test — go through the factory, so adding a
  required field breaks one file instead of forty.

```python
class ParticipantFactory(DjangoModelFactory):
    class Meta:
        model = Participant

    event = factory.SubFactory(KaraokeEventFactory)
    pseudo = factory.Sequence(lambda n: f"singer{n}")
    status = Participant.Status.CONFIRMED
```

## Database access

`@pytest.mark.django_db` on anything touching the ORM. Without it the test fails loudly — that is
intentional, it keeps pure-logic tests fast.

Use `django_assert_num_queries` to lock in query counts on overview pages:

```python
def test_overview_does_not_n_plus_one(client, django_assert_num_queries, event):
    ParticipantFactory.create_batch(20, event=event)
    with django_assert_num_queries(3):
        client.get(reverse("karaoke:overview", args=[event.access_token]))
```

## What to test, per layer

| Layer    | Test                                                       | Skip                          |
|----------|------------------------------------------------------------|-------------------------------|
| Model    | constraints, custom QuerySet methods, computed properties  | plain field declarations      |
| Form     | each `clean_*` rule, the error message text                | Django's own field validation |
| Service  | every business rule and every raised domain exception      | ORM plumbing                  |
| View     | status code, redirect target, template used, access gating | HTML markup details           |
| Template | only via view tests asserting a string is present          | rendering internals           |

Do not test Django. Test **your** rules.

## Coverage

`--cov=. --cov-fail-under=70` in CI. Coverage is a floor, not a target — a green 70% with the
service layer untested is a failing test suite. `htmlcov/` is gitignored; run `make cov` and open
it when a number looks wrong.

## Speed

- No `time.sleep`. Freeze time with a fixture if a test depends on it.
- No real network, no real email — `EMAIL_BACKEND` is the locmem backend under test, then assert
  on `mail.outbox`.
- `pytest -x -q` while iterating; the full run happens in CI.

## Before you say a feature is done

1. `make test` green.
2. A test exists that fails if the feature is reverted.
3. Every domain exception has a test that triggers it.
4. `docs/learning/` checklist updated — see skill `learning-checklist`.

## See also

- Function shape and error classes: skill `python-standards`
- Where the rule under test should live: skill `clean-architecture`
- Deeper coverage audits: agent `eval-harness`
