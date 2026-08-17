---
title: "検索"
# NOT `search`: that is a reserved layout name in PaperMod, and it makes
# partials/head.html inject the theme's own fuse.js bundle plus a
# `<link rel=preload as=fetch href=../index.json>`. With the JSON output
# removed both 404, and the page ships 17KB of dead search code alongside
# Pagefind. The URL stays /search/ because that comes from this file's path.
layout: "pagefind"
summary: "記事と Wiki を全文検索します"
placeholder: "キーワードを入力"
---
