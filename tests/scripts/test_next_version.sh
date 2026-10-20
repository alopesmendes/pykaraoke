#!/usr/bin/env bash
# Checks .github/scripts/next-version.sh against scratch repos with known tags.
# Run locally: bash tests/scripts/test_next_version.sh
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
script="$here/../../.github/scripts/next-version.sh"
failures=0

# check EXPECTED MODE [EXISTING_TAG...]: build a repo with those tags, run the script.
check() {
  local expected="$1" mode="$2"
  shift 2

  local repo
  repo="$(mktemp -d)"
  git -C "$repo" init -q
  git -C "$repo" -c user.name=test -c user.email=test@example.com commit -q --allow-empty -m init

  local tag
  for tag in "$@"; do
    git -C "$repo" tag "$tag"
  done

  local actual
  actual="$(cd "$repo" && "$script" "$mode")"

  if [ "$actual" = "$expected" ]; then
    echo "ok    $mode [$*] -> $actual"
  else
    echo "FAIL  $mode [$*] -> got '$actual', want '$expected'"
    failures=$((failures + 1))
  fi

  rm -rf "$repo"
}

# No tags yet: the first version is v0.0.0 and dev sits one patch above it.
check v0.0.1-dev.1 dev
check v0.0.1 patch
check v0.1.0 minor
check v1.0.0 major

# A prod tag exists: dev moves to the next patch.
check v1.2.4-dev.1 dev v1.2.3
check v1.2.4 patch v1.2.3
check v1.3.0 minor v1.2.3
check v2.0.0 major v1.2.3

# The dev counter goes up, numerically (dev.10 comes after dev.2).
check v1.2.4-dev.3 dev v1.2.3 v1.2.4-dev.1 v1.2.4-dev.2
check v1.2.4-dev.11 dev v1.2.3 v1.2.4-dev.2 v1.2.4-dev.10

# Prod versions compare numerically (1.10.0 is newer than 1.9.0).
check v1.10.1 patch v1.9.0 v1.10.0

# A dev tag never counts as a prod release.
check v0.0.1-dev.1 dev v1.2.3-dev.5

if [ "$failures" -gt 0 ]; then
  echo "$failures check(s) failed"
  exit 1
fi
echo "all checks passed"
