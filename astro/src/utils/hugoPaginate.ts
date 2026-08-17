/**
 * Hugo's pagination shape, which Astro's own `paginate()` does not produce.
 *
 * For a list of N items at 10 per page Hugo publishes:
 *
 *   /base/          full page 1
 *   /base/page/1/   315-byte redirect back to /base/
 *   /base/page/2/   full page 2
 *   ...
 *   /base/page/K/   full page K
 *
 * `page/1` being a redirect rather than a copy is why the site has 1648
 * redirect pages against 2879 real ones. AstroPaper paginates as `/posts/10/`,
 * so keeping the reader's bookmarks alive means rebuilding this shape rather
 * than adopting the theme's.
 */
export const PAGE_SIZE = 10;

export type PageParam = string | undefined;

export type HugoPageProps<T> = {
  items: T[];
  current: number;
  lastPage: number;
  /** Set when this route is `page/1`, which only redirects to the base URL. */
  redirectTo?: string;
};

export type HugoPageEntry<T> = {
  /** Rest-parameter value: `undefined` for the base, `page/N` otherwise. */
  param: PageParam;
  props: HugoPageProps<T>;
};

/**
 * @param baseUrl absolute path of the un-paginated page, used as the `page/1`
 *                redirect target. Pass it already prefixed and slash-terminated.
 */
export function hugoPaginate<T>(
  items: T[],
  baseUrl: string,
  pageSize: number = PAGE_SIZE
): HugoPageEntry<T>[] {
  // An empty list still gets one page, matching Hugo: a term with no entries
  // would not exist at all, but a section index can legitimately be empty.
  const lastPage = Math.max(1, Math.ceil(items.length / pageSize));
  const slice = (n: number) => items.slice((n - 1) * pageSize, n * pageSize);

  const entries: HugoPageEntry<T>[] = [
    { param: undefined, props: { items: slice(1), current: 1, lastPage } },
    {
      param: "page/1",
      props: { items: [], current: 1, lastPage, redirectTo: baseUrl },
    },
  ];

  for (let n = 2; n <= lastPage; n++) {
    entries.push({
      param: `page/${n}`,
      props: { items: slice(n), current: n, lastPage },
    });
  }

  return entries;
}
