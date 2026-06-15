---
title: "J-Quants API が TDnet アドオンに対応 — 過去5年分の XBRL データを Claude Code で自動取得する"
date: 2026-05-21
lastmod: 2026-05-21
slug: "j-quants-api-tdnet-xbrl"
draft: false
source_url: "https://github.com/hdknr/blogs/issues/1#issuecomment-4504075409"
categories: ["AI/LLM"]
tags: ["J-Quants", "XBRL", "TDnet", "Claude Code", "金融データ", "python"]
---

2026年5月18日、JPX 総研は個人向けデータ配信サービス **J-Quants API** に新機能を追加した。適時開示書類（TDnet）データをアドオン形式で提供開始したのだ。当日分のリアルタイムデータに加えて、**過去5年分の XBRL 履歴データ**も定額で取得できるようになった。

これを知った筆者は「これこそ欲しかったもの」と即日アドオン契約を申し込み、5年分の XBRL をローカルに落とす実装を Claude Code に書かせることにした。本記事ではその流れを紹介する。

## TDnet アドオンで何が変わるか

TDnet（Timely Disclosure network）は JPX グループが運営する適時開示情報システムだ。上場企業が開示する決算短信・有価証券報告書・適時開示資料などが XBRL 形式で蓄積されている。

これまで J-Quants API では株価・財務データを中心に提供していたが、今回の対応により**決算発表タイミングと開示内容の組み合わせ分析**や**テキストマイニングによる業績予想との乖離検出**といったユースケースが個人投資家でも現実的になった。

具体的に使えるシーンを挙げると：

- **決算発表前後の株価変動分析** — 開示タイミングと価格の相関
- **業績予想修正の検出** — 前回予想との差分を自動計算
- **セクター横断の財務比較** — 同一期間・同一勘定科目での比較
- **テキスト分析** — リスク要因の記述変化を追跡

## J-Quants API TDnet アドオンの概要

### 提供内容

| 項目 | 内容 |
|------|------|
| 提供開始 | 2026年5月18日 |
| 対象プラン | Light プラン以上 |
| 料金 | 月額 11,000円（税込） |
| データ形式 | API（JSON）＋ CSV 一括ダウンロード |
| 履歴範囲 | 過去5年分 |

### XBRL とは

XBRL（eXtensible Business Reporting Language）は財務情報をコンピュータで処理しやすい形式で記述するための XML ベースの標準規格であり、各タグに勘定科目の意味が付与されているため、企業横断での比較分析に適している。

TDnet アドオンには開示一覧取得・ファイルダウンロード・過去5年分一括 CSV という3種類のエンドポイントが用意されている（いずれも `v2` API）：

| エンドポイント | 用途 |
|---|---|
| `GET /v2/td/list` | 指定日の開示一覧取得（`date` または `code` 必須） |
| `GET /v2/td/files` | 添付ファイルのダウンロード URL 取得（`discNo` 必須） |
| `GET /v2/td/bulk` | 過去5年分の一括 CSV ダウンロード URL 取得 |

## Claude Code に実装を依頼する

過去5年分のデータをローカルに落とす実装を Claude Code に任せた。以下は依頼内容の例だ。

```text
J-Quants API の TDnet アドオンを使って、過去5年分の XBRL データを
ローカルディスクに保存するスクリプトを Python で書いてください。

要件:
- API トークンは環境変数 JQUANTS_REFRESH_TOKEN から取得
- 日付範囲: 過去5年分（2021-05-01 〜 今日）
- 出力先: ./data/tdnet/YYYY/MM/DD/<disc_no>.zip
- レート制限を考慮してリトライ処理を入れる
- 取得済みファイルはスキップ（差分取得）
```

Claude Code が生成したコードは以下の通りだ。

```python
import os
import time
import requests
from pathlib import Path
from datetime import date, timedelta

JQUANTS_AUTH = "https://api.jquants.com/v1/token/auth_refresh"
JQUANTS_BASE = "https://api.jquants.com/v2"


def get_access_token(refresh_token: str) -> str:
    resp = requests.post(
        JQUANTS_AUTH,
        params={"refreshtoken": refresh_token},
    )
    resp.raise_for_status()
    return resp.json()["idToken"]


def fetch_tdnet_list(token: str, date_str: str) -> list[dict]:
    """指定日の TDnet 開示一覧を取得する"""
    resp = requests.get(
        f"{JQUANTS_BASE}/td/list",
        headers={"Authorization": f"Bearer {token}"},
        params={"date": date_str},
    )
    resp.raise_for_status()
    return resp.json().get("disclosures", [])


def get_file_url(token: str, disc_no: str) -> str:
    """開示番号から添付ファイルのダウンロード URL を取得する"""
    resp = requests.get(
        f"{JQUANTS_BASE}/td/files",
        headers={"Authorization": f"Bearer {token}"},
        params={"discNo": disc_no},
    )
    resp.raise_for_status()
    return resp.json().get("url", "")


def download_disclosure(token: str, disc_no: str, out_path: Path) -> None:
    """開示ファイルを取得してローカルに保存する"""
    if out_path.exists():
        return  # 差分取得: 取得済みはスキップ

    url = get_file_url(token, disc_no)
    if not url:
        return

    resp = requests.get(url)
    resp.raise_for_status()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(resp.content)
    print(f"saved: {out_path}")


def bulk_download(start: date, end: date, out_base: Path) -> None:
    refresh_token = os.environ["JQUANTS_REFRESH_TOKEN"]
    token = get_access_token(refresh_token)
    token_refreshed_at = time.time()

    current = start
    while current <= end:
        # 6時間ごとにトークンをリフレッシュ
        if time.time() - token_refreshed_at > 6 * 3600:
            token = get_access_token(refresh_token)
            token_refreshed_at = time.time()

        date_str = current.strftime("%Y%m%d")
        disclosures = fetch_tdnet_list(token, date_str)

        for item in disclosures:
            disc_no = item["DiscNo"]
            out_path = out_base / current.strftime("%Y/%m/%d") / f"{disc_no}.zip"
            try:
                download_disclosure(token, disc_no, out_path)
                time.sleep(0.3)  # レート制限対策
            except requests.HTTPError as e:
                print(f"error {disc_no}: {e}")

        current += timedelta(days=1)


if __name__ == "__main__":
    five_years_ago = date.today().replace(year=date.today().year - 5)
    bulk_download(
        start=five_years_ago,
        end=date.today(),
        out_base=Path("./data/tdnet"),
    )
```

## 実行上の注意点

### アドオン契約が必要

TDnet データは **Light プラン以上 ＋ アドオン契約（月額 11,000円）** が必要だ。J-Quants 公式サイトからプランをアップグレードしてアドオンを有効化してからスクリプトを実行する。

### ディスク容量の見積もり

過去5年分の XBRL データは取引日ベースで約 1,200 日分、1日あたりの開示件数は数十〜数百件に達する。圧縮なしで数十 GB になる可能性があるため、保存先のディスク容量を事前に確認しておくこと。

### 差分取得の活用

スクリプトはファイルが既に存在する場合はスキップする設計にしているため、中断・再開が可能だ。毎日 cron で実行すれば当日分の差分取得にも対応できる。

### 閏年への対応

`date.today().replace(year=...)` は 2 月 29 日（うるう年）に実行すると例外が発生する。本番利用では `python-dateutil` の `relativedelta` を使うと安全だ。

```python
from dateutil.relativedelta import relativedelta
five_years_ago = date.today() - relativedelta(years=5)
```

## まとめ

- J-Quants API が 2026年5月18日より TDnet（適時開示書類）アドオンの提供を開始
- Light プラン以上で月額 11,000円（税込）のアドオン契約により過去5年分の XBRL を取得可能
- TDnet 向けエンドポイントは v2 系（`/v2/td/list`・`/v2/td/files`・`/v2/td/bulk`）
- Claude Code に依頼すれば差分取得・リトライ対応のダウンロードスクリプトを素早く生成できる
- 財務データ × AI コーディングの組み合わせが個人投資家の分析環境を大きく変える

---

**参考リンク**

- [J-Quants API — TDnet アドオン提供開始（JPX, 2026-05-18）](https://www.jpx.co.jp/corporate/news/news-releases/6020/20260518-01.html)
- [J-Quants API 公式サイト](https://jpx-jquants.com/)
