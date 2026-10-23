---
name: sign-up-sign-in
description: Sign-up / Sign-in as an anonymus user
branch: feat/28-sign-up-sign-in-as-an-anonymus-user
issue: 28
tools: Read, Glob, Grep, Bash, Edit, Write
model: claude-sonnet-5-5
effort: medium
memory: none
level: beginner
---

# 13: Sign-up / Sign-in as an anonymous user

*What to learn from passwordless access with a one-time recovery code and a JWT pair. Milestone 2.*

**Shipped so far:** a participant signs up with a fullname and a pseudo, gets a recovery code once and a token pair, and signs in again with pseudo and code. Refresh and admin reset are not built yet.
**Files:** `domain/karaoke/entities.py`, `application/karaoke/services.py`, `infrastructure/db/karaoke/repositories.py`, `infrastructure/security/tokens.py`, `interface/api/karaoke/views.py`, `pykaraoke/composition.py`

---

## Progress

Steps follow the layers: domain, application, infrastructure, interface. Tests come before code in each step.

### Done

| Step | What | Commit |
|------|------|--------|
| 1 | Domain: `Participant`, `Admin`, `RecoveryCode`, domain exceptions, length rules (120 and 60) | `35fcb9a` |
| 2a | Use case `sign_up` (128-bit code, only the hash is kept) | `30d5768` |
| 2b | Use case `sign_in` (constant-time compare, dummy hash for an unknown pseudo, one `InvalidCredentials`) | `167a9ec` |
| 2c | Use case `reset_recovery_code` (staff only, revokes all refresh tokens, logs ids only) | `86150eb` |
| 3a | Django models, migration, case-insensitive unique pseudo, `DjangoParticipantRepository` | `cc112e6` |
| 3b | `Sha256RecoveryCodeHasher`, `SimpleJwtTokenIssuer`, JWT settings and `JWT_SIGNING_KEY` in env, CI and Docker | `893287a` |
| 4a | Interface: sign-up and sign-in views, serializers, urls, composition root, interface tests | `96cec74` |
| tooling | `/guide next` mode | `6324b53` |

### Shown, not committed yet

| Step | What |
|------|------|
| 4b-1 | `TokenIssuer.refresh` port, `refresh_tokens` use case, simplejwt implementation, `Admin.id` becomes `str` |

### Missing

| Step | What | Requirement |
|------|------|-------------|
| 4b-2 | Refresh view, admin reset view (Django session, CSRF, non-staff gets 404), composition wiring | 10, 11, 13, 12 |
| 4c | Throttles: sign-in 5/min, sign-up 10/h, admin reset 10/h. Optional `ATOMIC_REQUESTS` so a failed token issue rolls back the sign-up | 12, 17 |
| 4d | Remove the temporary `ping` endpoint, its url, tests and doc line | |
| docs | `docs/DATABASE.md`, `docs/API.md`, `docs/SECURITY.md` (no longer "no accounts"), `docs/ARCHITECTURE.md` (composition root), `CHANGELOG.md` under `[Unreleased]` | |
| extra tests | Fullname never appears in logs. Old refresh token refused after rotation (covered by 4b-1) | |
| deploy | Set `JWT_SIGNING_KEY` in Render dev and prod before merge, or the app fails to boot | |
| learning | Add the index line in `docs/learning/README.md`, then run `/learning-checklist` to refine this file | |

## Concepts

- **Passwordless access**: no password to leak or reuse. The recovery code is the only secret, so it is generated with `secrets.token_urlsafe(16)` (128 bits), shown once and stored only as a SHA-256 hash. Without the hash, a database leak hands out working credentials.
- **Why SHA-256 and not a slow hash**: the code is random and long, so brute force is out of reach and a slow hash (bcrypt, argon2) adds cost for no gain. A human-chosen password would need one.
- **Constant-time comparison (`hmac.compare_digest`)**: a plain `==` stops at the first different character, so response time leaks how much of the guess was right.
- **Same answer for every failure**: unknown pseudo and wrong code give the same status, message and roughly the same time (a dummy hash is compared). Otherwise an attacker can list valid pseudos.
- **Clean architecture layers**: domain (plain Python rules), application (use cases and ports), infrastructure (Django, simplejwt), interface (DRF). Dependencies point inward, and each layer only imports what the table in `CLAUDE.md` allows.
- **Ports and adapters**: `interfaces.py` declares what a use case needs (`ParticipantRepository`, `TokenIssuer`). Infrastructure implements it. Tests of the application layer pass fakes, so they need no database.
- **Composition root**: `pykaraoke/composition.py` is the one place that imports both application and infrastructure and builds the real objects. Views call it and never import `infrastructure`.
- **JWT pair with rotation**: a short access token (10 min) and a longer refresh token (7 days). Each refresh issues a new pair and blacklists the old refresh token, so a stolen one is usable only until the real client refreshes.
- **Dedicated signing key**: `JWT_SIGNING_KEY` is separate from `DJANGO_SECRET_KEY`, so leaking one does not forge the other.
- **Tokens in the JSON body**: chosen because a website and a mobile app will both consume the API. The client stores the tokens. No cookie, so no CSRF on token endpoints. The admin reset uses a Django session, so CSRF applies there.
- **Case-insensitive unique pseudo**: `UniqueConstraint(Lower("pseudo"))` makes the database refuse `Marie` and `marie` together, even under a race between two requests.
- **Auth user per participant**: simplejwt's blacklist tables point at a Django user, so each participant gets one with `username=str(participant.id)`, an unusable password and no personal data.

## Docs to read

- [ ] [Django: `UniqueConstraint` with expressions](https://docs.djangoproject.com/en/6.1/ref/models/constraints/#uniqueconstraint). Why `Lower("pseudo")` works as a constraint.
- [ ] [Django: `transaction.atomic`](https://docs.djangoproject.com/en/6.1/topics/db/transactions/). Why the user, participant and code are saved together or not at all.
- [ ] [Python: `secrets`](https://docs.python.org/3/library/secrets.html). Why not `random` for a credential.
- [ ] [Python: `hmac.compare_digest`](https://docs.python.org/3/library/hmac.html#hmac.compare_digest). Timing attacks.
- [ ] [simplejwt: settings](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/settings.html). `ROTATE_REFRESH_TOKENS`, `BLACKLIST_AFTER_ROTATION`, `USER_ID_FIELD`, `ALGORITHM`.
- [ ] [DRF: testing with `APIClient`](https://www.django-rest-framework.org/api-guide/testing/). `format="json"`.
- [ ] [OWASP: Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html). Generic error messages.

## Hands-on

Do these in this repo, without Claude.

- [ ] Sign up twice with `Marie` and `marie`. Read the status code you get, then find which constraint fired in `infrastructure/db/karaoke/models.py`.
- [ ] In a Django shell, read the `RecoveryCodeModel` row of a participant. Confirm the stored value is 64 hex characters and is not the code you received.
- [ ] Break it: change `status.HTTP_409_CONFLICT` to 400 in `views.py` and read which test fails and why.
- [ ] Decode an access token at the payload level (`AccessToken(token).payload`) and list its claims. Explain why there is no fullname.
- [ ] Remove `JWT_SIGNING_KEY` from your environment and run `manage.py check`. Read the error.
- [ ] Run `grep -rnE "^\s*(from|import) infrastructure\b" interface/` and explain why it prints nothing.

## Quiz

Answer from memory. Open the answer only after committing to one.

1. Why does `sign_in` hash the submitted code even when the pseudo does not exist?
   <details><summary>Answer</summary>So both paths do the same work and take about the same time, and the answer is the same. Otherwise response time or message reveals which pseudos exist.</details>
2. Why is the pseudo uniqueness enforced by a database constraint and not only by a check in the use case?
   <details><summary>Answer</summary>Two requests can pass the check at the same moment. Only the database can refuse the second insert. The repository turns that error into `PseudoTaken`.</details>
3. Why does the view import `domain.karaoke.exceptions`, and is that allowed?
   <details><summary>Answer</summary>The exceptions are the contract the application raises, and the view maps them to HTTP codes. The layer table lists only application for the interface, so this is a reading of the rule, not a letter of it. The strict alternative is to re-export them from `application/`.</details>
4. What does `ROTATE_REFRESH_TOKENS` plus `BLACKLIST_AFTER_ROTATION` protect against?
   <details><summary>Answer</summary>Replay of a stolen refresh token. After the real client refreshes, the old token is blacklisted and refused.</details>
5. Why are tokens in the response body and not in an HttpOnly cookie?
   <details><summary>Answer</summary>A mobile app has no browser cookie jar and the website will read the same API. The trade-off is that the client must store tokens safely. Cookies would also bring CSRF.</details>
6. Why does the admin reset call `revoke_all`?
   <details><summary>Answer</summary>The reset exists for a participant who lost the code or may have lost control of it. Refresh tokens already issued must stop working, or the old holder keeps access for 7 days.</details>

## Gotchas hit

- **simplejwt blacklist failed with a UUID subject** -> the blacklist tables reference a Django user, and a participant is not one -> create one auth user per participant (`username=str(participant.id)`) and set `USER_ID_FIELD="username"`.
- **Fakes crashed with `AttributeError`** -> a `@classmethod` cannot read instance state -> make stateful fakes use instance methods, keep `@classmethod` only for stateless ones.
- **Sign-in tests overwrote the sign-up tests** -> both written into `test_sign_up.py` -> restored the file with `git checkout` and moved them to `test_sign_in.py`.
- **Repository equality tests failed** -> `auto_now_add=True` on `created_at` replaced the domain value -> plain `DateTimeField`, migration regenerated.
- **Pre-commit reformatted the migration and aborted the commit** -> the hook fixed files after staging -> re-stage and commit again.
- **`TOKEN_TYPE_CLAIM = "Bearer"`** -> a claim name was given a value -> `"typ"`, and the test fixed.
- **App failed to boot without a key** -> `JWT_SIGNING_KEY` has no default -> added to pytest env in `pyproject.toml`, `ci.yml` (3 jobs), `.env.example` and the Dockerfile `collectstatic` line.
- **Wrong user creation** -> `create(username=pseudo)` stored a pseudo as login -> `create_user(username=str(participant.id))`.
- **`views.py` imported from `gunicorn` and `tests/`** -> IDE auto-imports -> deleted. A view must never import from `tests/`.
- **Sign-up response had no tokens, and a taken pseudo gave 400** -> the response body and status were written from memory -> fixed to match the contract (tokens in body, 409), caught by the interface tests.
- **zsh and `sed -i` on macOS** -> `$FILES` is not split by zsh, `sed -i` needs a backup argument -> explicit paths, and the Edit tool for in-place changes.

## Still unclear

Concepts used but not understood yet. Name them honestly; they become the next checklist.

- How `ATOMIC_REQUESTS` and `transaction.atomic` nest, and what rolls back when token issuing fails after the participant is saved.
- Why `abstractclassmethod` is deprecated and what the `@classmethod` plus `@abstractmethod` form changes for the fakes.
- How DRF throttle rates are stored (cache backend) and how they behave behind Render's proxy (client IP).
- Why the admin endpoint uses session auth and CSRF while token endpoints do not.
- Whether a use case that only forwards to a port (`refresh_tokens`) is worth its layer.
