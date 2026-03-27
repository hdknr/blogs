---
title: "HuggingFace hf-mount: AIモデルをダウンロードせずに仮想ファイルシステムとしてマウント"
date: 2026-03-25
lastmod: 2026-03-25
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4129195588"
categories: ["AI/LLM"]
tags: ["llm", "huggingface", "fuse", "kubernetes", "agent"]
---

2026年3月、HuggingFace が新ツール **hf-mount** を[発表](https://x.com/ClementDelangue/status/2036452081750409383)しました。HuggingFace Hub にホスティングされている巨大な AI モデルやデータセットを、ダウンロードせずに仮想ファイルシステムとして直接マウントできるツールです。

## hf-mount とは

hf-mount は、HuggingFace の Storage Bucket、モデルリポジトリ、データセットをローカルファイルシステムとしてマウントするツールです。バックエンドには FUSE（Filesystem in Userspace: ユーザー空間でファイルシステムを実装する仕組み）または NFS を使用します。ファイルは最初の読み取り時に遅延フェッチ（lazy fetch）され、実際にアクセスしたバイトだけがネットワークを通ります。

HuggingFace CEO の Clement Delangue 氏は「ローカルマシンのディスクの 100 倍大きなリモートストレージをアタッチできる」と[述べています](https://x.com/ClementDelangue/status/2036452081750409383)。

## 主な特徴

- **ダウンロード不要**: モデルやデータセットを事前にダウンロードする必要がない
- **遅延フェッチ**: 実際にアクセスしたファイルだけがネットワーク経由で取得される
- **2つのバックエンド**: NFS（推奨）と FUSE から選択可能
- **読み書き対応**: Storage Bucket は読み書き両対応、モデル・データセットは読み取り専用
- **Kubernetes 対応**: CSI ドライバー（[hf-csi-driver](https://github.com/huggingface/hf-csi-driver)）で Pod 内に FUSE ボリュームとしてマウント可能

## インストール

Linux（x86_64, aarch64）と macOS（Apple Silicon）に対応しています。

```bash
curl -fsSL https://raw.githubusercontent.com/huggingface/hf-mount/main/install.sh | sh
```

デフォルトでは `~/.local/bin/` にインストールされます。`INSTALL_DIR` 環境変数で変更可能です。

## 使い方

公開モデルをマウントする例:

```bash
hf-mount start repo openai-community/gpt2 /tmp/gpt2
```

プライベートモデル:

```bash
hf-mount start --hf-token $HF_TOKEN repo myorg/my-private-model /tmp/model
```

データセット:

```bash
hf-mount start repo datasets/open-index/hacker-news /tmp/hn
```

サブフォルダのみ:

```bash
hf-mount start repo openai-community/gpt2/onnx /tmp/onnx
```

## ストレージ階層の拡張

この技術は、従来の「キャッシュ → メモリ → ディスク」というストレージ階層にさらに一階層（リモートストレージ）を追加するものです。ローカルにないデータを透過的にリモートから取得する仕組みは、大規模モデルの運用を大きく変える可能性があります。

特に以下のシナリオで効果的です:

- **開発環境**: 数十 GB のモデルをダウンロードせず、すぐに実験を開始できる
- **CI/CD パイプライン**: モデルのダウンロード時間を削減し、ビルド時間を短縮
- **エージェント型ストレージ**: Clement Delangue 氏が「Agentic storage に最適」と述べているように、AI エージェントが必要なモデルやデータに動的にアクセスするユースケース

## まとめ

hf-mount は、オープンな AI エコシステムの強みを活かしたツールです。モデルの巨大化が進む中、「まずダウンロード」という従来のワークフローを根本から変え、必要な部分だけをオンデマンドで取得するアプローチは、開発体験とインフラコストの両面で大きなインパクトをもたらすでしょう。

## 参考リンク

- [huggingface/hf-mount（GitHub）](https://github.com/huggingface/hf-mount)
- [Introducing hf-mount（HuggingFace Changelog）](https://huggingface.co/changelog/hf-mount)
- [huggingface/hf-csi-driver（GitHub）](https://github.com/huggingface/hf-csi-driver)
