#!/usr/bin/env python3
"""Fix broken internal links in wiki and post markdown files.

Two patterns are fixed:
  A) /blogs/posts/YYYY/MM/YYYY-MM-DD-<slug>/  →  /blogs/posts/YYYY/MM/<slug>/
  B) /blogs/posts/YYYY-MM-DD-<slug>/          →  /blogs/posts/YYYY/MM/<slug>/
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIRS = [ROOT / "content" / "wiki", ROOT / "content" / "posts"]

# Pattern A1: /blogs/posts/YYYY/MM/YYYY-MM-DD-<slug>/  (body links)
PATTERN_A1 = re.compile(r"/blogs/posts/(\d{4})/(\d{2})/(\d{4}-\d{2}-\d{2})-([^/\s\")]+)/")
# Pattern A2: /posts/YYYY/MM/YYYY-MM-DD-<slug>/  (frontmatter related_posts)
PATTERN_A2 = re.compile(r"(?<!blogs)/posts/(\d{4})/(\d{2})/(\d{4}-\d{2}-\d{2})-([^/\s\")]+)/")
# Pattern B1: /blogs/posts/YYYY-MM-DD-<slug>/  (body links missing year/month dir)
PATTERN_B1 = re.compile(r"/blogs/posts/(\d{4})-(\d{2})-\d{2}-([^/\s\")]+)/")
# Pattern B2: /posts/YYYY-MM-DD-<slug>/  (frontmatter form)
PATTERN_B2 = re.compile(r"(?<!blogs)/posts/(\d{4})-(\d{2})-\d{2}-([^/\s\")]+)/")


def fix_text(text: str) -> tuple[str, int]:
    """Apply all patterns. Returns (new_text, replacement_count)."""
    count = 0

    def sub_a1(m: re.Match) -> str:
        nonlocal count
        count += 1
        return f"/blogs/posts/{m.group(1)}/{m.group(2)}/{m.group(4)}/"

    def sub_a2(m: re.Match) -> str:
        nonlocal count
        count += 1
        return f"/posts/{m.group(1)}/{m.group(2)}/{m.group(4)}/"

    def sub_b1(m: re.Match) -> str:
        nonlocal count
        count += 1
        return f"/blogs/posts/{m.group(1)}/{m.group(2)}/{m.group(3)}/"

    def sub_b2(m: re.Match) -> str:
        nonlocal count
        count += 1
        return f"/posts/{m.group(1)}/{m.group(2)}/{m.group(3)}/"

    text = PATTERN_A1.sub(sub_a1, text)
    text = PATTERN_A2.sub(sub_a2, text)
    text = PATTERN_B1.sub(sub_b1, text)
    text = PATTERN_B2.sub(sub_b2, text)
    return text, count


def main() -> int:
    total_replacements = 0
    files_changed = 0
    for d in CONTENT_DIRS:
        for md in sorted(d.rglob("*.md")):
            original = md.read_text(encoding="utf-8")
            updated, n = fix_text(original)
            if n > 0:
                md.write_text(updated, encoding="utf-8")
                files_changed += 1
                total_replacements += n
                print(f"  {n:3d} fix(es) in {md.relative_to(ROOT)}")
    print(f"\ntotal: {total_replacements} replacements in {files_changed} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
