# Changelog

All notable changes to this project are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Entries are written for someone **using** the site, not for someone reading the diff.

## [Unreleased]

### Added
- Guided feature sessions: `/guide [beginner|intermediate|advanced]` walks through the feature on
  the current branch one layer at a time, showing the code (you type it). `/guide ignore` implements
  it without a walkthrough. `/guide verify` ends the session with lint, tests, Django checks, layer
  import rules and doc checks.
- Project documentation: architecture, database, API, security, epics.
- Learning checklists under `docs/learning/`, one per feature. Milestone 1 checklist added
  (app skeleton, settings split, Postgres, base template, i18n).
- Claude Code workflow: 6 skills, 8 agents, committed permissions, auto-format hook.

### Changed
- CI is one pipeline, `ci.yml`: BUILD, LINT, TEST, ANALYSIS/SECURITY. Each stage waits for the one
  before it. Deploys are separate workflows: dev deploys after a push to master passes CI, and prod
  is a manual run with the reviewer gate that deploys even if pip-audit failed. Python 3.13 only.
- Test coverage is reported on each pull request as a comment, and the README shows a coverage badge.
- GitHub issue and pull request templates.
- Spec-driven GitHub setup: issue templates hold the spec (goal, requirements, design, open
  questions), the pull request template holds the plan (accept criteria, tests, architecture).
  Status and area labels added. The label scheme and the issue-to-draft-PR rule are in
  `docs/AI-WORKFLOW.md`.
- `karaoke` app scaffolded and registered (empty, no behaviour yet).
- Site languages: French by default, Japanese available. The browser's language picks which one
  is shown. No page is translated yet.
- Static files (CSS, JavaScript, images) are served by WhiteNoise from the app server, with no CDN
  or separate web server needed. Files are compressed and fingerprinted for caching.
- Health check at `/health/`: answers `{"status": "ok"}` without touching the database, so the
  hosting platform can tell when the site is up.
- Docker image serves on the port the host sets (`PORT`), applies migrations when it starts, and
  reports healthy once `/health/` answers.
- API documentation (OpenAPI schema and Swagger UI at `/api/docs/`), on in development only.

### Changed
- Claude Code issue flow: `/karaoke-issue-launch` reads the issue's Requirements, opens a draft PR
  through the new `issue-orchestrator` agent (which refuses issues not marked `status:ready` in the
  current milestone), and waits for the Tests checklist to be validated before writing code.
  `/commit-push-pr` marks that draft ready instead of opening a new PR.
- Settings split into `pykaraoke/settings/{base,dev,prod}.py`; `DEBUG` and the security
  block are hardcoded per environment instead of read from `DJANGO_DEBUG`.
- Every merge to `master` deploys to the development site and is tagged `vX.Y.Z-dev.N`.
  Production is deployed by hand, after a reviewer approves, and tagged `vX.Y.Z`.

### Removed
- The workflow that built a container image and pushed it to GitHub's registry. The hosting
  platform builds the image from the repository on each deploy.

### Security
- Dependencies `urllib3` (2.8.0) and `virtualenv` (21.14.10) upgraded to clear 11 known
  vulnerabilities reported by `pip-audit`.

### Fixed
- Lint and security workflows failed at dependency install because `uv` picked Python 3.15. They
  now pin Python 3.13, matching the Docker image.
- Security workflow ran the Django deploy check against the dev settings and failed on HTTPS and
  `DEBUG` warnings. It now runs against `pykaraoke.settings.prod`.

[Unreleased]: https://github.com/alopesmendes/pykaraoke/commits/master
