---
name: django-mtv
description: Django 6.1 MTV patterns for pykaraoke — models, QuerySets, migrations, forms, views, templates, and URL naming. Use when creating or changing a model, writing a migration, building a form, adding a view or URL, editing a template, or fixing an N+1 query. Also use when choosing between a function-based and a class-based view.
---

# Django MTV (pykaraoke)

Django 6.1, PostgreSQL 15+. Project package `pykaraoke/` holds settings only; app code lives in
the `karaoke/` app. See `docs/ARCHITECTURE.md` for the layout, `docs/DATABASE.md` for the models.

## Models

```python
class Participant(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = "confirmed", _("Confirmed")
        WAITING = "waiting", _("Waiting list")
        CANCELLED = "cancelled", _("Cancelled")

    event = models.ForeignKey(
        "karaoke.KaraokeEvent", on_delete=models.CASCADE, related_name="participants"
    )
    pseudo = models.CharField(max_length=40)
    status = models.CharField(max_length=16, choices=Status, default=Status.WAITING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["event", "pseudo"], name="unique_pseudo_per_event"),
        ]
        ordering = ["created_at"]

    def __str__(self) -> str:
        return f"{self.pseudo} @ {self.event}"
```

Rules:
- **Never `null=True` on a text field.** Use `blank=True` + `default=""`. Ruff `DJ001` enforces it.
- **Always name your `related_name`.** `participants`, not `participant_set`.
- **Always `__str__`.** The admin overview page depends on it.
- Enforce invariants in the database with `UniqueConstraint` / `CheckConstraint`, not only in forms.
- `TextChoices` for every status field. Never free-form strings.

## QuerySets and N+1

Query logic goes on a custom manager/QuerySet, never inline in a view:

```python
class ParticipantQuerySet(models.QuerySet):
    def confirmed(self) -> "ParticipantQuerySet":
        return self.filter(status=Participant.Status.CONFIRMED)

    def for_overview(self) -> "ParticipantQuerySet":
        return self.select_related("event").prefetch_related("song_requests")
```

- `select_related` for forward FK / one-to-one. `prefetch_related` for reverse FK / M2M.
- Django 6.1 adds **fetch modes**: `.fetch_mode(models.FETCH_PEERS)` makes an unfetched field
  access load that field for every instance from the same queryset in one query. Good safety net
  for templates, **not** a replacement for `select_related` — reach for it when a template
  touches a field you did not plan for.
- Set `DEBUG_TOOLBAR` query count as the check: an overview page must be O(1) queries, not O(n).

## Migrations

- One migration per logical change; run `python manage.py makemigrations` and **read the file**
  before committing.
- Never edit an applied migration. Add a new one.
- Data migrations get `RunPython(forward, reverse)` — always supply the reverse.
- `python manage.py makemigrations --check --dry-run` runs in CI: a model change without a
  migration fails the build.

## Forms

Validation lives in the form for input shape, in the service for business rules.

```python
class SignUpForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ["pseudo", "full_name"]

    def clean_pseudo(self) -> str:
        pseudo = self.cleaned_data["pseudo"].strip()
        if len(pseudo) < 2:
            raise forms.ValidationError(_("Pseudo must be at least 2 characters."))
        return pseudo
```

- `clean_<field>` for one field, `clean()` for cross-field rules.
- Never trust a hidden field for identity — the event comes from the URL, not the POST body.
- Every user-facing string wrapped in `gettext_lazy as _` (FR is the default locale).

## Views

**Default to function-based views.** Reach for a CBV only when you get a real generic for free
(`ListView`, `DetailView`) with no `get_context_data` gymnastics.

```python
@require_http_methods(["GET", "POST"])
def sign_up(request: HttpRequest, token: str) -> HttpResponse:
    event = get_object_or_404(KaraokeEvent, access_token=token)
    form = SignUpForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        services.reserve_seat(event, **form.cleaned_data)
        messages.success(request, _("Your seat is reserved."))
        return redirect("karaoke:overview", token=token)

    return render(request, "karaoke/sign_up.html", {"form": form, "event": event})
```

- Views orchestrate; they never contain business rules. See skill `clean-architecture`.
- POST that changes state always redirects (POST/Redirect/GET). No re-render on success.
- `django.contrib.messages` drives the toaster.

## URLs

`app_name = "karaoke"` in `karaoke/urls.py`; always reverse by name, never hardcode a path.

| Name               | Pattern                                    |
|--------------------|--------------------------------------------|
| `karaoke:sign_up`  | `<str:token>/sign-up/`                     |
| `karaoke:overview` | `<str:token>/`                             |
| `karaoke:cancel`   | `<str:token>/cancel/<int:participant_id>/` |

Routes are specified in `docs/API.md` — update it in the same change.

## Templates

- `templates/base.html` holds `{% block content %}`, the toaster region, and the modal container.
- Partials live in `templates/karaoke/partials/` and are named `_participant_row.html`.
- Logic in templates is limited to `{% if %}` / `{% for %}`. Anything computed goes in the view
  context or a model property.
- `{% csrf_token %}` in every POST form. `{% translate %}` / `{% blocktranslate %}` for text.

## See also

- Layer boundaries: skill `clean-architecture`
- Testing models, forms, views: skill `testing`
- Template/HTMX/toaster patterns: agent `frontend-patterns`
