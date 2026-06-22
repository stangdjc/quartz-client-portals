#!/usr/bin/env bash
set -euo pipefail

find_repo_root() {
  if [ -n "${QUARTZ_REPO_PATH:-}" ] && [ -f "${QUARTZ_REPO_PATH}/scripts/export_client_notes.py" ]; then
    printf '%s\n' "$QUARTZ_REPO_PATH"
    return 0
  fi

  if [ -f "$HOME/quartz-client-portals/scripts/export_client_notes.py" ]; then
    printf '%s\n' "$HOME/quartz-client-portals"
    return 0
  fi

  local match
  match="$(find "$HOME" -maxdepth 5 -path '*/quartz-client-portals/scripts/export_client_notes.py' -print -quit 2>/dev/null || true)"
  if [ -n "$match" ]; then
    dirname "$(dirname "$match")"
    return 0
  fi

  return 1
}

find_vault_root() {
  if [ -n "${OBSIDIAN_VAULT_PATH:-}" ] && [ -d "$OBSIDIAN_VAULT_PATH" ]; then
    printf '%s\n' "$OBSIDIAN_VAULT_PATH"
    return 0
  fi

  if [ -d "$HOME/Obsidian-Vault-V2" ]; then
    printf '%s\n' "$HOME/Obsidian-Vault-V2"
    return 0
  fi

  local match
  match="$(find "$HOME" -maxdepth 4 -type d -name 'Obsidian-Vault-V2' -print -quit 2>/dev/null || true)"
  if [ -n "$match" ]; then
    printf '%s\n' "$match"
    return 0
  fi

  return 1
}

REPO_ROOT="$(find_repo_root)" || {
  echo "ERROR: Could not find quartz-client-portals under $HOME." >&2
  echo "Set QUARTZ_REPO_PATH and try again." >&2
  exit 1
}

VAULT_ROOT="$(find_vault_root)" || {
  echo "ERROR: Could not find Obsidian-Vault-V2 under $HOME." >&2
  echo "Set OBSIDIAN_VAULT_PATH and try again." >&2
  exit 1
}

cd "$REPO_ROOT"
echo "repo_root=$REPO_ROOT"
echo "vault_root=$VAULT_ROOT"
python3 scripts/export_client_notes.py --source-root "$VAULT_ROOT"
