#!/usr/bin/env bash
# PostToolUse hook: format + autofix a single edited Python file.
# No-ops silently when uv is missing (before Phase 0.2) or the file is not Python.
set -euo pipefail

file_path="$(python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))' 2>/dev/null || true)"

[ -n "$file_path" ] || exit 0
[ -f "$file_path" ] || exit 0
case "$file_path" in *.py) ;; *) exit 0 ;; esac
command -v uv >/dev/null 2>&1 || exit 0
[ -f "${CLAUDE_PROJECT_DIR:-.}/pyproject.toml" ] || exit 0

cd "${CLAUDE_PROJECT_DIR:-.}"
uv run --quiet ruff format "$file_path" >/dev/null 2>&1 || true
uv run --quiet ruff check --fix --quiet "$file_path" >/dev/null 2>&1 || true
exit 0
