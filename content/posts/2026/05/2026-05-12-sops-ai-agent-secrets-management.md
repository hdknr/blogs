---
title: "SOPS で AI エージェントのシークレット管理 — Claude Code に「平文を見せない」3つのガードレール"
description: "Claude Code などの AI エージェントに SOPS で暗号化されたシークレットを安全に扱わせるための3つのガードレール（平文をコンテキストに載せない／コミットさせない／復号鍵を分離する）と、Linux / macOS / Windows それぞれでの sops exec-env を使ったランタイム注入の具体例、permissions.deny の設定例を解説します。"
date: 2026-05-12
lastmod: 2026-05-12
draft: false
source_url: "https://github.com/hdknr/blogs/issues/93#issuecomment-4426426904"
categories: ["セキュリティ"]
tags: ["sops", "claude-code", "secrets", "security", "ai-agent"]
---

Claude Code をはじめとする AI エージェントの運用で **「シークレットをどこにどう置くか」** は避けて通れない設計判断になります。Git リポジトリに暗号化したまま置ける [SOPS](https://github.com/getsops/sops)（旧 Mozilla SOPS、現在は CNCF Sandbox プロジェクト）は GitOps と相性がよく、小〜中規模のチームや個人開発では有力な選択肢の一つです。

ただし、シェルやファイル操作の権限を持つ AI エージェントと組み合わせる場合、**「AI が自分で復号して中身を覗き見・漏洩させない」** ための3つのガードレール設計が前提になります。本記事では SOPS のメリットと AI エージェント特有のリスク、そして推奨構成をまとめます。

## SOPS を AI エージェント運用で使うメリット

SOPS は「Git リポジトリに暗号化したまま秘匿情報を保存できる」シンプルなツールです。AWS KMS、GCP KMS、Azure Key Vault、[age](https://github.com/FiloSottile/age)、PGP など、環境に合わせた暗号化バックエンドを選べます。

AI エージェントとの相性で見ると、特に次の3点でメリットがあります。

- **構成管理の簡素化** — 開発環境（`.env` など）とデプロイ環境の秘密情報を、同じ Git ワークフローで一貫管理できる
- **diff が読みやすい** — SOPS は YAML / JSON の **値だけを暗号化** し、キー（変数名）は平文で残せるため、AI エージェントが「どんな設定項目があるか」を構造として理解できる
- **柔軟なバックエンド** — クラウド KMS から手元の `age` キーまで、用途に応じて使い分けられる

特に「キー名は平文・値だけ暗号化」という設計は、AI エージェントに「設定の存在は知らせるが値は見せない」運用と非常に親和性が高い構造です。

なお、マネージド型のクラウドサービスでシークレットを集中管理したい場合は、[Infisical](/blogs/posts/2026/04/2026-04-21-infisical-secret-management/) のような選択肢もあります。「Git で持つか／サービスで持つか」は採用判断のポイントになります。

## AI エージェント特有のリスク

一方で、Claude Code のように Bash 実行権限を持つエージェントに SOPS を扱わせると、以下のリスクが顕在化します。

### ① AI による意図しない「平文」の出力

エージェントに `sops -d secrets.enc.yaml` を実行させる権限を与えると、復号結果が **エージェントのコンテキスト（会話ログ・ツール出力・要約サマリ）に平文として取り込まれてしまう** リスクがあります。

ツール出力はキャッシュされたり、トランスクリプトに残ったり、別セッションでサマリ化されたりする可能性があるため、「一度でも平文がコンテキストに乗ったらアウト」という前提で設計するのが安全です。

> **対策:** エージェントには直接 SOPS ファイルを復号させず、**ランタイム（実行環境）側で環境変数として注入**する。エージェントからは `.env` や復号済みファイルそのものを読み取れないよう、Claude Code の `permissions.deny` や `CLAUDE.md` でアクセス禁止を明示する。

### ② Git リポジトリへの「平文」コミット

AI が SOPS ファイルを編集しようとして、誤って暗号化を解いた平文のままコミット・プッシュしてしまうミスが想定されます。`sops` は通常 `sops <ファイル名>` で開けば暗号化を維持したまま編集できますが、エージェントが「とりあえず復号 → 編集 → 保存」という素朴な手順を踏むと事故につながります。

> **対策:**
>
> - Git の **pre-commit hook**（[gitleaks](https://github.com/gitleaks/gitleaks) や [detect-secrets](https://github.com/Yelp/detect-secrets) など）を仕込み、平文の秘密情報が含まれていないかチェックする
> - SOPS ファイルの編集は **人間が `sops <ファイル名>` で行う** ルールにし、AI には「設定ファイルにどんなキーがあるか」だけを教える運用にする

### ③ 復号鍵の取り扱い（プロンプトインジェクション対策）

最も深刻なのが、**復号鍵そのものが AI エージェントの実行環境に置かれているケース**です。KMS の権限や `age` の秘密鍵がエージェントから到達可能な場所にあると、プロンプトインジェクションを食らった瞬間、**AI が自ら鍵を使ってすべての秘匿情報を復号 → 外部送信** することが原理的に可能になります。

> **対策:** プロダクション環境の復号鍵は **CI/CD パイプラインや特定のセキュアな実行環境（サンドボックス）内のみ** に限定する。開発中の AI エージェントには **開発環境用の最小権限の鍵だけ** を与える。

## ランタイム側で環境変数として注入する具体策（OS 別）

リスク①の対策として挙げた「**ランタイム（実行環境）側で環境変数として注入**」は、OS 別に手段が異なります。ここでは Linux / macOS / Windows それぞれでの実践的な方法を整理します。

### 大前提（OS 共通）

「**AI エージェント自身が復号コマンドを実行する**」のは NG です。AI が `sops exec-env ...` を打てる時点で、子プロセスの環境変数を AI 側から `env` や `printenv` で覗き見できます。

**「復号して env を持つプロセス」と「AI が走るプロセス」を別系統に分離する**のが基本設計です。典型パターンは以下の2通り。

- **パターン A**: アプリは別ターミナル（または別ユーザー）で `sops exec-env` 経由で起動。AI エージェントには `Bash(sops:*)` を deny し、復号鍵にも触れさせない
- **パターン B**: CI/CD やデプロイ時のみ復号。開発中の AI エージェントには本番値そのものを渡さず、ダミー値 or dev 用の最小権限値だけを与える

### Linux / macOS

**1. `sops exec-env`（最も基本かつ推奨）**

`sops` 単体で「復号 → 環境変数として子プロセスへ注入 → 終了時に破棄」を実現できます。ファイルにも書きません。

```bash
# secrets.enc.yaml の中身を環境変数化して、その中だけで npm run dev を起動
sops exec-env secrets.enc.yaml 'npm run dev'

# Python アプリの例
sops exec-env secrets.enc.yaml 'python app.py'
```

ファイルとして渡したい場合は `sops exec-file`（FUSE 経由でメモリ上に置かれ、子プロセス終了時に消える）:

```bash
sops exec-file secrets.enc.yaml 'myapp --config {}'
```

**2. direnv + SOPS（開発で常用するなら）**

[direnv](https://direnv.net/) を入れて `.envrc` に書いておくと、ディレクトリに `cd` した瞬間に env が自動で注入され、出ると消えます。

```bash
# .envrc
export $(sops -d secrets.enc.yaml | yq -r 'to_entries | .[] | "\(.key)=\(.value)"')
```

ただし direnv は子プロセスにも env を継承するため、**この shell から Claude Code を起動すると AI に値が見えてしまいます**。AI 用ターミナルは別に開き、direnv を効かせない（`direnv deny` しておく）構成にしてください。

**3. systemd `LoadCredential`（Linux 本番環境）**

systemd 247+ なら、復号済みの値を子プロセスに **読み取り専用 tmpfs** として渡せます。`ExecStartPre` で `sops -d` した結果を `LoadCredential` に渡す構成です。

```ini
# /etc/systemd/system/myapp.service
[Service]
ExecStartPre=/usr/local/bin/sops -d --output /run/credentials/myapp/secrets /etc/myapp/secrets.enc.yaml
LoadCredential=secrets:/run/credentials/myapp/secrets
ExecStart=/usr/bin/myapp
```

アプリ側は `$CREDENTIALS_DIRECTORY/secrets` を読みます。AI エージェントが同じホスト上にいても、別ユニットの credential には触れません。

**4. macOS `launchd` + ラッパー**

launchd の `EnvironmentVariables` キーに直接書くと plist が平文になるため非推奨。macOS でアプリをデーモン化するなら、ラッパースクリプトで `sops exec-env` してから本体を起動するのが現実的です。

```xml
<!-- ~/Library/LaunchAgents/com.example.myapp.plist -->
<key>ProgramArguments</key>
<array>
  <string>/usr/local/bin/sops</string>
  <string>exec-env</string>
  <string>/Users/me/secrets.enc.yaml</string>
  <string>/Users/me/bin/myapp</string>
</array>
```

復号鍵（`age` 秘密鍵 や AWS 認証情報）は **macOS Keychain** に格納し、launchd 起動時にだけ読めるようにすると鍵自体の保護も上がります。

### Windows

**1. `sops exec-env`（PowerShell でもそのまま使える）**

`sops` は Windows ネイティブビルドが提供されており、PowerShell からも同じ流儀で使えます。

```powershell
# 単発実行
sops exec-env secrets.enc.yaml 'python app.py'

# 引数にスペースが入る場合は明示的にクォート
sops exec-env .\secrets.enc.yaml "node .\server.js --port 3000"
```

**2. WSL2 経由（実用上の推奨）**

実用上は **WSL2 上で Linux と同じ運用にするのが最も安全かつ楽** です。

- WSL2 側に `sops` と `age` を入れ、Linux と同じ `sops exec-env` で起動
- Claude Code は Windows 側 / WSL2 側どちらで動かすかを明確に分離
- 復号鍵（`~/.config/sops/age/keys.txt` など）は WSL2 内に置き、Windows 側ファイルシステム（`/mnt/c/...`）には絶対に置かない

**3. Windows Credential Manager + ラッパースクリプト**

復号鍵を Windows Credential Manager（`cmdkey` / `Get-StoredCredential`）に保管しておき、アプリ起動スクリプトの中だけで取り出して `sops` を呼び出す方式。AI エージェント側からは Credential Manager のエントリ名しか見えません。

```powershell
# launch-app.ps1（人間 or タスクスケジューラから起動）
$cred = Get-StoredCredential -Target "sops-age-key"
$env:SOPS_AGE_KEY = $cred.GetNetworkCredential().Password
sops exec-env .\secrets.enc.yaml "python .\app.py"
Remove-Item Env:SOPS_AGE_KEY
```

このスクリプト自体が AI から実行されないよう、Claude Code 側の deny ルールにも追加しておきます。

**4. Windows Service / タスクスケジューラ**

サービス化する場合、サービスアカウント専用の `age` キーやマネージド ID（クラウドなら）に紐付け、開発者ユーザーや AI エージェントが走るユーザーからはその鍵に到達できないよう ACL を設定します。

### AI エージェント側の権限分離（OS 共通の鉄板ルール）

どの OS でも、`.claude/settings.json` 側で以下を deny に入れておくのが鉄板です。

```json
{
  "permissions": {
    "deny": [
      "Bash(sops:*)",
      "Bash(env)",
      "Bash(printenv:*)",
      "Bash(set)",
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Read(~/.config/sops/**)",
      "Read(~/.aws/credentials)"
    ]
  }
}
```

ポイントは **`sops` の禁止だけでなく `env` / `printenv` も塞ぐ** こと。せっかく別プロセスで env を分離しても、AI が `env | grep KEY` を実行できれば自分の親シェルの env を覗けてしまいます。

### OS 別まとめ

| OS | 推奨手段 | 鍵の置き場所 |
| --- | --- | --- |
| **Linux** | `sops exec-env` ／本番は `systemd LoadCredential` | KMS or `~/.config/sops/age/keys.txt`（root 限定） |
| **macOS** | `sops exec-env` ／ launchd + ラッパー | Keychain |
| **Windows** | WSL2 上で Linux 流儀（推奨）／ネイティブなら PowerShell + Credential Manager | Credential Manager or WSL2 内 |

共通する設計指針は、**「復号する主体（アプリ／CI）」と「AI エージェントが動く主体」を別プロセス・別権限で完全に分離する**こと。`sops exec-env` はその分離を最小コストで実現する一番のおすすめ手段です。

## 「AI に env を渡す」の正しい意味 — エージェントとアプリの責務分離

ここまで読んで「でも AI に作業を依頼する以上、結局どこかで AI に env の値を渡す必要があるのでは？」と感じた方も多いはずです。実はこの直感には **混ざりやすい2軸** が隠れています。順に分解します。

### 区別したい2つの軸

「AI に env が要る」と感じる場面を分解すると、以下の2つに分かれます。

| 軸 | やること | env の **値** が必要か |
| --- | --- | --- |
| **A. AI がコードを書く・読む** | リポジトリのソース編集、設定ファイル編集、リファクタ | **不要**。**変数名**だけ知っていればコードは書ける |
| **B. AI が動作確認する** | アプリ起動、`curl` テスト、E2E 実行 | env が必要なのは **アプリ本体**。AI 自身は不要 |

A だけなら AI に env を渡す必要は本来ありません。問題が発生するのは B を「同じプロセス（AI 自身）」にやらせようとした瞬間です。

### direnv で何が起きるのか

direnv は **「その shell の子プロセス全部に env を継承する」** ツールです。Claude Code 自身がその shell の子プロセスとして起動すると、構造的に以下のようになります。

```text
[ shell (direnv 有効、env あり) ]
        │
        └── claude (env を継承する)
                │
                ├── Bash ツール:  env / printenv → 値が AI のコンテキストに乗る
                ├── Bash ツール:  curl ...        → URL に env を埋め込めば外部送信
                └── ファイル書き込み: AI が「デバッグ用に」.env を書き出す可能性
```

Claude Code は「AI が頭脳・Bash が手足」のプロセスなので、Claude Code プロセス自身が env を持つことは **「AI の手足が env に到達できる」** とほぼ同義です。プロンプトインジェクションを 1 回食らえば終わりです。

### 正しい分離パターン（ターミナル A / B 構成）

「AI に env を渡す」のではなく、**「env を持って動いているアプリと AI を通信させる」** のが基本パターンです。

| | ターミナル A（アプリ用） | ターミナル B（AI 用） |
| --- | --- | --- |
| **direnv** | 有効（`direnv allow`） | **無効（`direnv deny`）** |
| **env** | あり（`sops exec-env` 等で注入） | **なし** |
| **起動するもの** | `npm run dev` / `python app.py` などアプリ本体 | `claude` などの AI エージェント |
| **触れるもの** | アプリと env | ソースコード、`curl localhost:3000/...` |

- ターミナル A: 人間がアプリを起動。env はアプリプロセスにだけ入る
- ターミナル B: Claude Code を起動。env が無いので AI が `env` を打っても何も出ない
- AI は **アプリの公開インターフェース経由**（HTTP API、CLI 出力、ログファイル等）で動作確認する。env の値は知らなくても、アプリが env を使って結果を返してくれる

これが「AI に値は見せず、アプリの振る舞いだけ見せる」分離の核です。

### それでも AI に env を渡す必要があるケース

「AI にテストを実行させたい」「AI にバッチを走らせたい」など、どうしても AI が env を持つプロセスを起動する必要がある場合は、**3段階のレイヤー分け** で考えます。

| レイヤー | 値の例 | 誰が持つ |
| --- | --- | --- |
| **L1 本番シークレット** | 本番 API キー、本番 DB パスワード | **CI/CD のみ**。人間も AI も触れない |
| **L2 dev シークレット（最小権限）** | dev API キー（低レート上限）、dev DB パスワード | 人間 + アプリ用 shell（ターミナル A） |
| **L3 AI に渡してよい値** | sandbox 環境の値、課金/破壊リスクのない最小権限値 | AI 用 shell（ターミナル B） |

**L3 にあるのは「漏れても被害が限定的な値」だけ** です。例えば次のように分けます。

- 本番 OpenAI API キーは絶対渡さず、月額上限 $5 の dev キーを渡す
- 本番 DB ではなく、テスト用ローカル DB の認証情報を渡す
- AWS なら本番ロールではなく、`AWS_PROFILE=dev-readonly` だけ

「AI が env を見れる ≒ ネット上に流出している」と同じくらいの感覚で、**そのレベルでも漏れて困らない値だけを渡す** のが原則です。

### まとめると

- **「env を子プロセスに渡す」≠「AI が値を読み取れる」**。アプリプロセスに渡しても AI が同居していなければ AI のコンテキストには乗らない
- Claude Code 自身が direnv 入り shell の子プロセスになると **AI = env を持つ子プロセス** が成立してしまうので、そこを切り離す
- AI には **アプリの公開インターフェース（API / CLI 出力 / ログ）** だけ見せ、env そのものは見せない
- どうしても AI に env を渡す必要があるなら、**L3（漏れても痛くない値）だけ** にする

「AI に環境変数を見せない」という言葉は、正確には **「本番値を AI のコンテキストに乗せない」** という意味です。AI に何も渡さない、という極論ではありません。

## 推奨構成案

上記を踏まえると、AI エージェント時代の SOPS 運用は次のような構成に落ち着きます。

| コンポーネント | 管理方法 |
| --- | --- |
| **保存先** | Git リポジトリ（SOPS で暗号化済みの `secrets.enc.yaml`） |
| **復号タイミング** | アプリケーションの起動時、または CI/CD でのデプロイ時 |
| **AI への露出** | **させない。** エージェントには環境変数名（例: `OPENAI_API_KEY`）だけを教え、値は見せない |
| **アクセス制限** | Claude Code の `permissions.deny` や `CLAUDE.md` で、秘密情報を含むディレクトリや `.env` を読み取り禁止に指定 |
| **復号鍵の置き場所** | プロダクション鍵は CI/CD 専用。開発エージェントには dev 用の最小権限鍵のみ |

### Claude Code での `permissions.deny` 設定例

`.claude/settings.json` に以下のような deny ルールを書いておくと、Claude Code が `.env` や復号済みファイルに触れようとした時点でブロックされます。

```json
{
  "permissions": {
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Bash(sops:*)"
    ]
  }
}
```

`Read` だけでなく `Bash(sops:*)` も deny に入れておくのがポイントです。ファイルを直接読まれなくても、`sops -d` を呼ばれてしまえばコンテキストに平文が乗ります。`Bash(sops:*)` で全 `sops` コマンドを禁止しておき、必要に応じて `allow` 側で限定的に許可する設計が安全です。

なお、Claude Code のセキュリティ設定全般は [Claude Code を使うなら最低限やっておきたい『7つのセキュリティ設定』](/blogs/posts/2026/03/2026-03-23-claude-code-7-security-settings/) もあわせて参照してください。

## まとめ

SOPS は **「秘密情報を Git で安全に持ち運ぶ」** という目的では非常に有効で、AI エージェント時代の構成管理にも相性がよいツールです。ただし Claude Code のような強力なツールを使うなら、

1. **平文をコンテキストに載せない** — 復号は実行環境側で済ませ、エージェントには環境変数だけを見せる
2. **平文をコミットさせない** — pre-commit hook で機械的にチェック
3. **復号鍵をエージェント環境に置かない** — プロダクション鍵は CI/CD 専用、開発鍵は最小権限

この3つのガードレールを併用することを強くお勧めします。「SOPS を入れた = 安全」ではなく、「SOPS + AI エージェント向けの権限分離 = 安全」という発想が、これからのシークレット管理の最低ラインです。
