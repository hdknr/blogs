#!/usr/bin/env python3
"""Check that every internal link in the built site resolves to a file.

This is the blocking internal-link check on pull requests. It reads the built
`dist` directly instead of serving it, so it covers ~3000 distinct links in about
a second. lychee did the same job over a served copy and took 3.5 minutes of the
6 minutes /ship waited for — and it was not checking more: it ran without
`--include-fragments`, so anchors were never verified, and the static server
issues no redirects worth following. lychee still runs on pushes to main and in
the weekly sweep, so anything this misses surfaces there.

"Internal" means either form a post can use:
  - root-relative:  /blogs/posts/2026/11/<slug>/
  - absolute:       https://hdknr.github.io/blogs/posts/2026/11/<slug>/
The absolute form is what lychee's `--remap` used to catch; matching it here is
what lets this replace lychee on PRs. Only the /blogs/ path on that host counts —
hdknr.github.io also serves sibling Pages projects that are not in this build.

Images, CSS and JS are `check_assets.py`'s job, not this one.

Usage:
    python3 scripts/check_links.py <site-dir> [--base /blogs]
"""

import os
import re
import sys
from urllib.parse import unquote, urlparse

HREF = re.compile(r'href="([^"]+)"')
ORIGINS = ("https://hdknr.github.io", "http://hdknr.github.io")


def internal_path(url: str, base: str) -> str | None:
    """The site path a link points at, or None when it is not internal."""
    for origin in ORIGINS:
        if url.startswith(origin + "/"):
            url = url[len(origin):]
            break
    if url == f"{base}/" or url.startswith(f"{base}/"):
        return url
    return None


def find_missing(site: str, base: str) -> tuple[int, dict[str, str]]:
    """(distinct internal links, {unresolved link: first page that uses it})."""
    # First seen source page per link, so a failure names somewhere to look.
    refs: dict[str, str] = {}
    for root, _, files in os.walk(site):
        for name in files:
            if not name.endswith(".html"):
                continue
            page = os.path.relpath(os.path.join(root, name), site)
            with open(os.path.join(root, name), encoding="utf-8", errors="ignore") as f:
                for match in HREF.finditer(f.read()):
                    url = match.group(1).replace("&amp;", "&")
                    if internal_path(url, base) is not None:
                        refs.setdefault(url, page)

    missing: dict[str, str] = {}
    for url, page in refs.items():
        path = internal_path(url, base)
        rel = unquote(urlparse(path).path)[len(base):].lstrip("/")
        candidates = [
            os.path.join(site, rel),
            os.path.join(site, rel, "index.html"),
        ]
        if rel == "":
            candidates.append(os.path.join(site, "index.html"))
        if not any(os.path.exists(c) for c in candidates):
            missing[url] = page
    return len(refs), missing


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2

    site = os.path.abspath(sys.argv[1])
    base = "/blogs"
    if "--base" in sys.argv:
        base = sys.argv[sys.argv.index("--base") + 1]
    base = base.rstrip("/")

    total, missing = find_missing(site, base)
    print(f"{total} distinct internal links")

    if missing:
        for url in sorted(missing)[:40]:
            print(f"NG {url}   (from {missing[url]})")
        if len(missing) > 40:
            print(f"   ... and {len(missing) - 40} more")
        print(f"\n{len(missing)} internal links do not resolve", file=sys.stderr)
        return 1

    print("OK すべての内部リンクが解決します")
    return 0


if __name__ == "__main__":
    sys.exit(main())
