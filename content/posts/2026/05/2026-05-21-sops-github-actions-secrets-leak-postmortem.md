---
title: "SOPS復号後の secrets を GitHub Actions ログに平文露出した話 — masking バグの根本原因と4層防御の post-mortem"
date: 2026-05-21
lastmod: 2026-05-21
slug: "sops-github-actions-secrets-leak-postmortem"
draft: false
description: "SOPS で暗号化した secrets を GitHub Actions ログに平文露出した実インシデントの post-mortem。::add-mask:: 登録ループが存在しない一時ファイルを参照していたバグの根本原因、即時対応 (run 削除 + rotate)、source-from-file パターン + workflow lint による4層防御まで詳説。"
source_url: "https://gist.github.com/hdknr/735ddfb1794279872078ca27f8256378"
categories: ["セキュリティ"]
tags: ["sops", "GitHub Actions", "post-mortem", "add-mask", "$GITHUB_ENV"]
---

> **TL;DR**: SOPS で暗号化していた API トークン複数種が GitHub Actions の workflow log に平文で露出した。原因は **「masking 登録ループが存在しない一時ファイルから読まれていて空回りしていた」** という pre-existing なバグ。`gh run delete` でログ削除 + 該当 secrets を rotate して被害を抑制。再発防止のため **構造的予防 (source-from-file) + 静的検知 (lint) + ドキュメントルール + PR レビュー時 security review** の 4 層で対策。

## 0. 文脈

ある社内自動化基盤の Phase 0 検証中、`workflow_dispatch` で配信 workflow の dry_run を初めて起動したところ、復号済 secrets が workflow ログの env header に平文表示された。本記事はその post-mortem である。

技術スタック:

- GitHub Actions (Linux runner)
- SOPS + age による secrets 暗号化（リポ内 commit）
- LLM ベースの workflow agent (custom action 経由) による skill 実行
- メッセージング基盤 / CRM / 課題管理 SaaS への API トークン群

## 1. 何が起きたか

dry_run 検証で起動した workflow の途中 step、**`Run skill` step の `env:` block 表示**で複数の API トークンが平文表示された:

```
Run skill
  env:
    SOME_MESSAGING_TOKEN: ***REDACTED***
    SOME_MESSAGING_SECRET: ***REDACTED***
    SOME_CRM_KEY: ***REDACTED***
    SOME_ISSUE_TRACKER_KEY: ***REDACTED***
    ...
```

`${{ secrets.X }}` 参照で GH に保管されていた 1 つの API key (LLM 用) のみ自動 mask が効いており無事だった。SOPS 経由で渡していた secrets はすべて平文露出した。

## 2. 原因

### 設計上の意図

該当 workflow の `Decrypt secrets` step は、SOPS で暗号化された secrets ファイルを runtime に復号し、`$GITHUB_ENV` に展開する設計。値がログに出ないよう `::add-mask::` 登録もする「つもり」のコードがあった。

### 実装のバグ

問題の masking 登録コード:

```bash
sops --decrypt secrets.enc.yml > /tmp/secrets.env.yml
yq -r 'to_entries | .[] | "\(.key)=\(.value)"' /tmp/secrets.env.yml >> "$GITHUB_ENV"

# 値をログに露出させないため GH のマスクにも登録
while IFS='=' read -r k v; do
  [ -z "$k" ] && continue
  echo "::add-mask::$v"
done < /tmp/secrets.env.yml.flat 2>/dev/null || true   # ← この .flat ファイルは
                                                       #    どこにも作られていない

rm -f /tmp/secrets.env.yml /tmp/secrets.env.yml.flat
```

中間ファイル名のリファクタの過程で `.flat` という参照先が取り残されていた。

連鎖した障害:

- 参照先 `/tmp/secrets.env.yml.flat` は **スクリプト内のどこでも生成されない**
- `2>/dev/null || true` で「ファイルが無い」エラーが silent に握りつぶされる
- 結果として while ループは **常に空入力で回り、`::add-mask::` 登録が 1 件も走らない**
- それでも `$GITHUB_ENV` には secrets がそのまま書き込まれる
- 後続 step の `env:` block 表示で全 secret が平文表示

### なぜ早期発見できなかったか

1. **エラーが silent**: `2>/dev/null || true` でファイル不在エラーがログに出ない
2. **GitHub Actions の `env:` 仕様の罠**: `$GITHUB_ENV` に書いた env は subsequent step の env header に**自動表示される**。API 経由で監視ツールが拾うのと違い、step を 1 つでも追加すると即露出する
3. **「masking してるつもり」のコメント**: コードコメントが「正しく masking している」風だったため、レビュー時に流された
4. **dry_run の油断**: 「dry_run だから実 API は叩かない」という誤った安心感。dry_run でも secrets は env に展開されている

担当者 (AI コーディング agent を含む) は本 workflow を作業セッション中に複数回読んだが、毎回別の問題 (CLI 起動方式, runner OS の制約等) の修正に意識が向いていて、masking ロジックの破綻に気付けなかった。

## 3. 即時対応 (containment)

### 3-1. ログ削除

`gh run delete <run-id>` で漏出した複数の workflow run を削除:

```bash
for RUN in <run-id-list>; do
  gh run delete "$RUN" --repo <owner/repo>
done
```

> GitHub の内部キャッシュ / 監査ログには残る可能性があるため、削除だけでは完全な mitigation にならない。rotate が必須。

### 3-2. Secret rotate

| Secret 種別 | rotate 手順 | 確認 |
| --- | --- | --- |
| API key (issue tracker) | 個人設定で旧 key を削除 → 新規発行 | 新 key で `/me` 系 endpoint → 200, 旧 key → 401 ✅ |
| Access token (CRM, Private App) | provider の "Rotate" 機能で発行 + 旧 token を即 expire (grace period がある場合 manual expire 必須) | 新 token で API → 200, 旧 token → 401 ✅ |
| Long-lived access token (messaging) | 該当 console で「再発行」 | 別作業 |
| HMAC channel secret | 仕様上**再発行不可** (channel 削除→再作成しか手段がない) | 攻撃 surface 評価して現状維持判断 |

特に `HMAC channel secret` は鍵 + チャネル ID + 攻撃発火経路の全てを揃えないと悪用できないこと、relay の挙動が極めて限定的 (event を内側に転送するだけ) であることから、**現状維持** を選択。再発行 (channel 再作成) には数十分の運用断 + 各種 URL の再設定が必要で、得られるリスク低減と釣り合わないと判断。

トレードオフ判断は post-mortem に明文化し、後日プラン変更や脅威モデルの変化があれば再評価する。

## 4. 構造的対策 (multi-layer defense)

「ルール明文化だけ」では人間 (および AI) の注意力に頼ることになるため、複数層で防御する。

### 層 ①: 構造的予防 — source-from-file パターン

`$GITHUB_ENV` に decrypted 値を**書かない**設計に変更:

```yaml
- name: Decrypt secrets to sourceable file
  env:
    SOPS_AGE_KEY: ${{ secrets.SOPS_AGE_KEY }}
  run: |
    set -euo pipefail
    sops --decrypt secrets.enc.yml > /tmp/secrets.env.yml
    # add-mask 登録 (defense-in-depth)
    while IFS= read -r v; do
      [ -z "$v" ] && continue
      [ "$v" = "REPLACE_ME" ] && continue
      echo "::add-mask::$v"
    done < <(yq -r 'to_entries | .[] | .value' /tmp/secrets.env.yml)
    # source 可能な .env を /tmp に置く (GITHUB_ENV には書かない!)
    yq -r 'to_entries | .[] | "export " + .key + "=" + (.value | tostring | @sh)' \
      /tmp/secrets.env.yml > /tmp/secrets.env
    chmod 600 /tmp/secrets.env
    rm -f /tmp/secrets.env.yml

- name: Run skill
  uses: <some-action>@v1
  env:
    SECRETS_FILE: /tmp/secrets.env
  with:
    prompt: |
      最初に必ず `set -a; source "$SECRETS_FILE"; set +a` で
      env をロードしてから処理に入ること。
      ファイルパスの中身を stdout / stderr 等に echo しないこと。

- name: Cleanup secrets file
  if: always()
  run: rm -f /tmp/secrets.env
```

ポイント:

- `$GITHUB_ENV` 経由しないので **subsequent step の env header に物理的に出ない**
- skill 内で明示的に `source` するため、secrets は単一の bash subprocess scope に閉じる
- `chmod 600` でファイル権限も絞る
- `yq @sh` で shell-safe quote (`tostring` を挟むのは integer 値対策)
- `if: always()` の cleanup step で job 失敗時もファイルを消す

masking バグが将来再発しても **env header に出る経路がそもそも消えている** のが構造的に良い。

### 層 ②: 静的検知 — workflow lint

```python
#!/usr/bin/env python3
"""
Detect: sops --decrypt + $GITHUB_ENV write in same run block without
preceding ::add-mask::
"""

def check_run_block(run_script):
    sops_pos = run_script.find("sops --decrypt")
    env_pos = run_script.find('>> "$GITHUB_ENV"')
    mask_pos = run_script.find("::add-mask::")

    if sops_pos >= 0 and env_pos >= 0:
        if mask_pos < 0:
            return "add-mask not registered"
        if mask_pos > env_pos:
            return "add-mask AFTER env write (race window)"
    return None  # OK
```

検出ロジック:

- `run:` block 単位で YAML を parse
- `sops --decrypt` と `>> "$GITHUB_ENV"` が両方ある block について `::add-mask::` の存在・順序を検証
- 不在 / 逆順なら CI fail

検証実績:

- 現状の workflows (source-from-file 化済) → ✅ pass
- 旧 buggy pattern (本インシデントの根本原因) → ✅ FAIL 検出
- mask 完全欠落 → ✅ FAIL 検出
- 別 workflow の正しい順序 (per-variable mask 先行) → ✅ pass

CI lint job として組み込み、push 毎に実行。

### 層 ③: ドキュメントルール — agent / 人間向け規約

リポルートの agent 規約ファイル (`AGENTS.md` 系) に専用セクションを設けた:

```markdown
## CI / Workflow Security Rules

### Rule 1: secrets を扱う workflow は実行前に full trace
- $GITHUB_ENV に decrypted 値を書く箇所がある場合、その前に
  ::add-mask:: 登録が完了しているか手で追う
- ::add-mask:: の登録対象が動的生成される一時ファイルから読まれている
  場合、そのファイルが実際に生成されるパスをコード上で verify する

### Rule 2: 初回 run は dummy secrets で
本物の credentials を入れた状態で workflow を初めて回す前に、placeholder
値で 1 度回して masking が正しく動くか確認する。

### Rule 3: 構造的予防を優先
可能なら $GITHUB_ENV 書き込み自体を避ける。

### Rule 4: 漏出を疑ったら即対応
run 削除 → rotate → secrets ファイル更新 → 構造修正の順序。
```

人間 / AI 両方が参照する。完全予防ではないが、忘却率を下げる保険として機能。

### 層 ④: PR レビュー時の security review (検討中)

AI ベースの `/security-review` 系 tool を PR レビューに組み込む運用。層 ② と被るが、人間が見落とすケースで効く。チーム合意次第で導入。

## 5. 教訓

### 個別の technical lessons

- **`$GITHUB_ENV` は危険な界面**。ここに何を書いたかは subsequent step の env header に必ず展開されることを忘れない。masking でカバーできるが、masking はベストエフォートで race / バグに弱い
- **silent error suppression は禁止**。`2>/dev/null || true` は便利だが security-critical なコードでは致命的な隠蔽になりうる
- **dummy secret での dry run** を初期 onboarding 手順として組み込む。本物 secret は最後に入れる
- **暗号化 at rest** 自体は良い設計だが、復号後の取り扱いが最重要。「at rest が暗号化されている」は in-flight の安全性を保証しない

### Process / cultural lessons

- **コードコメントは検証されない**。「masking してるつもり」のコメントがあっても実装が動いていないケースは存在する。レビュー時はコメントではなくコードの挙動を見る
- **多層防御**。1 つの層 (ドキュメント、人間の注意、コードレビュー) で完全に防ぐのは無理。複数を組み合わせる
- **AI コーディング agent も人間と同じく注意力の限界がある**。長いセッションで意識が「workflow を動かす」に集中すると、横で潜在しているセキュリティバグを見落とす。専用の lint / 静的検知が必要
- **チェックリストに dummy-secret dry-run を組み込む**。「本番値の前にダミーで通せ」が最強の事前検知

### Incident response 自体について

- インシデント発生から containment 完了 (run 削除 + 主要 token rotate) まで 2 時間以内
- 構造的対策 (4 層) を翌日中に main へ landing
- 関係者には事実 + 必要作業 (再発行依頼) を明示してエスカレーション
- ドキュメント化で経験を resource 化（同じ罠を将来踏まないため）

完全に防げなかった事故から学習する文化を保つことが、似た規模の事故を 1/10 に減らす最短距離だと考えている。

## 6. 適用範囲 / 持ち帰り

本事例は **SOPS + GitHub Actions + LLM/CLI agent** という構成での話だが、本質的には以下のいずれかに該当するプロジェクトすべてに直接適用できる教訓を含む:

- CI 上で暗号化 secrets を復号して使う (SOPS, sealed-secrets, Vault sidecar 等問わず)
- 復号後の値を `$GITHUB_ENV` / `setEnv` 系の environment 共有機構に乗せる
- subsequent step / 外部 action にその env を継承させる
- masking / redaction を bash や script で実装している

これらのいずれかが当てはまるなら、4 層防御のうち少なくとも **層 ① (構造的予防)** と **層 ② (静的検知)** は導入する価値が高い。
