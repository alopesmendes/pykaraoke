# 04: Wire PostgreSQL via DATABASE_URL

*What to learn from the database switch. Milestone 0.*

**Shipped:** `DATABASES` reads one `DATABASE_URL`; blank means SQLite, a URL means Postgres.
**Files:** `pykaraoke/settings/base.py`, `docs/SETUP.md` (already documented), `.env.example` (unverified)

---

## Concepts

- **`env.db_url_config()`**: django-environ parses a URL like `postgres://user:pw@host:5432/name`
  into the dict Django's `DATABASES` expects (`ENGINE`, `HOST`, `NAME`...). Hand-parsing it is
  what `dj-database-url` would do; we did not add that dependency.
- **Absent vs blank env key**: `env("X", default=...)` only uses the default when `X` is *not set*.
  `X=` in `.env` is set to `""`, so the default is skipped. `base.py` adds `or sqlite...` to
  catch the blank case. Without it, `ENGINE` becomes `''` and Django fails on first query.
- **Separate databases**: `db.sqlite3` and the Postgres database share no data. Switching
  `DATABASE_URL` means running `migrate` again on the new one.
- **`CONN_MAX_AGE`**: Django defaults to `0`, so each request opens and closes a connection. That
  is the simple, safe default. Persistent connections or a pool trade that for fewer handshakes.
- **`ATOMIC_REQUESTS`**: wraps each view in one transaction. A view that raises rolls back every
  write it made. Off by default; turning it on also holds locks for the whole request.

## Docs to read

- [ ] [Databases setting](https://docs.djangoproject.com/en/6.1/ref/settings/#databases). The
  shape `DATABASES` must have.
- [ ] [Persistent database connections](https://docs.djangoproject.com/en/6.1/ref/databases/#persistent-connections).
  Why `CONN_MAX_AGE` exists and what it risks.
- [ ] [Tying transactions to HTTP requests](https://docs.djangoproject.com/en/6.1/topics/db/transactions/#tying-transactions-to-http-requests).
  `ATOMIC_REQUESTS` and its cost.
- [ ] [django-environ](https://django-environ.readthedocs.io/en/latest/). `db_url_config` and the
  `default=` rule.

## Hands-on

Do these in this repo, without Claude.

- [ ] Set `DATABASE_URL=` (blank) and run `uv run python manage.py shell -c "from django.conf
  import settings; print(settings.DATABASES['default']['ENGINE'])"`. Expect sqlite3. Then delete
  the `or` in `base.py` on a branch and see what changes.
- [ ] With `make db-up` running, set the Postgres URL and run `make migrate`. Count the tables
  that appear in `psql` and compare with `db.sqlite3`.
- [ ] Set `CONN_MAX_AGE=60` in `base.py` on a branch and explain what changes in
  `connection.close()` behaviour.

## Quiz

Answer from memory. Open the answer only after committing to one.

1. `.env` contains `DATABASE_URL=`. Which database does Django use?
   <details><summary>Answer</summary>SQLite. The key is set to "", the default is skipped, and the
   `or` falls back to `db.sqlite3`.</details>
2. What does `CONN_MAX_AGE = 0` (the default) mean for a request?
   <details><summary>Answer</summary>Django closes the database connection at the end of the request.
   The next request opens a new one.</details>
3. `ATOMIC_REQUESTS = True`, and the view writes two rows, then raises. What is in the database?
   <details><summary>Answer</summary>Neither row. The whole view ran inside one transaction, which
   is rolled back on the exception.</details>
4. You switch `DATABASE_URL` from SQLite to Postgres. Do your users still exist?
   <details><summary>Answer</summary>Not until you run `migrate` and load data. They are in the old
   SQLite file, a separate database.</details>

## Gotchas hit

- **Issue said "add `dj-database-url`", but the code already parsed the URL** → django-environ
  already provides `db_url_config` → ticked the parse and SQLite-fallback items, no new dependency.
- **Blank `DATABASE_URL=` produced an unusable engine** → `default=` only covers absent keys → the
  explicit `_database_url or sqlite...` fallback in `base.py`.
- **Could not read `.env.example`** (permission rule denied reads and grep) → the doc item stays
  unchecked until someone confirms the `DATABASE_URL` line is there.
- **`make db-up` cannot run here** (Docker not installed) → the Postgres connection item stays
  unchecked. Install Docker and run it.
- **`make check` prints six `security.W0xx` warnings** → `manage.py` defaults to dev settings
  (DEBUG on), so `check --deploy` flags them. Expected; `prod.py` is what the tests use.

## Still unclear

- Connection pooling: `CONN_MAX_AGE` vs Django 6.1's own pool option. Not tried.
- Whether `ATOMIC_REQUESTS` is worth its lock cost for this app.
- SQLite vs Postgres drift: case-sensitivity of `LIKE`, and how the ORM handles `JSONField`.
