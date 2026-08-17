#!/usr/bin/env python3
"""Collapse tag spelling variants that already share a URL.

Hugo urlizes a taxonomy term to build its page, so `Claude Code`, `claude-code`
and `CLAUDE CODE` all resolve to /tags/claude-code/. Only the display name
differs, and which variant becomes the display name is decided by map iteration
order -- so it changes between builds of identical content (#651).

Collapsing a colliding group therefore removes a real bug and changes no URL.

The canonical spelling is the variant used most often, which keeps the author's
own habit (`claude-code` lowercase, but `OSS` / `SaaS` / `Obsidian` capitalised)
and minimises the number of files touched. Ties fall back to the urlized form,
then alphabetical order, so the result does not depend on dict ordering.

Usage:
    python3 scripts/normalize_tags.py              # dry run, prints the plan
    python3 scripts/normalize_tags.py --apply      # rewrite the posts
"""

import os
import re
import sys
import glob
from collections import defaultdict

CONTENT_DIR = os.path.join(os.path.dirname(__file__), '..', 'content')

# Posts and wiki pages share one `tags` taxonomy, so both have to be normalised
# together. Doing posts alone leaves the wiki's spellings alive and the display
# name keeps flapping -- 152 wiki pages carry tags like `MCP` and `Claude Code`.
TAGGED_DIRS = ['posts', 'wiki']

FRONTMATTER = re.compile(r'^(---\n)(.*?)(\n---\n)', re.DOTALL)
TAGS_LINE = re.compile(r'^tags:[ \t]*(\[.*\])[ \t]*$', re.MULTILINE)


def urlize(term):
    """Approximate Hugo's urlize for taxonomy terms.

    Only used to decide which terms collide, never to build a URL, so it needs
    to agree with Hugo on the collapsing rules (case, spaces, underscores,
    slashes) rather than reproduce every escaping detail.
    """
    s = term.strip().lower()
    s = re.sub(r'[\s_/]+', '-', s)
    s = re.sub(r'[^\w\-]', '', s, flags=re.UNICODE)
    s = re.sub(r'-+', '-', s).strip('-')
    return s


def parse_tags(raw):
    """Parse an inline YAML list into a list of tag strings."""
    inner = raw.strip()[1:-1].strip()
    if not inner:
        return []
    return [t.strip().strip('"').strip("'") for t in inner.split(',')]


def format_tags(tags):
    return 'tags: [' + ', '.join(f'"{t}"' for t in tags) + ']'


def post_paths():
    for name in TAGGED_DIRS:
        pattern = os.path.join(CONTENT_DIR, name, '**', '*.md')
        for path in sorted(glob.glob(pattern, recursive=True)):
            if os.path.basename(path) != '_index.md':
                yield path


def read_tags(path):
    """Return (text, tags_or_None). None means the post has no inline tags line."""
    with open(path, encoding='utf-8') as f:
        text = f.read()

    fm = FRONTMATTER.match(text)
    if not fm:
        return text, None

    match = TAGS_LINE.search(fm.group(2))
    if not match:
        return text, None

    return text, parse_tags(match.group(1))


def build_canonical_map():
    """Map every variant spelling to the canonical one for its collision group."""
    counts = defaultdict(int)
    for path in post_paths():
        _, tags = read_tags(path)
        for tag in tags or []:
            if tag:
                counts[tag] += 1

    groups = defaultdict(list)
    for tag, n in counts.items():
        groups[urlize(tag)].append(tag)

    canonical = {}
    for key, variants in groups.items():
        if len(variants) < 2:
            continue
        # Most used wins; then the already-urlized spelling; then alphabetical.
        # The last two keys make the choice independent of iteration order.
        best = sorted(variants, key=lambda t: (-counts[t], t != key, t))[0]
        for variant in variants:
            if variant != best:
                canonical[variant] = best

    return canonical, counts, groups


def rewrite(path, canonical):
    """Return the new file text, or None when nothing changes."""
    text, tags = read_tags(path)
    if not tags:
        return None

    new_tags = []
    for tag in tags:
        mapped = canonical.get(tag, tag)
        # A post can carry both spellings (e.g. "claude" and "Claude"); after
        # mapping they collapse into one entry, so drop the duplicate.
        if mapped not in new_tags:
            new_tags.append(mapped)

    if new_tags == tags:
        return None

    fm = FRONTMATTER.match(text)
    head, body_fm, tail = fm.group(1), fm.group(2), fm.group(3)
    new_fm = TAGS_LINE.sub(lambda _: format_tags(new_tags), body_fm, count=1)
    return head + new_fm + tail + text[fm.end():]


def main():
    apply_changes = '--apply' in sys.argv

    canonical, counts, groups = build_canonical_map()

    print(f"ユニークタグ         : {len(counts)}")
    print(f"衝突グループ         : {sum(1 for v in groups.values() if len(v) > 1)}")
    print(f"統合で消える表記     : {len(canonical)}")
    print()

    ranked = sorted(
        ((v, k) for k, v in canonical.items()),
        key=lambda vk: (-counts[vk[0]], vk[0], vk[1]),
    )
    for target, variant in ranked:
        print(f"  {variant!r} ({counts[variant]}) -> {target!r} ({counts[target]})")

    print()
    changed = []
    for path in post_paths():
        new_text = rewrite(path, canonical)
        if new_text is None:
            continue
        changed.append(path)
        if apply_changes:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_text)

    verb = "書き換えた" if apply_changes else "書き換わる"
    print(f"{len(changed)} 記事が{verb}")
    if not apply_changes:
        print("（--apply を付けると実際に書き換えます）")

    return 0


if __name__ == '__main__':
    sys.exit(main())
