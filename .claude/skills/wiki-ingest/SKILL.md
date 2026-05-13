---
name: wiki-ingest
description: Auto-generate or update wiki pages by ingesting blog posts
arguments:
  - name: target
    description: "Target: a post path (`content/posts/...`), a category name, or `all` (batch over every post)"
    required: true
---

Read the specified blog posts and auto-generate or update the wiki pages (concepts / tools / guides).

## Wiki page classification

### `concepts/` — technical concepts and terminology

- Explanations of technical concepts, patterns, and architectures.
- Examples: RAG, prompt engineering, zero trust, microservices.
- Filename: `<concept-slug>.md`

### `tools/` — tools, services, libraries

- Concrete tools, services, frameworks, libraries.
- Examples: Claude Code, Hugo, Docker, Terraform.
- Filename: `<tool-slug>.md`

### `guides/` — how-tos / consolidated procedures

- Practical procedures and configuration sequences that span multiple posts.
- Examples: Hugo + GitHub Pages setup, Claude Code customisation.
- Filename: `<guide-slug>.md`

## Wiki page frontmatter

```yaml
---
title: "ページタイトル"
description: "1行の概要説明"
date: YYYY-MM-DD        # creation date
lastmod: YYYY-MM-DD     # last update date
aliases: ["別名1", "別名2"]  # search aliases (optional)
related_posts:          # source blog posts
  - "/posts/YYYY/MM/slug/"
tags: ["tag1", "tag2"]  # related tags
---
```

> Frontmatter string fields (`title`, `description`, `aliases`) are written in Japanese — wiki pages themselves are Japanese.

## Ingest procedure

### 1. Identify the target posts

- **Post-path arg**: read that file.
- **Category arg**: scan `content/posts/` for posts in that category.
- **`all`**: target every post under `content/posts/` (batch mode).

### 2. Analyse each post

For each post, extract:

- **Key entities**: the concepts, tools, and procedures the post is mainly about.
- **Category and tags**: read from the frontmatter.
- **Summary**: a 3–5 sentence summary of the main information.

### 3. Generate / update wiki pages

For each extracted entity:

1. **Check for an existing page** under `content/wiki/` matching the entity.
2. **Create** a new page in the appropriate subdirectory if none exists.
3. **Update** by appending to `related_posts` and merging new information into the body.
4. **Cross-link** related wiki pages to each other.

### 4. Wiki page body structure

```markdown
## 概要

{2–3 sentence concise description of the entity}

## 詳細

{detailed information distilled from the source posts}

## 関連ページ

- [関連 Wiki ページ](/blogs/wiki/section/slug/)

## ソース記事

- [記事タイトル](/blogs/posts/YYYY/MM/slug/) — YYYY-MM-DD
```

> Section headings inside wiki pages stay Japanese (`概要`, `詳細`, `関連ページ`, `ソース記事`) — they are reader-facing.

### 5. Index update

After processing, verify that each section's `_index.md` reflects the latest links.

## Batch mode (`all`)

When processing every post:

1. Group by category before processing.
2. Report progress after finishing each category.
3. Merge duplicate entities.
4. Report final statistics (pages created / updated).

## Notes

- **Wiki pages are written in Japanese.**
- Do NOT copy whole post bodies verbatim — summarise and integrate into reusable knowledge.
- Keep a single wiki page from growing too long (rule of thumb: ≤ 200 lines).
- Verify the Hugo build with `hugo --gc`.
