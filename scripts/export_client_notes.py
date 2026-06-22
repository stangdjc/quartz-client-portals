#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

MARKDOWN_SUFFIXES = {".md", ".markdown"}
ASSET_SUFFIXES = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".webp",
    ".avif",
    ".bmp",
    ".ico",
    ".pdf",
    ".csv",
    ".xlsx",
    ".xls",
    ".docx",
    ".pptx",
    ".mp4",
    ".mov",
    ".mp3",
    ".wav",
    ".m4a",
    ".ogg",
}
EMBED_RE = re.compile(r"!?\[\[([^\]|#]+)")
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)#?]+)")
CLIENT_TAG_RE = re.compile(r"^\s*clientTag:\s*([\w./-]+)\s*$", re.MULTILINE)


@dataclass
class ExportSummary:
    notes_copied: int = 0
    assets_copied: int = 0
    skipped_without_publish: int = 0
    skipped_without_tag: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export publish:true notes for the configured Quartz client tag into this repo.",
    )
    parser.add_argument(
        "--source-root",
        help="Root of the Obsidian vault. Defaults to OBSIDIAN_VAULT_PATH.",
    )
    parser.add_argument(
        "--destination-root",
        default="content/exported",
        help="Folder inside this repo that will hold exported notes. Default: content/exported",
    )
    parser.add_argument(
        "--tag",
        help="Client tag to export. Defaults to quartz.config.yaml clientTag or QUARTZ_CLIENT_TAG.",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Quartz repo root. Defaults to the parent of this script's directory.",
    )
    parser.add_argument(
        "--keep-existing",
        action="store_true",
        help="Do not clear the destination folder before exporting.",
    )
    return parser.parse_args()


def normalize_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        items: list[str] = []
        for item in value:
            items.extend(normalize_list(item))
        return items
    if isinstance(value, bool):
        return []
    return [part.strip() for part in str(value).split(",") if part.strip()]


def normalize_token(value: str) -> str:
    return str(value).strip().lower()


def parse_scalar(raw: str):
    value = raw.strip()
    if not value:
        return ""
    if value.startswith(('"', "'")) and value.endswith(('"', "'")) and len(value) >= 2:
        value = value[1:-1]
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    return value


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---", 4)
    if end == -1:
        return {}

    data: dict = {}
    current_key: str | None = None
    for line in text[4:end].splitlines():
        list_match = re.match(r"^\s*-\s*(.*)$", line)
        if list_match and current_key:
            existing_value = data.get(current_key)
            if not isinstance(existing_value, list):
                data[current_key] = [] if existing_value in (None, "") else [existing_value]
            data[current_key].append(parse_scalar(list_match.group(1)))
            continue

        field_match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if field_match:
            current_key = field_match.group(1)
            raw_value = field_match.group(2)
            data[current_key] = [] if raw_value == "" else parse_scalar(raw_value)
            continue

        current_key = None

    return data


def read_client_tag(repo_root: Path) -> str:
    env_tag = os.environ.get("QUARTZ_CLIENT_TAG")
    if env_tag:
        return env_tag.strip()

    config_path = repo_root / "quartz.config.yaml"
    config_text = config_path.read_text(encoding="utf-8")
    match = CLIENT_TAG_RE.search(config_text)
    if match:
        return match.group(1).strip()

    raise SystemExit(f"Could not find clientTag in {config_path}")


def is_publishable(frontmatter: dict, client_tag: str) -> tuple[bool, str]:
    if frontmatter.get("publish") is not True:
        return False, "publish"

    normalized_client_tag = normalize_token(client_tag)
    tags = [normalize_token(tag) for tag in normalize_list(frontmatter.get("tags"))]
    explicit_fields = [normalize_token(tag) for tag in normalize_list(
        [frontmatter.get("client"), frontmatter.get("clientTag"), frontmatter.get("clientPortal")]
    )]

    if normalized_client_tag not in tags and normalized_client_tag not in explicit_fields:
        return False, "tag"

    return True, "ok"


def resolve_asset_path(raw_reference: str, note_path: Path, source_root: Path) -> Path | None:
    reference = raw_reference.strip()
    if not reference or reference.startswith(("http://", "https://", "mailto:", "#")):
        return None
    if "|" in reference:
        reference = reference.split("|", 1)[0].strip()
    if not reference:
        return None

    reference_path = Path(reference)
    candidates = []
    if reference_path.is_absolute():
        candidates.append(reference_path)
    else:
        candidates.append((note_path.parent / reference_path).resolve())
        candidates.append((source_root / reference_path).resolve())

    for candidate in candidates:
        if candidate.exists() and candidate.is_file() and candidate.suffix.lower() in ASSET_SUFFIXES:
            return candidate
    return None


def extract_asset_references(markdown_text: str, note_path: Path, source_root: Path) -> set[Path]:
    assets: set[Path] = set()
    for matcher in (EMBED_RE, MARKDOWN_LINK_RE):
        for match in matcher.findall(markdown_text):
            asset_path = resolve_asset_path(match, note_path, source_root)
            if asset_path is not None:
                assets.add(asset_path)
    return assets


def clear_destination(destination_root: Path) -> None:
    if not destination_root.exists():
        return
    for child in destination_root.iterdir():
        if child.name.startswith("."):
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def ensure_relative_to(path: Path, root: Path) -> Path:
    return path.resolve().relative_to(root.resolve())


def copy_file(source_path: Path, source_root: Path, destination_root: Path) -> Path:
    relative_path = ensure_relative_to(source_path, source_root)
    destination_path = destination_root / relative_path
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, destination_path)
    return destination_path


def collect_notes(source_root: Path) -> Iterable[Path]:
    for path in source_root.rglob("*.md"):
        if any(part.startswith(".") for part in path.parts):
            continue
        yield path


def main() -> None:
    args = parse_args()
    script_path = Path(__file__).resolve()
    repo_root = Path(args.repo_root).resolve() if args.repo_root else script_path.parent.parent.resolve()

    source_root_raw = args.source_root or os.environ.get("OBSIDIAN_VAULT_PATH")
    if not source_root_raw:
        raise SystemExit("Provide --source-root or set OBSIDIAN_VAULT_PATH.")

    source_root = Path(source_root_raw).expanduser().resolve()
    if not source_root.exists():
        raise SystemExit(f"Source root does not exist: {source_root}")

    destination_root = Path(args.destination_root)
    if not destination_root.is_absolute():
        destination_root = (repo_root / destination_root).resolve()

    client_tag = (args.tag or read_client_tag(repo_root)).strip()
    if not client_tag:
        raise SystemExit("Client tag is empty.")

    if not args.keep_existing:
        clear_destination(destination_root)
    destination_root.mkdir(parents=True, exist_ok=True)

    summary = ExportSummary()
    copied_assets: set[Path] = set()

    for note_path in collect_notes(source_root):
        text = note_path.read_text(encoding="utf-8", errors="ignore")
        frontmatter = parse_frontmatter(text)
        publishable, reason = is_publishable(frontmatter, client_tag)
        if not publishable:
            if reason == "publish":
                summary.skipped_without_publish += 1
            elif reason == "tag":
                summary.skipped_without_tag += 1
            continue

        copy_file(note_path, source_root, destination_root)
        summary.notes_copied += 1

        for asset_path in extract_asset_references(text, note_path, source_root):
            if asset_path in copied_assets:
                continue
            copy_file(asset_path, source_root, destination_root)
            copied_assets.add(asset_path)
            summary.assets_copied += 1

    print(f"client_tag={client_tag}")
    print(f"source_root={source_root}")
    print(f"destination_root={destination_root}")
    print(f"notes_copied={summary.notes_copied}")
    print(f"assets_copied={summary.assets_copied}")
    print(f"skipped_without_publish={summary.skipped_without_publish}")
    print(f"skipped_without_tag={summary.skipped_without_tag}")


if __name__ == "__main__":
    main()
