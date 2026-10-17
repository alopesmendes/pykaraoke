# 02: Base template and template directory

*What to learn from `base.html` and the project `templates/` dir. Milestone 1, issue #7.*

**Shipped:** every page can extend one shell with a content block, an empty toaster region and an
empty modal container. `TEMPLATES["DIRS"]` points at the project `templates/` folder.
**Files:** `templates/base.html`, `pykaraoke/settings/base.py`, `tests/test_base_template.py`

---

## Concepts

- **Template inheritance**: a child says `{% extends "base.html" %}` and fills `{% block content %}`.
  Everything outside blocks in the child is ignored. Without a block in the parent, the child's
  content has nowhere to go and silently disappears.
- **`TEMPLATES["DIRS"]` vs `APP_DIRS`**: `DIRS` is searched first, as absolute paths. `APP_DIRS=True`
  then searches each installed app's `templates/` folder. A name in both places resolves to the
  `DIRS` copy, so project files can shadow app files.
- **`BASE_DIR / "templates"`**: `pathlib` joins paths with `/`. A plain string `"templates"` would
  be relative to the process working directory, so it breaks when `manage.py` runs from elsewhere.
- **Shared shell in the base, not per page**: the toaster and modal are needed by every page that
  has a form. Putting them in the base means one place to change, and no page can forget them.
- **`{% load i18n %}` and `{% get_current_language %}`**: the tag must be loaded in the file that
  uses it. The `lang` attribute is set from the active language, so the French and Japanese
  locales will not need a second base file.

## Docs to read

- [ ] [Template inheritance](https://docs.djangoproject.com/en/6.1/topics/templates/#template-inheritance):
      what a parent block is, and what a child block outside `{% block %}` does
- [ ] [`DIRS` and `APP_DIRS`](https://docs.djangoproject.com/en/6.1/ref/templates/api/#django.template.backends.django.DjangoTemplates):
      the search order
- [ ] [Internationalization in templates](https://docs.djangoproject.com/en/6.1/topics/i18n/translation/#translations-in-your-own-projects):
      `{% translate %}` and `{% get_current_language %}`

## Hands-on

- [ ] Add `{% block sidebar %}{% endblock %}` to `base.html`, then write a child that fills it and
      one that does not. Compare the HTML.
- [ ] Put a file `templates/base.html` copy in `karaoke/templates/karaoke/` with a different
      `<title>`. Which one does `get_template("base.html")` return? Then delete the copy.
- [ ] Change `BASE_DIR / "templates"` to `"templates"` in `base.py`, run
      `uv run python manage.py shell -c "from django.template.loader import get_template; print(get_template('base.html').origin.name)"`
      from another directory, and read the error.
- [ ] Run `uv run pytest tests/test_base_template.py -v` and explain why the test checks
      `origin.name` and not just that the call succeeds.

## Quiz

1. A child template has `<h1>Hi</h1>` outside any `{% block %}`. Does it appear in the output?
   <details><summary>Answer</summary>No. Only block contents of a child template are used when it
   extends a parent. Text outside blocks is dropped.</details>
2. Both `templates/base.html` and `karaoke/templates/base.html` exist. Which one wins, and why?
   <details><summary>Answer</summary>The one in `templates/`, because `DIRS` is searched before
   `APP_DIRS`.</details>
3. Why is `"templates"` a worse `DIRS` entry than `BASE_DIR / "templates"`?
   <details><summary>Answer</summary>A relative path is resolved against the current working
   directory, so it depends on where the process starts.</details>
4. What does `{% block content %}{% endblock %}` in the parent do if the child does not define it?
   <details><summary>Answer</summary>The parent's default contents are rendered, here empty.</details>

## Gotchas hit

- No failures this session. Tests and lint passed on the first run. The one judgement call: the
  toaster and modal are empty divs, so the tests assert on their `id` attributes, not on text.

## Still unclear

- How `get_template` caches templates in production (the cached loader) versus `DEBUG` mode, and
  why template edits sometimes need a restart.
- `{% get_current_language as ... %}` versus the `LANGUAGE_CODE` context processor.
