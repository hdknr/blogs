import { getRelativeLocaleUrl } from "astro:i18n";
import type { CollectionEntry } from "astro:content";
import config from "@/config";

type PostLike = Pick<CollectionEntry<"posts">, "data">;

/**
 * Rebuilds Hugo's permalink: `[permalinks.page] posts = '/posts/:year/:month/:slug/'`.
 *
 * Both parts come from frontmatter, never from the file path. The year/month
 * directories do happen to agree with `date` for all 1031 posts, but the slug
 * does NOT always agree with the filename: `2026-03-19-openclaw-overview.md`
 * carries `slug: "openclaw-agent-runtime"`, and one other post is the same.
 * Deriving from the filename would silently move those two URLs.
 *
 * Timezone matters here too. The dates are bare `YYYY-MM-DD`, which JS parses as
 * UTC midnight, so reading them back with local getters can roll a 1st-of-month
 * post into the previous month. Use the UTC getters.
 */
function getPostSlugPath(post: PostLike): string {
  const date = post.data.date;
  const year = date.getUTCFullYear();
  const month = String(date.getUTCMonth() + 1).padStart(2, "0");
  return `${year}/${month}/${post.data.slug}`;
}

/**
 * Route param for `getStaticPaths` in `posts/[...slug]`. The rest parameter
 * expands `2026/08/my-post` into `/posts/2026/08/my-post/`.
 */
export function getPostSlug(post: PostLike): string {
  return `/${getPostSlugPath(post)}`;
}

/** Navigable URL for `<a href>` and RSS, with base and locale applied. */
export function getPostUrl(
  post: PostLike,
  locale: string | undefined = config.site.lang
): string {
  return getRelativeLocaleUrl(locale, `posts/${getPostSlugPath(post)}/`);
}
