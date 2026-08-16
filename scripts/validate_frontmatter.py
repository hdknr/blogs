#!/usr/bin/env python3
"""Validate frontmatter and file placement of Hugo blog posts.

Every post here is drafted by an AI pipeline, so frontmatter drift is the main
failure mode: Hugo silently accepts an unknown category and happily builds a
taxonomy page for it, so nothing ever goes red. `お知らせ` sat in the tree that
way until it was found by counting categories by hand.

This turns that silence into a non-zero exit.

Usage:
    python3 scripts/validate_frontmatter.py            # validate, exit 1 on violations
    python3 scripts/validate_frontmatter.py --quiet     # only print violations
"""

import os
import re
import sys
import glob

POSTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'content', 'posts')

# The literal frontmatter values consumed by categorize.py. Keep in sync with the
# "Category list" section of CLAUDE.md.
VALID_CATEGORIES = {
    "AI/LLM",
    "セキュリティ",
    "クラウド/インフラ",
    "Web開発",
    "プログラミング言語",
    "モバイル",
    "データベース",
    "ツール/開発環境",
    "ビジネス/キャリア",
    "地域/グルメ",
    "その他",
}

REQUIRED_KEYS = ["title", "date", "slug", "categories", "tags"]

# content/posts/YYYY/MM/<anything>.md
PATH_PATTERN = re.compile(r'content/posts/\d{4}/\d{2}/[^/]+\.md$')

FRONTMATTER_PATTERN = re.compile(r'^---\n(.*?)\n---\n', re.DOTALL)


def parse_frontmatter(filepath):
    """Return the frontmatter as a dict of raw string values, or None if absent."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        return None

    fm = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, _, value = line.partition(':')
            fm[key.strip()] = value.strip()

    return fm


def parse_list_value(raw):
    """Parse a YAML inline list like ["a", "b"] into a list of strings.

    Posts here always use the inline form, which categorize.py also writes.
    A block list is reported as unparseable rather than silently skipped.
    """
    raw = raw.strip()
    if not (raw.startswith('[') and raw.endswith(']')):
        return None

    inner = raw[1:-1].strip()
    if not inner:
        return []

    return [item.strip().strip('"').strip("'") for item in inner.split(',')]


def validate_post(filepath, repo_relative):
    """Return a list of violation strings for one post."""
    violations = []

    fm = parse_frontmatter(filepath)
    if fm is None:
        return ["frontmatter が無い、または --- で囲まれていない"]

    for key in REQUIRED_KEYS:
        if key not in fm:
            violations.append(f"必須フィールド `{key}` が無い")

    raw_categories = fm.get('categories')
    if raw_categories is not None:
        categories = parse_list_value(raw_categories)
        if categories is None:
            violations.append(f"categories がインライン配列として読めない: {raw_categories}")
        elif not categories:
            # An empty list is not the same as a missing key: the key is present,
            # so the required-field check above passes and the post ends up in no
            # category at all. Silent, and exactly what an empty AI response looks
            # like.
            violations.append("categories が空。最低 1 つのカテゴリが要る")
        else:
            for category in categories:
                if category not in VALID_CATEGORIES:
                    violations.append(
                        f"規定外のカテゴリ `{category}`"
                        f"（許可: {', '.join(sorted(VALID_CATEGORIES))}）"
                    )

    raw_tags = fm.get('tags')
    if raw_tags is not None:
        tags = parse_list_value(raw_tags)
        if tags is None:
            violations.append(f"tags がインライン配列として読めない: {raw_tags}")
        # An empty `tags: []` is deliberately NOT a violation yet: 108 of the
        # Gist-imported posts have one, so failing on it would make this check
        # red on arrival and teach everyone to skip it. Tracked in #647, which
        # owns the tag vocabulary and can tag those posts before the rule lands.

    if not PATH_PATTERN.search(repo_relative):
        violations.append("配置が content/posts/YYYY/MM/ 規約から外れている")

    return violations


def main():
    quiet = '--quiet' in sys.argv

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    pattern = os.path.join(POSTS_DIR, '**', '*.md')

    failures = {}
    checked = 0

    for filepath in sorted(glob.glob(pattern, recursive=True)):
        # _index.md is a Hugo section page, not a post: it has no date, no
        # categories and no tags by design, and lives outside YYYY/MM.
        if os.path.basename(filepath) == '_index.md':
            continue

        checked += 1
        repo_relative = os.path.relpath(os.path.abspath(filepath), repo_root)
        violations = validate_post(filepath, repo_relative)
        if violations:
            failures[repo_relative] = violations

    for path in sorted(failures):
        print(f"NG {path}")
        for violation in failures[path]:
            print(f"     - {violation}")

    if failures:
        print(f"\n{checked} 件中 {len(failures)} 件が規約違反", file=sys.stderr)
        return 1

    if not quiet:
        print(f"OK {checked} 件すべて規約を満たしています")
    return 0


if __name__ == '__main__':
    sys.exit(main())
