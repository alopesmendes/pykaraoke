# 10: Trimming the Claude setup to what the project uses

*What to learn from the Claude setup refactor (issue #29). Milestone 1.*

**Shipped:** 6 skills and 8 agents, each checked against the code it describes. Two agents merged
into one, and the test environment no longer reads a developer's `.env` by accident.
**Files:** `pyproject.toml`, `.claude/agents/verifier.md`, `.claude/skills/*/SKILL.md`,
`docs/AI-WORKFLOW.md`, `CLAUDE.md`

---

## Concepts

- **Environment variable precedence**: `pytest-env` sets variables before settings load, and
  `environ.Env.read_env` fills in only what is still unset. So a value in the shell or in
  `pytest-env` beats a developer's `.env`. Without that, a test passes on one laptop and fails on
  another.
- **Test isolation**: a test asserting a default (`ENABLE_API_DOCS` is off in prod) must pin the
  input it depends on. Asserting the default while leaving the input open tests the machine, not
  the code.
- **`manage.py check --deploy` and fail levels**: the command prints warnings and exits 0 unless
  `--fail-level` says otherwise. `make audit` prints warnings and passes; `security.yml` and the
  test suite use stricter levels. Know which one is the gate.
- **Two web layers in one project**: app pages are server-rendered MTV, and only the operational
  endpoints in `interface/api/` are DRF JSON. An agent that proposes DRF for a page is wrong here.
- **Registry drift**: a skill or agent that exists but is not listed in `CLAUDE.md` or
  `docs/AI-WORKFLOW.md` is one Claude will not find. Check both lists against `ls` after a change.

## Docs to read

- [ ] [Settings, and how `DJANGO_SETTINGS_MODULE` is chosen](https://docs.djangoproject.com/en/6.1/topics/settings/).
  Why `prod.py` is the one the suite is held to.
- [ ] [Deployment checklist](https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/).
  Which settings `--deploy` looks at and why.
- [ ] [System check framework: fail levels](https://docs.djangoproject.com/en/6.1/ref/checks/).
  What `--fail-level` and `--tag` do.
- [ ] [django-environ, `read_env`](https://django-environ.readthedocs.io/en/latest/). Whether an
  existing variable is overwritten.
- [ ] [pytest-env](https://pypi.org/project/pytest-env/). When its variables are set, relative to
  the settings import.

## Hands-on

Do these in this repo, without Claude.

- [ ] Add `ENABLE_API_DOCS=True` to a local `.env`, then run
  `uv run pytest tests/interface/test_settings.py::test_api_docs_are_off_in_prod_by_default`.
  Explain the failure, then remove the line.
- [ ] Remove the `ENABLE_API_DOCS=False` line from `pyproject.toml`, rerun the same test with
  the `.env` line in place, and read the traceback. Put the line back.
- [ ] Run `uv run python manage.py check --deploy` with and without `--fail-level WARNING`. Say
  why the exit code is the same in both.
- [ ] Run `ls .claude/agents .claude/skills .claude/commands` and match every name against the
  table in `docs/AI-WORKFLOW.md`. Find one name missing from the table, or confirm there is none.

## Quiz

Answer from memory. Open the answer only after committing to one.

1. Your `.env` has `ENABLE_API_DOCS=True`, and `pytest-env` does not set the variable. Which value
   does `settings.ENABLE_API_DOCS` have in a test run?
   <details><summary>Answer</summary>True. Read_env fills in unset variables from .env, and nothing
   overrides it.</details>
2. Why does `manage.py check --deploy` exit 0 while printing six warnings?
   <details><summary>Answer</summary>No `--fail-level` was given, so only errors fail the command.
   Warnings are printed and ignored.</details>
3. A view needs to return a list of events as JSON. Which layer and which tool does this project
   use for it?
   <details><summary>Answer</summary>`interface/api/` with DRF. App pages are MTV; only operational
   JSON uses DRF.</details>
4. Where does the rule "views never hold business rules" live, and where does "a model method
   never spans two objects" live?
   <details><summary>Answer</summary>Both live in `django-mtv`: the layer rules are in
   `layers-and-python.md`, and the Django model rules are in `SKILL.md`.</details>

## Gotchas hit

- **`make check` failed on `test_api_docs_are_off_in_prod_by_default`** → a local `.env` set
  `ENABLE_API_DOCS` and the test did not pin it → pinned `ENABLE_API_DOCS=False` in the pytest env.
- **The issue said `frontend-patterns` had no template to review, but `templates/base.html` already
  had the toaster and modal regions** → the agent was deleted because frontend work moves to a later
  part, and `base.html` was left in place.
- **A `git rm` staged the deletions without being asked** → `git rm` stages by default → used
  `git restore --staged` to leave them unstaged for `/commit-push-pr` to stage by name.

## Still unclear

- Whether a Django 6.1 `fetch_mode` claim in `django-mtv` is accurate for this version. It is
  documented by the skill and not yet checked against the Django release notes.
- How `pytest-env` and `read_env` interact when a variable appears in both `pyproject.toml` and
  the shell. The fix works; the precedence rule is not confirmed in the plugin's docs.
