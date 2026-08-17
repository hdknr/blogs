import { defineCollection } from "astro:content";
import { z } from "astro/zod";
import { glob } from "astro/loaders";
import config from "@/config";

// Read the Hugo content tree in place. The 1032 posts are NOT copied or
// rewritten: the schema bends to the existing frontmatter, not the other way
// round. Renaming the frontmatter across 1032 files to match AstroPaper's own
// field names would be a huge diff whose only purpose is to satisfy a theme.
export const BLOG_PATH = "../content/posts";
export const WIKI_PATH = "../content/wiki";

// `_index.md` is a Hugo section page (no date, no categories, no tags by
// design), so it is excluded the same way validate_frontmatter.py excludes it.
const CONTENT_GLOB = "**/[^_]*.md";

const posts = defineCollection({
  loader: glob({ pattern: CONTENT_GLOB, base: BLOG_PATH }),
  schema: z.object({
    title: z.string(),
    // Hugo names these `date`/`lastmod`. Coerced rather than z.date() because
    // some posts quote the value, which YAML then hands over as a string.
    date: z.coerce.date(),
    lastmod: z.coerce.date().optional(),
    // The permalink is built from date + slug, so this is load-bearing for URL
    // preservation. All 1032 posts have it (verified).
    slug: z.string(),
    draft: z.boolean().default(false),
    // .nullish() rather than plain .default(): a bare `tags:` with no value
    // parses as null, not undefined, and 7 wiki files really are written that
    // way. Hugo tolerated it silently; the schema has to say so on purpose.
    categories: z.array(z.string()).nullish().transform(v => v ?? []),
    tags: z.array(z.string()).nullish().transform(v => v ?? []),
    // Optional on purpose: 755 of 1032 posts have no description. AstroPaper's
    // own schema requires it, which would fail the build on three quarters of
    // the site.
    description: z.string().optional(),
    summary: z.string().optional(),
    source_url: z.string().optional(),
    gist_id: z.string().optional(),
    gist_url: z.string().optional(),
  }),
});

const wiki = defineCollection({
  loader: glob({ pattern: CONTENT_GLOB, base: WIKI_PATH }),
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),
    date: z.coerce.date().optional(),
    lastmod: z.coerce.date().optional(),
    aliases: z.array(z.string()).nullish().transform(v => v ?? []),
    related_posts: z.array(z.string()).nullish().transform(v => v ?? []),
    tags: z.array(z.string()).nullish().transform(v => v ?? []),
  }),
});

const pages = defineCollection({
  loader: glob({ pattern: "**/[^_]*.{md,mdx}", base: "./src/content/pages" }),
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),
    ogImage: z.string().optional(),
    canonicalURL: z.string().optional(),
  }),
});

export const collections = { posts, wiki, pages };
