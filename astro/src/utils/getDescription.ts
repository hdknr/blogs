import type { CollectionEntry } from "astro:content";

/**
 * Per-post description for `<meta name="description">` and the OG tags.
 *
 * 755 of the 1032 posts have no `description`. Falling through to the site-wide
 * one -- AstroPaper's default -- stamps "Gist ブログのまとめサイト" onto three
 * quarters of the site, so every search snippet and every shared link says the
 * same thing. That is worse than saying nothing.
 *
 * Hugo's order was: `description`, else `summary`, else an excerpt of the body.
 * `summary` exists in the frontmatter of older posts and was being ignored
 * entirely -- it was in the schema but nothing read it.
 */
const MAX = 160;

function excerpt(body: string): string {
  const text = body
    .replace(/```[\s\S]*?```/g, "") // fenced code
    .replace(/!\[[^\]]*\]\([^)]*\)/g, "") // images
    .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1") // links -> their text
    // Strip the `#` markers but KEEP the heading text. Many of the imported
    // Gist posts open with a heading that is the only prose on the page; drop
    // it and the description becomes a bare URL.
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/[*_`>|]/g, "")
    .replace(/\s+/g, " ")
    .trim();

  if (text.length <= MAX) return text;
  return text.slice(0, MAX).trimEnd() + "…";
}

export function getDescription(post: CollectionEntry<"posts">): string {
  return post.data.description || post.data.summary || excerpt(post.body ?? "");
}
