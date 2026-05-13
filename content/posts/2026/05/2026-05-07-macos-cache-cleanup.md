---
title: "macOS キャッシュ掃除チートシート — 開発マシンの数百 GB を取り戻す"
date: 2026-05-07
lastmod: 2026-05-07
slug: "macos-cache-cleanup"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4401947250"
description: "macOS 開発マシンに溜まる uv・npm・Docker・JetBrains・Ollama などのキャッシュを安全に削除するコマンド集。月 1 回の定期掃除スクリプト付き。"
categories: ["ツール/開発環境"]
tags: ["macOS", "docker", "homebrew", "ollama", "開発環境"]
---

開発マシンを放置していると、パッケージマネージャやコンテナ、IDE のキャッシュが気づかないうちに数百 GB に膨れ上がります。本記事では、主要なツールごとにキャッシュを安全に削除するコマンドをまとめます。

## パッケージマネージャ系

Python 環境の `uv` は特に溜まりやすく、100 GB を超えることもあります。

```bash
# uv (Python) — 100 GB+ 溜まることも
uv cache clean

# npm
npm cache clean --force

# pnpm
pnpm store prune

# Yarn
yarn cache clean

# pip
pip cache purge

# Poetry — `poetry cache list` でキャッシュ名を確認してから個別削除も可能
# 下記の "." は全キャッシュソースを対象にする引数（Poetry バージョンによっては要確認）
poetry cache clear --all .

# Homebrew — ダウンロード済みアーカイブ
brew cleanup --prune=all
```

## コンテナ・仮想化

Docker は数百 GB になりがちです。OrbStack / Docker Desktop どちらでも同じコマンドが使えます。

```bash
# Docker — イメージ・コンテナ・ボリュームをまとめて削除
docker system prune -a --volumes
# ※ 使用中のコンテナ・ボリュームは残る

# 未使用イメージだけ削除
docker image prune -a

# 未使用ボリュームだけ削除
docker volume prune
```

## IDE・エディタ

```bash
# JetBrains (IntelliJ, WebStorm, etc.)
rm -rf ~/Library/Caches/JetBrains

# VS Code — 拡張キャッシュ
rm -rf ~/Library/Caches/com.microsoft.VSCode
rm -rf ~/Library/Caches/vscode-cpptools

# Xcode — DerivedData（ビルド生成物）
rm -rf ~/Library/Developer/Xcode/DerivedData
# Xcode — 不要な iOS Simulator を削除
xcrun simctl delete unavailable
```

## ブラウザ

```bash
# Arc
rm -rf ~/Library/Caches/Arc

# Brave
rm -rf ~/Library/Caches/BraveSoftware

# Chrome
rm -rf ~/Library/Caches/Google/Chrome
```

## AI/ML モデル

ローカルで LLM を動かしている場合、モデルファイルが GB 単位になります。

```bash
# Hugging Face
rm -rf ~/.cache/huggingface

# Whisper (CLI 版)
rm -rf ~/.cache/whisper

# Ollama — 不要モデルを個別削除
ollama list
ollama rm <model>

# MacWhisper — アプリ内からモデル管理
# ~/Library/Containers/com.goodsnooze.MacWhisper/
```

## その他ツール

```bash
# Playwright ブラウザバイナリ
rm -rf ~/Library/Caches/ms-playwright

# Puppeteer
rm -rf ~/.cache/puppeteer

# Go モジュールキャッシュ
go clean -modcache

# Rust / Cargo（要: cargo install cargo-cache）
cargo cache --autoclean
# cargo-cache 未インストールの場合: rm -rf ~/.cargo/registry/cache

# NuGet (.NET)
dotnet nuget locals all --clear

# CocoaPods
pod cache clean --all

# Nix — ガベージコレクション
nix-collect-garbage -d

# Prisma エンジン
rm -rf ~/.cache/prisma
```

## 月 1 回の定期掃除スクリプト

以下をまとめて実行するだけで、定期メンテナンスが簡単になります。

```bash
brew cleanup --prune=all
uv cache clean
npm cache clean --force
pnpm store prune
docker system prune -a --volumes  # 注意: 起動中のコンテナがない状態で実行すること
rm -rf ~/Library/Developer/Xcode/DerivedData
```

`crontab` や macOS の `launchd` に登録しておくと、手動で忘れずに済みます。

---

開発が活発になるほどキャッシュは増え続けます。月 1 回の掃除を習慣にして、ディスクを常に快適な状態に保ちましょう。
