---
title: "大量保有報告書の「前」を検知する — EDINET API とニュース見出しでアクティビストの兆候を捕まえる"
date: 2026-08-05
lastmod: 2026-08-05
slug: "activist-signal-news-detection"
draft: false
categories: ["ビジネス/キャリア"]
tags: ["株式投資", "アクティビスト", "大量保有報告書", "EDINET", "日経テレコン"]
description: "アクティビストの買い集めは 5% を超えるまで大量保有報告書に載らない。Google News RSS で見出しを集め、EDINET API v2 を「開示が無いこと」の確認に反転利用して 5% 未満の候補を絞る手順を、実測したノイズと日経テレコンの費用・規約まで含めて解説します。"
---

アクティビスト（物言う株主）の動きを早く知りたい、という要求に対して最初に出てくる答えは EDINET の大量保有報告書です。無料で、構造化されていて、報告義務ベースなので漏れがない。EDINET・J-Quants・RSS を機械可読性で 3 層に整理した話は [Claude Code で株式ニュース分析を自動化する](/blogs/posts/2026/07/claude-code-stock-news-automation/) に書きました。

ただし大量保有報告書は **すべて事後** です。保有比率が 5% を超えるまで報告義務は発生せず、超えてからも提出まで数営業日の猶予があります。つまり **買い集めの最も美味しい局面は、制度開示のどこにも存在しません**。ここを捕まえたいなら、情報源は取材ベースの報道 —— 現実には日経のスクープ —— しかありません。

一方で日経の記事本文は機械処理できません。[コンテンツ利用規定](https://www.nikkei.com/info/copyright.html)がスクレイピング・テキストマイニング・生成AI利用を三重に禁止しています。課金で解決する話ではありません。

この記事では、**本文を一切機械に入れずに、見出しだけで兆候アラートを成立させる**パイプラインを設計します。

- **入力**: Google News RSS の見出しのみ（本文は扱わない）
- **出力**: 「報道はあるが EDINET に開示が無い」ファンド × 銘柄の日次アラート
- **前提**: Python と無料 API のみ、1 日 1 回のバッチ、検知部分は実質 0 円

実際に叩いて出てきたノイズの中身と、それをどう落とすかまで含めて具体的に書きます。

> 本記事は投資判断の推奨ではありません。また法令・規約の解釈については専門家によるものではない整理です。実運用に載せるなら弁護士の確認が必要です。

## 兆候はどの時点に存在するのか

まず「兆候」がどこにあるのかを時間軸で確定させます。ここを曖昧にしたまま実装に入ると、必ず事後データを掴んで満足して終わります。

![アクティビストの買い集めから義務開示までの時間軸を示した図。保有1〜4%の買い集め開始から日経の観測記事、5%到達、EDINETへの大量保有報告書提出までの流れを一本の矢印で表し、5%到達までは制度開示に存在しない領域であること、その区間で検知できるのはニュース見出しだけであることを示している](/blogs/images/activist-signal-timeline.png)

### 大量保有報告書とは — 5% ルールと提出期限

上場会社の株式等の保有割合が **5% を超えた**とき、その保有者には大量保有報告書の提出義務が生じます。提出期限は義務発生日の**翌日起算 5 営業日以内**。提出後も保有割合が **1% 以上増減**するたびに変更報告書が必要です。

アクティビストの積み増しを追うなら、新規の大量保有報告書より**変更報告書のほうが本体**になります。そして最も効くシグナルは保有目的欄の「重要提案行為を行うことを保有の目的とする」という文言です。

なお 2026 年 5 月 1 日施行の制度改正で、現金決済型デリバティブが報告対象に追加されました。株式を持たずスワップでエクスポージャーを積む手口が見えるようになったので、検知側には有利な変更です。逆に協働エンゲージメント特例により、一定要件下で機関投資家が共同保有者から除外されるため、合算されず検知しにくくなるケースも増えます。

### EDINET と日経の非対称

| | EDINET | 日経（報道） |
| --- | --- | --- |
| 収録の根拠 | **報告義務**（5% 超、以後 1% 変動） | **取材** |
| 網羅性 | 100%。義務なので漏れない | 低い。書かれなければ存在しない |
| 適時性 | 5% 到達後、翌日起算 5 営業日以内 | **5% 到達前に出ることがある** |
| 機械可読性 | 構造化・無料 API | なし（見出しのみ間接的に取得可） |
| 検証可能性 | バックテスト可 | **不可** |

**EDINET は「遅いが漏れない」、日経は「早いが漏れる」。** この非対称そのものがシグナルになります。検知したい状態はこう定義できます。

> ある「ファンド × 銘柄」のペアについて、**報道は出ているのに EDINET にはまだ大量保有報告書が無い**

本記事ではこの状態を **候補（candidate）**、候補がスコア閾値を超えたものを **アラート** と呼びます。

### EDINET の使い方を反転させる

EDINET を起点にすると、取れるのは定義上「開示済みのもの」だけです。どれだけ高速にポーリングしても 5 営業日前に遡ることはできません。

そこで **シグナル源ではなく「まだ開示が無いこと」を確認するフィルタとして使います。** 存在の検出ではなく不在の検出に使うわけです。この一点から、あとの実装はほぼ導かれます。

## 仕組みの全体像

![ニュース見出しからアクティビストの兆候を検知するパイプラインを6段階で示した図。収集、同名衝突の除去、事後記事の除去、EDINETを反転利用した兆候判定、出来高による裏付けとアラート、人間による読解と構造化の各段階について、実装内容と実測でわかった落とし穴を3列で対比している](/blogs/images/activist-signal-pipeline.png)

機械が担うのは ① から ⑤ まで、すべて無料で完結します。⑥ だけが人間の作業として残り、ここが日経の窓口になります。

## ① 収集 — Google News RSS × ファンド名辞書

日経電子版本体に公式 RSS はありません（`https://www.nikkei.com/rss/index.rdf` は 404 を実測）。見出しを取る現実的なルートは Google News RSS です。

実装上のポイントは 2 つ。**辞書を 3 件ずつに分割**して投げること、そして**金融文脈語を AND で足す**こと。どちらも実測に基づく判断で、理由はコードの後に書きます。

```python
"""collect.py — Google News RSS からアクティビスト関連の見出しを集める"""
import html
import re
import urllib.parse
import urllib.request

GNEWS = "https://news.google.com/rss/search?q={q}&hl=ja&gl=JP&ceid=JP:ja"

# 日本で実際に活動が観測されているファンド名。運用しながら育てる前提の辞書
FUNDS = [
    "オアシス・マネジメント",
    "ストラテジックキャピタル",
    "シティインデックスイレブンス",
    "3Dインベストメント",
    "ダルトン・インベストメンツ",
    "エリオット・マネジメント",
    "パリサー・キャピタル",
    "タイヨウ・パシフィック",
    "ValueAct",
    "ミョウジョウ・アセット",
]

# Google 側に渡す文脈語。取りこぼしを避けるため、ここは広めにしておく
QUERY_CONTEXT = ["株", "保有", "株主", "提案", "議決権", "買い増し", "書簡"]


def build_queries(funds, batch=3, days=14):
    """辞書を分割して投げる。1 クエリの返却上限に当たるため"""
    ctx = " OR ".join(QUERY_CONTEXT)
    for i in range(0, len(funds), batch):
        names = " OR ".join(f'"{f}"' for f in funds[i:i + batch])
        yield f"({names}) ({ctx}) when:{days}d"


def fetch(query):
    url = GNEWS.format(q=urllib.parse.quote(query))
    req = urllib.request.Request(url, headers={"User-Agent": "activist-signal/1.0"})
    xml = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")

    items = []
    for m in re.finditer(r"<item>(.*?)</item>", xml, re.S):
        block = m.group(1)
        src = re.search(r"<source[^>]*>(.*?)</source>", block, re.S)
        items.append({
            "title": html.unescape(re.search(r"<title>(.*?)</title>", block, re.S).group(1)),
            "link": re.search(r"<link>(.*?)</link>", block, re.S).group(1),
            "pub_date": re.search(r"<pubDate>(.*?)</pubDate>", block, re.S).group(1),
            "source": html.unescape(src.group(1)) if src else "",
        })
    return items


def collect(funds=FUNDS):
    seen, out = set(), []
    for q in build_queries(funds):
        for item in fetch(q):
            if item["link"] in seen:
                continue
            seen.add(item["link"])
            out.append(item)
    return out
```

ファンド名 10 件を OR で連結した 1 クエリを投げると、**100 件ちょうど**で返ってきました。上限に張り付いているので、取りこぼしを避けるには分割が必要です。

## ② ファンド名の同名衝突（ラグビー選手・野球選手）を落とす

**カタカナ姓のファンド名は単独では使い物になりません。** 試した範囲での差は劇的でした。

| クエリ | 件数 | 中身 |
| --- | --- | --- |
| `"ダルトン" when:14d` | 53 件 | ラグビー選手、MLB の選手記事が大量に混入 |
| `("ダルトン" OR "エリオット") (株主 OR 保有 OR 提案) when:14d` | 19 件 | 栄研化学の株主提案、日経の対抗策記事など、狙った記事が上位 |

単独で引いたときに上位を占めたのは次のようなものです。

- 「ダルトン」→ コベルコ神戸スティーラーズに加入したラグビー選手
- 「エリオット」→ 栃木県民球団の選手名フェイスタオル

Google News の `q` は括弧と暗黙 AND を受け付けるので、文脈語との AND で大半は落ちます。ただし Google 側の AND は本文も見るため厳密ではありません。実際、無関係な銘柄の続伸記事が混ざるのを確認しました。**見出しの文字列に対してローカルでもう一度絞る**のが確実です。

```python
"""filter_noise.py"""
FUND_ALIASES = {
    "オアシス・マネジメント": ["オアシス・マネジメント", "オアシス"],
    "ダルトン・インベストメンツ": ["ダルトン・インベストメンツ", "ダルトン"],
    # 短い別名は誤検出のもとなので、下の LOCAL_CONTEXT 併用が前提
}

# ローカル側は Google 側より語を足して厳しく判定する
# （Google 側で絞りすぎると取りこぼすので、役割を分けている）
LOCAL_CONTEXT = QUERY_CONTEXT + ["投資", "ファンド"]


def match_fund(title):
    """見出しの中にファンド名と金融文脈語が同時に現れるものだけ通す"""
    if not any(w in title for w in LOCAL_CONTEXT):
        return None
    for canonical, aliases in FUND_ALIASES.items():
        if any(a in title for a in aliases):
            return canonical
    return None
```

## ③ 大量保有報告書から自動生成された事後記事を落とす — ここが最重要

実測でいちばん驚いたのはここです。ファンド名で引いたヒットの**大半が、EDINET の開示から機械的に自動生成された記事**でした。以降これを **事後記事** と呼びます。

```text
ニッコンＨＤ、オアシス・マネジメントの保有割合が１７．６７％に上昇 速報 - kabushiki.jp
日本紙について、シティインデックスイレブンスは保有割合が増加したと報告 [変更報告書No.4] - 株探
Ａ＆Ｄホロン－大幅に4日続伸 ストラテジックキャピタルが同社株買い増し 保有割合15.01％→15.72％ - トレーダーズ・ウェブ
大量保有報告書 提出者：株式会社グローイングアップ：日経会社情報DIGITAL - 日本経済新聞
```

これらは株探・kabushiki.jp・トレーダーズ・ウェブ・日経会社情報DIGITAL が EDINET を読んで生成したものです。**情報として正しいがすべて事後**であり、兆候検知の観点では全部ノイズです。しかも件数が多いので、放置するとアラートがこれで埋まります。

「アクティビスト」という単語で引くのも同様に筋が悪く、「デンマークの家具アクティビスト」のような別語義の記事まで拾いました。

```python
"""filter_disclosure.py — EDINET 由来の事後記事を落とす"""
import re

# 開示の機械的な言い換えに特徴的な定型句
DISCLOSURE_PATTERNS = [
    r"変更報告書\s*No\.?\d+",
    r"大量保有報告書\s*提出者",
    r"訂正報告書",
    r"保有割合が[\d．\.]+[%％]に(上昇|低下)",
    r"保有割合が(増加|減少)したと報告",
    r"[\d．\.]+[%％]\s*→\s*[\d．\.]+[%％]",
]

# 開示転載を主業務とする配信元
DISCLOSURE_SOURCES = ["kabushiki.jp", "株探", "moomoo", "日経会社情報DIGITAL", "ｄメニューニュース"]


def is_post_disclosure(item):
    title = item["title"]
    if any(re.search(p, title) for p in DISCLOSURE_PATTERNS):
        return True
    return any(s in item["source"] or s in title for s in DISCLOSURE_SOURCES)
```

このフィルタを通して初めて、観測記事（＝取材ベースの記事）が残ります。実測した 2 週間のウィンドウで残ったのは次の 3 本でした。

- ダイヤモンド・オンライン「ダルトンの株主提案が可決寸前で『首の皮一枚』なヘルスケア企業の実名」
- 月刊 FACTA「ダルトンらのおもちゃと化す『栄研化学』」
- 日本経済新聞「大量買い付け対抗策、3社可決 アクティビスト過激主張に株主『ノー』」

## ④ EDINET API v2 で提出状況を引く — 「開示が無いこと」の確認に反転利用する

残った「ファンド × 銘柄」ペアについて、EDINET に大量保有報告書が無いことを確認します。

XBRL 本体のパースについては [EDINET XBRL を Python で扱う](/blogs/posts/2026/04/edinet-xbrl-python/) に書きました。本節は**書類一覧 API のメタデータだけ**を使います。

### docTypeCode 350 / 360 と変更報告書の判別

書類種別コードは公式の [EDINET API 仕様書（Version 2）](https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/download/ESE140206.pdf)で確認済みです。

| コード | 名称 |
| --- | --- |
| **350** | 大量保有報告書 |
| **360** | 訂正大量保有報告書 |
| 240 / 250 | 公開買付届出書 / 訂正公開買付届出書 |
| 290 | 意見表明報告書 |

**変更報告書に独立したコードはありません。** 新規か変更かは `docDescription`（提出書類概要）の文字列で判別します。アクティビストの積み増しを追うなら変更報告書のほうが本体なので、ここは落とせません。

### secCode は提出者のコード — issuerEdinetCode で対象銘柄を特定する

コードを書く前に、いちばん引っかかりやすい点を先に書きます。

**`secCode` は提出者の証券コードです。** 仕様書の項目 15 に「提出者の証券コードが出力されます」とあります。大量保有報告書の提出者はファンドなので、多くの場合 `null` になります。**買われている側の銘柄コードは `secCode` からは取れません。**

対象企業を特定するには `issuerEdinetCode`（項目 26：「大量保有について発行会社の EDINET コードが出力されます」）を使います。だからコードはこうなります。

```python
"""edinet.py — 大量保有報告書の提出状況を引く"""
import os
import requests

ENDPOINT = "https://api.edinet-fsa.go.jp/api/v2/documents.json"
LARGE_HOLDING = ("350", "360")


def list_docs(date):
    """date: 'YYYY-MM-DD'。Subscription-Key は必須（無いと 401 が返る）"""
    res = requests.get(ENDPOINT, params={
        "date": date,
        "type": 2,  # 提出書類一覧 + メタデータ
        "Subscription-Key": os.environ["EDINET_API_KEY"],
    }, timeout=30)
    res.raise_for_status()
    return res.json().get("results", [])


def large_holdings(date):
    for d in list_docs(date):
        if d.get("docTypeCode") not in LARGE_HOLDING:
            continue
        yield {
            "doc_id": d["docID"],
            "filer": d.get("filerName"),               # 提出者＝ファンド側
            "issuer_code": d.get("issuerEdinetCode"),  # 発行会社＝買われている側
            "description": d.get("docDescription"),
            "submitted": d.get("submitDateTime"),
            "is_amendment": "変更報告書" in (d.get("docDescription") or ""),
        }
```

EDINET コードを銘柄コードに変換する対応表は、仕様書に記載のある配布 URL から取れます。

```bash
curl -o Edinetcode.zip https://disclosure2dl.edinet-fsa.go.jp/searchdocument/codelist/Edinetcode.zip
```

CSV は cp932 で、1 行目がダウンロード日と件数のメタ行、2 行目がヘッダという構造です。ヘッダ行を探してから読む必要があります。

```python
"""codelist.py — EDINET コード → 証券コードの対応表を作る"""
import csv
import io
import zipfile


def load_edinet_code_map(zip_path="Edinetcode.zip"):
    with zipfile.ZipFile(zip_path) as z:
        name = next(n for n in z.namelist() if n.lower().endswith(".csv"))
        raw = z.read(name).decode("cp932")

    lines = raw.splitlines()
    start = next(i for i, line in enumerate(lines) if "ＥＤＩＮＥＴコード" in line)
    reader = csv.DictReader(io.StringIO("\n".join(lines[start:])))

    out = {}
    for row in reader:
        code = (row.get("証券コード") or "").strip()
        edinet = (row.get("ＥＤＩＮＥＴコード") or "").strip()
        if edinet and code:
            out[edinet] = code[:4]  # 5 桁表記なので上 4 桁が銘柄コード
    return out
```

**報道側は銘柄コード、EDINET 側は EDINET コードで出てくるので、この対応表で揃えてから集合演算します。**

```python
def build_disclosed_pairs(dates, code_map):
    """過去 N 日の EDINET から {(ファンド名, 銘柄コード)} を作る"""
    pairs = set()
    for date in dates:
        for doc in large_holdings(date):
            ticker = code_map.get(doc["issuer_code"] or "")
            if ticker:
                pairs.add((doc["filer"], ticker))
    return pairs


def classify(pair, disclosed_pairs):
    if (pair.fund, pair.ticker) in disclosed_pairs:
        return "known"      # 開示済み。兆候ではなく既知の事実
    return "candidate"      # 報道はあるが開示が無い → 5% 未満の候補
```

ファンド名は報道と EDINET の提出者名で表記が揺れるので、`FUND_ALIASES` を使って正規化してから突き合わせます。

### 観測記事の語彙で加点する

「開示が無い」だけでは、単なる論評記事も候補に入ってしまいます。日経が義務開示より前に書くときには定型があるので、それをスコアに使います。一次ソースと二次ソースの切り分けという考え方は [「悪材料出尽くし（アク抜け）」の見抜き方](/blogs/posts/2026/07/news-analysis-stock-rebound/) に整理しています。

```python
OBSERVATION_LEXICON = {
    # 未確定情報を示す取材記事の定型（強い）
    "関係者によると": 3, "関係者への取材": 3, "複数の関係者": 3,
    "方針を固めた": 3, "検討している": 2, "協議している": 2,
    # 具体的な行動（強い）
    "書簡を送": 3, "株主提案": 2, "大株主に浮上": 3, "買い増し": 2,
    "株式を取得": 2, "資本政策": 1, "対話を要求": 2,
    # 事後・論評寄り（弱い、あるいは減点対象）
    "解説": -1, "識者": -1, "まとめ": -1,
}


def observation_score(title):
    return sum(w for k, w in OBSERVATION_LEXICON.items() if k in title)
```

「関係者によると」は、報告義務が発生していない段階の情報であることを示すほぼ確実なマーカーです。最も加点すべきパターンになります。

### 米系ファンドの場合は SEC EDGAR も使える

米系ファンドが絡む場合は SEC EDGAR の全文検索が無料で使えます。

- エンドポイント: `https://efts.sec.gov/LATEST/search-index`（`forms=SC 13D` などを指定）
- 認証: 不要
- 必須: User-Agent に連絡先を入れること
- レート制限: 10 req/s（全 EDGAR API 共通）

## ⑤ 出来高の急増で裏付ける — J-Quants 無料プランは12週遅延で使えない

買い集めが進行中なら出来高に痕跡が出ます。ただし JPX 公式の株価データ API である **J-Quants の無料プランは 12 週遅延**なので、リアルタイムの裏付けには使えません（この制約は [Claude Code で株式ニュース分析を自動化する](/blogs/posts/2026/07/claude-code-stock-news-automation/) に詳しく書きました）。有料プランが必要です。無料で回すなら、この段は「あれば加点」の任意項目にします。

```python
import statistics


def volume_zscore(volumes, window=60):
    """直近の出来高が過去 window 日に対して何σ上振れているか"""
    hist = volumes[-(window + 1):-1]
    if len(hist) < 20:
        return 0.0
    sd = statistics.pstdev(hist)
    return 0.0 if sd == 0 else (volumes[-1] - statistics.fmean(hist)) / sd
```

立会外取引（ToSTNeT）の大口約定も同じ位置づけです。**「誰が買っているか」はわからないが「異常な買いが入った」ことはわかる**ので、報道と組み合わせたときだけ意味を持ちます。出来高と相対力から「本物度」を確認する手法は [セクターローテーションは株価・出来高で予測できるか](/blogs/posts/2026/07/sector-rotation-detection-price-volume/) に書きました。

ここまでで機械が出す成果物はこうなります。

```json
{
  "ticker": "4549",
  "company": "栄研化学",
  "fund": "ダルトン・インベストメンツ",
  "status": "candidate",
  "edinet_350": false,
  "observation_score": 5,
  "volume_z": 2.3,
  "headline": "ダルトンらのおもちゃと化す「栄研化学」",
  "source": "月刊FACTA",
  "url": "https://...",
  "pub_date": "2026-07-23"
}
```

**`edinet_350: false` と `status: candidate` の組み合わせが、この仕組みが探しているものそのものです。** 人間はここから先を受け取ります。

## ⑥ 人間が読んで構造化する

### 日経のどの窓口を使うか

アラートが立ったら本文を読みます。**この工程を機械にやらせないことが、この設計の前提そのもの**です。窓口には選択肢があります。

| ルート | 費用 | 向き／制約 |
| --- | --- | --- |
| [日経テレコン（楽天証券版）](https://www.rakuten-sec.co.jp/web/service/investment/nikkei.html) | **0 円**（口座が必要） | 直近 3 日分の紙面＋過去 1 年のキーワード検索。iSPEED / マーケットスピード内のみでブラウザ直アクセス不可 |
| [日経電子版 個人プラン](https://www.nikkei.com/help/subscribe/price/plan.html) | 4,277 円/月 | 速報を読むには十分。過去記事の網羅的な検索は弱い |
| [日経テレコン 正規契約](https://telecom.nikkei.co.jp/price/) | 基本料 1 ID 6,000〜8,000 円/月＋[本文 75〜200 円/本](https://telecom.nikkei.co.jp/price/usage/)（中心価格帯・税抜） | 500 超媒体の全文検索。**数年分のファンド行動履歴を遡るときだけ効く** |

**アラート後に読むのは「今週立った記事」なので、楽天証券版の直近 3 日分で足ります。** つまりこの仕組みを回すのにテレコンの正規契約は必須ではありません。正規契約が効くのは「このファンドは過去 5 年でどの銘柄に何を要求してきたか」を洗う場面で、これは日次パイプラインの外側にある任意の背景調査です。

### 読んだ結果だけを YAML でデータにする

書き出すのは、**記事の要約ではなく事実の骨だけ**です。日経コンテンツを生成AIの参照データにしないための線引きです。

```yaml
# signals/2026-08-05.yaml
- ticker: "4549"
  company: "栄研化学"
  fund: "ダルトン・インベストメンツ"
  stake_pct: null          # 未開示なので不明。これが 5% 未満候補の証拠
  action: "株主提案"
  demand: "取締役選任"
  source: "月刊FACTA 2026-07-23"
  edinet_350: false        # ④ の判定結果
  observation_score: 5
  read_by_human: true
  note: "可決寸前との報道。会社側の対抗策の有無を次に確認する"
```

以降は EDINET の変更報告書を自動追跡して、実際に 5% を超えてきたかどうかで答え合わせをします。

## 正規サービスで機械化する場合の選択肢

キーワード監視を正規のサービスに任せる道もありますが、個人には現実的ではありません。

[日経スマートクリップ](https://telecom.nikkei.co.jp/guide/relevance/smart/)は著作権クリア済みの自動クリッピングで、毎日定刻の自動送信とメールアラートに対応しています。ただし[料金](https://www.nks.co.jp/project/smart/price/index.html)は日経各紙のみで月額 **83,000 円から**、全国紙＋Web ニュース込みで基本料 **396,000 円から**（いずれも税別）。しかも[機能一覧](https://telecom.nikkei.co.jp/guide/relevance/smart/function/)にあるのはメール・PDF・社内システム連携で、**API や CSV での機械可読提供の記載はありません**。あくまで人間に配信するサービスです。

記事本文を正規に機械処理したいなら次の 3 ルートになります。

| ルート | 内容 |
| --- | --- |
| [NIKKEI KAI](https://nkbb.nikkei.co.jp/kai/) | 生成AI用途の公式ルート。KAI Agent は「外部システムから回答を呼び出せる API に対応します」と明記。利用人数に応じた月額固定料金 |
| [日経APIソリューションズ](https://nkbb.nikkei.co.jp/api/) | 記事・企業情報・マーケット情報の API 配信。料金・技術仕様とも非公開で要問い合わせ |
| 別途の有償利用許諾契約 | テレコンのサポート告知（2023 年 9 月 11 日改定）によると、日経提供コンテンツに限り、別途有償の利用許諾契約を前提に生成AIへのコンテンツ投入を例外的に認める場合がある |

## 日次バッチで回す

```bash
#!/usr/bin/env bash
# daily.sh — 1 日 1 回、寄り前に回す
set -euo pipefail

python -m activist.collect            > work/raw.json
python -m activist.filter_noise       < work/raw.json > work/matched.json
python -m activist.filter_disclosure  < work/matched.json > work/observations.json
python -m activist.edinet_check       < work/observations.json > work/candidates.json
python -m activist.score              < work/candidates.json > work/alerts.json
python -m activist.notify             < work/alerts.json
```

本文に載せたのは判定ロジックの中核だけで、各モジュールの `__main__` と stdin/stdout のグルーは省略しています。

EDINET コードリストは日次で更新されますが、新規上場やコード変更の頻度は低いので週 1 回の取り直しで足ります。Google News RSS は非公式ルートなので、`when:` の挙動や返却件数が変わることを前提に、**件数が急に 0 になったら気づける監視**を入れておきます。

## この仕組みの限界 — バックテスト不可、recall が低い

用途を決める前に確認すべき構造的な限界が 2 つあります。

**1. バックテストができない。** 過去のスクープを機械可読で揃えられません。テレコンの本文は 75〜200 円/本の従量課金なので、履歴を数百件集めるのは非現実的です。検証できないシグナルを売買ロジックに埋めると、後から効いていたのか判定できなくなります。**アラート層に留めるのが正しい扱い**で、自動売買のトリガーにはできません。

**2. recall（再現率＝取りこぼしの少なさ）が低い。** 日経が書かなければ兆候は存在しません。網羅性を求める用途には原理的に向きません。最終的な補足は EDINET 側、つまり「遅いが漏れないほう」で取る前提になります。

## 法務上の前提 — 見出しだけで済ませる理由

なぜ本文を機械に入れない設計にしたのか、根拠を整理しておきます。

**見出し利用も完全な安全圏ではありません。** YOL 事件（知財高裁 平成 17 年 10 月 6 日判決、平成 17 年（ネ）第 10049 号。[判決要旨 PDF](https://www.courts.go.jp/assets/hanrei/hanrei-point_pdf-9350.pdf)）は、記事見出しの著作物性を否定した上で、**無断配信について不法行為責任を肯定**しました。「見出しに創作性はないから自由」という発想はこの判例で封じられています。Google の配信を購読する形なので日経のサイトを巡回してはいない、という違いはありますが、見出しを蓄積して DB 化する方向はグレーです。

**本文の機械処理は形態素解析でも通りません。** 著作権法 30 条の 4 は情報解析目的の利用を認めていますが、但書は「著作権者の利益を不当に害することとなる場合」を除外しています。文化庁の「[AI と著作権に関する考え方について](https://www.bunka.go.jp/seisaku/bunkashingikai/chosakuken/pdf/94057901_01.pdf)」には、該当例が明記されています。

> 情報解析用に販売されているデータベースの著作物を、有償で利用することなく情報解析目的で複製する行為

日経は日経APIソリューションズ・日経オルタナティブデータ・NIKKEI KAI というライセンス市場を現に持っているため、ここに正面から当たります。加えて利用規定は「データマイニング、テキストマイニング」を名指しで禁止し、自動化された手段による取得を保存・キャッシュを含めて禁じています。**生成AIを避けても、取得の時点で止まります。**

## コスト構成 — 検知パイプラインは実質 0 円

| 段 | 手段 | 費用 |
| --- | --- | --- |
| ① 収集 | Google News RSS | 0 円 |
| ② ③ フィルタ | ローカル処理 | 0 円 |
| ④ 兆候判定 | EDINET API v2（要キー・無料） | 0 円 |
| ⑤ 裏付け | J-Quants 無料プラン | 0 円（ただし 12 週遅延で実質使えない） |
| ⑤ 裏付け（実用） | J-Quants 有料プラン | 有料 |
| ⑥ 読解 | 楽天証券版テレコン | 0 円（口座が必要） |
| ⑥ 読解（強化） | 日経電子版 | 4,277 円/月 |

金がかかるのは「読む」工程と、リアルタイムの株価データだけです。

## よくある疑問

### EDINET でアクティビストの動きを事前に知れるか

知れません。EDINET は報告義務ベースなので、収録されるのは 5% を超えた後のものだけです。構造的に事後であり、ポーリング間隔を詰めても解決しません。だから本記事では「開示が無いこと」の確認に反転利用しています。

### 日経テレコンを正規契約すれば Claude Code から記事検索できるか

**できません。** テレコンはブラウザの検索 UI で、契約者向けの公開 API がありません。加えてオンライン契約の[利用規約](https://telecom.nikkei.co.jp/credit/terms/)第 7 条 3 項 (5) が次を禁止しています。

> 本サービスで提供される情報を生成ＡＩ等（人工知能、ＲＰＡ、ロボット、プログラム、ソフトウエア等を含むがこれに限られない）に入力したり学習させたり解析・加工させたりすること

**「プログラム、ソフトウエア等を含む」** が決定的です。生成AIかどうかを問わず、プログラムに情報を入力する行為そのものが禁止対象なので、Claude Code から扱うのは正面からここに当たります。自動ログインしてスクレイピングする形なら「自動化された手段による取得」にも当たります。

正規に機械化したいなら NIKKEI KAI か日経APIソリューションズ、または営業経由の個別の有償利用許諾契約です。**テレコン正規契約は「人間が読む権利」を買うものであって、機械に読ませる権利ではありません。**

### 日経テレコンは無料で使えるか

楽天証券版が 0 円で使えます（口座が必要）。日経朝夕刊・日経産業新聞・日経MJ と速報が対象で、直近 3 日分の紙面と過去 1 年のキーワード検索が可能です。ただし iSPEED / マーケットスピード内からのみで、ブラウザ直アクセスはできません。

## まとめ

- アクティビストの買い集めは 5% を超えるまで制度開示に存在しない。**兆候をニュースから取るのは選択ではなく必然**
- EDINET を主シグナルに置くと事後しか取れない。**「まだ開示が無いこと」の確認に反転利用する**
- ファンド名だけで引くと同名衝突（ラグビー選手・野球選手）で埋まる。金融文脈語との AND が必須
- 最大のノイズは**開示から自動生成された事後記事**。株探・kabushiki.jp・日経会社情報DIGITAL の定型句を落として初めて観測記事が残る
- `secCode` は提出者のコード。買われている側は `issuerEdinetCode` から EDINET コードリスト経由で引く
- 日経本文は機械に入れない。**検知は機械、読解は人間**の分離が規約上の前提であり、テレコン正規契約は必須ではない
- バックテスト不可なのでアラート層に留める。売買の自動トリガーにはしない

関連記事:

- [Claude Code で株式ニュース分析を自動化する](/blogs/posts/2026/07/claude-code-stock-news-automation/) — EDINET・J-Quants・RSS を機械可読性で 3 層に整理した、本記事の前提になる記事
- [「悪材料出尽くし（アク抜け）」の見抜き方](/blogs/posts/2026/07/news-analysis-stock-rebound/) — 一次ソースと二次ソースの切り分け、ニュース分析の 4 ステップ
- [株価が上昇に転じる兆候](/blogs/posts/2026/08/stock-turnaround-signals/) — 銘柄分類ごとの先行指標。アクティビストの登場をカタリストの一例として扱っている
- [EDINET XBRL を Python で扱う](/blogs/posts/2026/04/edinet-xbrl-python/) — 書類取得と XBRL パースの基本
