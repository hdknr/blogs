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

# Same shape, but capturing year and month so the permalink can be rebuilt.
PATH_YM_PATTERN = re.compile(r'content/posts/(\d{4})/(\d{2})/[^/]+\.md$')

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
        elif not tags:
            # Live since #653 filled the last of the 108 Gist-imported posts that
            # used to have one. An empty list is not the same as a missing key:
            # the key is present, so the required-field check above passes and the
            # post silently drops out of every tag page while still looking valid.
            violations.append("tags が空。タグページから外れるので最低 1 つ要る")

    if not PATH_PATTERN.search(repo_relative):
        violations.append("配置が content/posts/YYYY/MM/ 規約から外れている")

    return violations


def find_permalink_collisions(repo_root):
    """Return {permalink: [paths]} for posts that build the same URL.

    The permalink is /posts/:year/:month/:slug/, taken from the directory the
    post sits in plus its frontmatter slug -- NOT from the date field, because
    the build derives the path from the directory. Two posts that agree on all
    three collapse into one page.

    **Neither builder reports this.** Hugo silently kept one and dropped the
    other; Astro cannot emit the same route twice, so it also keeps one -- but
    it keeps a *different* one, because it iterates the collection in filename
    order. The migration flipped which of the pair was readable without any
    error on either side, and the dropped post's tags stay registered in the
    taxonomy, so a tag page lists an article nobody can open.

    Four pairs shipped that way before this check existed (#658).
    """
    seen = {}
    pattern = os.path.join(POSTS_DIR, '**', '*.md')
    for filepath in sorted(glob.glob(pattern, recursive=True)):
        if os.path.basename(filepath) == '_index.md':
            continue
        repo_relative = os.path.relpath(os.path.abspath(filepath), repo_root)
        match = PATH_YM_PATTERN.search(repo_relative)
        if not match:
            continue
        fm = parse_frontmatter(filepath)
        if not fm:
            continue
        if str(fm.get('draft', '')).strip().strip('"\'').lower() == 'true':
            continue
        slug = (fm.get('slug') or '').strip().strip('"\'')
        if not slug:
            continue
        year, month = match.group(1), match.group(2)
        seen.setdefault(f"/posts/{year}/{month}/{slug}/", []).append(repo_relative)
    return {url: paths for url, paths in seen.items() if len(paths) > 1}


def urlize(term):
    """The path Hugo builds for a taxonomy term, used only to spot collisions.

    Verified against real build output rather than assumed:

    - whitespace collapses to `-`   `Claude Code` -> claude-code
    - case is folded                `MCP`         -> mcp
    - `/` stays a PATH SEPARATOR    `AI/LLM`      -> ai/llm   (two directories)
    - `_` is preserved                `$GITHUB_ENV` -> github_env
    - `.` is preserved                `Claude.md`   -> claude.md
    - repeated `-` is NOT collapsed   `claude -p`   -> claude--p

    Checked against a real build: urlizing all 1161 tags reproduces the 1161
    directories under public/tags/ exactly. Folding `/` or `_` into `-` would
    fail CI on two tags that really do have separate pages.
    Keep this in sync with scripts/normalize_tags.py.
    """
    s = term.strip().lower()
    s = re.sub(r'\s+', '-', s)
    return re.sub(r'[^\w\-/.]', '', s, flags=re.UNICODE)


def collect_tags(repo_root):
    """Every tag spelling used across posts and the wiki, keyed by spelling."""
    spellings = {}
    for section in ('posts', 'wiki'):
        pattern = os.path.join(repo_root, 'content', section, '**', '*.md')
        for filepath in sorted(glob.glob(pattern, recursive=True)):
            if os.path.basename(filepath) == '_index.md':
                continue
            fm = parse_frontmatter(filepath)
            if not fm or 'tags' not in fm:
                continue
            for tag in parse_list_value(fm['tags']) or []:
                if tag:
                    spellings.setdefault(tag, os.path.relpath(filepath, repo_root))
    return spellings


def find_tag_collisions(repo_root):
    """Return {url_key: [spellings]} for tags that share one taxonomy page.

    Posts and the wiki feed one `tags` taxonomy, so `MCP` and `mcp` both build
    /tags/mcp/ and only the display name differs -- and which one wins is decided
    by map iteration order, so it changes between builds of identical content.
    Keeping the spellings unique is what makes the build reproducible (#651).
    """
    groups = {}
    for tag in collect_tags(repo_root):
        groups.setdefault(urlize(tag), []).append(tag)
    return {k: sorted(v) for k, v in groups.items() if len(v) > 1}


HUGO_SHORTCODE = re.compile(r'\{\{<\s*(\w+)')


def find_hugo_shortcodes(repo_root):
    """Return {relative_path: [shortcode names]} for leftover Hugo syntax.

    The site runs on Astro, which renders `{{< ref "..." >}}` as literal text.
    19 posts shipped that way after the migration, showing readers raw Hugo
    syntax where a cross-link should have been.

    Nothing else catches it. The pages build, no asset is missing, and a link
    that never becomes an <a> has no href for a link checker to fetch — so the
    internal link check stayed green throughout.

    Convert with scripts/convert_hugo_shortcodes.py.
    """
    found = {}
    for section in ('posts', 'wiki'):
        pattern = os.path.join(repo_root, 'content', section, '**', '*.md')
        for filepath in sorted(glob.glob(pattern, recursive=True)):
            with open(filepath, encoding='utf-8') as f:
                names = HUGO_SHORTCODE.findall(f.read())
            if names:
                found[os.path.relpath(filepath, repo_root)] = sorted(set(names))
    return found


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

    shortcodes = find_hugo_shortcodes(repo_root)
    for path in sorted(shortcodes):
        names = ', '.join(f'{{{{< {n} >}}}}' for n in shortcodes[path])
        print(f"NG {path}")
        print(f"     - Hugo ショートコードが残っている: {names}")

    permalinks = find_permalink_collisions(repo_root)
    for url in sorted(permalinks):
        print(f"NG パーマリンクの重複 {url}")
        for path in permalinks[url]:
            print(f"     - {path}")
        print("     - 同じ (年, 月, slug) の記事は 1 本しか公開されない。片方の slug を変えるか統合する")

    collisions = find_tag_collisions(repo_root)
    for key in sorted(collisions):
        print(f"NG タグの表記ゆれ /tags/{key}/")
        print(f"     - {', '.join(repr(t) for t in collisions[key])} が同じページに落ちる")

    if failures or collisions or shortcodes or permalinks:
        print(
            f"\n{checked} 件中 {len(failures)} 件が規約違反、"
            f"タグの表記ゆれ {len(collisions)} 件、"
            f"Hugo ショートコード残存 {len(shortcodes)} 件、"
            f"パーマリンク重複 {len(permalinks)} 件",
            file=sys.stderr,
        )
        return 1

    if not quiet:
        print(f"OK {checked} 件すべて規約を満たしています")
    return 0


if __name__ == '__main__':
    sys.exit(main())
