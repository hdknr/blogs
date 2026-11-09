---
title: "Capacitor 入門：Web アプリをそのまま iOS・Android アプリにする仕組みと手順"
date: 2026-11-09
lastmod: 2026-11-09
slug: "capacitor-cross-platform"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/694#issuecomment-6732155735"
categories: ["モバイル"]
tags: ["Capacitor", "モバイルアプリ開発", "ios", "Android", "Flutter"]
---

手元に動いている Web アプリがあり、「これをそのまま App Store や Google Play に出したい」と考えたとき、最初の候補になるのが **Capacitor** です。

Capacitor は、Web アプリを iOS・Android のネイティブアプリとして動かすためのオープンソースのランタイムです。対象は HTML・CSS・JavaScript / TypeScript で書かれたアプリで、同じコードを Web（PWA）としても配信できます。開発元は Ionic チームです。Apache Cordova の課題を踏まえて Cordova とは別プロジェクトとして作られたもので、公式に Cordova からの移行ガイドも用意されています。

この記事では、Capacitor の仕組みと特徴、React Native・Flutter との違い、基本的な開発の流れを整理します。

## Capacitor の仕組み

Capacitor アプリの実体は、**ネイティブアプリの中に埋め込まれた WebView** です。ビルドした Web アプリ（HTML・JS・CSS）は、WebView に読み込んで表示します。カメラや位置情報などの端末機能は、JavaScript からネイティブ側を呼び出す「ブリッジ」を経由して使います。

UI はあくまで Web として描画されるので、Web で作った画面がほぼそのまま動きます。これが Capacitor の最大の利点であり、同時に後述する性能面の制約の出どころでもあります。

## 主な特徴

### フロントエンドフレームワークを選ばない

React、Vue、Svelte、Angular、フレームワークなしの素の JavaScript など、普段使っているフロントエンドの技術をそのまま UI とロジックに使えます。Capacitor が求めるのは「ビルドすると静的な Web アセットが出力されること」だけです。

### ネイティブプロジェクトをソースコードとして管理する

Cordova との大きな違いがここです。Cordova では、ネイティブプロジェクトはビルドのたびに生成し直す成果物という扱いでした。そのため、生成されたプロジェクトを手で編集しても、次の生成で上書きされがちです。

一方 Capacitor では、`npx cap add` で生成した `ios/` や `android/` ディレクトリを **Git で管理するソースコードの一部** として扱います。

そのため、Xcode や Android Studio でプロジェクトを直接開き、署名の設定や `Info.plist`・`AndroidManifest.xml` の編集、ネイティブコードの追加を、通常のネイティブアプリと同じ手順で行えます。

### TypeScript から使えるプラグイン

カメラ、位置情報、プッシュ通知、触覚フィードバック（Haptics）などの端末機能は、公式プラグインとして提供されています。いずれも TypeScript の型定義付きの JavaScript API で呼び出せます。

```typescript
import { Geolocation } from '@capacitor/geolocation';

const position = await Geolocation.getCurrentPosition();
console.log(position.coords.latitude, position.coords.longitude);
```

### ネイティブ側の拡張がしやすい

公式プラグインにない機能は、Swift（iOS）や Kotlin / Java（Android）でカスタムプラグインを書いて追加できます。OS の新機能やサードパーティ製のネイティブ SDK を使いたい場合は、ネイティブ側で実装し、JavaScript から呼べる形で公開します。

## Capacitor と React Native・Flutter の違い

1 つのコードで iOS・Android 両方のアプリを作る手段は、Capacitor だけではありません。代表的な 3 つを比べると、違いは「画面を誰が描画するか」に集約されます。

| ツール | 描画の仕組み | 強み | 注意点 |
| --- | --- | --- | --- |
| **Capacitor** | ネイティブの WebView 上で Web として描画し、端末機能はブリッジ経由で呼ぶ | 既存の Web 資産と Web 開発のスキルをほぼそのまま活かせる。導入の手間が最も小さい | 複雑な 3D 描画、高頻度の再描画、重いアニメーションには向かない |
| **React Native** | JavaScript からネイティブの UI コンポーネントを操作する | ネイティブの部品で描画されるため、見た目と操作感がネイティブアプリに近い | React での記述が前提。Web 向けのコード（DOM・CSS）はそのままでは再利用できない |
| **Flutter** | 独自の描画エンジン（iOS・Android では Impeller、Web では Skia）で画面を直接描画する | OS をまたいで UI が一貫し、性能も高い | Dart の習得が必要。Web 開発のエコシステムとは別の世界になる |

Capacitor は「Web をそのまま持ち込む」、React Native は「JavaScript でネイティブ UI を組む」、Flutter は「自前で全部描く」と捉えると、選択の軸が見えやすくなります。

## 基本的な開発の流れ

既存の Web プロジェクトに Capacitor を追加する場合の流れです。Node.js に加えて、iOS 向けには macOS と Xcode、Android 向けには Android Studio が必要です。現行の Capacitor 8 では Node.js 22 以上と Xcode 26.0 以上が求められます（詳しくは後述）。

### 1. Capacitor のインストールと初期化

```bash
npm install @capacitor/core @capacitor/cli
npx cap init
```

`npx cap init` ではアプリ名とアプリ ID（`com.example.app` のような逆ドメイン形式）を尋ねられます。フレームワークを自動検出できない場合は、Web アセットのディレクトリ（既定値は `www`）も尋ねられます。

設定ファイルは、プロジェクトに TypeScript が入っていれば `capacitor.config.ts`、なければ `capacitor.config.json` として作られます。設定の `webDir` は、Web ビルドの出力先（Vite なら `dist`）に合わせておきます。

### 2. プラットフォームの追加

```bash
npm install @capacitor/android @capacitor/ios
npx cap add android
npx cap add ios
```

ここでプロジェクト直下に `android/` と `ios/` が生成されます。これらはコミットして管理します。

### 3. Web アプリのビルドと同期

まず、通常どおり Web アプリをビルドします（Vite、Next.js の static export など）。続いて `npx cap sync` で、ビルド成果物とプラグインをネイティブプロジェクトへ反映します。

```bash
npm run build
npx cap sync
```

Web 側のコードを変更したら、ビルドしてから `npx cap sync` を実行する、というのが日常の作業サイクルになります。

### 4. ネイティブ IDE で開いて実行

`npx cap open ios` で Xcode が、`npx cap open android` で Android Studio が開きます。

```bash
npx cap open ios
npx cap open android
```

あとはそれぞれの IDE からシミュレーターや実機で実行し、ストア申請用のビルドも通常のネイティブアプリと同じ手順で行います。IDE を開かずに動作確認だけしたいときは、`npx cap run ios` や `npx cap run android` でシミュレーター・エミュレーターに直接起動できます。

### 日々の開発は「ブラウザで 8 割」

実際の開発では、毎回ネイティブのビルドを回すわけではありません。React + Capacitor 8 で iOS アプリを個人開発し App Store で公開した開発者は、日常の流れを次のように紹介しています（[note の体験記](https://note.com/shiny_liger4141/n/na81df95fcb9c)）。

1. `npm run dev` で Vite の開発サーバーを起動し、ブラウザで UI を作り込む
2. ネイティブ API が絡む機能だけ、`npx cap sync` で反映してから `npx cap run ios` でシミュレーターで確認する
3. 本番ビルドは Xcode で Archive して App Store Connect に提出する

ネイティブ API に触れない部分は、Vite のホットリロードとブラウザの開発者ツールだけで完結するので、「ブラウザで 8 割作り、残り 2 割をシミュレーターで確かめる」という進め方になります。

## Capacitor 8 で変わったこと

2026 年 11 月時点の最新安定版は 8 系（npm の `latest` は 8.6.0）です。Capacitor 8 は 2025 年 12 月に公開され、その後もマイナーリリースが続いています。次のメジャーである 9 系もベータ版が公開されています。

7 系からの主な変更点は次のとおりです（[公式の移行ガイド](https://capacitorjs.com/docs/updating/8-0)より）。

- **iOS の依存管理が SPM に**: `npx cap add ios` で作る新規プロジェクトは、CocoaPods ではなく Swift Package Manager（SPM）を使う構成が既定になりました。既存の CocoaPods 構成のプロジェクトはそのまま動きます。CocoaPods で新規に作りたい場合は `npx cap add ios --packagemanager CocoaPods` を使います。
- **Android の edge-to-edge 対応**: 新しいコアプラグイン System Bars が、ステータスバーやナビゲーションバーの下まで画面を広げる最近の Android の表示に対応します。これに伴い、設定項目 `android.adjustMarginsForEdgeToEdge` は廃止され、余白は CSS 変数で扱う方式になりました。
- **動作要件の引き上げ**: Node.js 22 以上、Xcode 26.0 以上、iOS の Deployment Target は 15.0、Android は `minSdkVersion` 24・`compileSdkVersion` / `targetSdkVersion` 36 が新しい下限です。

## 実運用での注意点

WebView ベースであることは、開発の速さと引き換えに、いくつかの制約も生みます。先の体験記で挙げられている注意点のうち、Capacitor アプリ全般に当てはまるものを整理します。

- **バックグラウンドでは JavaScript が止まる**: iOS はバックグラウンドに回ったアプリを強く制限するので、`setInterval` などのタイマーは当てになりません。体験記では、録音の経過時間を「開始時刻を保存しておき、表示するときに差分を計算する」方式に変えて解決しています。バックグラウンドで録音を続けたい場合は、`Info.plist` の `UIBackgroundModes` に `audio` を設定する必要があります。
- **権限の説明文は審査で見られる**: マイクや位置情報を使うアプリでは、`NSMicrophoneUsageDescription` などの説明文が App Store の審査で確認されます。体験記では WebView ベースのアプリでも問題なく審査を通ったと報告されていますが、「なぜその権限が必要か」ははっきり書く必要があります。
- **公式以外のプラグインも選択肢になる**: 公式プラグインにない機能は、コミュニティ製のプラグインや、サービス提供元の SDK（例: アプリ内課金の RevenueCat が出している `@revenuecat/purchases-capacitor`）で補えます。体験記では録音もコミュニティ製プラグインで実装しています。ただし、記事で紹介されているパッケージ名が npm に見当たらないこともあるので、導入前に npm で実在と Capacitor 8 への対応状況を確かめておくと安全です。

## どんなプロジェクトに向いているか

Capacitor が力を発揮するのは、次のようなケースです。

- すでに **既存の Web アプリ**（SaaS、EC サイト、社内ツールなど）があり、素早くアプリストアにも展開したい
- **Web フロントエンドのチームだけで**、モバイルアプリも内製・保守したい
- 画面の中心がフォーム入力、一覧表示、CRUD 操作で、**描画性能への要求が高くない**

逆に、ゲームのような描画負荷の高いアプリや、ネイティブと見分けがつかない操作感を最優先するアプリでは、React Native や Flutter、あるいは純粋なネイティブ開発のほうが適しています。

## まとめ

Capacitor は、Web アプリを WebView ごとネイティブアプリに包み、端末機能をプラグインで補うランタイムです。ネイティブプロジェクトを Git で管理するソースとして扱う設計により、Cordova の「生成物をいじれない」という弱点を解消しています。

「Web の資産とチームを活かして、最小の手間でアプリを出す」ことが目的なら、まず検討する価値のある選択肢です。

## 参考

- [Capacitor 公式サイト](https://capacitorjs.com/)
- [Capacitor ドキュメント](https://capacitorjs.com/docs)
- [ionic-team/capacitor（GitHub）](https://github.com/ionic-team/capacitor)
- [Updating to 8.0（Capacitor 公式の移行ガイド）](https://capacitorjs.com/docs/updating/8-0)
- [Announcing Capacitor 8（Ionic Blog）](https://ionic.io/blog/announcing-capacitor-8)
- [Swift なしで iOS アプリを公開する方法 ― React + Capacitor 8 で個人開発した全記録（note）](https://note.com/shiny_liger4141/n/na81df95fcb9c)
