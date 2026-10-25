# AI を戦力にする職場づくり（経営者向けセミナー）

事務作業に AI を使って効率と正確さを上げたい経営者向けに、「ハーネス」の考え方を技術用語なしで説明するスライド（全 18 枚）の元データと、PPTX を生成するスクリプト。

元になったブログ記事：[ハーネスエンジニアリング入門 — 馬具・柵・境界の3層で AI エージェントを自走させる](https://hdknr.github.io/blogs/posts/2026/10/harness-design-intro-guardrails-boundary/)

## ファイル

| ファイル | 役割 |
|---|---|
| `slides.json` | 元データ。全スライドの文言とスピーカーノート |
| `build.mjs` | `slides.json` を読んで PPTX を組み立てる（pptxgenjs） |
| `dist/` | 生成物の出力先（コミットしない） |

## 生成

```bash
npm install
npm run build
```

`dist/ai-harness-for-executives.pptx` ができる。

## 文言を直すとき

`slides.json` だけを直して、もう一度 `npm run build` する。`build.mjs` は配置だけを受け持つので、文言は書かない。

各スライドは `layout` で見た目の型を選ぶ。

| layout | 使っているスライド | 主な項目 |
|---|---|---|
| `cover` | 表紙・質疑応答 | `eyebrow` `title`（行の配列） `subtitle` `meta` |
| `statement` | 結論 | `eyebrow` `title`（行ごとの run 配列。`accent` で強調色） `body` |
| `cards` | 新人・失敗パターン・4 点セット・維持管理・まとめ | `columns` `cards[]`（`number` `heading` `sub` `text` `tone`） `intro` `footer` |
| `rows` | 導入の順番 | `items[]`（`number` `heading` `text`） `footer` |
| `equation` | ハーネスとは | `terms[]` `operators[]` `body` `footer` |
| `lists` | 業務マニュアル | `lists[]`（`heading` `tone` `items`） `footer` `note` |
| `table` | チェック・Git・経営判断 | `table`（`headers` `widths`（%） `rows`） `intro` `note` `tips` `footer` |
| `boundary` | 触れてよい範囲 | `body` `callouts[]` `zones[]` `note` |
| `flow` | 合格基準 | `steps[]` `loop` `example` |
| `stairs` | 守りの強さ | `bars[]`（3 本） `footer` |
| `measure` | 効果の測り方 | `callout` `tableHeading` `table` |

`[会社名]` `[登壇者名]` `[開催日]` `[連絡先]` と、効果測定の表の `[__分]` などはプレースホルダー。使う前に埋める。

## 注意

- フォントは BIZ UDPゴシック（Windows 10 1809 以降に標準搭載）。入っていない環境では、PowerPoint が別の日本語ゴシック体で表示する。
- `npm audit` が pptxgenjs の依存する `image-size` の脆弱性（細工された JXL・HEIF・ICNS 画像の解析で無限ループ）を報告する。pptxgenjs の最新版（4.0.1）も同じ範囲に依存しているため解消できない。このデッキは画像を読み込まないので、影響はない。
