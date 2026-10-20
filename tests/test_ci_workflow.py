"""Prove the CI and deploy workflows keep their shape: stages in order, deploys gated on CI,
least privilege.

Reads the workflow files as data, so a broken `needs:` chain, a widened token or a deploy that
skips CI fails here, not on a GitHub run. The stages themselves (uv, pytest, the Render hooks)
only run on GitHub.
"""

import re
import tomllib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
COVERAGE_ACTION = "py-cov-action/python-coverage-comment-action"


def load(name: str) -> dict:
    return yaml.safe_load((WORKFLOWS / name).read_text())


def ci() -> dict:
    return load("ci.yml")


def needs_of(job: dict) -> list[str]:
    needs = job.get("needs", [])
    return [needs] if isinstance(needs, str) else needs


def steps_using(job: dict, prefix: str) -> list[dict]:
    return [s for s in job["steps"] if s.get("uses", "").startswith(prefix)]


# --- ci.yml -----------------------------------------------------------------------------


def test_ci_stages_chain_in_order() -> None:
    jobs = ci()["jobs"]

    assert needs_of(jobs["build"]) == []
    assert needs_of(jobs["lint"]) == ["build"]
    assert needs_of(jobs["test"]) == ["lint"]
    assert needs_of(jobs["analysis"]) == ["test"]


def test_pip_audit_runs_on_its_own_so_the_weekly_scan_survives_a_red_lint() -> None:
    workflow = ci()

    assert "needs" not in workflow["jobs"]["pip-audit"]
    assert workflow[True]["schedule"] == [{"cron": "0 6 * * 1"}]


def test_ci_has_no_deploy_and_no_manual_trigger() -> None:
    workflow = ci()

    assert "deploy" not in workflow["jobs"]
    assert "workflow_dispatch" not in workflow[True]


def test_only_pull_requests_cancel_a_run_in_progress() -> None:
    concurrency = ci()["concurrency"]

    assert concurrency["cancel-in-progress"] == "${{ github.event_name == 'pull_request' }}"


def test_test_job_runs_project_code_with_read_only_token() -> None:
    test = ci()["jobs"]["test"]

    assert test["permissions"] == {"contents": "read"}
    assert steps_using(test, COVERAGE_ACTION) == []


def test_test_job_uploads_the_coverage_data_the_comment_jobs_read() -> None:
    upload = steps_using(ci()["jobs"]["test"], "actions/upload-artifact")

    assert len(upload) == 1
    assert upload[0]["with"]["include-hidden-files"] is True
    assert ".coverage" in upload[0]["with"]["path"]


def test_test_job_collects_static_files_before_pytest() -> None:
    # Prod settings use a manifest storage. pytest fails without the manifest, and BUILD's
    # collectstatic output is on a different runner, so TEST has to build its own.
    steps = ci()["jobs"]["test"]["steps"]
    names = [s.get("name", "") for s in steps]

    collect = names.index("Collect static files")
    run_tests = names.index("Run tests")
    assert collect < run_tests
    assert steps[collect]["env"]["DJANGO_SETTINGS_MODULE"] == "pykaraoke.settings.prod"


def test_only_the_badge_job_can_write_contents() -> None:
    jobs = ci()["jobs"]

    for name, job in jobs.items():
        writes = job.get("permissions", {}).get("contents") == "write"
        assert writes == (name == "coverage-badge"), name


def test_pr_coverage_job_posts_the_comment_without_contents_write() -> None:
    job = ci()["jobs"]["coverage-pr"]

    assert job["permissions"] == {"contents": "read", "pull-requests": "write"}
    assert "pull_request" in job["if"]
    assert steps_using(job, "actions/download-artifact")
    assert not steps_using(job, "astral-sh/setup-uv")
    assert steps_using(job, COVERAGE_ACTION)


def test_badge_job_saves_coverage_on_push_only() -> None:
    job = ci()["jobs"]["coverage-badge"]

    assert job["permissions"] == {"contents": "write"}
    assert "push" in job["if"]
    assert steps_using(job, COVERAGE_ACTION)


def test_coverage_action_is_pinned_to_a_commit_sha() -> None:
    jobs = ci()["jobs"]

    for name in ("coverage-pr", "coverage-badge"):
        for step in steps_using(jobs[name], COVERAGE_ACTION):
            assert re.search(r"@[0-9a-f]{40}$", step["uses"]), name


def test_coverage_checkout_keeps_no_credentials() -> None:
    jobs = ci()["jobs"]

    for name in ("coverage-pr", "coverage-badge"):
        checkouts = steps_using(jobs[name], "actions/checkout")
        assert checkouts[0]["with"]["persist-credentials"] is False, name


def test_every_python_is_the_dockerfile_version() -> None:
    dockerfile = (ROOT / "Dockerfile").read_text()

    assert "python3.13" in dockerfile
    for name, job in ci()["jobs"].items():
        for step in steps_using(job, "astral-sh/setup-uv"):
            assert step["with"]["python-version"] == "3.13", name


def test_coverage_records_relative_paths_for_the_comment_action() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text())

    assert pyproject["tool"]["coverage"]["run"]["relative_files"] is True


# --- deploy-dev.yml ---------------------------------------------------------------------


def test_dev_deploy_waits_for_a_completed_ci_run() -> None:
    workflow = load("deploy-dev.yml")

    assert workflow[True]["workflow_run"] == {"workflows": ["CI"], "types": ["completed"]}


def test_dev_deploy_needs_a_green_push_to_master_not_a_schedule() -> None:
    condition = load("deploy-dev.yml")["jobs"]["deploy"]["if"]

    assert "workflow_run.conclusion == 'success'" in condition
    assert "workflow_run.event == 'push'" in condition
    assert "workflow_run.head_branch == 'master'" in condition


def test_dev_deploy_tags_and_builds_the_commit_ci_tested() -> None:
    job = load("deploy-dev.yml")["jobs"]["deploy"]
    checkout = steps_using(job, "actions/checkout")[0]
    tag = [s for s in job["steps"] if s.get("name") == "Tag the commit"][0]

    assert checkout["with"]["ref"] == "${{ github.event.workflow_run.head_sha }}"
    assert checkout["with"]["fetch-depth"] == 0
    assert tag["env"]["SHA"] == "${{ github.event.workflow_run.head_sha }}"


def test_dev_deploy_uses_the_dev_hook_and_environment() -> None:
    job = load("deploy-dev.yml")["jobs"]["deploy"]
    trigger = [s for s in job["steps"] if s.get("name") == "Trigger the Render dev deploy"][0]

    assert job["environment"]["name"] == "development"
    assert trigger["env"]["DEPLOY_HOOK"] == "${{ secrets.RENDER_DEPLOY_HOOK_DEV }}"


# --- deploy-prod.yml --------------------------------------------------------------------


def test_prod_deploy_is_manual_with_a_bump_choice() -> None:
    workflow = load("deploy-prod.yml")

    assert set(workflow[True]) == {"workflow_dispatch"}
    assert workflow[True]["workflow_dispatch"]["inputs"]["bump"]["options"] == [
        "patch",
        "minor",
        "major",
    ]


def test_prod_deploy_checks_ci_before_the_reviewer_is_asked() -> None:
    workflow = load("deploy-prod.yml")

    assert needs_of(workflow["jobs"]["deploy"]) == ["verify"]
    assert "environment" not in workflow["jobs"]["verify"]
    assert workflow["jobs"]["deploy"]["environment"]["name"] == "production"


def test_prod_check_requires_every_gate_but_pip_audit() -> None:
    verify = load("deploy-prod.yml")["jobs"]["verify"]
    check = [s for s in verify["steps"] if s.get("name") == "Check CI passed for this commit"][0]

    assert "for job in build lint test analysis; do" in check["run"]
    assert "pip-audit" not in check["run"]


def test_prod_deploy_only_runs_from_master() -> None:
    verify = load("deploy-prod.yml")["jobs"]["verify"]
    refuse = [s for s in verify["steps"] if s.get("name") == "Refuse to run off master"][0]

    assert "refs/heads/master" in refuse["run"]


def test_prod_deploy_uses_the_prod_hook() -> None:
    job = load("deploy-prod.yml")["jobs"]["deploy"]
    trigger = [s for s in job["steps"] if s.get("name") == "Trigger the Render prod deploy"][0]

    assert trigger["env"]["DEPLOY_HOOK"] == "${{ secrets.RENDER_DEPLOY_HOOK_PROD }}"
