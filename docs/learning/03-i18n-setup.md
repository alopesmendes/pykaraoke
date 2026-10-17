# 03: i18n setup: fr default, ja secondary

*What to learn from the i18n wiring. Milestone 1.*

**Shipped:** French is the default language, Japanese is offered, and the browser's
`Accept-Language` header picks between them. No page is translated yet.
**Files:** `pykaraoke/settings/base.py`, `locale/`, `templates/base.html` (already used `{% translate %}`)

---

## Concepts

- **`LANGUAGE_CODE` vs `LANGUAGES`**: `LANGUAGE_CODE` is the fallback when nothing else picks a
  language. `LANGUAGES` is the whitelist of languages Django will ever activate. A browser asking
  for `de` gets `fr`, because `de` is not in the list.
- **`LocaleMiddleware` and per-request activation**: it reads the language for each request and
  activates it for that request's thread. Without it every request renders in `LANGUAGE_CODE`.
- **Middleware order**: the list runs top-down on the way in. `LocaleMiddleware` sits after
  `SessionMiddleware` (it may read the session) and before `CommonMiddleware` (later middleware
  should already see the active language).
- **`{% translate %}` / `{% trans %}` vs `{% blocktrans %}`**: `trans` translates one literal
  string. `blocktrans` translates a paragraph with `{{ variables }}` and plural forms. `{% load i18n %}`
  is needed in every template that uses them.
- **gettext workflow**: `makemessages` scans the source and writes `.po` files (human-edited text).
  `compilemessages` turns them into binary `.mo` files, which are what Django reads at runtime.
  `LOCALE_PATHS` must list the project-level `locale/` directory, or Django never looks there.

## Docs to read

- [ ] [Translation in your own projects](https://docs.djangoproject.com/en/6.1/topics/i18n/translation/#translations-in-your-own-projects). The settings and the workflow.
- [ ] [How Django discovers language preference](https://docs.djangoproject.com/en/6.1/topics/i18n/translation/#how-django-discovers-language-preference). The resolution order.
- [ ] [`LocaleMiddleware`](https://docs.djangoproject.com/en/6.1/topics/i18n/translation/#how-django-discovers-language-preference). Why it must come after `SessionMiddleware`.
- [ ] [`makemessages` and `compilemessages`](https://docs.djangoproject.com/en/6.1/topics/i18n/translation/#localization-how-to-create-language-files). The commands and their output.

## Hands-on

Do these without Claude.

- [ ] Run `uv run python manage.py shell`, then `from django.utils import translation` and
      `with translation.override("ja"): print(translation.gettext("pykaraoke"))`. You get `pykaraoke`
      back, because nothing is translated yet. Explain why.
- [ ] Wrap a new string in `{% translate "Bienvenue" %}` in a template, run `uv run python manage.py makemessages -l fr`,
      and find the new `msgid` in `locale/fr/LC_MESSAGES/django.po`. Fill its `msgstr`.
- [ ] Run `uv run python manage.py compilemessages`, then check the `.mo` file appeared.
      Explain why the `.po` is committed and the `.mo` is not.
- [ ] Move `LocaleMiddleware` above `SessionMiddleware` and read the Django docs section on why that is wrong. Put it back.

## Quiz

Answer from memory. Open the answer only after committing to one.

1. A browser sends `Accept-Language: de` and the site has `LANGUAGES = [fr, ja]`. Which language renders?
   <details><summary>Answer</summary>`LANGUAGE_CODE`, which is `fr`. `de` is not in `LANGUAGES`, so it is ignored.</details>
2. Why is `LocaleMiddleware` placed before `CommonMiddleware`?
   <details><summary>Answer</summary>So the active language is set before later middleware runs, and anything they render sees the right language.</details>
3. Which command writes the `.mo` file Django reads at runtime?
   <details><summary>Answer</summary>`compilemessages`. `makemessages` writes the `.po` source.</details>
4. A `locale/` directory sits at the project root and nothing in `LOCALE_PATHS` points at it. What happens to its translations?
   <details><summary>Answer</summary>Django never loads them. Only app `locale/` folders and `LOCALE_PATHS` are searched.</details>

## Gotchas hit

- **A top-level `locale/` directory is not searched by default** → Django only scans app locale
  folders and `LOCALE_PATHS` → added `LOCALE_PATHS = [BASE_DIR / "locale"]`. This line was not in the issue's
  checklist; it was added so the directory has a purpose.
- **`make check` ends with six `security.W0xx` warnings and looks like a failure** → the audit
  step runs `check --deploy` against local settings (DEBUG on, a dev secret key). The Makefile comment
  says these are expected. Read the exit status, not the warning count.

## Still unclear

- The Japanese switch was not tested at runtime. Only the settings are in place. A test with
  `Client().get(..., HTTP_ACCEPT_LANGUAGE="ja")` against a real page would prove it.
- `makemessages` was not run, so no `.po` files exist yet. The `gettext` binaries are installed
  (`msgfmt`, `xgettext` from Homebrew), so it will work when the first string is translated.
