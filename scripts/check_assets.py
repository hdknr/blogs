#!/usr/bin/env python3
"""Verify every local asset referenced by the built site actually exists.

The URL comparison used during the Astro migration counted `index.html` files,
which is blind to images, stylesheets and scripts. Under that check the build
looked perfect while `dist/images/` was empty and all 120 diagrams 404'd.

This closes that gap: pull every local `src`, `srcset` and `href` out of the
built HTML and confirm the file is on disk.

Usage:
    python3 scripts/check_assets.py <site-dir> [--base /blogs]
"""

import os
import re
import sys
from html.parser import HTMLParser
from urllib.parse import unquote, urlparse

ASSET_ATTRS = {"src", "href", "srcset"}
# Only assets, not page links: a missing page is what the link checker is for.
ASSET_EXT = {
    ".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".ico",
    ".css", ".js", ".mjs", ".json", ".xml", ".woff", ".woff2", ".ttf",
}


class AssetCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs: set[str] = set()

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name not in ASSET_ATTRS or not value:
                continue
            if name == "srcset":
                # "a.webp 640w, b.webp 1024w" -> the URLs only
                candidates = [p.strip().split(" ")[0] for p in value.split(",")]
            else:
                candidates = [value]
            for candidate in candidates:
                if candidate:
                    self.refs.add(candidate)


def is_local_asset(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme or parsed.netloc:
        return False  # external
    if not parsed.path.startswith("/"):
        return False  # relative; resolved against the page, skip
    ext = os.path.splitext(parsed.path)[1].lower()
    return ext in ASSET_EXT


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2

    site = os.path.abspath(sys.argv[1])
    base = "/blogs"
    if "--base" in sys.argv:
        base = sys.argv[sys.argv.index("--base") + 1]
    base = base.rstrip("/")

    refs: set[str] = set()
    pages = 0
    for root, _, files in os.walk(site):
        for name in files:
            if not name.endswith(".html"):
                continue
            pages += 1
            collector = AssetCollector()
            with open(os.path.join(root, name), encoding="utf-8", errors="ignore") as f:
                collector.feed(f.read())
            refs |= collector.refs

    assets = {r for r in refs if is_local_asset(r)}

    missing = set()
    for ref in assets:
        path = unquote(urlparse(ref).path)
        if base and path.startswith(base + "/"):
            path = path[len(base):]
        candidate = os.path.join(site, path.lstrip("/"))
        if not os.path.exists(candidate):
            missing.add(ref)

    print(f"{pages} pages, {len(assets)} distinct local assets referenced")

    if missing:
        for ref in sorted(missing)[:40]:
            print(f"NG {ref}")
        if len(missing) > 40:
            print(f"   ... and {len(missing) - 40} more")
        print(f"\n{len(missing)} referenced assets are missing", file=sys.stderr)
        return 1

    print("OK すべての参照アセットが存在します")
    return 0


if __name__ == "__main__":
    sys.exit(main())
