import { defineAstroPaperConfig } from "./src/types/config";

export default defineAstroPaperConfig({
  site: {
    url: "https://hdknr.github.io/blogs/",
    title: "hdknr blog",
    description: "Gist ブログのまとめサイト",
    author: "hdknr",
    profile: "https://github.com/hdknr",
    ogImage: "default-og.jpg",
    lang: "ja",
    timezone: "Asia/Tokyo",
    dir: "ltr",
  },
  posts: {
    // Matches Hugo's `paginate = 10`. Changing it would renumber every
    // /posts/page/N/ and /tags/<tag>/page/N/ URL.
    perPage: 10,
    perIndex: 10,
    scheduledPostMargin: 15 * 60 * 1000,
  },
  features: {
    lightAndDarkMode: true,
    dynamicOgImage: true,
    showArchives: true,
    showBackButton: true,
    // Off, as it was under Hugo. AstroPaper's default points the per-post
    // "Edit page" link at the theme author's own repository.
    editPost: {
      enabled: false,
      url: "",
    },
    search: "pagefind",
  },
  socials: [{ name: "github", url: "https://github.com/hdknr" }],
  // Empty, matching `ShowShareButtons = false` in the old hugo.toml. The stock
  // list is WhatsApp/Facebook/X/Telegram/Pinterest placeholders.
  shareLinks: [],
});