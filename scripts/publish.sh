#!/usr/bin/env bash
# One-command publish: export scoped notes from the vault -> build -> commit -> push to v5.
#
#   bash scripts/publish.sh            # export, build, commit, push (GitHub Pages deploys)
#   bash scripts/publish.sh --preview  # export + build + serve at http://localhost:8080, no commit
#   bash scripts/publish.sh --dry-run  # export + build + show what would change, no commit
#
# Honors OBSIDIAN_VAULT_PATH / QUARTZ_REPO_PATH like run_export_universal.sh.
set -euo pipefail

MODE="publish"
case "${1:-}" in
  --preview) MODE="preview" ;;
  --dry-run) MODE="dry-run" ;;
  "") ;;
  *)
    echo "Usage: $0 [--preview | --dry-run]" >&2
    exit 2
    ;;
esac

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
DEPLOY_BRANCH="v5"
cd "$REPO_ROOT"

echo "==> 1/4 Exporting publish:true notes for this portal's client tag"
QUARTZ_REPO_PATH="$REPO_ROOT" bash "$SCRIPT_DIR/run_export_universal.sh"

if [ ! -d node_modules ]; then
  echo "==> Installing dependencies (first run only)"
  npm ci --no-audit --no-fund
fi

if [ "$MODE" = "preview" ]; then
  echo "==> 2/4 Building and serving locally (Ctrl+C to stop)"
  exec npx quartz build --serve
fi

echo "==> 2/4 Building site to verify it compiles"
npx quartz build >/dev/null

echo "==> 3/4 Changes to publish"
git add -A content
if git diff --cached --quiet -- content; then
  echo "No content changes. The live site is already up to date."
  exit 0
fi
git diff --cached --stat -- content

if [ "$MODE" = "dry-run" ]; then
  git reset -q -- content
  echo "Dry run: nothing committed. Re-run without --dry-run to publish."
  exit 0
fi

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [ "$CURRENT_BRANCH" != "$DEPLOY_BRANCH" ]; then
  git reset -q -- content
  echo "ERROR: on branch '$CURRENT_BRANCH'; publishing deploys from '$DEPLOY_BRANCH'." >&2
  echo "Run: git checkout $DEPLOY_BRANCH" >&2
  exit 1
fi

echo "==> 4/4 Committing and pushing to $DEPLOY_BRANCH"
git commit -q -m "content: publish vault update $(date '+%Y-%m-%d %H:%M')" -- content
git push origin "$DEPLOY_BRANCH"

SITE_URL="$(node -p "require('./package.json').homepage" 2>/dev/null || true)"
echo "Done. GitHub Pages will redeploy in ~1-2 minutes: ${SITE_URL}"
