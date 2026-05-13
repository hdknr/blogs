#!/usr/bin/env python3
"""Add `slug:` frontmatter to posts that lack one.

Slug is derived from filename:
  2026-04-06-gemma4-31b-abliterated-crack.md  →  gemma4-31b-abliterated-crack

This makes generated URLs match the convention used by wiki pages and
post-to-post internal links (e.g. /posts/2026/04/gemma4-31b-abliterated-crack/).
"""

import re
import sys
from pathlib import Path

POSTS_DIR = Path(__file__).resolve().parent.parent / "content" / "posts"

DATE_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}-")
FRONTMATTER_DELIM = "---"


def derive_slug(filename: str) -> str:
    stem = filename.rsplit(".", 1)[0]
    return DATE_PREFIX.sub("", stem)


def has_slug(frontmatter_lines: list[str]) -> bool:
    return any(line.startswith("slug:") for line in frontmatter_lines)


def find_insert_position(frontmatter_lines: list[str]) -> int:
    """Insert slug right after the `date:` line if present, else after title."""
    for i, line in enumerate(frontmatter_lines):
        if line.startswith("lastmod:"):
            return i + 1
    for i, line in enumerate(frontmatter_lines):
        if line.startswith("date:"):
            return i + 1
    for i, line in enumerate(frontmatter_lines):
        if line.startswith("title:"):
            return i + 1
    return len(frontmatter_lines)


def process_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")

    if not lines or lines[0].strip() != FRONTMATTER_DELIM:
        return False

    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == FRONTMATTER_DELIM)
    except StopIteration:
        return False

    fm = lines[1:end]
    if has_slug(fm):
        return False

    slug = derive_slug(path.name)
    pos = find_insert_position(fm)
    fm.insert(pos, f'slug: "{slug}"')

    new_text = "\n".join([lines[0]] + fm + lines[end:])
    path.write_text(new_text, encoding="utf-8")
    return True


def main() -> int:
    updated = 0
    skipped = 0
    for md in sorted(POSTS_DIR.rglob("*.md")):
        if process_file(md):
            updated += 1
        else:
            skipped += 1
    print(f"updated: {updated}, skipped: {skipped}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
