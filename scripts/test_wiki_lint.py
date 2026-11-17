#!/usr/bin/env python3
"""Tests for wiki_lint.

Run with `python3 scripts/test_wiki_lint.py`. Dependency-free, like the other
script tests.

A lint that reports nothing looks exactly like a healthy wiki, so every check
gets a positive control: plant one defect in a throwaway tree and require that
check -- and only that check -- to fire. The clean tree must come back empty,
or the run is permanently noisy and nobody reads it.
"""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import wiki_lint as wl

POST = """---
title: "記事"
date: 2026-11-01
lastmod: {lastmod}
slug: "{slug}"
draft: {draft}
categories: ["AI/LLM"]
tags: ["test"]
---

本文。
"""

WIKI = """---
title: "{title}"
description: "説明"
date: 2026-11-01
lastmod: {lastmod}
aliases: ["{title}"]
related_posts:
  - "/posts/2026/11/{related}/"
tags: ["test"]
---

## 関連ページ

- [相手](/blogs/wiki/concepts/{other}/)
- [ソース](/blogs/posts/2026/11/{related}/)
- [一覧](/blogs/posts/)

```markdown
[コードブロック内の例](/blogs/wiki/concepts/does-not-exist/)
```

`[インラインの例](/blogs/posts/2026/11/nope/)`
"""


def build(tmp, a=None, b=None, posts=None):
    """A clean two-page wiki that links both ways, plus overrides."""
    files = {
        'content/posts/2026/11/2026-11-01-alpha.md':
            POST.format(lastmod='2026-11-01', slug='alpha', draft='false'),
        'content/wiki/_index.md': '---\ntitle: "Wiki"\n---\n',
        'content/wiki/concepts/_index.md': '---\ntitle: "C"\n---\n',
        'content/wiki/concepts/a.md': a or WIKI.format(
            title='a', lastmod='2026-11-01', related='alpha', other='b'),
        'content/wiki/concepts/b.md': b or WIKI.format(
            title='b', lastmod='2026-11-01', related='alpha', other='a'),
    }
    files.update(posts or {})
    for rel, text in files.items():
        path = os.path.join(tmp, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
    return wl.lint(tmp)


def fired(result):
    return {k for k in ('orphans', 'broken', 'dangling', 'stale', 'missing', 'recommended')
            if result[k]}


def check(name, cond):
    print(f"{'ok  ' if cond else 'FAIL'} {name}")
    return cond


def main():
    results = []
    with tempfile.TemporaryDirectory() as tmp:
        r = build(tmp)
        results.append(check("clean tree reports nothing (code blocks ignored, /posts/ ok)",
                             fired(r) == set()))

    with tempfile.TemporaryDirectory() as tmp:
        a = WIKI.format(title='a', lastmod='2026-11-01', related='alpha', other='a')
        r = build(tmp, a=a)
        results.append(check("orphan: b loses its only inbound link; self-link doesn't count",
                             fired(r) == {'orphans'}
                             and r['orphans'] == ['content/wiki/concepts/b.md']))

    with tempfile.TemporaryDirectory() as tmp:
        a = WIKI.format(title='a', lastmod='2026-11-01', related='alpha', other='b') \
            + "\n[壊れ](/blogs/wiki/tools/ghost/)\n"
        r = build(tmp, a=a)
        results.append(check("broken wiki link is reported",
                             fired(r) == {'broken'}
                             and r['broken'][0][1] == '/wiki/tools/ghost/'))

    with tempfile.TemporaryDirectory() as tmp:
        a = WIKI.format(title='a', lastmod='2026-11-01', related='alpha', other='b') \
            + "\n[下書き](/blogs/posts/2026/11/beta/#sec)\n"
        posts = {'content/posts/2026/11/2026-11-02-beta.md':
                 POST.format(lastmod='2026-11-02', slug='beta', draft='true')}
        r = build(tmp, a=a, posts=posts)
        results.append(check("link to a draft post is broken, and says draft",
                             fired(r) == {'broken'} and 'draft' in r['broken'][0][2]))

    with tempfile.TemporaryDirectory() as tmp:
        a = WIKI.format(title='a', lastmod='2026-11-01', related='old', other='b') \
            .replace('/blogs/posts/2026/11/old/', '/blogs/posts/')
        posts = {'content/archive/posts/2026/11/2026-11-01-old.md':
                 POST.format(lastmod='2026-11-01', slug='old', draft='false')}
        r = build(tmp, a=a, posts=posts)
        results.append(check("related_posts to an archived post dangles, and says archived",
                             fired(r) == {'dangling'} and 'アーカイブ' in r['dangling'][0][2]))

    with tempfile.TemporaryDirectory() as tmp:
        # Filename slug differs from frontmatter slug: resolve by frontmatter.
        posts = {'content/posts/2026/11/2026-11-01-alpha.md':
                 POST.format(lastmod='2026-11-01', slug='renamed', draft='false')}
        r = build(tmp, posts=posts)
        results.append(check("posts resolve by frontmatter slug, not filename",
                             'dangling' in fired(r) and 'broken' in fired(r)))

    with tempfile.TemporaryDirectory() as tmp:
        posts = {'content/posts/2026/11/2026-11-01-alpha.md':
                 POST.format(lastmod='2026-11-10', slug='alpha', draft='false')}
        r = build(tmp, posts=posts)
        results.append(check("stale: post lastmod newer than wiki lastmod",
                             fired(r) == {'stale'} and len(r['stale']) == 2))

    with tempfile.TemporaryDirectory() as tmp:
        a = WIKI.format(title='a', lastmod='2026-11-01', related='alpha', other='b') \
            .replace('description: "説明"\n', '') \
            .replace('related_posts:\n  - "/posts/2026/11/alpha/"\n', 'related_posts:\n') \
            .replace('aliases: ["a"]', 'aliases: []')
        r = build(tmp, a=a)
        keys = {(k, why) for _, k, why in r['missing']}
        results.append(check("missing description, empty block related_posts, empty aliases",
                             fired(r) == {'missing', 'recommended'}
                             and keys == {('description', 'が無い'), ('related_posts', 'が空')}))

    with tempfile.TemporaryDirectory() as tmp:
        a = WIKI.format(title='a', lastmod='2026-11-01', related='alpha', other='b') \
            + "\n[壊れ](/blogs/wiki/tools/ghost/)\n"
        build(tmp, a=a)
        sys.argv = ['wiki_lint.py', '--root', tmp]
        devnull = open(os.devnull, 'w')
        stdout, sys.stdout = sys.stdout, devnull
        try:
            code = wl.main()
        finally:
            sys.stdout = stdout
            devnull.close()
        results.append(check("exit status 1 on a broken link", code == 1))

    failed = results.count(False)
    print(f"\n{len(results) - failed}/{len(results)} passed")
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
