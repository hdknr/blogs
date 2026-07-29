---
title: "Dockerify Android"
description: "Docker コンテナの中で完全な Android エミュレーター(AVD)を動かす OSS。KVM 対応 Linux があれば docker compose up -d の1コマンドで起動し、CI/CD にも組み込める"
date: 2026-07-15
lastmod: 2026-07-15
aliases: ["Dockerify Android", "dockerify-android"]
related_posts:
  - "/posts/2026/06/dockerify-android/"
tags: ["Docker", "Android", "エミュレーター", "CI/CD", "KVM", "scrcpy"]
---

## 概要

Dockerify Android（`Shmayro/dockerify-android`）は、Docker コンテナで Android 仮想デバイス（AVD）を動かす MIT ライセンスの OSS。Android Studio + AVD Manager の重いセットアップを、`docker compose up -d` の1コマンドに置き換える。CI/CD への組み込みや、再現性のある開発・テスト環境の即時立ち上げに向く。

## 詳細

### 主な特徴

- **ブラウザから操作**: 統合 scrcpy-web（ポート 8000）でブラウザから操作。デスクトップ版 scrcpy のミラーリングにも対応
- **KVM ハードウェアアクセラレーション**: ネイティブに近いパフォーマンス
- **ARM/ARM64 変換**: `ndk_translation` で ARM アプリを x86_64 上で実行
- **ADB・scrcpy 対応**: `adb connect localhost:5555` でホストから接続
- **PICO GAPPS と Magisk**: Google サービス・root 化を環境変数で有効化

### 前提: 実質 KVM 対応 Linux 専用

KVM は Linux カーネルの機能で、`/dev/kvm` がコンテナから見えることが前提。macOS（Docker Desktop/OrbStack）や Windows はネストされた仮想化が必要だが、macOS のハイパーバイザはこれをゲストに公開しないため起動失敗か実用外の低速になる。CI では KVM 対応の Linux ランナーを使う。確認は `egrep -c '(vmx|svm)' /proc/cpuinfo`。

### 環境変数によるカスタマイズ

`docker-compose.yml` で `RAM_SIZE`・`SCREEN_RESOLUTION`・`ROOT_SETUP`・`GAPPS_SETUP`・`ARM_TRANSLATION` などを設定できる（一度有効化するとデータボリューム再作成まで戻せないものがある）。

### CI/CD への活用

ヘッドレスモードで動くため GitHub Actions などと組み合わせた自動テストに適する。エミュレーター設定を `docker-compose.yml` に集約でき、ローカルに Android Studio を入れずチーム全体で一貫した環境を共有できる。

## 関連ページ

- [Docker で Android エミュレーターを動かす（本ツールの入門記事）](/blogs/posts/2026/06/dockerify-android/)

## ソース記事

- [Docker で Android エミュレーターを動かす ─ Dockerify Android 入門](/blogs/posts/2026/06/dockerify-android/) — 2026-06-24
