---
title: "Capacitor の Live Updates（OTA 更新）を自前の AWS で配信する：S3・CloudFront 構成"
date: 2026-11-09
lastmod: 2026-11-09
slug: "capacitor-live-updates-aws"
draft: false
categories: ["クラウド/インフラ"]
tags: ["Capacitor", "aws", "CloudFront", "GitHub Actions", "OTA"]
---

Capacitor アプリは中身の大半が WebView で動く Web アセットなので、その部分だけをサーバーから配って差し替える **Live Updates（OTA 更新）** が使えます。仕組みとストア規約との関係は、[Capacitor 入門の記事の「Live Updates（OTA 更新）」の節](/blogs/posts/2026/11/capacitor-cross-platform/#live-updatesota-更新)で整理しました。

この記事では、その配信側を **自分の AWS アカウントに作る** 方法を紹介します。Ionic の Appflow は 2027 年 12 月 31 日でサービスを終えます。乗り換え先を探している場合や、配信の基盤とデータを自分で管理したい場合の選択肢になります。

端末側の更新処理には、オープンソースの Capgo プラグイン（`@capgo/capacitor-updater`）を使います。Capgo Cloud にはつながず、**手動モード**（いつ何をダウンロードして切り替えるかを、アプリのコードで決めるモード）で動かします。AWS 側は S3、CloudFront、GitHub Actions だけで、常時動くサーバーはありません。

## 全体の構成

![Capacitor の Live Updates を自前の AWS で配信する構成図。GitHub Actions がビルドした Web アセットを zip に固めてチェックサムを計算し、OIDC で引き受けた IAM ロールで S3 に zip と manifest.json を書き込む。S3 は非公開で、CloudFront が OAC 経由で読んで HTTPS で配信する。アプリは起動直後に notifyAppReady を呼び、前面に来たら manifest.json を取得し、自分のストア版に対応するバンドルを選んで、チェックサム付きで zip をダウンロードし、次にバックグラウンドへ回ったときに切り替える。新しい版で notifyAppReady が期限内に呼ばれなければ前の版へ自動で戻る](/blogs/images/capacitor-live-updates-aws.png)

役割は 3 つに分かれます。

- **GitHub Actions**: Web アプリをビルドして zip に固め、SHA-256 のチェックサムを計算し、S3 に置いて `manifest.json` を書き換えます。
- **AWS**: 非公開の S3 バケットに zip と `manifest.json` を置き、CloudFront が HTTPS で配信します。
- **アプリ**: `manifest.json` を見て、自分のストア版に向けた新しいバンドルがあればダウンロードし、次にバックグラウンドへ回ったときに切り替えます。

## manifest.json の設計

この記事では、ストアで配るアプリの版番号（例: `1.4.0`）を **ストア版**、OTA で配る Web の版（例: `1.4.0-web.13`）を **バンドルの版** と呼びます。

配信の中心は、**ストア版ごとに、配るバンドルを 1 つ決める** `manifest.json` です。

```json
{
  "1.3.0": {
    "version": "1.3.0-web.7",
    "url": "https://updates.example.com/bundles/1.3.0-web.7.zip",
    "checksum": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
  },
  "1.4.0": {
    "version": "1.4.0-web.13",
    "url": "https://updates.example.com/bundles/1.4.0-web.13.zip",
    "checksum": "debd3b29509fcc4a934b9b5decb994623bfc44344d526198718e140ffeb7efed"
  }
}
```

ストア版をキーにするのは、OTA で差し替えられるのが Web 層だけだからです。ネイティブのプラグインを増やした 1.4.0 向けの JavaScript を 1.3.0 の端末に配ると、存在しないネイティブのメソッドを呼んで壊れます。キーで分けておけば、各ストア版には、そのネイティブ部分に合わせてビルドしたバンドルだけが届きます。

この形にしておくと、次の 2 つも manifest の操作だけで済みます。

- **審査中の版には配らない**: 審査に出したストア版は、審査が終わるまで manifest に載せません。載っていない版の端末には何も配られないので、審査中にアプリの中身が変わることはありません。Capgo Cloud は、審査端末からの要求を既定で止めています。自前で運用する場合はこの対策を自分で用意する必要がある、とプラグインの README に明記されています。
- **ロールバック**: `manifest.json` を前の内容に戻せば、全端末への配信が前のバンドルに戻ります。

## アプリ側の実装

### プラグインの導入と設定

```bash
npm install @capgo/capacitor-updater @capacitor/app
npx cap sync
```

`capacitor.config.json`（TypeScript なら `capacitor.config.ts` の `plugins`）で自動更新を切り、手動モードにします。

```json
{
  "plugins": {
    "CapacitorUpdater": {
      "autoUpdate": false
    }
  }
}
```

### 更新を確かめるコード

どの版を配るかの判定は、テストしやすいように関数に切り出しておきます。

```typescript
// src/manifest.ts
export interface BundleEntry {
  version: string;
  url: string;
  checksum: string;
}

// キーはストア版（ネイティブ）の版。値はその版に配る Web バンドル
export type Manifest = Record<string, BundleEntry>;

export function pickBundle(
  manifest: Manifest,
  nativeVersion: string,
  currentVersion: string,
): BundleEntry | null {
  const entry = manifest[nativeVersion];
  if (!entry || entry.version === currentVersion) return null;
  return entry;
}
```

更新を確かめる処理です。アプリのエントリポイント（Vite なら `src/main.ts`）の先頭で `import './live-update';` として読み込みます。

```typescript
// src/live-update.ts
import { App } from '@capacitor/app';
import { CapacitorUpdater } from '@capgo/capacitor-updater';
import { type Manifest, pickBundle } from './manifest';

const MANIFEST_URL = 'https://updates.example.com/manifest.json';

// 起動直後に呼ぶ。一定時間（既定 10 秒）内に呼ばれないと前の版に戻る
CapacitorUpdater.notifyAppReady();

async function checkForUpdate(): Promise<void> {
  const { version: nativeVersion } = await App.getInfo(); // ストア版の版（例: 1.4.0）
  const { bundle } = await CapacitorUpdater.current(); // いま動いている Web バンドル
  const res = await fetch(MANIFEST_URL, { cache: 'no-store' });
  if (!res.ok) return;
  const entry = pickBundle((await res.json()) as Manifest, nativeVersion, bundle.version);
  if (!entry) return;

  const downloaded = await CapacitorUpdater.download({
    url: entry.url,
    version: entry.version,
    checksum: entry.checksum, // 8.54 系では必須。無いと "Checksum required" で失敗する
  });
  // 次にバックグラウンドへ回ったときに切り替える（操作中の再読み込みを避ける）
  await CapacitorUpdater.next({ id: downloaded.id });
}

App.addListener('appStateChange', ({ isActive }) => {
  if (isActive) void checkForUpdate();
});
void checkForUpdate();
```

ポイントは 4 つです。

- **`notifyAppReady()` は起動直後に呼ぶ**: 新しいバンドルで起動したあと、期限（`appReadyTimeout`、既定 10 秒）内にこれが呼ばれないと、プラグインは前の版に自動で戻します。ネットワーク通信より前に呼ぶよう、型定義のコメントでも指示されています。
- **ストア版は `App.getInfo()` で取る**: `@capacitor/app` の `App.getInfo()` が返す `version` は、iOS の `CFBundleShortVersionString`、Android の `versionName` です。manifest のキーと同じ文字列になるよう、ストア版の番号をそのまま使います。
- **`checksum` を必ず渡す**: プラグインの README にある手動モードの例には `checksum` がありません。しかし 8.54.2 のネイティブコードでは、iOS・Android とも、チェックサムが空だと `Checksum required` でダウンロードが失敗します。値は zip の SHA-256 を小文字の 16 進で書いたものです。
- **`set()` ではなく `next()` を使う**: `set()` はその場で JavaScript の実行環境を捨てて再読み込みします。`next()` は、次にバックグラウンドへ回ったときに切り替えるので、利用者の操作を邪魔しません。

### 画面の文言

プラグインの README は、App Store の審査で誤解されないよう、利用者に見える画面で「アップデート」「ダウンロード中」のような言葉を使わないことを勧めています。切り替えを `next()` でバックグラウンドに回しているのは、利用者に何も見せずに済ませるためでもあります。

## AWS 側の準備：S3・CloudFront・IAM ロール

### S3 バケット

- パブリックアクセスはすべてブロックしたままにします。読むのは CloudFront だけです。
- **バージョニングを有効にします**。`manifest.json` を前の状態に戻すロールバックに使います。
- 最初に一度だけ、空の manifest を置いておきます。CI は「既存の manifest を読んで 1 項目を書き換える」動きなので、manifest が読めなければ失敗するようにしてあります。次のコマンドは手元で一度だけ実行します。

```bash
echo '{}' > manifest.json
aws s3 cp manifest.json s3://my-app-updates/manifest.json \
  --content-type application/json --cache-control "max-age=60"
```

### CloudFront

CloudFront のディストリビューションはコンソールで作成します。押さえる設定は次の 3 点です。

- オリジンに S3 バケットを指定し、**OAC（Origin Access Control）** を使います。OAC は、非公開の S3 バケットを CloudFront からだけ読めるようにする仕組みです。
- キャッシュポリシーには、オリジンの `Cache-Control` を TTL の範囲内で尊重するもの（マネージドの `CachingOptimized` など）を選びます。zip は版ごとにファイル名が変わるので 1 年キャッシュし、`manifest.json` は 60 秒にします。こうすると、無効化（invalidation）を発行しなくても 1 分ほどで新しい manifest が行き渡ります。
- プラグインは既定で HTTPS 以外の URL を拒否します（`httpsOnly`、8.54.0 以降の既定は `true`）。CloudFront の HTTPS の URL か、独自ドメインに証明書を付けた URL を使います。

バケットポリシーで、この配信からの読み取りだけを許可します。

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCloudFrontRead",
      "Effect": "Allow",
      "Principal": { "Service": "cloudfront.amazonaws.com" },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-app-updates/*",
      "Condition": {
        "StringEquals": {
          "AWS:SourceArn": "arn:aws:cloudfront::123456789012:distribution/E1234567890ABC"
        }
      }
    }
  ]
}
```

### GitHub Actions 用の IAM ロール

アクセスキーを GitHub に置かず、**OIDC** で一時的な認証情報を受け取ります。GitHub Actions が実行ごとに発行する短命のトークンを AWS に示し、一時的な認証情報と交換する仕組みです。IAM に GitHub の OIDC プロバイダ（`token.actions.githubusercontent.com`）を登録し、次の信頼ポリシーを持つロールを作ります。`sub` の条件で、引き受けられるのを特定のリポジトリの `main` ブランチからの実行に絞っています。

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:my-org/my-app:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

権限は、zip の置き場所と manifest への書き込みだけにします。

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PutBundles",
      "Effect": "Allow",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::my-app-updates/bundles/*"
    },
    {
      "Sid": "ReadWriteManifest",
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:PutObject"],
      "Resource": "arn:aws:s3:::my-app-updates/manifest.json"
    }
  ]
}
```

## GitHub Actions の配信ワークフロー

手動で起動し、配信先のストア版を入力して実行するワークフローです。ビルドや CI 全般については、[Capacitor 入門の記事の「GitHub Actions で CI を回す」の節](/blogs/posts/2026/11/capacitor-cross-platform/#github-actions-で-ci-を回す)も参照してください。

```yaml
name: Live update

on:
  workflow_dispatch:
    inputs:
      native_version:
        description: 配信先のストア版（例 1.4.0）
        required: true

permissions:
  id-token: write # OIDC で AWS のロールを引き受けるため
  contents: read

concurrency: live-update # manifest.json の同時更新を防ぐ

env:
  BUCKET: my-app-updates
  BASE_URL: https://updates.example.com

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-node@v7
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm run build

      - name: Zip the web bundle
        id: bundle
        env:
          NATIVE_VERSION: ${{ inputs.native_version }}
        run: |
          [[ "$NATIVE_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo "native_version must be x.y.z"; exit 1; }
          VERSION="${NATIVE_VERSION}-web.${GITHUB_RUN_NUMBER}"
          (cd dist && zip -qr "../${VERSION}.zip" . -x '.*' -x '*/.*')
          echo "version=${VERSION}" >> "$GITHUB_OUTPUT"
          echo "checksum=$(sha256sum "${VERSION}.zip" | cut -d' ' -f1)" >> "$GITHUB_OUTPUT"

      - uses: aws-actions/configure-aws-credentials@v6
        with:
          role-to-assume: arn:aws:iam::123456789012:role/live-update-publisher
          aws-region: ap-northeast-1

      - name: Upload the bundle
        env:
          VERSION: ${{ steps.bundle.outputs.version }}
        run: |
          aws s3 cp "${VERSION}.zip" "s3://${BUCKET}/bundles/${VERSION}.zip" \
            --content-type application/zip \
            --cache-control "public, max-age=31536000, immutable"

      - name: Point the manifest at the new bundle
        env:
          NATIVE_VERSION: ${{ inputs.native_version }}
          VERSION: ${{ steps.bundle.outputs.version }}
          CHECKSUM: ${{ steps.bundle.outputs.checksum }}
        run: |
          aws s3 cp "s3://${BUCKET}/manifest.json" manifest.json
          jq --arg n "$NATIVE_VERSION" --arg v "$VERSION" \
             --arg u "${BASE_URL}/bundles/${VERSION}.zip" --arg c "$CHECKSUM" \
             '.[$n] = {version: $v, url: $u, checksum: $c}' manifest.json > manifest.next.json
          aws s3 cp manifest.next.json "s3://${BUCKET}/manifest.json" \
            --content-type application/json \
            --cache-control "max-age=60"
```

いくつか意図して書いている箇所があります。

- **入力値は `env` 経由で渡し、形式を検査する**: `${{ inputs.native_version }}` を `run:` の中に直接書くと、入力した文字列がシェルのコードとして解釈され得ます（スクリプトインジェクション）。環境変数で受けて、`x.y.z` の形式でなければ止めます。
- **zip は `dist` の中で作る**: プラグインは、zip の直下（または直下の 1 フォルダ）に `index.html` があることを求めます。`.DS_Store` のような隠しファイルが入ると展開に失敗することがある、と README にあるので除外しています。
- **manifest が読めなければ失敗させる**: `aws s3 cp ... || echo '{}'` のように、読めなかったときに空の manifest で始める書き方は危険です。権限の設定ミスがひとつあるだけで、ほかのストア版の項目がすべて消えた manifest を書き戻してしまいます。
- **`concurrency` で直列にする**: 2 つの実行が同時に manifest を読み書きすると、片方の更新が消えます。

## 運用：ロールバックと改ざん対策

### ロールバック

S3 のバージョニングを有効にしてあれば、`manifest.json` を S3 上の一つ前のオブジェクトバージョンに戻すだけで、全端末への配信が前のバンドルに戻ります。まずバージョンの一覧から戻したい `VersionId` を探し、`<戻したいバージョンID>` をその値に置き換えてコピーします。

```bash
aws s3api list-object-versions --bucket my-app-updates --prefix manifest.json \
  --query 'Versions[].[VersionId,LastModified,IsLatest]' --output table
aws s3api copy-object --bucket my-app-updates --key manifest.json \
  --copy-source "my-app-updates/manifest.json?versionId=<戻したいバージョンID>"
```

同じキーに前のバージョンをコピーすると、それが新しい現行のバージョンになり、それまでのバージョンもすべて残ります（AWS のドキュメントにある復元の手順と同じです）。

すでに新しいバンドルで起動に失敗した端末は、`notifyAppReady()` の仕組みで端末側でも前のバンドルに戻ります。ただしこれは「起動して JavaScript が動き始めたか」だけを見ているので、起動後の不具合は manifest を戻して直します。

### 改ざん対策について

この構成で配信物を守っているのは、次の 2 つです。

- **書き込める主体を絞る**: S3 に書けるのは、特定のリポジトリの `main` ブランチから OIDC で引き受けた IAM ロールだけです。
- **HTTPS で配る**: CloudFront の HTTPS の URL を使い、プラグインも既定で HTTPS 以外を拒否します。

`checksum` が防ぐのは、転送中の破損や、zip だけが差し替えられた場合です。チェックサムは `manifest.json` に書いてあるので、manifest ごと書き換えられると防げません。

プラグインには、公開鍵（`publicKey`）を設定し、対応する秘密鍵で作ったバンドルしか入れないようにする仕組み（エンドツーエンドの暗号化 v2）もあります。ただし型定義には、CLI の `encrypt` コマンドで暗号化した場合は `checksum` と `sessionKey` の指定が必須で、値はそのコマンドの結果として受け取る、とあります。ネイティブ側の実装でも、`publicKey` を設定すると `sessionKey` の無いダウンロードは拒否されます。この記事の手動モードと組み合わせる方法は扱っていません。署名の検証まで必要な場合は、Capgo の CLI とドキュメントで確かめてください。

## この記事のコードについて

`src/manifest.ts` と `src/live-update.ts` は、`@capgo/capacitor-updater` 8.54.2、`@capacitor/app` 8、`@capacitor/core` 8 の型定義に対して `tsc --strict` で型チェックを通しています。`pickBundle()` は、次の 4 件のテストで確かめています。

- 新しいバンドルを返す
- 同じバンドルの版なら何もしない
- manifest に無いストア版には配らない
- 古いストア版には、その版向けのバンドルだけを配る

ワークフローの `run:` の行は、AWS CLI を呼ぶ行を除いて、手元のシェルで同じものを実行し、次のことを確かめました。

- zip の直下に `index.html` があり、隠しファイルが除外されること
- チェックサムが、別の手段で計算した SHA-256 と一致すること
- manifest の既存の項目が残ること
- 形式の違う入力を拒否すること

ワークフローの YAML と 3 つのポリシーの JSON は、構文として読み込めることを確かめています。**実際の端末での動作と、実際の AWS への配置は試していません**。

## まとめ

Capacitor の Live Updates は、配信側を S3 と CloudFront だけで作れます。要になるのは、ストア版ごとに配るバンドルを決める `manifest.json` です。これ 1 つで、ネイティブ部分との互換、審査中の保留、ロールバックをまとめて扱えます。改ざん対策は、書き込める主体の制限と HTTPS までで、バンドルの署名検証はこの記事では扱っていません。

端末側は Capgo のオープンソースのプラグインに任せられますが、手動モードでは `checksum` が必須であること、審査中の端末を避ける対策は自分で用意することの 2 点を押さえておく必要があります。

## 参考

- [Capacitor 入門：Web アプリをそのまま iOS・Android アプリにする仕組みと手順](/blogs/posts/2026/11/capacitor-cross-platform/)
- [Cap-go/capacitor-updater（GitHub）](https://github.com/Cap-go/capacitor-updater)
- [App（@capacitor/app）の API](https://capacitorjs.com/docs/apis/app)
- [Restoring previous versions（Amazon S3 ユーザーガイド）](https://docs.aws.amazon.com/AmazonS3/latest/userguide/RestoringPreviousVersions.html)
- [Restrict access to an Amazon S3 origin（CloudFront 開発者ガイド）](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/private-content-restricting-access-to-s3.html)
- [Configuring OpenID Connect in Amazon Web Services（GitHub Docs）](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws)
- [aws-actions/configure-aws-credentials（GitHub）](https://github.com/aws-actions/configure-aws-credentials)
- [Important Announcement: The Future of Ionic's Commercial Products（Ionic Blog）](https://ionic.io/blog/important-announcement-the-future-of-ionics-commercial-products)
