#!/usr/bin/env bash
# One-command publish: sync -> export scoped notes from the vault -> build -> commit -> push to v5.
# Cloudflare Workers Builds deploys automatically on push. Safe to run from any directory.
#
#   bash scripts/publish.sh            # sync, export, build, commit, push
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

if [ "$MODE" = "publish" ]; then
  # content/exported is regenerated from the vault below, so leftovers from an interrupted run are safe to drop.
  git checkout -q -- content/exported 2>/dev/null || true
  git clean -fdq -- content/exported
  CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
  if [ "$CURRENT_BRANCH" != "$DEPLOY_BRANCH" ]; then
    if [ -n "$(git status --porcelain -- . ':!content')" ]; then
      echo "ERROR: on branch '$CURRENT_BRANCH' with uncommitted changes; commit or stash them first." >&2
      exit 1
    fi
    echo "==> Switching to $DEPLOY_BRANCH"
    git checkout -q "$DEPLOY_BRANCH"
  fi
  echo "==> Syncing with origin/$DEPLOY_BRANCH"
  git pull -q --ff-only origin "$DEPLOY_BRANCH"
fi

echo "==> 1/4 Exporting publish:true notes for this portal's client tag"
QUARTZ_REPO_PATH="$REPO_ROOT" bash "$SCRIPT_DIR/run_export_universal.sh"

if [ ! -d node_modules ]; then
  echo "==> Installing dependencies (first run only)"
  npm ci --no-audit --no-fund
fi
if [ ! -d .quartz/plugins ]; then
  echo "==> Installing Quartz plugins (first run only)"
  npx quartz plugin install >/dev/null
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

echo "==> 4/4 Committing and pushing to $DEPLOY_BRANCH"
git commit -q -m "content: publish vault update $(date '+%Y-%m-%d %H:%M')" -- content
git push origin "$DEPLOY_BRANCH"

SITE_URL="$(node -p "require('./package.json').homepage" 2>/dev/null || true)"
echo "Done. Cloudflare will redeploy in ~1-2 minutes: ${SITE_URL}"
