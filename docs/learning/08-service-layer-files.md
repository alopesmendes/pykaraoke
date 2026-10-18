# 08: The service layer files: services, exceptions, managers

*What to learn from the empty layer files. Milestone 1.*

**Shipped:** `karaoke/services.py`, `karaoke/exceptions.py`, `karaoke/managers.py`, each with a
one-line module docstring stating its job. No behaviour yet.
**Files:** `karaoke/services.py`, `karaoke/exceptions.py`, `karaoke/managers.py`

---

## Concepts

- **Where business logic lives**: `services.py` holds the rules and state changes. Views only
  translate HTTP into a service call and back. The rule is "never in a view or a template" because
  a rule in a view cannot be reused from a management command or a test without a request object.
- **Custom `Manager` vs custom `QuerySet`**: a `QuerySet` holds chainable filters
  (`SongRequest.objects.pending().for_event(event)`). A `Manager` is the entry point on the model
  (`objects`). Use `QuerySet.as_manager()` to get both from one class. Put a method on a `Manager`
  only when it is not a filter, such as a bulk operation that returns a new kind of result.
- **Module-level exceptions as a hierarchy**: a base `KaraokeError` lets a view catch "anything the
  app meant to raise" in one `except`. Subclasses carry the case (`EventFull`, `AlreadyRequested`).
  Without the base, the view either catches `Exception` (hides real bugs) or lists every case.
- **Django's built-in exceptions**: `ObjectDoesNotExist` and `ValidationError` already exist. A
  custom class earns its place only when the view must show a different toaster message, or when
  a service must refuse something Django would allow.
- **Layer direction**: `models.py` and `managers.py` never import from `services.py`. The arrow
  points from views to services to models. Reversing it creates a circular import at startup.

## Docs to read

- [ ] [Django: Managers, custom QuerySet and `as_manager()`](https://docs.djangoproject.com/en/6.1/topics/db/managers/#creating-a-manager-with-queryset-methods).
  Why `as_manager()` exists and when a plain `Manager` subclass is still right.
- [ ] [Django: Built-in exceptions](https://docs.djangoproject.com/en/6.1/ref/exceptions/).
  List what Django already raises before writing a new class.
- [ ] [Python: User-defined exceptions](https://docs.python.org/3/tutorial/errors.html#user-defined-exceptions).
  Why a base class is subclassed rather than raised directly.

## Hands-on

Do these in this repo, without Claude.

- [ ] Open `karaoke/services.py` and `karaoke/managers.py` side by side. Write down, in one
  sentence each, what a future function in each file would do and why it would not go in the
  other.
- [ ] In a shell (`uv run python manage.py shell`), `from karaoke import exceptions` and inspect
  `dir(exceptions)`. Confirm it is empty except for imports. Then explain why an empty module still
  matters for the import graph.
- [ ] Put a throwaway `class KaraokeError(Exception): pass` in `exceptions.py`, raise it in the
  shell, and catch it by its base name. Revert the file afterwards.

## Quiz

Answer from memory. Open the answer only after committing to one.

1. A view needs "list pending requests for this event". Filter on a `QuerySet` or add a `Manager`
   method?
   <details><summary>Answer</summary>A `QuerySet` method. It is a chainable filter, so it composes
   with other filters. A `Manager` method is for entry points that are not filters.</details>
2. Why should `services.py` never be imported by `models.py`?
   <details><summary>Answer</summary>The direction is views to services to models. The reverse
   creates a circular import, because services already import the models.</details>
3. Why does `KaraokeError` exist when `Exception` is available?
   <details><summary>Answer</summary>So a view can catch every app-raised error in one clause
   without catching unrelated bugs such as `KeyError`.</details>
4. What does `QuerySet.as_manager()` give you that a bare `QuerySet` does not?
   <details><summary>Answer</summary>A `Manager` wrapping the same methods, so
   `Model.objects.pending()` works. A bare `QuerySet` is not attached to the model.</details>

## Gotchas hit

- **No problems this session.** The three files are empty and have no code paths yet. The one
  point worth remembering: an empty module still runs its imports when Django loads the app, so a
  bad import added here later breaks startup, not just the feature.

## Still unclear

- The exact moment `ValidationError` should be raised from a service versus from a form. Not
  decided until Milestone 2 has real rules.
- `make check` printed `security.W018: DEBUG set to True in deployment` while the run used
  `pykaraoke.settings.prod`. Not investigated. Check which settings `check --deploy` actually loads
  before trusting that output.
