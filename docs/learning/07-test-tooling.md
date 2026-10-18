# 07: Test tooling: factories, shared fixtures, the db access model

*What to learn from the test scaffold. Milestone 1.*

**Shipped:** `tests/factories.py` (a `UserFactory`), `tests/conftest.py` (`member` and
`member_client` fixtures), `tests/test_factories.py` proving both work.
**Files:** `tests/factories.py`, `tests/conftest.py`, `tests/test_factories.py`

---

## Concepts

- **factory-boy vs raw `Model.objects.create()`**: a factory holds defaults in one place. A test
  overrides only what it cares about. Add a required field later and you edit one factory, not
  every `create()` call. The testing skill forbids direct `objects.create` in tests for this reason.
- **`Sequence` for unique fields**: `factory.Sequence(lambda n: f"singer{n}")` gives each user a
  new username. A fixed string would break on the second `UserFactory()` (unique constraint).
- **String model path `"auth.User"`**: the factory's `Meta.model` takes a string so the module can
  be imported before Django's app registry is ready. A class reference needs the registry. Reason
  taken from the factory-boy docs; not yet broken on purpose (see Hands-on).
- **pytest-django's `db` access model**: database access is blocked by default. A test needs the
  `db` fixture or the `django_db` mark. `member` depends on `db`, so anything built on it is
  allowed to write. A test that touches the ORM without it gets `RuntimeError: Database access not
  allowed`.
- **Fixture dependency chain**: `member_client` asks for `client` and `member`. pytest builds them
  in that order and passes the results in. Naming a fixture as an argument *is* the wiring.

## Docs to read

- [ ] [factory-boy: Django integration](https://factoryboy.readthedocs.io/en/stable/orms.html#django).
  `DjangoModelFactory`, and how string model paths are resolved.
- [ ] [factory-boy: Sequence](https://factoryboy.readthedocs.io/en/stable/reference.html#sequences).
  Why the counter is per factory class.
- [ ] [pytest-django: Database access](https://pytest-django.readthedocs.io/en/latest/database.html).
  `db` vs `django_db` vs `transactional_db`, and what the blocking error means.
- [ ] [pytest: fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html). `conftest.py`
  discovery, and why fixtures need no import.

## Hands-on

Do these in this repo, without Claude.

- [ ] Remove `db` from `member` and run `make test`. Read which test fails and the full error.
  Put `db` back.
- [ ] Change `"auth.User"` to `User` imported from `django.contrib.auth.models` at the top of
  `factories.py`, then run `make test`. Read the error. Revert. (Confirms the string-path reason.)
- [ ] Delete the `username` line in `UserFactory` and run the tests. Which assertion breaks, and
  why does the error mention a unique constraint?
- [ ] Run `uv run pytest -v` and notice the order. Explain why `test_factories.py` tests appear
  in two groups.

## Quiz

Answer from memory. Open the answer only after committing to one.

1. A test calls `UserFactory()` but has no `db` fixture and no `django_db` mark. What happens?
   <details><summary>Answer</summary>pytest-django raises `RuntimeError: Database access not
   allowed`. The database is blocked unless a test asks for it.</details>
2. Why use `factory.Sequence` for `username` instead of a fixed string?
   <details><summary>Answer</summary>Usernames are unique. A fixed value makes the second factory
   call fail the unique constraint.</details>
3. How does `conftest.py` make `member` available to a test without an import?
   <details><summary>Answer</summary>pytest discovers `conftest.py` automatically. A test that names
   `member` as an argument gets the fixture's return value.</details>
4. Why does `factories.py` use `model = "auth.User"` and not the class?
   <details><summary>Answer</summary>The module loads before Django's app registry is ready, and a
   class reference needs that registry.</details>

## Gotchas hit

- **`from factories import UserFactory` works with no `tests/__init__.py`** → pytest's default
  import mode puts `tests/` on `sys.path` → relying on this. Adding `__init__.py` later would turn
  it into a package import and break it.
- **A stale `tests/__pycache__/conftest.*.pyc` existed before any `conftest.py`** → left over from
  an earlier run → harmless, pytest ignores it when the source is missing. Clear with `make clean`.
- **Hook reformatted the new files after each write** → a formatter ran on save → no code change
  needed, but re-read a file before editing it again.

## Still unclear

- Whether `member(db) -> object` should be `-> User`. The return type is weak and the hook left
  it as written.
- Why `pytest-django` reorders DB tests before non-DB tests (seen in the output), and whether that
  can ever hide an ordering bug.
- How `factory.PostGenerationMethodCall` and `post_generation` differ, once a user needs a
  password or a relation set after creation.
