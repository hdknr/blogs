import type { CollectionEntry } from "astro:content";
import { postFilter } from "./postFilter";

/**
 * Posts eligible to be shown, newest first by `date`.
 *
 * Sorting by `lastmod ?? date` -- AstroPaper's default -- is wrong for this
 * site. 1031 of the 1032 posts carry a `lastmod`, and touching a post updates
 * it, so an old article rises to the top of the home page and the feed the
 * moment anyone edits it. It showed up immediately: `hello.md` is dated
 * 2026-03-08, picked up `lastmod: 2026-08-16` during the frontmatter cleanup in
 * #646, and took first place on the home page ahead of the August posts.
 *
 * Hugo orders lists by `date`. Match it.
 */
export function getSortedPosts(posts: CollectionEntry<"posts">[]) {
  return posts
    .filter(postFilter)
    .sort(
      (a, b) => new Date(b.data.date).getTime() - new Date(a.data.date).getTime()
    );
}
