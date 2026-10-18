# 06: Static files pipeline via WhiteNoise

*What to learn from serving CSS and JS without a CDN. Milestone 1.*

**Shipped:** WhiteNoise serves `STATIC_ROOT` from gunicorn; `STORAGES` gives compressed, hashed
filenames; `make collectstatic` runs in `make check` and in `test.yml`.
**Files:** `pykaraoke/settings/base.py`, `Makefile`, `.github/workflows/test.yml`,
`docs/SETUP.md`, `pyproject.toml`, `uv.lock`

---

## Concepts

- **`STATIC_URL` vs `STATIC_ROOT`**: `STATIC_URL` is the URL prefix the browser asks for.
  `STATIC_ROOT` is the folder `collectstatic` copies every app's files into. Serving needs both
  to agree, and `STATIC_ROOT` is empty in dev unless you run collection.
- **`STORAGES` replaces `STATICFILES_STORAGE`**: since Django 5.1 storage backends are declared in
  one dict. Django 6.1 does not read `STATICFILES_STORAGE` at all. Setting it does nothing, with
  no error. Found by grepping Django's own source, not by a failing test.
- **Middleware order**: `WhiteNoiseMiddleware` sits right after `SecurityMiddleware`. It answers
  static requests early and skips the session, auth and CSRF work for them. Placed last, it would
  still serve files but after every other layer ran.
- **Manifest storage (`CompressedManifestStaticFilesStorage`)**: `collectstatic` writes
  `app.css` plus `app.<hash>.css` and `.gz` copies, and a manifest mapping one to the other.
  `{% static %}` looks up the hashed name. Hashed URLs can be cached forever. Cost: a template
  that names a file missing from the manifest raises at render time, but only with `DEBUG` off.
- **Why `collectstatic` runs in `make check` and CI**: manifest errors only appear in production
  mode. Running the collection with prod settings is the only local way to see them before deploy.

## Docs to read

- [ ] [Managing static files](https://docs.djangoproject.com/en/6.1/howto/static-files/).
  The `STATIC_ROOT` and `collectstatic` sections.
- [ ] [`STORAGES`](https://docs.djangoproject.com/en/6.1/ref/settings/#storages). The backend
  dict and the removal of `STATICFILES_STORAGE`.
- [ ] [WhiteNoise docs](https://whitenoise.readthedocs.io/en/stable/django.html). Why the
  middleware sits second, and what the manifest storage does.

## Hands-on

Do these in this repo, without Claude.

- [ ] Run `make collectstatic`, then open `staticfiles/admin/css/` and find a `.gz` file and a
  hashed filename. Explain what each one is for.
- [ ] Put `STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"` back
  into `base.py` and run `make collectstatic`. Confirm nothing changes in the output. Revert.
- [ ] Move `WhiteNoiseMiddleware` to the bottom of `MIDDLEWARE`, run the tests, and read what
  changes (if anything). Revert.
- [ ] Add `<link rel="stylesheet" href="{% static 'nope.css' %}">` to a template, run
  `DJANGO_SETTINGS_MODULE=pykaraoke.settings.prod` with a page render, and read the error. Revert.

## Quiz

Answer from memory. Open the answer only after committing to one.

1. You set `STATICFILES_STORAGE` in Django 6.1. What happens?
   <details><summary>Answer</summary>Nothing. Django no longer reads that setting, so the default
   storage stays in use with no warning.</details>
2. Why does `WhiteNoiseMiddleware` go right after `SecurityMiddleware`?
   <details><summary>Answer</summary>So static requests are answered early, skipping the session,
   auth and CSRF middleware that have no role for a static file.</details>
3. Why does the hashed filename let you cache a file forever?
   <details><summary>Answer</summary>The name changes whenever the content changes, so an old
   cached copy is never requested again under the new name.</details>
4. Why does `make collectstatic` pass the prod settings explicitly?
   <details><summary>Answer</summary>The manifest storage only behaves like production when
   `DEBUG` is off. The dev default would hide production-only errors.</details>

## Gotchas hit

- **`STATICFILES_STORAGE` from the issue was ignored by Django 6.1** → the setting was removed in
  5.1 → used `STORAGES["staticfiles"]`. The issue's checkbox wording still names the old setting.
- **First CI comment claimed `collectstatic` catches missing `{% static %}` references** → it does
  not; that only fails at render → comment rewritten to say what it actually checks.
- **Dockerfile does not run `collectstatic`** → the image would ship with no `staticfiles/`
  folder → not in this issue's scope; needed before any real deploy.

## Still unclear

- How the manifest is loaded at startup, and whether a missing `staticfiles/` folder makes
  WhiteNoise fail or just warn. Read `whitenoise/middleware.py`.
- How `CompressedManifestStaticFilesStorage` decides which files to gzip.
