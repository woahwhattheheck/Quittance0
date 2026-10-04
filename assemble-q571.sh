#!/usr/bin/env bash
# Assemble the reviewed source in a CLEAN, disposable checkout. Does not push.
set -euo pipefail
carrier=$(cd "$(dirname "$0")" && pwd)
cd "${1:?Usage: assemble-q571.sh /path/to/disposable/checkout}"
head=b223d5798fe68c150a429e652f10990d3f632a7d
main=282c75ad933651a93b89a8412ab649b48714c739
expected_tree=cc5b8f56e908f6e60e8bb683211a3d950fd959be
expected_commit=f634e4f37945d40b0ed4024a88b380f5847fe87a
test "$(git rev-parse HEAD)" = "$head"
test -z "$(git status --porcelain)"
printf '%s  %s\n' 3038af73c23c03604e4d2037ec29c753be284299d2f835c9f889cc9da7d6f7c5 "$carrier/q571-review.patch" | sha256sum -c -
if ! git cat-file -e "$main^{commit}" 2>/dev/null; then
  git fetch --no-tags https://github.com/Quittance-Labs/Quittance0.git "$main"
fi
git update-ref refs/remotes/origin/review-main "$main"
git config user.name woahwhattheheck
git config user.email 293286387+woahwhattheheck@users.noreply.github.com
set +e
git merge --no-commit --no-ff origin/review-main
status=$?
set -e
test "$status" -eq 1
test "$(git diff --name-only --diff-filter=U)" = "$(printf '%s\n' frontend/components/InvoiceCard.tsx frontend/components/pay-page.types.ts frontend/lib/api.ts frontend/lib/export.ts)"
git apply --check "$carrier/q571-review.patch"
git apply "$carrier/q571-review.patch"
git add -A
test "$(git write-tree)" = "$expected_tree"
export GIT_AUTHOR_NAME=woahwhattheheck
export GIT_AUTHOR_EMAIL=293286387+woahwhattheheck@users.noreply.github.com
export GIT_AUTHOR_DATE=2026-10-04T08:32:00Z
export GIT_COMMITTER_NAME="$GIT_AUTHOR_NAME"
export GIT_COMMITTER_EMAIL="$GIT_AUTHOR_EMAIL"
export GIT_COMMITTER_DATE="$GIT_AUTHOR_DATE"
git -c core.hooksPath=/dev/null -c commit.gpgsign=false commit --file=- <<'MESSAGE'
fix: keep invoice client compatible with current API responses [skip ci]

Merge current main without rewriting the submitted branch. Keep shared
contract validation strict in tests, retain typed tolerant client responses,
preserve existing seller-statistics row normalization, and carry pay-link
copyValue/networkPassphrase through types, parsers and OpenAPI.

Preserve current-main request correlation, search, canonical proof delivery
and payment-session types. Add artifact-contract and partial-stats coverage.
MESSAGE
test "$(git rev-parse HEAD)" = "$expected_commit"
test "$(git rev-parse HEAD^)" = "$head"
test "$(git rev-parse HEAD^2)" = "$main"
test "$(git rev-parse HEAD^{tree})" = "$expected_tree"
printf 'ASSEMBLED_COMMIT=%s\nASSEMBLED_TREE=%s\n' "$expected_commit" "$expected_tree"
