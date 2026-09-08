---
name: python-standards
description: Python coding conventions for pykaraoke — type hints, early returns, naming, error handling, and the Ruff rules this repo enforces. Use when writing or reviewing any .py file, when a lint error needs explaining, when deciding how to raise or handle an exception, or when asked "is this Pythonic?".
---

# Python standards (pykaraoke)

Python 3.13+. Ruff is the only linter/formatter — no Black, no Flake8, no isort.

## Non-negotiables

1. **Type hints on every function signature.** Never `Any`. Use `X | None`, not `Optional[X]`.
2. **Early return over nesting.** Max 2 levels of indentation inside a function body.
3. **No bare `except:`** and no `except Exception` without re-raising or logging.
4. **f-strings** for interpolation. Never `%` or `.format()`.
5. **No mutable default arguments.** Ruff `B006` catches it.

## Shape of a function

```python
def reserve_seat(event: KaraokeEvent, pseudo: str) -> Participant:
    """Reserve a seat, or put the participant on the waiting list."""
    if not event.is_open:
        raise EventClosedError(event.pk)

    if event.seats_left <= 0:
        return Participant.objects.create(event=event, pseudo=pseudo, status=Status.WAITING)

    return Participant.objects.create(event=event, pseudo=pseudo, status=Status.CONFIRMED)
```

Read it top to bottom: guard clauses first, happy path last, one return type.

## Naming

| Thing    | Convention               | Example                |
|----------|--------------------------|------------------------|
| Module   | `snake_case`, singular   | `services.py`          |
| Class    | `PascalCase`             | `SongRequest`          |
| Function | `snake_case`, verb first | `cancel_reservation`   |
| Boolean  | `is_` / `has_` / `can_`  | `is_open`, `has_seat`  |
| Constant | `UPPER_SNAKE`            | `MAX_SONGS_PER_PERSON` |
| Private  | leading `_`              | `_build_token`         |

Never abbreviate: `participant`, not `part`. Never `data`, `info`, `obj`, `tmp` as a name.

## Errors

Domain failures get their own exception class in the app's `exceptions.py`:

```python
class KaraokeError(Exception):
    """Base for every domain failure in this app."""


class EventClosedError(KaraokeError):
    def __init__(self, event_id: int) -> None:
        super().__init__(f"Event {event_id} is closed for sign-ups.")
        self.event_id = event_id
```

Views catch `KaraokeError` and turn it into a message + redirect. Services raise, never
return `None` to signal failure. Never `return False` as an error channel.

## Ruff rule families enabled, and why

| Code     | Family                 | Why it's on                                                       |
|----------|------------------------|-------------------------------------------------------------------|
| `E`, `F` | pycodestyle / Pyflakes | Baseline correctness: undefined names, unused imports             |
| `I`      | isort                  | Import ordering, replaces the isort tool                          |
| `UP`     | pyupgrade              | Keeps syntax modern for the target Python                         |
| `B`      | bugbear                | Mutable defaults, loop-variable capture, silent `except`          |
| `S`      | bandit-in-ruff         | Catches `assert` in prod code, weak hashes, hardcoded secrets     |
| `DJ`     | flake8-django          | `null=True` on `CharField`, missing `__str__`, `Model.Meta` order |
| `C4`     | comprehensions         | `list(x for ...)` → `[x for ...]`                                 |
| `SIM`    | simplify               | Collapses redundant `if`/`else`, nested `with`                    |

Per-file ignores: `tests/**` drops `S101` (asserts are the point) and `**/migrations/**` is
excluded entirely (generated code).

## When Ruff and readability disagree

Ruff wins on style. If a rule is genuinely wrong for a line, add a scoped
`# noqa: <CODE>  # reason` on that line — never a file-level or blanket `# noqa`. A `noqa`
without a reason comment is a review blocker.

## Docstrings

One-line docstring on anything non-obvious: every service function, every model method, every
custom manager. Skip them on views whose name and template already say everything. Explain
**why**, not what the code already shows.

## See also

- Test conventions: skill `testing`
- Where logic belongs (model vs service vs view): skill `clean-architecture`
- Django-specific ORM and form rules: skill `django-mtv`
