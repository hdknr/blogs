import { getRelativeLocaleUrl } from "astro:i18n";
import config from "@/config";

/**
 * Wiki URLs mirror the file tree: content/wiki/concepts/abliteration.md is
 * published at /wiki/concepts/abliteration/. The glob loader's entry id is
 * already `concepts/abliteration`, so no slugifying is involved -- the
 * filenames are ASCII slugs to begin with.
 *
 * The Japanese-looking wiki URLs (/wiki/concepts/1万通りシナリオ/ and friends)
 * are NOT pages: they are alias redirects declared in frontmatter, 514 of them
 * across 147 files.
 */
export function getWikiUrl(
  id: string,
  locale: string | undefined = config.site.lang
): string {
  return getRelativeLocaleUrl(locale, `wiki/${id}/`);
}

/** `concepts` | `guides` | `tools` — the section a wiki page belongs to. */
export function getWikiSection(id: string): string {
  return id.split("/")[0] ?? "";
}
