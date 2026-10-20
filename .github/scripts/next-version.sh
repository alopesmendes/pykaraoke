#!/usr/bin/env bash
# Print the next version tag, computed from the git tags in the current repo.
#
#   next-version.sh dev     -> vX.Y.(Z+1)-dev.N   (N counts up per base version)
#   next-version.sh patch   -> vX.Y.(Z+1)         (bump of the latest prod tag)
#   next-version.sh minor   -> vX.Y+1.0
#   next-version.sh major   -> vX+1.0.0
#
# Prod tags are plain vX.Y.Z. Dev tags are vX.Y.Z-dev.N and never count as a
# prod release. Needs the tags fetched: actions/checkout with fetch-depth: 0.
set -euo pipefail

mode="${1:?usage: next-version.sh dev|patch|minor|major}"

# Newest prod tag, compared numerically (sort -V), so v1.10.0 beats v1.9.0.
# grep finds nothing on a fresh repo: `|| true` keeps that from failing the script.
latest="$(git tag --list 'v*' \
  | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' \
  | sed 's/^v//' \
  | sort -V \
  | tail -n 1 || true)"
latest="${latest:-0.0.0}"

IFS=. read -r major minor patch <<<"$latest"

case "$mode" in
  dev)
    base="$major.$minor.$((patch + 1))"
    # Highest existing counter for this base, +1. Empty list -> starts at 1.
    last="$(git tag --list "v$base-dev.*" \
      | sed 's/.*-dev\.//' \
      | sort -n \
      | tail -n 1 || true)"
    echo "v$base-dev.$((${last:-0} + 1))"
    ;;
  patch)
    echo "v$major.$minor.$((patch + 1))"
    ;;
  minor)
    echo "v$major.$((minor + 1)).0"
    ;;
  major)
    echo "v$((major + 1)).0.0"
    ;;
  *)
    echo "unknown mode '$mode': use dev, patch, minor or major" >&2
    exit 1
    ;;
esac
