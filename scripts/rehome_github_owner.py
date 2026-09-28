#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REPO = "quartz-client-portals"

# Hosting is on Cloudflare (URL is not tied to the GitHub owner), so only repo references change.
# Every occurrence of the current `owner/repo` slug in these files is rewritten.
TEXT_FILES = ["README.md"]


def current_repo_slug(package_json: Path) -> str:
    url = json.loads(package_json.read_text(encoding="utf-8")).get("repository", {}).get("url", "")
    match = re.search(r"github\.com/([^/]+/[^/]+?)(?:\.git)?/?$", url)
    if not match:
        raise SystemExit(f"Could not read the current GitHub repo from repository.url in {package_json}")
    return match.group(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare this Quartz repo for a new GitHub owner/org by updating owner-specific URLs.",
    )
    parser.add_argument("--owner", required=True, help="Target GitHub owner or org, e.g. CASIL")
    parser.add_argument("--repo", default=DEFAULT_REPO, help=f"Repo name (default: {DEFAULT_REPO})")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write changes in place. Omit for a dry run preview.",
    )
    return parser.parse_args()


def update_text(content: str, old_slug: str, new_slug: str) -> tuple[str, int]:
    return content.replace(old_slug, new_slug), content.count(old_slug)


def update_package_json(path: Path, values: dict[str, str], apply: bool) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    changes = 0
    repository = data.setdefault("repository", {})
    if repository.get("url") != f"{values['repo_url']}.git":
        repository["url"] = f"{values['repo_url']}.git"
        changes += 1
    if apply and changes:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return changes


def main() -> int:
    args = parse_args()
    owner = args.owner.strip()
    repo = args.repo.strip()
    old_slug = current_repo_slug(REPO_ROOT / "package.json")
    new_slug = f"{owner}/{repo}"
    values = {"repo_url": f"https://github.com/{new_slug}"}

    changed_files: list[str] = []

    for rel_path in TEXT_FILES:
        path = REPO_ROOT / rel_path
        original = path.read_text(encoding="utf-8")
        updated, count = update_text(original, old_slug, new_slug)
        if updated != original:
            changed_files.append(f"{rel_path} ({count} replacements)")
            if args.apply:
                path.write_text(updated, encoding="utf-8")

    package_json_changes = update_package_json(REPO_ROOT / "package.json", values, args.apply)
    if package_json_changes:
        changed_files.append(f"package.json ({package_json_changes} field updates)")

    mode = "APPLY" if args.apply else "DRY RUN"
    print(f"mode={mode}")
    print(f"current_repo={old_slug}")
    print(f"target_owner={owner}")
    print(f"target_repo={repo}")
    print(f"repo_url={values['repo_url']}")
    if changed_files:
        print("files_to_update=")
        for item in changed_files:
            print(f"- {item}")
    else:
        print("files_to_update=none")

    if not args.apply:
        print("next_step=rerun with --apply after the repo transfer is complete")

    return 0


if __name__ == "__main__":
    sys.exit(main())
