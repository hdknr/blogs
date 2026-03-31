---
title: "Claude Code の sensitive file チェックを回避する — git worktree の配置場所を .claude/ の外に移す"
date: 2026-03-31
lastmod: 2026-03-31
draft: false
categories: ["AI/LLM"]
tags: ["Claude Code", "git worktree", "自動化", "パーミッション"]
---

Claude Code の auto モードでブログ記事作成を完全自動化しようとしたところ、`.claude/` ディレクトリ配下のファイルへの書き込みで毎回同意を求められる問題に遭遇しました。原因と対処法を記録します。

## 問題：`.claude/` 配下は sensitive file 扱い

Claude Code には、`.claude/` ディレクトリ内のファイルを「sensitive file」（設定やスキル定義など、ツールの動作に影響する重要ファイル）として扱う組み込みのセキュリティチェックがあります。`settings.local.json` の `permissions.allow` に Write/Edit の許可パターンを追加しても回避できません。sensitive file チェックは permissions とは別レイヤーで動作するためです。

実際に発生したメッセージ:

```
Claude requested permissions to edit .claude/temp/pr_body.md
which is a sensitive file.
```

## 背景：ブログ記事作成の自動化ワークフロー

このブログでは `/blog` スキルで記事作成から PR 作成まで自動化しています。ワークフローの概要:

1. git worktree を作成してブランチを切る
2. worktree 内に記事ファイルを作成
3. Hugo ビルド確認
4. コミット・プッシュ
5. **PR 本文ファイルを書き出し**、`gh pr create --body-file` で PR 作成
6. ソース元に PR リンクを追記

問題が起きたのはステップ 5 です。PR 本文ファイル（`pr_body.md`）を `.claude/temp/` に Write ツールで書き込もうとすると、sensitive file チェックに引っかかります。

## 以前の回避策：`cat >` で書き込む

一時的な回避策として、Write ツールではなく Bash の `cat >` コマンドでファイルを書き込んでいました。

```bash
cat > .claude/temp/pr_body.md <<'EOF'
## Summary
- ...
EOF
```

`settings.local.json` には以下の許可パターンを登録:

```json
"Bash(cat > .claude/temp/:*)"
```

これで同意プロンプトは回避できますが、Write ツールを使えないのは不自然です。worktree 自体も `.claude/` 配下にあるため、記事ファイルの作成でも同じ sensitive file チェックに引っかかる可能性がありました。

## 根本原因：worktree が `.claude/` の中にある

それまでの構成では、git worktree を `.claude/temp/worktree-<slug>/` に作成していました。

```
.claude/
  temp/
    worktree-<slug>/     ← ここが worktree
      content/posts/...  ← 記事ファイル
    pr_body.md           ← PR 本文
```

`.claude/` 配下にあるため、worktree 内のすべてのファイルが sensitive file チェックの対象になります。

## 解決策：worktree をリポジトリルートの `.worktrees/` に移動

worktree の作成先を `.claude/` の外に移すことで、sensitive file チェックを根本的に回避しました。

```
.worktrees/              ← .claude/ の外
  <slug>/                ← worktree
    content/posts/...    ← 記事ファイル
    pr_body.md           ← PR 本文（worktree 内に直接置く）
```

### 変更箇所

**1. `.gitignore` に `.worktrees/` を追加**

```
.worktrees/
```

**2. worktree の作成先を変更**

```bash
# 旧
git worktree add -b "$BRANCH_NAME" ".claude/temp/worktree-<slug>" main

# 新
git worktree add -b "$BRANCH_NAME" ".worktrees/<slug>" main
```

**3. PR 本文ファイルの書き出し先を変更**

```bash
# 旧: .claude/temp/ に cat > で書き込み
cat > .claude/temp/pr_body.md <<'EOF'
...
EOF

# 新: worktree 内に Write ツールで直接書き込み
# Claude Code の Write ツールで $WORKTREE_DIR/pr_body.md に書き出す
# .claude/ の外なので sensitive file チェックに引っかからない
```

**4. `settings.local.json` に許可パターンを追加**

先頭の `//` は Claude Code のパターン記法で、絶対パスを表します。

```json
"Write(//Users/hdknr/Projects/hdknr/blogs/.worktrees/**)",
"Edit(//Users/hdknr/Projects/hdknr/blogs/.worktrees/**)"
```

## auto モードで完全自動化するための教訓

Claude Code の auto モードで同意プロンプトなしに動作させるには、以下の 2 つのレイヤーをクリアする必要があります。

| レイヤー | 対処法 |
|---|---|
| **permissions.allow パターン** | `settings.local.json` にパターンを登録 |
| **sensitive file チェック** | `.claude/` ディレクトリの外にファイルを配置 |

`permissions.allow` だけでは不十分な場合があることを覚えておくと、ワークフロー設計時のハマりどころを減らせます。

## まとめ

- `.claude/` 配下は Claude Code の組み込みセキュリティにより sensitive file 扱いされる
- `permissions.allow` の許可パターンとは別レイヤーのチェックなので、パターン追加では回避できない
- git worktree や一時ファイルの配置場所を `.claude/` の外に移すのが根本的な解決策
- `.worktrees/` をリポジトリルートに置き、`.gitignore` に追加するだけで対応完了
