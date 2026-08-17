import type { UIStrings } from "../types";

/**
 * Japanese UI strings. The site is `lang: "ja"`, and without this file every
 * label falls back to English via useTranslations().
 */
export default {
  nav: {
    home: "ホーム",
    posts: "記事",
    tags: "タグ",
    about: "このサイトについて",
    archives: "アーカイブ",
    search: "検索",
  },
  post: {
    publishedAt: "公開日",
    updatedAt: "更新日",
    sharePostIntro: "この記事を共有:",
    sharePostOn: "{{platform}} で共有",
    sharePostViaEmail: "メールで共有",
    tagLabel: "タグ",
    backToTop: "先頭へ戻る",
    goBack: "戻る",
    editPage: "このページを編集",
    previousPost: "前の記事",
    nextPost: "次の記事",
  },
  pagination: {
    prev: "前へ",
    next: "次へ",
    page: "ページ",
  },
  home: {
    socialLinks: "リンク",
    featured: "注目の記事",
    recentPosts: "最近の記事",
    allPosts: "すべての記事",
  },
  footer: {
    copyright: "Copyright",
    allRightsReserved: "All rights reserved.",
  },
  pages: {
    tagTitle: "タグ",
    tagDesc: "このタグが付いた記事",

    tagsTitle: "タグ",
    tagsDesc: "記事で使われているタグの一覧",

    postsTitle: "記事一覧",
    postsDesc: "これまでに書いた記事",

    archivesTitle: "アーカイブ",
    archivesDesc: "年月別の記事一覧",

    searchTitle: "検索",
    searchDesc: "記事と Wiki を全文検索",
  },
  a11y: {
    skipToContent: "本文へスキップ",
    openMenu: "メニューを開く",
    closeMenu: "メニューを閉じる",
    toggleTheme: "テーマを切り替える",
    searchPlaceholder: "キーワードを入力…",
    noResults: "該当する記事はありません",
    goToPreviousPage: "前のページへ",
    goToNextPage: "次のページへ",
  },
  notFound: {
    title: "404 Not Found",
    message: "ページが見つかりません",
    goHome: "ホームへ戻る",
  },
} satisfies UIStrings;
