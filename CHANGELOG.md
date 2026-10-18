# Changelog

All notable changes to this project are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Entries are written for someone **using** the site, not for someone reading the diff.

## [Unreleased]

### Added
- Project documentation: architecture, database, API, security, epics.
- Learning checklists under `docs/learning/`, one per feature. Milestone 1 checklist added
  (app skeleton, settings split, Postgres, base template, i18n).
- Claude Code workflow: 9 skills, 9 agents, committed permissions, auto-format hook.
- GitHub issue and pull request templates.
- `karaoke` app scaffolded and registered (empty, no behaviour yet).
- Site languages: French by default, Japanese available. The browser's language picks which one
  is shown. No page is translated yet.

### Changed
- Settings split into `pykaraoke/settings/{base,dev,prod}.py`; `DEBUG` and the security
  block are hardcoded per environment instead of read from `DJANGO_DEBUG`.

### Security
- Dependencies `urllib3` (2.8.0) and `virtualenv` (21.14.10) upgraded to clear 11 known
  vulnerabilities reported by `pip-audit`.

### Fixed
- Lint and security workflows failed at dependency install because `uv` picked Python 3.15. They
  now pin Python 3.13, matching the Docker image.
- Security workflow ran the Django deploy check against the dev settings and failed on HTTPS and
  `DEBUG` warnings. It now runs against `pykaraoke.settings.prod`.

[Unreleased]: https://github.com/alopesmendes/pykaraoke/commits/master
