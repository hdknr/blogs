#!/usr/bin/env python3
"""Convert leftover Hugo shortcodes in content to plain Markdown.

The site moved to Astro, which has no idea what `{{< ref >}}` or `{{< x >}}`
mean, so 19 posts were showing readers the raw syntax:

    {{< ref "posts/2026/04/2026-04-29-claude-code-obsidian-ai-second-brain.md" >}}

None of the migration checks caught it. The pages exist, no asset is missing,
and a link that never becomes an <a> is invisible to a link checker -- there is
no href to return 404.

Two shortcodes are in use:

`{{< ref "PATH" >}}` (47) always sits in a Markdown link target,
`[text]({{< ref "..." >}})`. PATH is the content file, with or without a leading
slash and with or without `.md`. Hugo resolved it to the permalink, which is
built from frontmatter `date` + `slug` -- NOT from the filename, because two
posts have a slug that differs from their file name.

`{{< x user="U" id="I" >}}` (2) fetched Twitter's oEmbed at build time. That was
one of the two causes of the nondeterministic builds in #651: the markup came
back pointing at twitter.com on one build and x.com on the next. Replaced with a
static link, which removes the build-time network call along with the syntax.

Usage:
    python3 scripts/convert_hugo_shortcodes.py            # dry run
    python3 scripts/convert_hugo_shortcodes.py --apply
"""

import glob
import os
import re
import sys

CONTENT = os.path.join(os.path.dirname(__file__), "..", "content")
BASE = "/blogs"

FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
REF = re.compile(r'\{\{<\s*ref\s+"([^"]+)"\s*>\}\}')
TWEET = re.compile(r'\{\{<\s*x\s+user="([^"]+)"\s+id="([^"]+)"\s*>\}\}')
ANY_SHORTCODE = re.compile(r"\{\{<")


def permalinks():
    """Map every content file path (as a ref might spell it) to its URL."""
    mapping = {}
    for path in glob.glob(os.path.join(CONTENT, "posts", "**", "*.md"), recursive=True):
        if os.path.basename(path) == "_index.md":
            continue
        with open(path, encoding="utf-8") as f:
            match = FRONTMATTER.match(f.read())
        if not match:
            continue
        fm = match.group(1)
        slug = re.search(r'^slug:\s*"?([^"\n]+)"?\s*$', fm, re.M)
        date = re.search(r"^date:\s*\"?(\d{4})-(\d{2})", fm, re.M)
        if not slug or not date:
            continue

        url = f"{BASE}/posts/{date.group(1)}/{date.group(2)}/{slug.group(1).strip()}/"

        # `content/posts/2026/04/2026-04-03-foo.md` may be written as
        # `posts/2026/04/2026-04-03-foo.md`, with a leading slash, or without
        # the extension. Register every spelling.
        rel = os.path.relpath(path, CONTENT).replace(os.sep, "/")
        for key in (rel, rel[:-3]):
            mapping[key] = url
            mapping["/" + key] = url

    return mapping


def convert(text, urls, unresolved):
    def ref(match):
        target = match.group(1).strip()
        if target in urls:
            return urls[target]
        unresolved.append(target)
        return match.group(0)

    text = REF.sub(ref, text)

    # A plain link, not an embed: an embed would mean fetching Twitter at build
    # time again, which is what made the build nondeterministic.
    text = TWEET.sub(
        lambda m: f"> [@{m.group(1)} のポスト](https://x.com/{m.group(1)}/status/{m.group(2)})",
        text,
    )
    return text


def main():
    apply_changes = "--apply" in sys.argv
    urls = permalinks()
    unresolved = []
    changed = []

    for path in sorted(glob.glob(os.path.join(CONTENT, "**", "*.md"), recursive=True)):
        with open(path, encoding="utf-8") as f:
            original = f.read()
        if "{{<" not in original:
            continue

        updated = convert(original, urls, unresolved)
        if updated == original:
            continue

        changed.append(os.path.relpath(path, os.path.join(CONTENT, "..")))
        if apply_changes:
            with open(path, "w", encoding="utf-8") as f:
                f.write(updated)

    print(f"{len(urls) // 4} 記事の permalink を解決")
    verb = "変換した" if apply_changes else "変換される"
    print(f"{len(changed)} ファイルが{verb}")
    for path in changed:
        print(f"  {path}")

    if unresolved:
        print("\n解決できなかった ref:", file=sys.stderr)
        for target in sorted(set(unresolved)):
            print(f"  {target}", file=sys.stderr)
        return 1

    if not apply_changes:
        print("\n（--apply を付けると実際に書き換えます）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
