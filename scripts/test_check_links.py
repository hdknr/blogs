#!/usr/bin/env python3
"""Tests for check_links.

Run with `python3 scripts/test_check_links.py`. Dependency-free, like the other
tests that guard this workflow.

check_links.py is the only blocking internal-link check on pull requests, so the
weight sits on the ways it could go quietly blind: a link form it stops
recognising as internal is a link it never checks, and that looks exactly like a
site with no broken links. Each case below is a positive control — a link that
must be reported — paired with the resolving form that must not be.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_links as cl

failures: list[str] = []


def check(name: str, ok: bool) -> None:
    print(f"  {'OK' if ok else 'NG'} {name}")
    if not ok:
        failures.append(name)


def site_with(links: list[str]) -> tuple[int, dict[str, str]]:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        live = root / "posts" / "2026" / "11" / "live"
        live.mkdir(parents=True)
        (live / "index.html").write_text("<p>live</p>", encoding="utf-8")
        (root / "index.html").write_text("<p>home</p>", encoding="utf-8")
        body = "".join(f'<a href="{u}">x</a>' for u in links)
        (root / "page.html").write_text(body, encoding="utf-8")
        return cl.find_missing(str(root), "/blogs")


print("root-relative links")
_, missing = site_with(["/blogs/posts/2026/11/live/", "/blogs/posts/2026/11/gone/"])
check("存在するページは通す", "/blogs/posts/2026/11/live/" not in missing)
check("存在しないページは報告する", "/blogs/posts/2026/11/gone/" in missing)

print("absolute links on this site")
_, missing = site_with([
    "https://hdknr.github.io/blogs/posts/2026/11/live/",
    "https://hdknr.github.io/blogs/posts/2026/11/gone/",
    "http://hdknr.github.io/blogs/posts/2026/11/gone2/",
])
check("絶対 URL で存在するページは通す",
      "https://hdknr.github.io/blogs/posts/2026/11/live/" not in missing)
check("絶対 URL で存在しないページは報告する（lychee の --remap の代わり）",
      "https://hdknr.github.io/blogs/posts/2026/11/gone/" in missing)
check("http の絶対 URL も検査する",
      "http://hdknr.github.io/blogs/posts/2026/11/gone2/" in missing)

print("links that are not ours")
total, missing = site_with([
    "https://hdknr.github.io/claude-code-setup/",
    "https://example.com/blogs/x/",
    "/blogsx/",
])
check("同じホストの別 Pages プロジェクトは対象外", missing == {})
check("対象外のリンクは数えない", total == 0)

print("fragments and queries")
_, missing = site_with([
    "/blogs/posts/2026/11/live/#section",
    "/blogs/posts/2026/11/live/?a=1&amp;b=2",
    "/blogs/posts/2026/11/gone/#section",
])
check("フラグメント付きでもページがあれば通す", "/blogs/posts/2026/11/live/#section" not in missing)
check("クエリ付きでもページがあれば通す", "/blogs/posts/2026/11/live/?a=1&b=2" not in missing)
check("フラグメント付きでもページがなければ報告する", "/blogs/posts/2026/11/gone/#section" in missing)

print("site root")
_, missing = site_with(["/blogs/", "https://hdknr.github.io/blogs/"])
check("トップページは解決する", missing == {})

if failures:
    print(f"\n{len(failures)} 件失敗", file=sys.stderr)
    sys.exit(1)

print("\nすべて成功")
