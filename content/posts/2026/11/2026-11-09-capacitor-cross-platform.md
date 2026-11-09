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

![Capacitor アプリの構成図。ネイティブアプリの中に WebView があり、Web アプリは既製プラグインの JS API や自作プラグインの JS 定義を呼び出す。呼び出しは Capacitor ブリッジを通ってネイティブ側の公式プラグイン・コミュニティ製 SDK・自作プラグインに届き、各プラグインが OS の API やネイティブ SDK を使う。自作プラグインはアプリ本体のネイティブコードで登録し、結果は call.resolve() でブリッジ経由で JS に Promise として返る](/blogs/images/capacitor-app-architecture.png)

図のオレンジ色の部分が、自分で書くネイティブ拡張です。JavaScript 側の定義、Swift / Kotlin・Java 側のプラグイン本体、アプリ本体での登録の 3 か所がそろって初めて、JavaScript から自作の機能を呼べるようになります。

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

アプリ内に自作プラグインを置く場合に書くものは、次の 3 つです（公式ドキュメントの `Echo` プラグインの例に沿っています）。

1. **JavaScript 側の定義**: `@capacitor/core` の `registerPlugin<EchoPlugin>('Echo')` で、ネイティブのプラグインにつながるオブジェクトを作ります。型引数のインターフェースが、メソッドの型になります。
2. **ネイティブ側の本体**: iOS は `CAPPlugin` と `CAPBridgedPlugin` を継承したクラスに `@objc func echo(_ call: CAPPluginCall)` を書きます。Android は `@CapacitorPlugin(name = "Echo")` を付けた `Plugin` のサブクラスに、`@PluginMethod` を付けたメソッドを書きます。どちらも、結果は `call.resolve(...)` で返します。
3. **アプリ本体での登録**: iOS は独自の ViewController の `capacitorDidLoad()` で `bridge?.registerPluginInstance(EchoPlugin())` を呼びます。Android は `MainActivity` の `onCreate()` で `registerPlugin(EchoPlugin.class)` を呼びます（公式の例では `super.onCreate()` の前に置いています）。

```typescript
import { registerPlugin } from '@capacitor/core';

export interface EchoPlugin {
  echo(options: { value: string }): Promise<{ value: string }>;
}

const Echo = registerPlugin<EchoPlugin>('Echo');

const { value } = await Echo.echo({ value: 'hi' });
```

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

## GitHub Actions で CI を回す

Capacitor のプロジェクトは、GitHub Actions で Web のテストからネイティブのビルドまで自動化できます。ジョブは次の 3 つに分けると見通しがよくなります。

| ジョブ | ランナー | やること |
| --- | --- | --- |
| Web | `ubuntu-latest` | `npm ci`、lint、単体テスト、`npm run build` |
| Android | `ubuntu-latest` | `npx cap sync android` のあと、Gradle でビルドと単体テスト |
| iOS | `macos-latest` | `npx cap sync ios` のあと、`xcodebuild` でビルド |

iOS のビルドには Xcode が要るので、macOS ランナーが必須です。private リポジトリでは macOS ランナーの分単価が Linux より高いので、iOS のジョブは実行する条件を絞っておくと費用を抑えられます。

### ワークフローの例

Web と Android のジョブを 1 つにまとめた例です。

```yaml
name: CI
on:
  pull_request:
  push:
    branches: [main]

jobs:
  android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-node@v7
        with:
          node-version: 22
          cache: npm
      - uses: actions/setup-java@v6
        with:
          distribution: temurin
          java-version: 21
      - run: npm ci
      - run: npm test --if-present
      - run: npm run build
      - run: npx cap sync android
      - run: ./gradlew assembleDebug test
        working-directory: android

  ios:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-node@v7
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm run build
      - run: npx cap sync ios
      - run: >-
          xcodebuild -project ios/App/App.xcodeproj -scheme App
          -configuration Debug -sdk iphonesimulator
          -destination "generic/platform=iOS Simulator"
          CODE_SIGNING_ALLOWED=NO build
```

この例の Android と iOS のビルドコマンドは、Capacitor 8.6.0 の `npx cap add` で作った素のプロジェクトを使い、手元の Mac（Xcode 27.2、JDK 22）で通ることを確かめています。CI ランナー（Xcode 26.6、JDK 21）で実際に走らせた結果ではありません。

### 押さえておく点

- **ランナーが Capacitor 8 の要件を満たすか**: Capacitor 8 は Node.js 22 以上と Xcode 26.0 以上を求めます。2026 年 11 月時点の `macos-latest` は macOS 26（Arm64）のイメージで、既定の Xcode は 26.6 です。`-latest` が指す先は時期によって変わるので、固定したい場合は `macos-26` のようにバージョンを明示します。Android 側は JDK 21 を前提にしています（JDK 21 が必須になったのは Capacitor 7 からで、8 の移行ガイドでは改めて触れられていません）。
- **iOS のプロジェクト形式で引数が変わる**: Capacitor 8 の既定である SPM 構成では、上の例のように `-project ios/App/App.xcodeproj` を指定します。CocoaPods 構成なら、`pod install` のあとで `-workspace ios/App/App.xcworkspace` を指定します。
- **CI でのビルドは署名なしでよい**: シミュレーター向けに `CODE_SIGNING_ALLOWED=NO` でビルドすれば、証明書は要りません。TestFlight や Google Play への配信まで自動化する場合は、証明書・プロビジョニングプロファイル・keystore を GitHub Secrets に置き、fastlane などで署名と提出を行います。

### 単体テストをどこで回すか

| 対象 | テンプレートの状態 | 実行コマンド | 実行環境 |
| --- | --- | --- | --- |
| Web（Vitest、Jest など） | プロジェクト次第 | `npm test` | どの OS でも可 |
| Android（JVM 上の単体テスト） | `app/src/test` に `ExampleUnitTest` が入っている | `./gradlew test` | Linux・macOS どちらも可。エミュレーター不要 |
| Android（端末上のテスト） | `app/src/androidTest` に `ExampleInstrumentedTest` が入っている | `./gradlew connectedAndroidTest` | エミュレーターか実機が必要 |
| iOS（XCTest） | **テストターゲットが入っていない** | `xcodebuild test` | macOS とシミュレーターが必要 |

テストの大半はブラウザで動くロジックに対するものなので、まず Web 側の単体テストを Linux ランナーで回すのが安上がりです。Android の JVM 単体テストも、上の例のように同じ Linux ランナーで実行できます。

iOS のネイティブコード（自作プラグインの Swift など）をテストしたい場合は、先に Xcode で `App` プロジェクトに Unit Testing Bundle のターゲットを追加し、スキーム `App` のテストに含めます。そのうえで、macOS 上でシミュレーターを指定して実行します。手元の Mac でも macOS ランナーでも、同じコマンドで動きます。

```bash
xcodebuild test -project ios/App/App.xcodeproj -scheme App \
  -destination "platform=iOS Simulator,name=iPhone 17"
```

`name=` に指定するシミュレーターは、実行環境に入っているものでなければなりません。手元では `xcrun simctl list devices` で一覧を確かめられます。

## Live Updates（OTA 更新）

Capacitor アプリの中身の大半は、WebView で動く Web アセットです。そこで、**Web 層（HTML・CSS・JS）だけをサーバーから配信して差し替え、ストアの審査を通さずにバグ修正や画面の変更を届ける**ことができます。これを Live Updates（OTA 更新）と呼びます。

### 差し替えられるのは WebView の層だけ

冒頭の構成図でいえば、OTA で差し替えられるのは WebView の中（Web アプリと JS 側の定義）だけです。ブリッジから下のネイティブ側は差し替えられません。

- **OTA で届けられる**: `npm run build` で出力される Web アセット。
- **ストアのリリースが必要**: Swift / Kotlin・Java のコード、ネイティブ側のプラグインの追加や更新、自作プラグインの変更、`Info.plist` や `AndroidManifest.xml` の権限の変更。

自作プラグインに新しいメソッドを足した場合、それを呼ぶ JS は OTA で配れても、ネイティブ側はストア版を更新するまで古いままです。OTA の設計で一番気をつけるのは、この **Web バンドルとインストール済みのネイティブ部分の組み合わせ** です。

### ストアの規約との関係

どちらのストアも、ダウンロードしたコードでアプリの機能を変えることを原則として禁じています。ただし、WebView で動く JavaScript は条件付きで例外になっています。

- **Apple**: App Review Guidelines の 2.5.2 は、アプリの機能を追加・変更するコードのダウンロードと実行を禁じています。一方、Apple Developer Program 使用許諾契約の 3.3.1 B（Executable Code）は、ダウンロードした「解釈実行されるコード」を、次の 3 条件を満たす範囲で認めています。
  - 宣伝している本来の目的と食い違う機能を足して、アプリの主目的を変えないこと
  - OS の署名・サンドボックスなどのセキュリティ機能を迂回しないこと
  - App Store で配布するアプリの場合、ほかのアプリのストアを作らないこと
- **Google Play**: デバイスとネットワークの不正使用に関するポリシーで、Google Play 以外からの実行コード（dex、JAR、.so など）のダウンロードを禁じています。ただし、この制限は「WebView やブラウザの JavaScript のように、仮想マシンやインタプリタ上で動き、Android API に間接的にしかアクセスしないコード」には適用されない、と明記されています。

実務上は、**バグ修正や小さな改善にとどめ、審査を通したものと別のアプリに変えない**という線引きになります。

### 手段の選び方

| 手段 | 状況 |
| --- | --- |
| Ionic Appflow（`@capacitor/live-updates`） | Ionic 公式の Live Updates サービス。2025 年 2 月に新規の受付を止めており、2027 年 12 月 31 日でサービスを終える。新しく採用する選択肢ではない |
| Capgo（`@capgo/capacitor-updater`） | プラグインはオープンソースで、ホスティングされたサービスのほか自前のサーバーでも運用できる |
| Capawesome Cloud（`@capawesome/capacitor-live-update`） | Capacitor 向けのホスティング型 Live Updates サービス |
| Codemagic Patch | 自前のサーバーで運用するセルフホスト型の OTA 更新の仕組み。React Native 向けに始まり、Capacitor の Web 層の更新にも対応した |

Microsoft の CodePush（App Center）も、2025 年 3 月 31 日の App Center の終了とともに使えなくなっています。

### 導入前に決めておくこと

- **互換性の管理**: 新しい Web バンドルを、どのネイティブの版に配ってよいか。ネイティブ側を変えたストア版を出したら、それ以降の版にだけ新しいバンドルを配る、といった振り分けが必要です。
- **ロールバック**: 配ったバンドルで起動に失敗したとき、前の版に自動で戻せるか。
- **改ざん対策**: バンドルに署名し、アプリ側で検証するか。配信経路を乗っ取られると、任意の JavaScript をアプリに流し込まれることになります。

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
- [App Review Guidelines（Apple）](https://developer.apple.com/app-store/review/guidelines/)
- [Apple Developer Program License Agreement](https://developer.apple.com/support/terms/apple-developer-program-license-agreement/)
- [Device and Network Abuse（Google Play ポリシー）](https://support.google.com/googleplay/android-developer/answer/16273414)
- [Important Announcement: The Future of Ionic's Commercial Products（Ionic Blog）](https://ionic.io/blog/important-announcement-the-future-of-ionics-commercial-products)
