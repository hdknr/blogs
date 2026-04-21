---
title: "ANOLISA とは — Alibaba が公開した AI Agent 向け Linux OS（Copilot Shell / Agent Sec Core / AgentSight / OS Skills）"
date: 2026-04-21
lastmod: 2026-04-21
draft: false
description: "Alibaba が 2026 年 3 月に公開した Agentic OS プロジェクト ANOLISA の全体像を解説。Copilot Shell / Agent Sec Core / AgentSight / OS Skills の 4 コンポーネントと導入手順をまとめます。"
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4286240942"
categories: ["AI/LLM"]
tags: ["alibaba", "agent", "ebpf", "agentic-os", "security"]
---

2026 年 3 月末、Alibaba は [`alibaba/anolisa`](https://github.com/alibaba/anolisa) を公開しました。これは同社が保守するサーバー向け Linux ディストリビューション **Anolis OS** を AI Agent 実行基盤として再構築した「Agentic OS」プロジェクトで、正式名称は **ANOLISA**（**A**gentic **N**exus **O**perating **L**ayer & **I**nterface **S**ystem **A**rchitecture）です。

本記事では、ANOLISA が解こうとしている問題と、公開されている 4 つのコアコンポーネント（Copilot Shell / Agent Sec Core / AgentSight / OS Skills）の役割、そして開発者が今すぐ触れられる導入手順を整理します。

## ANOLISA が目指すもの

ANOLISA は Anolis OS の「Agentic 進化版」と位置づけられており、AI Agent ワークロードをサーバー側で安全かつ観測可能な形で動かすためのベストプラクティス実装を狙っています。LLM / Agent がコード編集・シェル実行・ネットワークアクセス・プロセス管理といった OS レベルの操作を当たり前に行う時代において、「アプリケーション境界で守る」従来型セキュリティでは不十分になってきました。ANOLISA はその問題意識を背景に設計されています。

- リポジトリ: [alibaba/anolisa](https://github.com/alibaba/anolisa)
- ホームページ: [agentic-os.sh](https://agentic-os.sh)
- ライセンス: Apache License 2.0
- 主言語: TypeScript（Copilot Shell）/ Rust（AgentSight）/ C（eBPF プローブ）
- 公開: 2026 年 3 月 30 日（初版リポジトリ作成）

## 4 つのコンポーネント

ANOLISA は単一のカーネルモジュールではなく、Agent 実行に必要な「シェル・セキュリティ・観測・スキル」を別々のプロダクトとして分離し、RPM で同居運用する構成を取っています。

| Component | 役割 |
|-----------|------|
| [Copilot Shell](https://github.com/alibaba/anolisa/tree/main/src/copilot-shell) | AI Agent が常駐するターミナル UI |
| [Agent Sec Core](https://github.com/alibaba/anolisa/tree/main/src/agent-sec-core) | OS 層のセキュリティカーネル |
| [AgentSight](https://github.com/alibaba/anolisa/tree/main/src/agentsight) | eBPF ベースの Agent オブザーバビリティ |
| [OS Skills](https://github.com/alibaba/anolisa/tree/main/src/os-skills) | 運用スキルの標準ライブラリ |

### Copilot Shell（cosh）

[Qwen Code](https://github.com/QwenLM/qwen-code) を上流に据えた AI ターミナルアシスタントです。記事執筆時点の公開リリースは `copilot-shell v2.1.0`（2026-04-19 公開、上流 Qwen Code v0.9.0 ベース）となっています。

特徴的な機能:

- 自然言語でのコード修正・リファクタリング
- `/bash` でインタラクティブシェルへのドロップイン
- **Skill System**: Project > User > Extension > Remote の優先順で local / remote のスキルをディスカバリ
- **Hooks System**: `PreToolUse` でツール呼び出しを事前インターセプト
- **Multi-Provider 対応**: Aliyun 認証（ECS RAM ロールの Web 認証または AK/SK）、Qwen OAuth、DashScope / DeepSeek / Kimi / GLM / MiniMax などの OpenAI 互換エンドポイント
- **PTY モード**: `sudo` を含む完全な擬似端末サポート

インストールは Anolis OS / ALinux 環境で RPM から、もしくはソースビルドから行えます。

```bash
# RPM で全コンポーネントを導入
sudo yum install copilot-shell agent-sec-core agentsight anolisa-skills

# 起動
cosh
# または
co
copilot
```

ソースビルドの場合はリポジトリを clone して `make` を使います:

```bash
cd src/copilot-shell
make build
make start
```

Node.js は 20 以上が必要で、`make install` は husky の pre-commit フック（Prettier + ESLint）もセットアップします。

### Agent Sec Core

**AI Agent 向け OS 層セキュリティカーネル**。ANOLISA だけでなく OpenClaw など他の Agent OS プラットフォームにも組み込める独立コンポーネントとして設計されています。

設計原則は 5 本柱:

1. **最小権限** — タスク完了に必要な最小の権限しか Agent に渡さない
2. **明示的認可** — 機密操作は必ずユーザー確認、サイレントな権限昇格は禁止
3. **ゼロトラスト** — スキル同士が互いに信頼しない。操作ごとに独立認証
4. **多層防御** — System Hardening → Asset Verification → Security Decision
5. **Security Over Execution** — セキュリティと機能が競合したら、セキュリティが勝つ

Agent 実行のたびに 3 フェーズのセキュリティチェックが強制されます:

| Phase | チェック内容 | PASS 条件 |
|-------|-------------|-----------|
| **Phase 1** | `loongshield seharden --scan --config agentos_baseline` でシステム堅牢化をスキャン | 出力に `结果：合规`（「結果: 準拠」の意） |
| **Phase 2** | 全スキルの GPG 署名と SHA-256 ハッシュを検証 | `VERIFICATION PASSED` |
| **Phase 3** | Phase 1 + Phase 2 を再走させる最終確認 | 両方再パス |

どこかで PASS しなければ、以降のフェーズはキャンセルされ Agent 実行そのものがブロックされます。

リスク区分は 4 段階で、コマンド種別ごとに Linux Sandbox（`linux-sandbox`）のテンプレートが紐づけられています。

| テンプレート | ファイルシステム | ネットワーク | 用途 |
|--------------|----------------|-------------|------|
| **read-only** | 全体読み取りのみ | 拒否 | `ls` / `cat` / `grep` / `git status` など |
| **workspace-write** | cwd と `/tmp` のみ書き込み可、他は読み取り | 拒否 | ビルド・編集・スクリプト実行 |
| **danger-full-access** | 制限なし | 許可 | ⚠ 特殊用途のみ、原則使わない |

保護対象としてハードコードされている資産には、`~/.ssh/` 配下、GPG 秘密鍵、API トークン、`/etc/shadow`、`/etc/sudoers`、`/etc/ssh/sshd_config`、`/boot/`、`/usr/lib/systemd/` などが含まれます。**Agent はこれらを触れない**ことが OS 側で保証される、という発想です。

### AgentSight

eBPF ベースの「ゼロ侵襲」Agent オブザーバビリティツール。Agent のコードや設定を一切変更せずに、LLM API コール・トークン消費・プロセス挙動・SSL/TLS トラフィックをカーネル側から観測します。

> **補足: eBPF とは** — **extended Berkeley Packet Filter** の略で、Linux カーネルにユーザー空間から小さなプログラムを安全に差し込める仕組みです。検証器付きの専用 VM でプログラムが実行されるため、カーネルをクラッシュさせずに内部挙動を観測・制御できます。syscall / 関数呼び出し / パケット処理 / セキュリティ判断点など、さまざまなフックポイントに差し込めるのが特徴で、[Cilium](https://cilium.io/)、[Falco](https://falco.org/)、[bpftrace](https://github.com/bpftrace/bpftrace) など多くの観測・セキュリティツールの基盤になっています。アプリ側にコードを入れずに外から見られるため、LLM SDK や Agent ハーネスが頻繁に入れ替わる AI Agent ワークロードとは相性が良い技術です。公式ポータル: [ebpf.io](https://ebpf.io/)。

パイプライン構成はシンプルで、`Probes → Parser → Aggregator → Analyzer → GenAI → Storage` と流れます。保存先はローカル SQLite とオプションの Alibaba Cloud SLS（Simple Log Service）。

| Probe | 役割 |
|-------|------|
| **sslsniff** | `SSL_read` / `SSL_write` に uprobe を仕掛けて暗号化前後の平文を捕捉 |
| **proctrace** | `execve` シスコールをトレースし、コマンドライン引数とプロセス木を記録 |
| **procmon** | プロセスの生成・終了を軽量監視し、AI Agent を自動発見 |

SSE（Server-Sent Events）の解析も入っており、ストリーミング応答でも token 数を正確に数えられます。トークナイザーは Hugging Face 互換（Qwen 系をサポート）。

CLI は `agentsight trace` でプローブを走らせ、`agentsight token` でトークン使用量を週次・日次で集計できます:

```bash
# デーモンモード + SLS エクスポート
sudo agentsight trace --daemon \
  --sls-endpoint <endpoint> \
  --sls-project <project> \
  --sls-logstore <logstore>

# 今週と先週のトークン使用量比較
agentsight token --period week --compare
```

### OS Skills

Copilot Shell が自動ディスカバリする「運用スキル」の標準ライブラリ。RPM でインストールすると `/usr/share/anolisa/skills/` に展開されます。カテゴリと同梱スキルの一部を抜粋すると以下のとおり:

- **AI ツール**: `install-claude-code`, `install-openclaw`, `install-copaw`, `setup-mcp`
- **システム管理**: `alinux-admin`, `backup-restore`, `storage-resize`, `upgrade-alinux-kernel`, `shell-scripting`
- **DevOps**: `github`, `kernel-dev`, `sysom-agentsight`, `sysom-diagnosis`
- **Alibaba Cloud**: `aliyun-ecs`
- **Security**: `alinux-cve-query`

各スキルは `SKILL.md`（YAML フロントマター + Markdown）と、任意の `scripts/` `reference/` `docs/` で構成されます。Claude Code / OpenClaw の「Skill」概念を OS 運用向けに移植したものと捉えると分かりやすいでしょう。

## ANOLISA の位置づけ — なぜ OS 層なのか

Claude Code や各種 Agent SDK が抱える「権限」「観測」「再現性」の課題は、多くの場合アプリケーション層のラッパーで解こうとしています。`allowedTools` の設定、プロンプトキャッシュ計測、Hooks での介入といった仕組みはその典型です。

ANOLISA のアプローチは、これらを **OS 側の責務** に落とし込む点で異なります。

- **権限**: `agent-sec-core` がサンドボックステンプレートと GPG 署名検証で強制
- **観測**: `agentsight` が eBPF で Agent の外側から捕捉
- **スキル**: `os-skills` が RPM パッケージとして配布・バージョニング
- **UI**: `cosh` が Aliyun 認証や PTY を OS ネイティブにバインド

「Agent がアプリケーション層の約束事を破っても OS で止まる」設計のため、Copilot Shell 以外の Agent（Claude Code、OpenClaw など）からも同じ Agent Sec Core / AgentSight を共有できます。これが OS 層実装の大きな利点です。Agent Sec Core の README にも「OpenClaw などの Agent OS プラットフォームにも適用可能」と明記されています。

## まず触ってみるには

Anolis OS / ALinux 4 環境があれば RPM で最短 1 行、なくてもリポジトリからソースビルドで試せます。

1. リポジトリを clone: `git clone https://github.com/alibaba/anolisa`
2. Copilot Shell をビルド: `cd src/copilot-shell && make build && make start`
3. AgentSight は Rust + eBPF ツールチェイン（clang + libbpf）が必要。`cargo build --release` で `agentsight` バイナリが生成される
4. OS Skills は `/usr/share/anolisa/skills/` に展開されることを想定しているので、手元で試す場合は `cosh` の設定でスキルディレクトリを指定する

Alibaba Cloud 上の ALinux 4 ECS で動かすのがもっとも摩擦が少なく、SLS への観測ログ集約まで含めた「想定された形」の ANOLISA を体験できます。一方で、コンポーネントだけ切り出して別環境で使う方向性も十分現実的です:

- Agent Sec Core だけを他の Linux ディストリビューションに移植する
- AgentSight だけを Kubernetes 上の AI ワークロード監視に使う

## まとめ

- ANOLISA は Alibaba の Agentic OS 実装で、Anolis OS を AI Agent 実行基盤として進化させたもの
- Copilot Shell（AI ターミナル）/ Agent Sec Core（セキュリティ）/ AgentSight（観測）/ OS Skills（スキル）の 4 コンポーネント構成
- OS 層での権限・観測・スキル管理という方針で、Claude Code / OpenClaw 等の別 Agent からも部品として利用できる
- Apache 2.0 で公開されており、RPM またはソースビルドですぐ試せる

アプリケーション層の Agent ハーネスに続く「次の主戦場」は OS 側である、というメッセージをもっともはっきり体現しているプロジェクトの一つです。
