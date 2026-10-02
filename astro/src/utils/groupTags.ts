import { collectTerms, type Taggable } from "./getTerms";
import { slugifyStr } from "./slugify";

export type TagEntry = {
  tag: string;
  tagName: string;
  count: number;
};

export type TagGroup = {
  id: string;
  label: string;
  tags: TagEntry[];
};

const KANA_ROWS: [string, string][] = [
  ["ア", "アイウエオ"],
  ["カ", "カキクケコ"],
  ["サ", "サシスセソ"],
  ["タ", "タチツテト"],
  ["ナ", "ナニヌネノ"],
  ["ハ", "ハヒフヘホ"],
  ["マ", "マミムメモ"],
  ["ヤ", "ヤユヨ"],
  ["ラ", "ラリルレロ"],
  ["ワ", "ワヲン"],
];

const SMALL_KANA: Record<string, string> = {
  ァ: "ア",
  ィ: "イ",
  ゥ: "ウ",
  ェ: "エ",
  ォ: "オ",
  ッ: "ツ",
  ャ: "ヤ",
  ュ: "ユ",
  ョ: "ヨ",
  ヮ: "ワ",
  ヵ: "カ",
  ヶ: "ケ",
};

const KANJI = "漢字";
const OTHER = "その他";

/**
 * Index heading for a tag: A–Z, a kana row (ア行…ワ行), 漢字, or その他.
 *
 * Kanji are not split further — ordering them by reading needs a dictionary.
 */
function headingOf(tagName: string): string {
  // NFD drops dakuten/handakuten (ガ → カ, パ → ハ, ヴ → ウ)
  const first = [...tagName.normalize("NFD")][0] ?? "";
  if (/^[a-z]$/i.test(first)) return first.toUpperCase();

  let kana = first;
  if (/^[ぁ-ゖ]$/.test(kana)) {
    // hiragana → katakana
    kana = String.fromCharCode(kana.charCodeAt(0) + 0x60);
  }
  kana = SMALL_KANA[kana] ?? kana;
  const row = KANA_ROWS.find(([, chars]) => chars.includes(kana));
  if (row) return `${row[0]}行`;

  if (/^\p{Script=Han}$/u.test(first)) return KANJI;
  return OTHER;
}

/**
 * Tags grouped under index headings, each with its entry count.
 * Groups come out as A–Z, ア行…ワ行, 漢字, その他; empty ones are omitted.
 *
 * Pass the same entries the tag routes use (visible posts + wiki), so every
 * tag page is listed and each count matches what that page shows.
 */
export function groupTags(entries: Taggable[]): TagGroup[] {
  const counts = new Map<string, number>();
  for (const entry of entries) {
    const tags = (entry.data as { tags?: string[] }).tags ?? [];
    // an entry listing two spellings of one tag counts once
    for (const tag of new Set(tags.map(slugifyStr))) {
      counts.set(tag, (counts.get(tag) ?? 0) + 1);
    }
  }

  const order = [
    ..."ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    ...KANA_ROWS.map(([head]) => `${head}行`),
    KANJI,
    OTHER,
  ];
  const byHeading = new Map<string, TagEntry[]>(order.map(h => [h, []]));
  for (const { term, name } of collectTerms(entries, "tags")) {
    byHeading
      .get(headingOf(name))!
      .push({ tag: term, tagName: name, count: counts.get(term) ?? 0 });
  }

  const collator = new Intl.Collator("ja", { sensitivity: "base" });
  return order
    .map((label, i) => ({
      id: `tag-group-${i}`,
      label,
      tags: byHeading
        .get(label)!
        .sort((a, b) => collator.compare(a.tagName, b.tagName)),
    }))
    .filter(group => group.tags.length > 0);
}
