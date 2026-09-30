---
title: "沈黙する失敗（成功に見える失敗）"
description: "終了コード 0・出力あり・手元では正常に見えるのに中身が壊れている失敗。エラーを出さないため、コマンドの成否やファイルの有無で検証すると全部すり抜ける"
date: 2026-09-30
lastmod: 2026-09-30
aliases: ["沈黙する失敗", "silent failure", "サイレント故障", "0件成功", "成功したように見える失敗"]
related_posts:
  - "/posts/2026/09/video-use-silent-failures-hard-rules/"
  - "/posts/2026/09/claude-code-jsonl-log-verified/"
  - "/posts/2026/09/smb-norton-wfp/"
  - "/posts/2026/09/wireguard-relay-hub/"
  - "/posts/2026/09/mutation-harness/"
  - "/posts/2026/09/whitebox-blackbox-boundary-coverage/"
  - "/posts/2026/09/rokid-glasses-app-ideas/"
tags: ["エージェント設計", "テスト", "トラブルシューティング", "監視", "品質保証"]
---

## 概要

**コマンドは通り、ファイルはでき、手元では正しく見えるのに、中身だけが壊れている**種類の失敗。落ちてくれるバグはエージェントでも人間でもすぐ気づいて直すが、沈黙するバグは成果物が世に出るまで残る。「コマンドが成功した」「ファイルができた」「テストが緑だった」を完了の根拠にすると、この種の失敗は全部すり抜ける。

AI エージェントにパイプラインを任せるほど効いてくる。エージェントは終了コードとエラーメッセージを見て自己修正するので、**エラーを出さない失敗はループの外側に残り続ける**。

## 詳細

### 典型的な現れ方

| 領域 | 沈黙の形 | 何を見れば気づけたか |
|---|---|---|
| 動画パイプライン（Video Use） | ffmpeg が正常終了するが、音声トラックの取り違え・HDR タグ残留・24fps 固定・回転メタデータ誤判定・字幕のセーフゾーン侵入 | アップロード先での再生、ストリーム属性の ffprobe |
| ログ解析（Claude Code JSONL） | 他 CLI 向けパーサが `.get()` で受けて全行「該当なし」、出力 0 件で正常終了 | 抽出件数のアサーション |
| Windows のファイアウォール | `Set-NetFirewallRule` がエラーなしで値を変えない。規則は ActiveStore に載るのに効かない | 設定の読み直し、別マシンからのポート測定 |
| VPN（WireGuard 中継） | networkd がポリシールールを消してもトンネルは繋がり、EC2 のステータスチェックは正常 | カーネルに経路を直接問う（`ip route get`） |
| テスト | 到達不能なガードを消しても全テスト緑。壊れた変異が `IndentationError` で「落ちたテストなし＝GREEN」に化ける | ミューテーション、`returncode` の確認 |
| 実機アプリ（Rokid AIUI） | ドキュメントにある `crypto` が実機に無い。プレビューでは動く | 実機での確認 |

### 共通する構造

- **否定的な結論ほど危ない** — 「変わらない」「起きない」「0 件」は、実験が壊れていても同じ形で出る。テストが空振りしても、対象が存在しなくても、早期 return で到達していなくても、出力は同じ「緑」になる
- **検査の視野と壊れる場所がずれている** — Video Use の自己評価ループはカット境界のフィルムストリップと波形を見るので、コンテナ全体の属性（fps・HDR タグ・音声ストリーム選択）の異常は原理的に捕まらない
- **「確認できた」の根拠が主張を支えていない** — IP 制限の確認にルート URL の 200 を見たが、HTML パスは送信元に関係なく OAuth へリダイレクトして 200 を返していた。遮断の確認に使った ping は、そもそも遮断ルールを通っていなかった
- **環境が良すぎる** — AWS 上のテストクライアントは公開リゾルバとジャンボフレームを持っていたため、DNS 欠落と MTU 超過という 2 つの障害をどちらも再現しなかった

### 対策の型

1. **件数をアサーションに入れる** — `assert matched > 0` の 1 行で「0 件成功」は例外に変わる
2. **設定したら読み直す** — 「成功した」は「効いた」ではない。値を書いたら同じ値を読み出して比べる
3. **対照実験を用意する** — 「通る条件」と「通らない条件」の両方を測り、差が出ることを確かめて初めて証明になる。片方だけでは何も言えない
4. **ポジティブコントロールを先に通す** — 「検出されなかった」と言う前に、検出されるはずの対象で実際に検出されることを見る（[ミューテーションテスト](/blogs/wiki/concepts/mutation-testing/)）
5. **非交渉の規則を taste から切り離す** — Video Use の `SKILL.md` は、外れると沈黙する失敗になる 12 項目だけを Hard Rules として「correctness」に分け、それ以外はエージェントの裁量に任せている
6. **状態ではなく結果を問う** — 設定値を並べて見るより、カーネルに「このパケットをどこへ出すか」を直接問うほうが確実。WireGuard ハブの故障は個別の設定値ではなくこの結果に現れた
7. **自動修復しない** — 黙って直すと同じ故障が再発しても誰も気づかない。検出してアラームを上げるところまでに留める

### 自分のワークフローに当てる問い

> この工程が黙って間違った出力を出すとしたら、どこで、何を見れば気づけるのか。

この問いに答えられない工程は、「コマンドが通った＝完了」で運用されている。

## 関連ページ

- [ミューテーションテスト](/blogs/wiki/concepts/mutation-testing/) — 「緑」が何も語っていないことを壊して確かめる技法
- [テストの導出元（ホワイトボックスとブラックボックス）](/blogs/wiki/concepts/whitebox-blackbox-testing/) — カバレッジ 100% でもバグを守るテスト
- [作る役と確かめる役の分離（maker-checker）](/blogs/wiki/concepts/maker-checker/) — 自己採点の盲点
- [AI エージェントにリファクタさせる時の完了の定義](/blogs/wiki/concepts/ai-refactor-completion-boundary/) — 「コマンドが通った＝完了」ではない
- [Video Use](/blogs/wiki/tools/video-use/) — 12 の Hard Rules
- [WireGuard](/blogs/wiki/tools/wireguard/) — 検出できない半壊状態とヘルスチェック
- [Windows の受信ブロックを WFP で切り分ける](/blogs/wiki/guides/windows-inbound-block-wfp/) — 「コマンドは成功したのに効いていない」
- [Claude Code の JSONL ログを読む](/blogs/wiki/guides/claude-code-jsonl-logs/) — 0 件で成功するパーサ

## ソース記事

- [Video Use の「沈黙する失敗」— ffmpeg が成功しても動画が壊れる 5 つの罠と 12 の Hard Rules](/blogs/posts/2026/09/video-use-silent-failures-hard-rules/) — 2026-09-02
- [Mac から Windows の共有に繋がらない — WFP まで降りて犯人（ノートンのスマートファイアウォール）を特定した話](/blogs/posts/2026/09/smb-norton-wfp/) — 2026-09-03
- [Claude Code の JSONL ログを 29,043 行で検証 — 解説記事の前提が自分の環境で成り立たなかった 6 点](/blogs/posts/2026/09/claude-code-jsonl-log-verified/) — 2026-09-04
- [社外から「許可された IP」で出るための WireGuard 中継ハブ — 構成と、4 日かかった障害の話](/blogs/posts/2026/09/wireguard-relay-hub/) — 2026-09-07
- [Rokid スマートAIグラスで何を作るか — 実装 2 本でわかった制約から、道案内と売り場検索を設計する](/blogs/posts/2026/09/rokid-glasses-app-ideas/) — 2026-09-12
- [テストを信じる前に、テストを壊す — mutation harness で「緑」に意味を持たせる](/blogs/posts/2026/09/mutation-harness/) — 2026-09-16
- [ホワイトボックスとブラックボックスの違いを実測した — 分岐カバレッジ 100% でミューテーションスコアは 0% と 100%](/blogs/posts/2026/09/whitebox-blackbox-boundary-coverage/) — 2026-09-17
