import type { CollectionEntry } from "astro:content";
import { postFilter } from "./postFilter";
import { slugifyStr } from "./slugify";

export type Term = {
  /** Slug used in the URL, via Hugo's urlize. */
  term: string;
  /** Original spelling, used for display. */
  name: string;
};

export type Taggable =
  | CollectionEntry<"posts">
  | CollectionEntry<"wiki">;

/**
 * Posts and wiki pages feed ONE `tags` taxonomy in Hugo, so a tag route built
 * from posts alone loses every tag that only a wiki page carries -- 86 of them
 * here, `ALB`, `Arrow`, `ASGI` and the like. Exactly the shared-taxonomy shape
 * that hdknr/blogs#647 hit from the other direction.
 *
 * `categories` is posts-only; wiki frontmatter has no such field.
 */
export function collectTerms(
  entries: Taggable[],
  field: "tags" | "categories"
): Term[] {
  const seen = new Map<string, string>();

  for (const entry of entries) {
    const values = (entry.data as Record<string, unknown>)[field];
    if (!Array.isArray(values)) continue;
    for (const value of values as string[]) {
      const term = slugifyStr(value);
      if (term && !seen.has(term)) seen.set(term, value);
    }
  }

  return [...seen]
    .map(([term, name]) => ({ term, name }))
    .sort((a, b) => a.term.localeCompare(b.term));
}

export function hasTerm(
  entry: Taggable,
  field: "tags" | "categories",
  term: string
): boolean {
  const values = (entry.data as Record<string, unknown>)[field];
  if (!Array.isArray(values)) return false;
  return (values as string[]).some(value => slugifyStr(value) === term);
}

/**
 * Hugo orders list pages by `date` descending. AstroPaper sorts by
 * `lastmod ?? date`, which would shuffle which post lands on which page --
 * same URLs, different contents.
 */
export function sortByDate<T extends Taggable>(entries: T[]): T[] {
  return [...entries].sort(
    (a, b) =>
      new Date(b.data.date ?? 0).getTime() -
      new Date(a.data.date ?? 0).getTime()
  );
}

export function visiblePosts(
  posts: CollectionEntry<"posts">[]
): CollectionEntry<"posts">[] {
  return posts.filter(postFilter);
}
