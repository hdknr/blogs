# Archived posts

Posts dated 2025 and earlier (298 files), moved out of `content/posts/` because
they are too thin to publish.

Nothing here is built or checked:

- Astro's `posts` collection reads only `content/posts/` (`astro/src/content.config.ts`).
- `scripts/validate_frontmatter.py`, `categorize.py` and `normalize_tags.py` scan
  `content/posts/` and `content/wiki/` only.

To republish a post, `git mv` it back to `content/posts/YYYY/MM/` — its URL is
built from date + slug, so it returns at the same address.
