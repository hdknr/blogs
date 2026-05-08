---
title: "Claude Code を Level 5 まで育てたら、開発が「指示と確認だけ」になった"
date: 2026-04-21
lastmod: 2026-04-23
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4291430905"
categories: ["AI/LLM"]
tags: ["Claude Code", "CLAUDE.md", "Hooks", "Agents", "VibeCoding", "自動化"]
---

Qiita に投稿された「[Claude Code を Level 5 まで育てたら、開発が「指示と確認だけ」になった — 実ファイル構成で解説](https://qiita.com/teppei19980914/items/8da88b33ffa8cf88dfa2)」が大きな反響を呼んでいる。CLAUDE.md・Skills・Hooks・Agents を組み合わせて Claude Code を 5 段階で「育てる」ことで、人間の作業を「指示と確認だけ」に絞り込むアプローチを実ファイル構成とともに解説した記事だ。

## 「AI にコードを書かせている」と「AI と開発している」は違う

Claude Code を導入した当初は、毎回こんなプロンプトを書いていたという：

```text
UIテキストはハードコーディングしないでください。
src/i18n/ja.ts に追加してから使ってください。
テストも書いてください。
外部リンクには rel="noopener noreferrer" を付けてください。
コミット前に npx astro check と npm test を実行してください。
```

毎回同じことを書くのは「AI にコードを書かせている」状態であり、「AI と開発している」とは言えない。同氏は 1 か月の試行錯誤を経て、作業は「何を作るか指示する」と「動作確認する」だけになったという。

## Claude Code 5 つのレベルの全体像

| Level | 追加要素 | 何が自動化されるか | 人間がやること |
|-------|----------|-------------------|----------------|
| 1 | 素のプロンプト | なし | 全指示を毎回手打ち |
| 2 | + CLAUDE.md | プロジェクトルールの自動読み込み | ルール違反の指摘が不要に |
| 3 | + Skills | 手順書のオンデマンド注入 | 定型作業の手順説明が不要に |
| 4 | + Hooks | 品質チェックの自動実行 | 「テスト実行して」が不要に |
| 5 | + Agents | 並行レビューの自動実行 | レビュー依頼が不要に |

## Level 2: CLAUDE.md — 「プロジェクトの憲法」を持たせる

プロジェクトルートに `CLAUDE.md` を置くと、Claude Code が会話開始時に自動で読み込む。これは「プロジェクトの憲法」だ。

```text
プロジェクトルート/
├── CLAUDE.md          ← これを追加
├── src/
├── package.json
└── ...
```

筆者の CLAUDE.md（抜粋）：

```markdown
# HomePage - Claude Code 運用ガイド

## テキスト管理ルール（最重要）
- **UIテキストのハードコーディングは禁止**
- 多言語対応: ja / en の 2 言語を src/i18n/ja.ts / src/i18n/en.ts で管理

## コミットルール
- テストコードの追加・修正を伴わないソースコード変更はコミットしない

## コミット前チェック（毎回必須）
1. 横展開チェック — 同一パターンを検索し漏れなく対応
2. セキュリティチェック — XSS、外部リンク rel 属性、機密情報
3. デプロイチェック — npx astro check → npm test → npm run build
```

コツは「150 行以内に収め、優先度を明示し、具体的なパスやコマンドを書く」こと。詳細な手順は Level 3（Skills）に分離する。

## Level 3: Skills — 「手順書」をオンデマンドで注入する

CLAUDE.md にすべてを書こうとすると膨張する。Skills は `.claude/skills/` に置いた Markdown ファイルで、Claude Code が必要に応じて参照する「手順書」だ。

```text
.claude/
└── skills/
    ├── fix-issue.md       ← 問題修正の手順書
    ├── create-blog.md     ← ブログ記事作成の手順書
    ├── analyze-trend.md   ← トレンド分析の手順書
    ├── check-deploy.md    ← デプロイ確認の手順書
    ├── release.md         ← リリースの手順書
    └── update-labels.md   ← ラベル更新の手順書
```

「ブログ記事を作って」と指示するだけで、Claude はスキルを参照してトレンド分析 → SEO 最適化 → 記事作成を自動実行する。人間が手順を説明する必要がなくなる。

## Level 4: Hooks — 「品質チェック」を自動実行する

Hooks は「自動で実行される仕組み」で、`.claude/settings.json` に定義する。

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write $TOOL_INPUT_FILE"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "npx astro check && npm test"
          },
          {
            "type": "prompt",
            "prompt": "6つの観点で最終チェックを実施してください..."
          }
        ]
      }
    ]
  }
}
```

| トリガー | 自動実行される処理 |
|----------|-------------------|
| ファイル保存時（PostToolUse） | Prettier でコード整形 |
| 会話終了時（Stop） | 静的解析 + テスト実行 + 6 観点の品質チェック |

「テスト実行して」と毎回言う必要がなくなる。

> **注意:** Stop フックでファイル書き込みやコマンド実行を行うと無限ループが発生するリスクがある。副作用を持つコマンドは `PreToolUse` や `PostToolUse` で処理し、Stop フックでは軽量なチェックのみにとどめることが推奨される。

## Level 5: Agents — 「レビュー」を並行自動実行する

Agents は独立したレビュワーを並行して走らせる仕組みで、`.claude/agents/` に定義する。

```text
.claude/
└── agents/
    ├── label-checker.md        ← ハードコード文字列の検出
    ├── security-reviewer.md    ← セキュリティ観点のレビュー
    ├── performance-reviewer.md ← パフォーマンス観点のレビュー
    └── seo-reviewer.md         ← SEO 観点のレビュー
```

コードが書き上がった後、Claude がオーケストレーションする形で：

- `label-checker` が UI テキストのハードコードを検出
- `security-reviewer` が XSS やサニタイズ漏れをチェック
- `performance-reviewer` がループ内 DB 問い合わせを検出
- `seo-reviewer` がブログ記事の SEO を全件検査

これらをサブエージェントとして呼び出すことで、人間がレビューする前にほとんどの問題が検出される。

## 「AI を育てる」という考え方

Level 1 から Level 5 まで、一気に構築したわけではない。開発を進める中で「またこの指示を書いている」と気づいたら CLAUDE.md に追記し、「この手順を毎回説明している」と気づいたら Skills に分離し、「このチェックを忘れがち」と気づいたら Hooks で自動化する。

**繰り返しの苦痛が、次のレベルへの動機になる。** これが「AI を育てる」ということだ。

VibeCoding（バイブコーディング）に対して「品質が不安」という声もあるが、Level 4 の Hooks と Level 5 の Agents があれば品質チェックは人間が忘れても AI が自動で実行する。仕組みに組み込めば VibeCoding でも一定の品質を担保できる。

## まとめ：あなたの Claude Code は今、Level いくつ？

| あなたの状況 | 推奨レベル | 最初にやること |
|-------------|-----------|---------------|
| Claude Code を使い始めたばかり | Level 2 | CLAUDE.md にプロジェクトルールを書く |
| 毎回同じ手順を説明している | Level 3 | `.claude/skills/` に手順書を分離する |
| 「テスト実行して」と毎回言っている | Level 4 | `settings.json` に Hooks を追加する |
| レビューで毎回同じ指摘をしている | Level 5 | `.claude/agents/` にレビュワーを追加する |

Level 5 まで育てると、人間の役割は「何を作るか決める」と「動作確認する」だけになる。Claude Code は「使うツール」ではなく「育てるパートナー」だ。
