---
title: "バイブコーディングの落とし穴 — AIで爆速アプリを作っても、セキュリティを無視したら法廷行き"
date: 2026-05-20
lastmod: 2026-05-20
slug: "vibecoding-security-checklist"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4502125123"
categories: ["セキュリティ"]
tags: ["vibe-coding", "セキュリティ", "owasp", "claude", "チェックリスト", "next.js"]
description: "AIで高速開発したアプリを本番公開する前に必ず確認すべき5つのセキュリティチェックリスト。SQLインジェクション・.env漏洩・プライバシーポリシー整備・レートリミット・APIキー隔離を、OWASP ZAP・slowapi・Next.jsのコード例とともに解説。"
---

「Claude に作らせたアプリを即デプロイして稼ぐ」——この流れが加速する一方で、セキュリティや法的義務を丸ごとスキップしたまま本番リリースしてしまうケースが急増している。トルコのデザイン系インフルエンサー Yiğit Akın Kaya が X（旧Twitter）に投稿した辛辣なツイートが、エンジニアコミュニティで話題になっている。

> 「バイブコーダーに悲しいお知らせ。Claude にアプリを作らせて即リリース、即マネタイズしようとしていた連中が、次々と法廷に引きずられ始めている」

この記事ではそのツイートをもとに、**AIで高速開発したアプリを本番公開する前に必ず確認すべきセキュリティチェックリスト**を日本語でまとめる。

---

## なぜ今、バイブコーダーが訴訟リスクを抱えるのか

Claude や GPT-4o などの LLM を使えば、数時間でそれなりの外観と機能を持つ Web アプリが作れる。しかしツイートが指摘するように、開発者の多くが「派手なUI」には投資するが「退屈なセキュリティと基盤」はスキップしてしまう。

問題は、セキュリティ上の欠陥はサービス開始後に顕在化することだ。個人情報漏洩・不正アクセス・著作権侵害・プライバシーポリシー不備——これらは各国の規制（日本なら個人情報保護法、EUなら GDPR など）に抵触し、法的責任を問われる。

---

## 本番公開前に確認すべき5つのセキュリティチェックリスト

ツイート原文（トルコ語）では 5 つの項目が挙げられている。日本のコンテキストに合わせて補足する。

### 1. SQL インジェクションと XSS の脆弱性スキャン

LLM が生成するコードは、入力値の検証やエスケープ処理を省略しがちだ。

```bash
# OWASP ZAP による簡易スキャン例
docker run -t ghcr.io/zaproxy/zaproxy:stable zap-baseline.py \
  -t https://your-app.example.com
```

- **SQL インジェクション**: ORM やプリペアドステートメントを使っているか確認する。生の文字列結合で SQL を組み立てていたら即アウト。
- **XSS**: ユーザー入力を HTML に埋め込む箇所では必ずエスケープ処理を入れる。React / Vue はデフォルトで対策済みだが、`dangerouslySetInnerHTML` や `v-html` の使用箇所は要チェック。

### 2. `.env` ファイルの漏洩防止

API キーやデータベース接続文字列が `.env` ファイルに入っていたとして、それが意図せず公開されていないか確認する。

```bash
# .gitignore に .env が含まれているか確認
grep -n '\.env' .gitignore

# GitHub にすでに push されていないか確認
git log --all --full-history -- '*.env'
```

`.env` を誤って `git push` してしまった場合は、**まず API キーをローテーション（無効化・再発行）してから**、`git filter-repo` または BFG Repo Cleaner で履歴からも削除する。キーが有効なまま履歴削除作業を進めても、その間に悪用されるリスクがある。

### 3. プライバシーポリシーと利用規約の整備

ユーザーデータ（メールアドレス、IPアドレス、行動ログなど）を収集するなら、プライバシーポリシーの掲載は**法的義務**だ。

- 日本：個人情報保護法で「取得目的の通知または公表」が必須
- EU ユーザーが対象に含まれる場合：GDPR でのオプトイン取得・データ処理の透明性が必要
- California（米国）ユーザーが含まれる場合：CCPA

LLM に「このサービス向けのプライバシーポリシーを生成して」と頼めばたたき台は作れるが、**法律の専門家によるレビューは必須**。特に医療・金融・子ども向けサービスは規制が厳しい。

### 4. レートリミットの設定

API コストを度外視してレートリミットなしでサービスを公開すると、悪意あるユーザーに大量リクエストを送られてクラウド請求が爆発する「API コスト攻撃」を受ける可能性がある。

```python
# FastAPI + slowapi を使ったレートリミット例
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/data")
@limiter.limit("10/minute")
async def get_data(request: Request):
    ...
```

Vercel、Cloudflare、AWS API Gateway などのプラットフォームレベルのレートリミット機能も積極的に活用する。

### 5. API キーをフロントエンドに露出させない

Next.js や React の `.env.local` で定義した変数のうち、`NEXT_PUBLIC_` プレフィックスが付いたものはブラウザに露出する。OpenAI や Anthropic の API キーを誤ってクライアントサイドで参照していないか確認する。

```javascript
// NG: NEXT_PUBLIC_ はビルド時にブラウザバンドルへインライン展開されるため API キーが丸見えになる
const openai = new OpenAI({ apiKey: process.env.NEXT_PUBLIC_OPENAI_KEY });

// OK: NEXT_PUBLIC_ を付けない変数はサーバーサイドのみで参照可能
// pages/api/chat.ts または app/api/chat/route.ts でのみ参照
const openai = new OpenAI({ apiKey: process.env.OPENAI_KEY });
```

ブラウザの DevTools → Network タブ → Request Headers を確認し、API キーが漏れていないかを必ず目視確認する。

---

## 「AI は秒でシステムを作れる、でも……」

ツイートの締めくくりはこうだ。

> 「AI はそのシステムを秒で作れる。でもセキュリティとプライバシーの壁を立てずに『シェア』ボタンを押したら……合掌。  
> 出来上がったのは『プロダクト』じゃなく、爆発寸前の法的時限爆弾だ。気をつけて」

バイブコーディングは**プロトタイプ作成の速度を劇的に上げる**。しかしリリース後に法的・セキュリティ的な問題が発覚すると、信頼の回復コストは開発コストの何倍にもなる。

---

## まとめ

| チェック項目 | ツール例 |
|---|---|
| SQL インジェクション / XSS スキャン | OWASP ZAP、Semgrep |
| `.env` 漏洩防止 | git-secrets、truffleHog |
| プライバシーポリシー整備 | 弁護士レビュー必須 |
| レートリミット設定 | slowapi、Cloudflare、API Gateway |
| API キーのサーバーサイド隔離 | Next.js API Routes、Backend Proxy |

AIがコードを書く時代だからこそ、**人間が「退屈なセキュリティ」に責任を持つ**必要がある。本番公開の前に、このリストを一度通しで確認してほしい。
