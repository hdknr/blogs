---
name: wiki-lint
description: Health-check the wiki — inconsistencies, orphan pages, broken links, stale entries
arguments: []
---

Inspect the wiki knowledge base for problems and report (and optionally fix) them.

## Run the script — do not re-check by hand

All five checks below are mechanical and implemented in `scripts/wiki_lint.py`. Run it
and use its output as the report; **do not Read/Grep the wiki pages to redo the checks**
(that was ~150 pages of reading for answers a script gives in under a second).

```bash
python3 scripts/wiki_lint.py
```

- Output is the Markdown report in the format below, already in Japanese.
- Exit 1 = broken links, dangling `related_posts`, or missing required fields.
  Orphans, stale pages and missing `aliases` are advisory (exit 0).
- Read individual pages only when proposing a concrete fix (e.g. which page should link
  to an orphan).
- If you change the script, run `python3 scripts/test_wiki_lint.py` — each check has a
  positive control there.

The sections below document what the script checks.

## Checks

### 1. Orphan page detection

Find wiki pages that no other wiki page links to.

- Scan every page under `content/wiki/`.
- Collect `/blogs/wiki/...` link targets anywhere in each page's body (not only the
  "関連ページ" section), ignoring code blocks and self-links.
- List the pages that nobody links to.

### 2. Broken link detection

Find wiki-internal links that point at non-existent pages.

- Extract internal links (`/blogs/wiki/...` and `/blogs/posts/...`) from each page.
- Wiki links must match a page under `content/wiki/`; post links must match a published
  post by permalink (directory year/month + frontmatter `slug`). Draft and archived posts
  count as dangling, and the report says which.
- List the dangling links.

### 3. `related_posts` validation

Confirm that every `related_posts` entry refers to an existing blog post.

- Extract `related_posts` from each wiki page's frontmatter.
- Confirm the corresponding `content/posts/` file exists.
- List the dangling references.

### 4. Staleness detection

Find wiki pages whose `lastmod` is older than their source posts.

- For each wiki page, compare its `lastmod` against the `lastmod` of every post in `related_posts`.
- Flag any wiki page that is older than its source — it likely needs refreshing.

### 5. Frontmatter completeness

Find pages missing required frontmatter fields.

- Required: `title`, `description`, `date`, `lastmod`, `related_posts`, `tags`.
- Recommended: `aliases`.

## Output format

```markdown
## Wiki Lint レポート

### 孤立ページ (X件)
- `concepts/xxx.md` — どこからもリンクされていない

### 欠落リンク (X件)
- `tools/yyy.md` → `/blogs/wiki/concepts/zzz/` — リンク先が存在しない

### related_posts 不整合 (X件)
- `guides/aaa.md` → `/posts/2026/01/bbb/` — 記事が存在しない

### 古い可能性のあるページ (X件)
- `concepts/ccc.md` (lastmod: 2026-01-01) — ソース記事が 2026-03-15 に更新

### フロントマター不備 (X件)
- `tools/ddd.md` — aliases が未設定

### 統計
- 総ページ数: XX
- concepts: XX / tools: XX / guides: XX
```

> The report is user-facing, so its headings and prose stay Japanese.

## Suggested fixes

When problems are found, suggest:

- **Orphan page** → add a reciprocal link from a related wiki page.
- **Broken link** → create the missing target page, or remove the link.
- **`related_posts` mismatch** → correct the path, or drop the reference.
- **Stale page** → re-run `/wiki-ingest` against the source post.
- **Missing frontmatter** → fill in the missing fields.

Apply fixes only after the user confirms.
