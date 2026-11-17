#!/usr/bin/env python3
"""Mechanical health checks for the wiki (content/wiki/).

`/wiki-lint` used to have the model do these by reading every page: ~150 wiki
pages, each with a dozen links and related_posts entries, all checked against
the file tree. None of it needs judgement, so it lives here and the skill only
reads the report and proposes fixes.

Checks:
  1. orphan pages      -- no other wiki page links to it
  2. broken links      -- /blogs/wiki/... or /blogs/posts/... in the body that
                          resolve to no page
  3. related_posts     -- entries that resolve to no published post
  4. stale pages       -- wiki lastmod older than a related post's lastmod
  5. frontmatter       -- required fields missing or empty; aliases recommended

Links inside fenced code blocks and inline code are ignored: a wiki page that
explains link syntax is not a broken link.

Posts are resolved by permalink, /posts/<dir year>/<dir month>/<frontmatter
slug>/, the same way the build does -- not by filename. Draft posts and posts
under content/archive/ are not built, so a link to one is dangling; the report
says which of those it was.

Exit status: 1 when there are broken links, dangling related_posts or missing
required fields; orphans, stale pages and missing aliases are advisory and do
not fail the run.

Usage:
    python3 scripts/wiki_lint.py              # Markdown report (Japanese)
    python3 scripts/wiki_lint.py --root DIR   # run against another checkout
"""

import argparse
import glob
import os
import re
import sys

REQUIRED = ["title", "description", "date", "lastmod", "related_posts", "tags"]
RECOMMENDED = ["aliases"]

FRONTMATTER = re.compile(r'^---\n(.*?)\n---\n?', re.DOTALL)
FENCE = re.compile(r'^(```|~~~).*?^\1[^\n]*$', re.DOTALL | re.MULTILINE)
INLINE_CODE = re.compile(r'`[^`\n]*`')
# Markdown link targets pointing into the site, root-relative or absolute.
LINK = re.compile(r'\]\(\s*(?:https?://hdknr\.github\.io)?(/blogs/(?:wiki|posts)/[^)\s]*)')
POST_PATH = re.compile(r'content/(?:archive/)?posts/(\d{4})/(\d{2})/[^/]+\.md$')


def unquote(value):
    return value.strip().strip('"').strip("'")


def parse_frontmatter(text):
    """Return (frontmatter dict, body). Lists come back as lists of strings.

    Handles both YAML list forms used here: inline `["a", "b"]` and block
    `key:` followed by `  - "a"` lines. Returns ({}, text) when absent.
    """
    match = FRONTMATTER.match(text)
    if not match:
        return {}, text
    fm = {}
    key = None
    for line in match.group(1).split('\n'):
        stripped = line.strip()
        if key and stripped.startswith('- '):
            fm[key].append(unquote(stripped[2:]))
            continue
        if ':' not in line or line[:1].isspace():
            continue
        key, _, value = line.partition(':')
        key, value = key.strip(), value.strip()
        if value == '':
            fm[key] = []          # block list follows (or the field is empty)
        elif value.startswith('[') and value.endswith(']'):
            inner = value[1:-1].strip()
            fm[key] = [unquote(v) for v in inner.split(',')] if inner else []
            key = None
        else:
            fm[key] = unquote(value)
            key = None
    return fm, text[match.end():]


def normalize(path):
    """'/blogs/posts/2026/11/x' -> '/posts/2026/11/x/' (no base, no fragment)."""
    path = path.split('#', 1)[0].split('?', 1)[0]
    if path.startswith('/blogs/'):
        path = path[len('/blogs'):]
    if not path.endswith('/'):
        path += '/'
    return path


def day(value):
    return value[:10] if isinstance(value, str) else ''


def index_posts(root):
    """({permalink: lastmod} for published posts, {permalink: reason} for the rest)."""
    published, unpublished = {}, {}
    for pattern in ('content/posts/**/*.md', 'content/archive/posts/**/*.md'):
        for filepath in glob.glob(os.path.join(root, pattern), recursive=True):
            rel = os.path.relpath(filepath, root)
            match = POST_PATH.search(rel)
            if not match:
                continue
            with open(filepath, encoding='utf-8') as f:
                fm, _ = parse_frontmatter(f.read())
            slug = fm.get('slug')
            if not isinstance(slug, str) or not slug:
                continue
            url = f"/posts/{match.group(1)}/{match.group(2)}/{slug}/"
            if rel.startswith('content/archive/'):
                unpublished.setdefault(url, f"アーカイブ済み（{rel}）")
            elif str(fm.get('draft', '')).lower() == 'true':
                unpublished.setdefault(url, f"draft（{rel}）")
            else:
                published[url] = day(fm.get('lastmod')) or day(fm.get('date'))
    return published, unpublished


def load_wiki(root):
    """{wiki url: {'rel', 'fm', 'links'}} for every page, plus the section urls."""
    # /posts/ is the post listing route (astro/src/pages/posts/[...page].astro).
    pages, sections = {}, {'/wiki/', '/posts/'}
    for filepath in sorted(glob.glob(os.path.join(root, 'content/wiki/**/*.md'), recursive=True)):
        rel = os.path.relpath(filepath, root)
        parts = rel[len('content/wiki/'):-len('.md')].split('/')
        if parts[-1] == '_index':
            sections.add('/wiki/' + ''.join(p + '/' for p in parts[:-1]))
            continue
        with open(filepath, encoding='utf-8') as f:
            fm, body = parse_frontmatter(f.read())
        body = INLINE_CODE.sub('', FENCE.sub('', body))
        links = [normalize(m) for m in LINK.findall(body)]
        pages['/wiki/' + '/'.join(parts) + '/'] = {'rel': rel, 'fm': fm, 'links': links}
    return pages, sections


def lint(root):
    published, unpublished = index_posts(root)
    pages, sections = load_wiki(root)

    inbound = {url: 0 for url in pages}
    broken, dangling, stale, missing, recommended = [], [], [], [], []

    for url, page in pages.items():
        rel, fm = page['rel'], page['fm']

        for link in dict.fromkeys(page['links']):
            if link in pages:
                if link != url:
                    inbound[link] += 1
            elif link in sections or link in published:
                continue
            else:
                broken.append((rel, link, unpublished.get(link, 'リンク先が存在しない')))

        related = fm.get('related_posts')
        newest = None
        for entry in related if isinstance(related, list) else []:
            post = normalize(entry)
            if post not in published:
                dangling.append((rel, entry, unpublished.get(post, '記事が存在しない')))
            elif newest is None or published[post] > newest[1]:
                newest = (post, published[post])

        lastmod = day(fm.get('lastmod'))
        if newest and lastmod and newest[1] > lastmod:
            stale.append((rel, lastmod, newest[1], newest[0]))

        for key in REQUIRED:
            if not fm.get(key):
                missing.append((rel, key, 'が無い' if key not in fm else 'が空'))
        for key in RECOMMENDED:
            if not fm.get(key):
                recommended.append((rel, key))

    orphans = sorted(pages[u]['rel'] for u, n in inbound.items() if n == 0)
    return {
        'pages': pages, 'orphans': orphans, 'broken': broken, 'dangling': dangling,
        'stale': stale, 'missing': missing, 'recommended': recommended,
    }


def short(rel):
    return rel[len('content/wiki/'):]


def report(r):
    out = ["## Wiki Lint レポート", ""]

    out.append(f"### 孤立ページ ({len(r['orphans'])}件)")
    out += [f"- `{short(p)}` — どこからもリンクされていない" for p in r['orphans']]
    out.append("")

    out.append(f"### 欠落リンク ({len(r['broken'])}件)")
    out += [f"- `{short(p)}` → `/blogs{l}` — {why}" for p, l, why in r['broken']]
    out.append("")

    out.append(f"### related_posts 不整合 ({len(r['dangling'])}件)")
    out += [f"- `{short(p)}` → `{e}` — {why}" for p, e, why in r['dangling']]
    out.append("")

    out.append(f"### 古い可能性のあるページ ({len(r['stale'])}件)")
    out += [f"- `{short(p)}` (lastmod: {lm}) — ソース記事が {pm} に更新（`{post}`）"
            for p, lm, pm, post in r['stale']]
    out.append("")

    out.append(f"### フロントマター不備 ({len(r['missing']) + len(r['recommended'])}件)")
    out += [f"- `{short(p)}` — {k} {why}（必須）" for p, k, why in r['missing']]
    out += [f"- `{short(p)}` — {k} が未設定（推奨）" for p, k in r['recommended']]
    out.append("")

    counts = {}
    for page in r['pages'].values():
        section = short(page['rel']).split('/')[0]
        counts[section] = counts.get(section, 0) + 1
    out.append("### 統計")
    out.append(f"- 総ページ数: {len(r['pages'])}")
    out.append("- " + " / ".join(f"{s}: {n}" for s, n in sorted(counts.items())))
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--root', default=os.path.join(os.path.dirname(__file__), '..'))
    args = parser.parse_args()

    result = lint(os.path.abspath(args.root))
    print(report(result))
    return 1 if result['broken'] or result['dangling'] or result['missing'] else 0


if __name__ == '__main__':
    sys.exit(main())
