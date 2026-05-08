---
title: "Claude Code の Skills が会話ごとにずれる原因は auto-memory だった — 1行で直す方法"
date: 2026-04-21
lastmod: 2026-04-21
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4291440274"
categories: ["AI/LLM"]
tags: ["Claude Code", "claude", "auto-memory", "settings.json", "スキル"]
---

Claude Code の Skills を使い込むうちに「あれ、前と挙動が違う……」と感じたことはないだろうか。`~/.claude/settings.json` に 1 行追記するだけで解決できる。原因は **auto-memory** だ。

## Claude Code の auto-memory が Skills の挙動を変える仕組み

Claude Code は会話のたびに学習内容を **Memory**（`~/.claude/projects/.../memory/MEMORY.md`）へ自動で書き込む機能（auto-memory）を持っている。
問題はこの Memory の内容が**次の会話でコンテキストウィンドウに自動挿入される**点だ。これにより、Skills に記述した指示と競合し、設計どおりの挙動から少しずつずれていく。

会話を重ねるほど症状が顕著になるため、原因の特定に時間がかかりやすい。

## 解決策：`autoMemoryEnabled: false`

`~/.claude/settings.json` に 1 行追記するだけで解決する。ファイルが存在しない場合は新規作成し、既存の設定がある場合は `{}` 内に追記する。

```json
{
  "autoMemoryEnabled": false
}
```

これで Memory への自動書き込み・読み込みが停止し、auto-memory 機能全体が無効化される。

## 影響範囲

| 機能 | `autoMemoryEnabled: false` にしたときの変化 |
|------|------|
| Memory への自動書き込み・読み込み | **停止** |
| `CLAUDE.md` の読み込み | **変化なし（従来どおり動作）** |
| Skills に書いたルールの適用 | **変化なし（従来どおり動作）** |

`CLAUDE.md` や Skills の設定はそのまま有効なので、プロジェクト固有のルールが失われる心配はない。

## Claude Code Skills の再現性を確保したいときに有効

- Skills を精密に動かしたい
- Skills の挙動が会話を重ねるにつれて変化している
- 再現性のある動作を担保したい

Skills ベースで Claude Code をカスタマイズしている場合、この設定を有効にすることを強く推奨する。
