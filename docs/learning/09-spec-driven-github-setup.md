# 09: Spec-driven GitHub setup

*What to learn from issue templates, labels and draft PRs. Milestone 1.*

**Shipped:** issue templates hold the spec, the PR template holds the plan, `status:*` and area
labels exist on the repo, and the label scheme is documented.
**Files:** `.github/ISSUE_TEMPLATE/{task,feature,bug}.md`, `.github/pull_request_template.md`,
`docs/AI-WORKFLOW.md`, `CONTRIBUTING.md`

This one touches no Python or Django code. What you learn is how GitHub stores process, and how
a shell pipeline can hide a failure.

---

## Concepts

- **Issue template frontmatter**: the `---` block at the top (`name`, `about`, `labels`). GitHub
  reads it to offer the template and to attach the labels on creation. Editing the body changes
  the next issue only, never existing ones.
- **Orthogonal labels**: type (`task`, `enhancement`, `bug`), status (`status:*`) and area
  (`security`, `database`, ...) answer three different questions. One issue can carry one type,
  one status and many areas. Mixing them in one list makes filters useless.
- **Idempotent CLI calls**: `gh label create --force` updates the label if it exists instead of
  failing. Rerunning a setup script is then safe. The same idea as `CREATE ... IF NOT EXISTS`.
- **Draft PR needs a diff**: GitHub refuses a PR where head and base are identical. An empty
  commit (`git commit --allow-empty`) gives the draft something to open on, so the template can
  be the plan before any code.
- **Pipe exit status**: in `cmd | tail`, the shell reports the exit status of `tail`, not `cmd`.
  A failing `make check | tail` would still look green. Read `$?` or `${PIPESTATUS[0]}`, or run
  without the pipe.

## Docs to read

- [Issue templates with YAML frontmatter](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository).
  The `labels` key and the file location.
- [gh label create](https://cli.github.com/manual/gh_label_create). `--force` and `--color`.
- [Creating a pull request from a draft](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests#draft-pull-requests).
  Draft state and when it can be marked ready.

## Hands-on

Do these without Claude.

- [ ] Open a new issue from each template. Check that the labels are attached and the sections
      appear in the body.
- [ ] Run `gh issue list --label security` and read which issues it returns. Then add a second
      label to one of them and run it again.
- [ ] Run `gh label list` and find which labels are type, status and area. Say why `bug` is not a
      status.
- [ ] Run `make check | tail -n 1; echo $?` and then `make check > /dev/null; echo $?`. Explain
      why the two results can differ when `make` fails.

## Quiz

Answer from memory. Open the answer only after committing to one.

1. An issue template changes from `labels: feature` to `labels: enhancement`. What happens to
   issues created before the change?
   <details><summary>Answer</summary>Nothing. Templates only shape new issues. Existing issues keep
   their labels, which is why the old feature label is not renamed on them.</details>
2. Why does `gh label create` with `--force` make a setup script safe to rerun?
   <details><summary>Answer</summary>It updates the existing label instead of erroring on the
   duplicate, so the end state is the same after one run or many.</details>
3. Why does a draft PR need an empty commit before it can be opened?
   <details><summary>Answer</summary>GitHub rejects a PR whose head has no changes compared with
   the base branch.</details>
4. In `make check | tail -n 1`, whose exit status does the shell report?
   <details><summary>Answer</summary>`tail`. Use `${PIPESTATUS[0]}` or run without the pipe to get
   the status of `make`.</details>

## Gotchas hit

- **`feature.md` used a label that does not exist** (`feature`) → the repo only has `enhancement`
  as the type label → changed the template to `enhancement` and kept `feature` out of the scheme.
- **`gh issue view 22` failed with "not a git repository"** → the working directory was the
  scratchpad, not the repo → pass `-R alopesmendes/pykaraoke` when running `gh` outside the repo.
- **Piped `make check` hid its exit code** → the output was piped through `tail`, so the status
  printed was not `make`'s → rerun without the pipe and read `$?`. The real run exited 0.

## Still unclear

- The final area-label list is still an open question in issue #22. Nothing is decided about
  extra labels.
- Whether `gh` can mark a draft PR ready from the CLI without the web UI. Not tried yet.
