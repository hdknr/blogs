---
title: "Capacitor"
description: "Ionic チームの OSS ランタイム。Web アプリを WebView ごと iOS・Android のネイティブアプリに包み、端末機能はプラグイン経由で呼ぶ。ネイティブプロジェクトを Git 管理のソースとして扱うのが Cordova との違い"
date: 2026-11-09
lastmod: 2026-11-09
aliases: ["capacitor", "Ionic Capacitor", "Capacitor 8", "Live Updates", "OTA 更新"]
related_posts:
  - "/posts/2026/11/capacitor-cross-platform/"
tags: ["Capacitor", "モバイルアプリ開発", "ios", "Android", "Flutter"]
---

## 概要

Capacitor は、HTML・CSS・JavaScript / TypeScript で書いた Web アプリを、iOS・Android のネイティブアプリとして動かすオープンソースのランタイム。開発元は Ionic チームで、Apache Cordova の課題を踏まえて別プロジェクトとして作られた（Cordova からの移行ガイドあり）。同じコードを Web（PWA）としても配信できる。

アプリの実体は**ネイティブアプリに埋め込まれた WebView**。Web で作った画面がほぼそのまま動くのが最大の利点で、同時に描画性能面の制約の出どころでもある。

## 詳細

### 仕組みと特徴

- **ブリッジ**: カメラ・位置情報・プッシュ通知などの端末機能は、JavaScript からブリッジ経由でネイティブ側のプラグインを呼ぶ。公式プラグインは TypeScript の型付き API（例: `@capacitor/geolocation`）
- **フレームワークを選ばない**: React・Vue・Svelte・Angular・素の JS など、ビルドで静的な Web アセットが出れば何でもよい
- **ネイティブプロジェクトはソースコード**: Cordova ではビルドのたびに生成し直す成果物だったが、Capacitor では `npx cap add` で作った `ios/`・`android/` を Git 管理し、Xcode や Android Studio で署名・`Info.plist`・`AndroidManifest.xml`・ネイティブコードを直接編集する
- **自作プラグイン**: JS 側の定義（`registerPlugin<EchoPlugin>('Echo')`）、ネイティブ側の本体（iOS は `CAPPlugin`、Android は `@CapacitorPlugin`。結果は `call.resolve()`）、アプリ本体での登録の 3 か所がそろって初めて JS から呼べる

### React Native・Flutter との違い

違いは「画面を誰が描画するか」に集約される。

| ツール | 描画 | 強み | 注意点 |
|---|---|---|---|
| Capacitor | WebView 上で Web として描画 | Web 資産とスキルをほぼそのまま活かせる。導入の手間が最小 | 複雑な 3D、高頻度の再描画、重いアニメーションに不向き |
| React Native | JS からネイティブ UI コンポーネントを操作 | 見た目と操作感がネイティブに近い | React 前提。DOM・CSS のコードはそのまま再利用できない |
| Flutter | 独自エンジン（iOS・Android は Impeller）で直接描画 | OS をまたいで UI が一貫、性能も高い | Dart の習得が必要 |

既存の Web アプリ（SaaS・EC・社内ツール）を素早くストアに出したい、Web フロントエンドのチームだけで保守したい、画面がフォーム・一覧・CRUD 中心、という場合に向く。

### 開発の流れ

1. `npm install @capacitor/core @capacitor/cli` → `npx cap init`（アプリ名と逆ドメイン形式のアプリ ID。`webDir` を Web ビルドの出力先に合わせる）
2. `npx cap add android` / `npx cap add ios`（生成物はコミットする）
3. `npm run build` → `npx cap sync` で Web アセットとプラグインを反映
4. `npx cap open ios|android` で IDE を開く、または `npx cap run` で直接起動

日常は「**ブラウザで 8 割、シミュレーターで 2 割**」。Vite の開発サーバーで UI を作り込み、ネイティブ API が絡む部分だけシミュレーターで確かめる。`npx cap run ios --live-reload --port 5173` なら実機でもホットリロードでき、書き換えた設定は終了時に戻るのでストア版に紛れ込まない。WebView の中は iOS なら Mac の Safari の Web インスペクタ、Android なら `chrome://inspect` で調べる。

### Capacitor 8（2025 年 12 月公開）の主な変更

- iOS の新規プロジェクトは CocoaPods ではなく Swift Package Manager が既定（`--packagemanager CocoaPods` で従来構成）
- Android の edge-to-edge 対応としてコアプラグイン System Bars を追加し、余白は CSS 変数で扱う
- 要件は Node.js 22 以上、Xcode 26.0 以上、iOS 15.0、Android `minSdkVersion` 24・`targetSdkVersion` 36

### ストア公開までに用意するもの

- **ディープリンク**: `@capacitor/app` の `appUrlOpen` で URL を受けてルーティング。iOS は `apple-app-site-association` と Associated Domains、Android は `assetlinks.json` と intent filter
- **プッシュ通知**: `@capacitor/push-notifications`。Android は FCM、iOS は APNs のトークンが返る（FCM に一本化するなら iOS にも Firebase SDK を入れる）。実行時の許可も要る
- **アイコンとスプラッシュ**: `@capacitor/assets` で元画像 1 枚ずつから全サイズを生成
- **環境の切り替え**: バンドル ID と表示名は Xcode のターゲット・Gradle の flavor で決まる。`capacitor.config.ts` からは `ios.scheme` / `android.flavor` を切り替える
- **プライバシーの申告**: App Store は Privacy Manifest（Required Reason API の理由）、Google Play はデータセーフティのフォーム。プラグインも対象

### 実運用での注意点

- **「Web サイトを包んだだけ」は審査で落ちうる**: App Review Guidelines 4.2 は再パッケージした Web サイトを超える機能を求める。プッシュ通知・オフライン動作・端末連携などアプリにする理由を持たせる
- **オリジンが変わる**: WebView のオリジンは iOS が `capacitor://localhost`、Android が `https://localhost`。サーバーの CORS で許可するか、`CapacitorHttp` でネイティブ通信に置き換える
- **保存先**: `localStorage` は OS に消されうる。`@capacitor/preferences` は暗号化されないので、トークンや鍵は Keychain / Keystore 系のプラグインかメモリーに置く。独自 URL スキームでトークンを受け渡さない。OAuth は PKCE 必須
- **バックグラウンドでは JS が止まる**: iOS では `setInterval` が当てにならない。経過時間は開始時刻からの差分で計算する

### CI（GitHub Actions）

Web（`ubuntu-latest`）、Android（`ubuntu-latest` + JDK 21、Gradle）、iOS（`macos-latest`、`xcodebuild`）の 3 ジョブに分ける。iOS はシミュレーター向けに `CODE_SIGNING_ALLOWED=NO` でビルドすれば証明書不要。SPM 構成は `-project ios/App/App.xcodeproj`、CocoaPods 構成は `-workspace`。iOS テンプレートにはテストターゲットが入っていないので、ネイティブをテストするなら Unit Testing Bundle を追加する。

### Live Updates（OTA 更新）

Web 層（HTML・CSS・JS）だけをサーバーから配信して差し替え、審査を通さずに修正を届けられる。ネイティブ側（Swift / Kotlin、プラグインの追加・更新、権限の変更）はストアのリリースが必要で、**Web バンドルとインストール済みネイティブ部分の組み合わせ**が設計の要。Apple・Google とも WebView で動く JavaScript は条件付きで認めているが、実務上はバグ修正や小さな改善にとどめ、別のアプリに変えない。

手段は Capgo（OSS、セルフホスト可）、Capawesome Cloud、Codemagic Patch など。Ionic Appflow は 2027 年 12 月 31 日でサービス終了、Microsoft の CodePush も App Center 終了で使えない。導入前に互換性の振り分け、ロールバック、バンドル署名による改ざん対策を決めておく。

## 関連ページ

- [GitHub Actions のセキュリティ](/blogs/wiki/guides/github-actions-security/) — CI で署名鍵などのシークレットを扱う際の注意
- [JWT Bearer Grant](/blogs/wiki/concepts/jwt-bearer-grant/) — モバイルの認証・トークン発行に関わる仕組み
- [Git](/blogs/wiki/tools/git/) — `ios/`・`android/` をソースとして管理する前提

## ソース記事

- [Capacitor 入門：Web アプリをそのまま iOS・Android アプリにする仕組みと手順](/blogs/posts/2026/11/capacitor-cross-platform/) — 2026-11-09
