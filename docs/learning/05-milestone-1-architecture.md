# 05: Milestone 1 close-out: an empty app that boots

*What to learn from the project skeleton. Milestone 1.*

**Shipped:** `karaoke` is a registered, empty Django app; settings are split per environment; the
site boots with `manage.py check` and the test suite.
**Files:** `karaoke/apps.py`, `karaoke/models.py`, `karaoke/admin.py`, `karaoke/views.py`,
`pykaraoke/settings/{base,dev,prod}.py`, `manage.py`

---

## Concepts

- **App registry (`INSTALLED_APPS`)**: `startapp` only creates a folder. Until `"karaoke"` is in
  `INSTALLED_APPS`, Django ignores it: no model discovery, no migrations, no admin, no app
  templates via `APP_DIRS`.
- **`AppConfig` and `default_auto_field`**: `karaoke/apps.py` declares `BigAutoField`, so every
  implicit primary key is a 64-bit integer. Django auto-detects a single `AppConfig` subclass in
  `apps.py`; no `default_app_config` line is needed any more.
- **Settings module selection**: `manage.py` calls `setdefault("DJANGO_SETTINGS_MODULE", ...dev)`.
  `setdefault` only fills the variable when it is unset, so an exported variable wins. Production
  gets `prod` by setting it explicitly.
- **Layers are plain modules**: `services.py`, `exceptions.py` and `managers.py` are not Django
  features. Django never imports them. A view must import `services` and call it. This is why
  "business logic in `services.py`" is a convention enforced by review, not by the framework.
- **Why split per environment before Milestone 2**: M2 adds access tokens and cookies. Those need
  `Secure`, HSTS and SSL redirect in prod, and `DEBUG` off. `manage.py check --deploy` only means
  something if prod has those flags on from day one.

## Docs to read

- [ ] [Applications](https://docs.djangoproject.com/en/6.1/ref/applications/). What `AppConfig`
  holds and how Django finds it.
- [ ] [`startapp`](https://docs.djangoproject.com/en/6.1/ref/django-admin/#startapp). What the
  generated files are for, one by one.
- [ ] [Deployment checklist](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/).
  The flags `prod.py` must set.

## Hands-on

Do these in this repo, without Claude.

- [ ] Comment out `"karaoke"` in `INSTALLED_APPS`, run `python manage.py makemigrations karaoke`,
  read the error, then restore the line.
- [ ] Run `python manage.py check --deploy --settings=pykaraoke.settings.prod` and list which
  warnings are about settings you can see in `prod.py`.
- [ ] Run `python manage.py shell -c "from django.conf import settings; print(settings.SETTINGS_MODULE, settings.DEBUG)"`
  with and without `DJANGO_SETTINGS_MODULE` exported. Explain both outputs.
- [ ] Open `karaoke/apps.py`, change `default_auto_field` to `AutoField`, and find where it shows
  up (`makemigrations` output or `sqlmigrate`). Revert it.

## Quiz

Answer from memory. Open the answer only after committing to one.

1. You run `startapp karaoke` but forget `INSTALLED_APPS`. What happens to a model you add to
   `karaoke/models.py`?
   <details><summary>Answer</summary>Nothing. Django never imports it, so no migration is created
   and the table never exists.</details>
2. What does `os.environ.setdefault` do when `DJANGO_SETTINGS_MODULE` is already exported?
   <details><summary>Answer</summary>It keeps the exported value. It only sets the variable when
   it is absent.</details>
3. What does `BigAutoField` change compared with `AutoField`?
   <details><summary>Answer</summary>The implicit primary key is a 64-bit integer instead of a
   32-bit one, so the id space does not run out at about 2.1 billion rows.</details>
4. Why does `views.py` need an explicit `from . import services`?
   <details><summary>Answer</summary>`services.py` is an ordinary Python module. Only the names
   Django loads by convention (models, admin, app config, migrations) are imported for you.</details>
5. Which settings file must a production deploy use, and what does a `DEBUG = True` there expose?
   <details><summary>Answer</summary>`pykaraoke.settings.prod`. With `DEBUG = True` the error
   pages show tracebacks and settings to visitors.</details>

## Gotchas hit

- **The close-out was first planned before its work was done.** `EPICS.md` still listed the
  layer files, WhiteNoise and `tests/factories.py` as open, so the milestone was not finished
  when the issue said it was. The fix was to finish those items first (see checklists 06–08)
  and tick the Milestone 1 boxes only when the files exist.

## Still unclear

- Exact order in which Django imports `apps.py`, `models.py` and `admin.py` at startup. Read
  `django/apps/registry.py` once.
- Why a view should never hold business rules: what breaks when `reserve_seat` lives in a view
  and a management command both need it.
