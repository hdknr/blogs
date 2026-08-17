#!/usr/bin/env python3
"""Check that every internal link in the built site resolves to a file.

CI already runs lychee over a served copy, which is more thorough — it follows
redirects and checks fragments. But it takes over five minutes, and the first
cutover attempt burned a full run on 115 pagination links pointing at `page/0`
and `page/<lastPage + 1>`. This finds that class of mistake in seconds, before
the push.

Not a replacement for the CI check. A cheap first pass.

Usage:
    python3 scripts/check_links.py <site-dir> [--base /blogs]
"""

import os
import re
import sys
from urllib.parse import unquote, urlparse

HREF = re.compile(r'href="([^"]+)"')


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2

    site = os.path.abspath(sys.argv[1])
    base = "/blogs"
    if "--base" in sys.argv:
        base = sys.argv[sys.argv.index("--base") + 1]
    base = base.rstrip("/")

    # First seen source page per link, so a failure names somewhere to look.
    refs: dict[str, str] = {}
    for root, _, files in os.walk(site):
        for name in files:
            if not name.endswith(".html"):
                continue
            page = os.path.relpath(os.path.join(root, name), site)
            with open(os.path.join(root, name), encoding="utf-8", errors="ignore") as f:
                for match in HREF.finditer(f.read()):
                    url = match.group(1)
                    if url == f"{base}/" or url.startswith(f"{base}/"):
                        refs.setdefault(url, page)

    missing: dict[str, str] = {}
    for url, page in refs.items():
        rel = unquote(urlparse(url).path)[len(base):].lstrip("/")
        candidates = [
            os.path.join(site, rel),
            os.path.join(site, rel, "index.html"),
        ]
        if rel == "":
            candidates.append(os.path.join(site, "index.html"))
        if not any(os.path.exists(c) for c in candidates):
            missing[url] = page

    print(f"{len(refs)} distinct internal links")

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
