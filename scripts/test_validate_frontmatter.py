#!/usr/bin/env python3
"""Tests for validate_frontmatter.

Run with `python3 scripts/test_validate_frontmatter.py`. No test runner needed --
this ships alongside a CI workflow, so it stays dependency-free.

The weight sits on the ways this validator could go *quietly* blind, because a
validator that passes everything looks exactly like a clean repo:

- The category parser is the whole check. `categories: ["お知らせ"]` has to come
  apart into `お知らせ` and be rejected; if the quote stripping or the split is
  off, every category silently reads as valid and the drift this script exists
  to catch walks straight through.
- A block-style YAML list must be REPORTED, not skipped. Skipping an unparseable
  value is the same failure as accepting it -- the post goes unchecked either way.
- `_index.md` is a Hugo section page with no date, categories or tags by design.
  If it is not excluded, the run is permanently red and everyone learns to ignore
  it, which is worse than not having the check.
"""

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import validate_frontmatter as vf

VALID_POST = """---
title: "テスト記事"
date: 2026-08-16
lastmod: 2026-08-16
draft: false
slug: "test-post"
categories: ["AI/LLM"]
tags: ["claude", "test"]
---

本文。
"""

UNKNOWN_CATEGORY = VALID_POST.replace('["AI/LLM"]', '["お知らせ"]')

MISSING_SLUG = VALID_POST.replace('slug: "test-post"\n', '')

BLOCK_LIST_CATEGORIES = """---
title: "テスト記事"
date: 2026-08-16
slug: "test-post"
categories:
  - AI/LLM
tags: ["claude"]
---

本文。
"""

EMPTY_CATEGORIES = VALID_POST.replace('["AI/LLM"]', '[]')

EMPTY_TAGS = VALID_POST.replace('["claude", "test"]', '[]')

NO_FRONTMATTER = "見出しだけの本文。\n"

GOOD_PATH = "content/posts/2026/08/2026-08-16-test-post.md"
BAD_PATH = "content/posts/test-post.md"

failures = []


def check(label, condition):
    if condition:
        print(f"  ok   {label}")
    else:
        print(f"  FAIL {label}")
        failures.append(label)


def validate(text, repo_relative=GOOD_PATH):
    """Write `text` to a temp file and run the real validator over it."""
    with tempfile.NamedTemporaryFile('w', suffix='.md', encoding='utf-8', delete=False) as f:
        f.write(text)
        path = f.name
    try:
        return vf.validate_post(path, repo_relative)
    finally:
        os.unlink(path)


print("parse_list_value")
check('インライン配列を分解する',
      vf.parse_list_value('["AI/LLM", "その他"]') == ["AI/LLM", "その他"])
check('シングルクォートも剥がす',
      vf.parse_list_value("['AI/LLM']") == ["AI/LLM"])
check('空配列は空リスト',
      vf.parse_list_value('[]') == [])
check('余分な空白があっても分解できる',
      vf.parse_list_value('[  "AI/LLM" ,  "その他"  ]') == ["AI/LLM", "その他"])
# None means "could not parse" and must stay distinguishable from [] (= no
# categories). Collapsing the two would let a block list read as "nothing to check".
check('ブロック形式は None を返す（空リストと区別する）',
      vf.parse_list_value('') is None)

print("validate_post")
check('正しい記事は違反なし', validate(VALID_POST) == [])

violations = validate(UNKNOWN_CATEGORY)
check('規定外カテゴリを検出する',
      any('お知らせ' in v for v in violations))

violations = validate(MISSING_SLUG)
check('必須フィールドの欠落を検出する',
      any('slug' in v for v in violations))

violations = validate(BLOCK_LIST_CATEGORIES)
check('ブロック形式の categories を黙って通さない',
      any('インライン配列' in v for v in violations))

# `categories: []` keeps the key present, so the required-field check passes and
# the post silently lands in no category. An empty AI response looks like this.
violations = validate(EMPTY_CATEGORIES)
check('空の categories を検出する',
      any('categories が空' in v for v in violations))

# Enforced since #653 tagged the last of the 108 Gist-imported posts that used to
# carry `tags: []`. Same shape as the empty-categories case above: the key is
# present so the required-field check passes, and the post drops out of every tag
# page while still looking valid.
violations = validate(EMPTY_TAGS)
check('空の tags を検出する',
      any('tags が空' in v for v in violations))

violations = validate(NO_FRONTMATTER)
check('frontmatter 無しを検出する',
      any('frontmatter' in v for v in violations))

violations = validate(VALID_POST, repo_relative=BAD_PATH)
check('YYYY/MM から外れた配置を検出する',
      any('YYYY/MM' in v for v in violations))

print("urlize")
# Every case below was read off a real build's public/tags/ directories, not
# guessed. Two earlier guesses were wrong -- `/` and `_` were assumed to fold
# into `-`, and repeated hyphens were assumed to collapse -- and each wrong guess
# makes the collision guard fail CI on two tags that have genuinely separate
# pages. Pin the rules so the next edit has to face the same evidence.
check('空白は - になる', vf.urlize('Claude Code') == 'claude-code')
check('大文字は畳まれる', vf.urlize('MCP') == 'mcp')
check('/ はパス区切りとして残る', vf.urlize('AI/LLM') == 'ai/llm')
check('_ は残る', vf.urlize('$GITHUB_ENV') == 'github_env')
check('. は残る', vf.urlize('Claude.md') == 'claude.md')
check('連続する - は畳まれない', vf.urlize('claude -p') == 'claude--p')
check('/ と - は別物として扱う', vf.urlize('AI/LLM') != vf.urlize('AI-LLM'))

print("find_permalink_collisions")
# The permalink is built from the DIRECTORY plus the slug, not from the date
# field, because that is what the builder does. Four pairs shipped colliding
# before this check existed (#658) and neither Hugo nor Astro said a word --
# they just kept one and dropped the other, and disagreed about which.
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    month = root / 'content' / 'posts' / '2026' / '03'
    month.mkdir(parents=True)

    def post(name, slug, draft=False):
        (month / name).write_text(
            f'---\ntitle: "t"\ndate: 2026-03-01\ndraft: {str(draft).lower()}\n'
            f'slug: "{slug}"\ncategories: ["AI/LLM"]\ntags: ["x"]\n---\n\n本文。\n',
            encoding='utf-8')

    post('2026-03-09-a.md', 'same-slug')
    post('2026-03-10-b.md', 'same-slug')
    post('2026-03-11-c.md', 'other-slug')

    original = vf.POSTS_DIR
    try:
        vf.POSTS_DIR = str(root / 'content' / 'posts')
        found = vf.find_permalink_collisions(str(root))
    finally:
        vf.POSTS_DIR = original

    check('同じ (年, 月, slug) の2本を検出する',
          list(found) == ['/posts/2026/03/same-slug/'])
    check('衝突している両方のパスを報告する',
          len(found.get('/posts/2026/03/same-slug/', [])) == 2)
    check('衝突していない記事は報告しない',
          not any('other-slug' in u for u in found))

# A draft never builds a page, so it cannot collide with anything. Counting it
# would make the check fire on a pair that does not actually exist in the output.
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    month = root / 'content' / 'posts' / '2026' / '03'
    month.mkdir(parents=True)
    (month / '2026-03-09-live.md').write_text(
        '---\ntitle: "t"\ndate: 2026-03-01\ndraft: false\nslug: "dup"\n'
        'categories: ["AI/LLM"]\ntags: ["x"]\n---\n\n本文。\n', encoding='utf-8')
    (month / '2026-03-10-draft.md').write_text(
        '---\ntitle: "t"\ndate: 2026-03-01\ndraft: true\nslug: "dup"\n'
        'categories: ["AI/LLM"]\ntags: ["x"]\n---\n\n本文。\n', encoding='utf-8')

    original = vf.POSTS_DIR
    try:
        vf.POSTS_DIR = str(root / 'content' / 'posts')
        found = vf.find_permalink_collisions(str(root))
    finally:
        vf.POSTS_DIR = original

    check('draft は衝突として数えない', found == {})

print("VALID_CATEGORIES")
# The list is duplicated in CLAUDE.md for humans; a mismatch there is a doc bug,
# but a shrunk set here would silently start rejecting real posts.
check('11 カテゴリが定義されている', len(vf.VALID_CATEGORIES) == 11)
check('その他 が含まれる（categorize.py のフォールバック先）',
      "その他" in vf.VALID_CATEGORIES)

if failures:
    print(f"\n{len(failures)} 件失敗", file=sys.stderr)
    sys.exit(1)

print("\nすべて成功")
