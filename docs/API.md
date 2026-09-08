# API

*Every URL, what it accepts, what it returns, and who is allowed to reach it.*

This is a server-rendered Django MTV app. "API" here means URL patterns, forms and templates —
there are no JSON endpoints. Status: **designed, not implemented** (Milestones 2–3).

## Routes

All app routes are namespaced `karaoke:` and reversed by name, never hardcoded.

| Name                     | Pattern                                             | Methods   | View             | Template              | Access                    |
|--------------------------|-----------------------------------------------------|-----------|------------------|-----------------------|---------------------------|
| `karaoke:enter`          | `/e/<str:token>/`                                   | GET       | `enter`          | `enter.html`          | valid token               |
| `karaoke:sign_up`        | `/e/<str:token>/sign-up/`                           | GET, POST | `sign_up`        | `sign_up.html`        | valid token               |
| `karaoke:overview`       | `/e/<str:token>/overview/`                          | GET       | `overview`       | `overview.html`       | valid token               |
| `karaoke:update_status`  | `/e/<str:token>/me/status/`                         | POST      | `update_status`  | — (redirect)          | valid token + own session |
| `karaoke:cancel`         | `/e/<str:token>/me/cancel/`                         | POST      | `cancel`         | — (redirect)          | valid token + own session |
| `karaoke:songs`          | `/e/<str:token>/me/songs/`                          | GET, POST | `songs`          | `songs.html`          | valid token + own session |
| `karaoke:admin_overview` | `/e/<str:token>/admin/`                             | GET       | `admin_overview` | `admin_overview.html` | staff                     |
| `karaoke:admin_cancel`   | `/e/<str:token>/admin/cancel/<int:participant_id>/` | POST      | `admin_cancel`   | — (redirect)          | staff                     |

Rules baked into that table:

- **Every state change is POST and ends in a redirect** (POST/Redirect/GET). A GET never mutates.
- **Identity comes from the URL token plus the session**, never from a hidden form field.
- **An invalid or unknown token returns 404, not 403** — a 403 confirms the event exists.
- Admin routes require `request.user.is_staff`; a non-staff visitor gets 404 for the same reason.

## Forms

### SignUpForm → `karaoke:sign_up`

| Field             | Type                       | Required | Constraints                            | Error (source string)                                                                    |
|-------------------|----------------------------|----------|----------------------------------------|------------------------------------------------------------------------------------------|
| `pseudo`          | `CharField`                | yes      | 2–40 chars, stripped, unique per event | "Pseudo must be at least 2 characters." / "That pseudo is already taken for this event." |
| `full_name`       | `CharField`                | no       | ≤ 80 chars                             | —                                                                                        |
| `contact`         | `CharField`                | no       | valid email or E.164 phone             | "Enter a valid email address or phone number."                                           |
| `attending_dates` | `ModelMultipleChoiceField` | yes      | ≥ 1, must belong to this event         | "Pick at least one date."                                                                |
| `invites`         | `IntegerField`             | no       | 0–3                                    | "You can bring at most 3 guests."                                                        |

Error strings are written in English here and wrapped in `gettext_lazy`; the French translation is
the one users see.

### SongRequestFormSet → `karaoke:songs`

| Field      | Type           | Required | Constraints     |
|------------|----------------|----------|-----------------|
| `title`    | `CharField`    | yes      | ≤ 160 chars     |
| `artist`   | `CharField`    | no       | ≤ 120 chars     |
| `position` | `IntegerField` | no       | reordering only |

`MAX_SONGS_PER_PARTICIPANT` (default 3) is enforced in `services.py`, not in the form — it is
per-event policy.

### StatusForm → `karaoke:update_status`

Single `status` field, `ChoiceField` limited to `confirmed` / `cancelled`. A participant can never
put themselves into `waiting`; only the promotion rule in `services.py` does that.

## Responses

| Route           | Success                                                                                                           | Failure                                   |
|-----------------|-------------------------------------------------------------------------------------------------------------------|-------------------------------------------|
| `sign_up`       | 302 → `karaoke:overview`, message `success` ("Your seat is reserved.") or `info` ("You are on the waiting list.") | 200, re-render with field errors          |
| `update_status` | 302 → `karaoke:overview`, message `success`                                                                       | 302 → `karaoke:overview`, message `error` |
| `cancel`        | 302 → `karaoke:overview`, message `warning` ("Your seat has been released.")                                      | 302, message `error`                      |
| `songs`         | 302 → `karaoke:songs`, message `success`                                                                          | 200, re-render with formset errors        |
| `admin_cancel`  | 302 → `karaoke:admin_overview`, message `warning`                                                                 | 302, message `error`                      |

## Toaster contract

The toaster is `django.contrib.messages`, rendered once in `base.html`. Level → meaning:

| Level     | Used for                                                                      |
|-----------|-------------------------------------------------------------------------------|
| `success` | Seat confirmed, songs saved                                                   |
| `info`    | Placed on the waiting list                                                    |
| `warning` | Seat released, participant cancelled by admin                                 |
| `error`   | Action refused — event closed, not your row, validation failed after redirect |

## Confirmation modal

Every cancellation route (`karaoke:cancel`, `karaoke:admin_cancel`) is fronted by a modal that
names the pseudo and the event. The modal submits a real POST form with `{% csrf_token %}` — never
a link. Without JavaScript the form still submits, so cancellation degrades to a plain page.

## Errors

| Situation                                | Response                                 |
|------------------------------------------|------------------------------------------|
| Unknown or expired token                 | 404                                      |
| Event closed for sign-ups                | 302 + `error` message                    |
| Acting on someone else's participant row | 404                                      |
| Rate limit exceeded                      | 429                                      |
| Server error                             | 500, generic page, no PII in the message |

## See also

- Where each rule is implemented: [ARCHITECTURE.md](ARCHITECTURE.md)
- Fields backing these forms: [DATABASE.md](DATABASE.md)
- Token handling and rate limiting: [SECURITY.md](SECURITY.md)
