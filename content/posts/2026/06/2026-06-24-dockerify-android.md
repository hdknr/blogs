---
title: "DockerでAndroidエミュレーターを動かす ─ Dockerify Android 入門"
date: 2026-06-24
lastmod: 2026-06-24
slug: "dockerify-android"
draft: false
description: "DockerコンテナでAndroidエミュレーターを動かすOSS「Dockerify Android」のセットアップから、ADB接続・CI/CD活用・ARM変換まで解説。KVM対応Linuxがあれば docker compose up -d の1コマンドで環境が整う。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4785298022"
categories: ["クラウド/インフラ"]
tags: ["Docker", "Android", "エミュレーター", "CI/CD", "scrcpy", "KVM", "AVD", "docker-compose"]
---

Androidエミュレーターの起動には、Android Studio をインストールし AVD Manager で仮想デバイスを作成する手順が一般的です。しかしこの作業は重く、環境の再現性も低くなりがちです。**Dockerify Android** はこの問題を解決する OSS ツールで、Dockerコンテナの中で完全なAndroidエミュレーターを動かせます。この記事ではセットアップ手順から CI/CD への活用まで順を追って解説します。

## Dockerify Android とは

[Dockerify Android](https://github.com/Shmayro/dockerify-android)（`Shmayro/dockerify-android`）は、DockerコンテナでAndroid仮想デバイス（AVD）を動かすためのプロジェクトです。MITライセンスで公開されており、CI/CDパイプラインへの組み込みや、ローカルの開発・テスト環境を素早く立ち上げる用途に向いています。

主な特徴は以下のとおりです。

- **Webブラウザから操作**: 統合された [scrcpy-web](https://github.com/Shmayro/ws-scrcpy-docker)（ブラウザ版）でポート 8000 からエミュレーターを操作可能。デスクトップ版の `scrcpy` でのミラーリングにも対応
- **KVMハードウェアアクセラレーション**: ネイティブに近いパフォーマンスでエミュレーターを動作
- **ARM/ARM64変換**: `ndk_translation` による ARM アプリの x86_64 環境での実行
- **ADB・scrcpy対応**: ホストから `adb connect` や `scrcpy` で接続可能
- **PICO GAPPSとMagisk**: Google サービスおよびroot化を環境変数で有効化
- **ログの一元管理**: エミュレーター・起動ログをすべてDockerの標準ログへ出力

## 前提条件

- Docker および Docker Compose がインストール済みであること
- KVM（Kernel-based Virtual Machine）のサポート

KVMが利用可能かどうかは次のコマンドで確認できます。

```bash
egrep -c '(vmx|svm)' /proc/cpuinfo
```

0以外の数値が表示されればKVM対応です。

## セットアップ手順

リポジトリをクローンして、Docker Composeで起動するだけです。

```bash
git clone https://github.com/shmayro/dockerify-android.git
cd dockerify-android
docker compose up -d
```

初回起動時はAndroid 11（API 30）のAVD作成や各種設定が走るため、完了まで10〜15分程度かかります。進捗はログで確認できます。

```bash
docker compose logs -f
```

次のログが出力されたら準備完了です。

```
Broadcast completed: result=0
Success !!
```

その後、ブラウザで `http://localhost:8000` を開くと、ブラウザ版の scrcpy-web インターフェースからエミュレーターを操作できます。

## ADBおよびscrcpyでの接続

ホスト側から直接ADBを使って接続することもできます。

```bash
adb connect localhost:5555
adb devices
```

```
connected to localhost:5555
List of devices attached
localhost:5555  device
```

デスクトップアプリの scrcpy を使って画面をミラーリングする場合は次のようにします。

```bash
scrcpy -s localhost:5555
```

## 環境変数によるカスタマイズ

`docker-compose.yml` の環境変数でエミュレーターの動作を調整できます。

| 変数 | 説明 | デフォルト |
| --- | --- | --- |
| `DNS` | エミュレーター内のDNSサーバー | `one.one.one.one` |
| `RAM_SIZE` | 割り当てRAM（MB） | `4096` |
| `SCREEN_RESOLUTION` | 解像度（例: `1080x1920`） | デバイス既定 |
| `SCREEN_DENSITY` | 画面密度（DPI） | デバイス既定 |
| `ROOT_SETUP` | `1` でroot化とMagiskを有効化 | `0` |
| `GAPPS_SETUP` | `1` でPICO GAPPSをインストール | `0` |
| `ARM_TRANSLATION` | `1` でARMアプリをx86_64で動作させる | `0` |

`ROOT_SETUP`・`GAPPS_SETUP`・`ARM_TRANSLATION` は初回起動後にONにすることも可能です。

> **注意:** 一度有効化するとデータボリュームを再作成しない限り元に戻せません。

## ARM/ARM64アプリを動かす

ARMネイティブライブラリしか同梱していないアプリ（多くのリリースビルドがこれに該当）は、x86_64のエミュレーター上では通常インストールできません。`ARM_TRANSLATION=1` を設定すると `ndk_translation` が導入され、次のABIリストが有効になります。

```bash
adb shell getprop ro.product.cpu.abilist
# → x86_64,x86,arm64-v8a,armeabi-v7a,armeabi
```

## CI/CDへの活用

Dockerify Android はヘッドレスモードでも動作します。そのため、GitHub Actions などの CI 環境と組み合わせた自動テストに適しています。コンテナを起動し、ADBで接続した後にテストスクリプトを実行するだけで、クリーンなAndroid環境を毎回用意できます。ローカルにAndroid Studioをインストールする必要がなく、エミュレーターの設定手順を `docker-compose.yml` に集約できるため、チーム全体で一貫した環境を共有しやすくなります。

## まとめ

Dockerify AndroidはDockerの再現性とAndroidエミュレーターの利便性を組み合わせたツールです。`docker compose up -d` の1コマンドでブラウザからAndroidを操作できる環境が整い、ADB・scrcpy・CI/CDとの連携もスムーズです。Androidアプリのテスト自動化や開発環境の統一を検討している方は、ぜひ試してみてください。

- リポジトリ: [Shmayro/dockerify-android](https://github.com/Shmayro/dockerify-android)
