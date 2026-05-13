#!/usr/bin/env python3
"""Remove dead link lines from wiki/post markdown.

Reads a list of dead URLs and strips any markdown line that references them
(both `- "/posts/..."` frontmatter entries and `- [text](/blogs/posts/...) — ...`
list-item references). If "## ソース記事" or "## 関連ページ" sections become
empty after the removal, the section heading is also removed.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIRS = [ROOT / "content" / "wiki", ROOT / "content" / "posts"]

DEAD_LINKS = {
    "/blogs/posts/2021/06/terraform/",
    "/blogs/posts/2023/04/celery/",
    "/blogs/posts/2023/05/drf/",
    "/blogs/posts/2023/05/redis/",
    "/blogs/posts/2023/07/celery-on-ecs/",
    "/blogs/posts/2024/01/django-cache-lock/",
    "/blogs/posts/2024/04/getai-rag/",
    "/blogs/posts/2024/06/fastapi/",
    "/blogs/posts/2024/07/site-security-check/",
    "/blogs/posts/2024/10/grafana/",
    "/blogs/posts/2025/01/supabase/",
    "/blogs/posts/2026/04/claude-mem-persistent-memory/",
}
# Also strip the frontmatter forms (without /blogs prefix).
DEAD_FRONTMATTER = {link.replace("/blogs/posts/", "/posts/") for link in DEAD_LINKS}


def line_has_dead_link(line: str) -> bool:
    for url in DEAD_LINKS | DEAD_FRONTMATTER:
        if url in line:
            return True
    return False


def strip_empty_sections(text: str) -> str:
    """Remove ## headings whose body has nothing but blank lines."""
    out_lines = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("## "):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("## "):
                j += 1
            body = lines[i + 1:j]
            if not any(b.strip() for b in body):
                while out_lines and out_lines[-1].strip() == "":
                    out_lines.pop()
                i = j
                continue
        out_lines.append(line)
        i += 1
    return "\n".join(out_lines)


def collapse_blank_runs(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text)


def process_file(path: Path) -> int:
    original = path.read_text(encoding="utf-8")
    lines = original.split("\n")
    kept = [line for line in lines if not line_has_dead_link(line)]
    new_text = "\n".join(kept)
    new_text = strip_empty_sections(new_text)
    new_text = collapse_blank_runs(new_text)
    if new_text != original:
        path.write_text(new_text, encoding="utf-8")
        return original.count("\n") - new_text.count("\n")
    return 0


def main() -> int:
    total = 0
    for d in CONTENT_DIRS:
        for md in sorted(d.rglob("*.md")):
            diff = process_file(md)
            if diff:
                print(f"  -{diff} line(s) in {md.relative_to(ROOT)}")
                total += diff
    print(f"\ntotal lines removed: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
