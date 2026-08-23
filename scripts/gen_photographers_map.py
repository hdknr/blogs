#!/usr/bin/env python3
"""Generate the "photographers by era" map diagram as drawio XML.

Three parallel columns per era: Western art/press photography, advertising and
fashion photography, and Japan. The advertising column is separated on purpose
— the canon largely omits it, so putting it beside the art/press names is the
point of the figure. See
content/posts/2026/08/2026-08-23-photographers-by-era.md.

Chip layout is computed from the name lists, so adding a photographer means
editing ERAS and re-running; no mxCell geometry to hand-maintain.

Usage:
    python3 scripts/gen_photographers_map.py [--out PATH]

Then export the PNG the post references:
    /Applications/draw.io.app/Contents/MacOS/draw.io --export --format png --scale 2 \
        --output static/images/photographers-by-era-map.png \
        static/images/photographers-by-era-map.drawio
"""

import argparse
import html
from pathlib import Path

# (era label, years, west[], advertising[], japan[], fill, stroke)
ERAS = [
    (
        "I. 発明と定着", "1839〜1880年代",
        ["ダゲール", "タルボット", "ナダール", "J.M.キャメロン", "マイブリッジ"],
        ["ディスデリ", "M.ブレイディ", "（広告写真は網版の普及後）"],
        ["上野彦馬", "下岡蓮杖"],
        "#dae8fc", "#6c8ebf",
    ),
    (
        "II. 自立と職業化", "1890年代〜1930年代",
        ["スティーグリッツ", "ポール・ストランド", "E.ウェストン", "アンセル・アダムス",
         "I.カニンガム", "モホイ＝ナジ", "ザンダー"],
        ["スタイケン", "ド・メイヤー", "ホイニンゲン＝ヒューネ", "ホルスト",
         "セシル・ビートン", "マン・レイ"],
        ["野島康三", "中山岩太"],
        "#e1d5e7", "#9673a6",
    ),
    (
        "III. 記録・報道・宣伝", "1930年代〜1955",
        ["ドロシア・ラング", "ウォーカー・エヴァンズ", "ロバート・キャパ",
         "カルティエ＝ブレッソン", "W.ユージン・スミス"],
        ["バーク＝ホワイト", "ムンカーチ", "ブロドヴィッチ（AD）",
         "アーヴィング・ペン", "アヴェドン"],
        ["木村伊兵衛", "土門拳", "名取洋之助"],
        "#d5e8d4", "#82b366",
    ),
    (
        "IV. 主観への転回", "1958〜1970年代",
        ["ロバート・フランク", "ウィリアム・クライン", "ダイアン・アーバス",
         "フリードランダー", "ワイノグランド"],
        ["デヴィッド・ベイリー", "ドノヴァン", "ダフィー"],
        ["細江英公", "東松照明", "森山大道", "中平卓馬", "荒木経惟", "篠山紀信"],
        "#f8cecc", "#b85450",
    ),
    (
        "V. 即物性とカラー", "1963〜1981",
        ["エド・ルシェ", "ベッヒャー夫妻", "ロバート・アダムス", "ルイス・ボルツ",
         "★ エグルストン", "★ スティーブン・ショア"],
        ["ヘルムート・ニュートン", "ギイ・ブルダン"],
        ["（本記事の範囲外）"],
        "#ffe6cc", "#d79b00",
    ),
    (
        "VI. 美術としての写真", "1977〜1990年代",
        ["シンディ・シャーマン", "リチャード・プリンス", "ジェフ・ウォール",
         "ナン・ゴールディン", "グルスキー", "シュトゥルート", "ルフ", "ヘーファー"],
        ["ブルース・ウェバー", "ハーブ・リッツ", "トスカーニ", "レボヴィッツ"],
        ["杉本博司", "横須賀功光"],
        "#fff2cc", "#d6b656",
    ),
    (
        "VII. 脱物質化", "1990〜現在",
        ["アレック・ソス", "ヴォルフガング・ティルマンス"],
        ["コリンヌ・デイ", "ユルゲン・テラー", "ニック・ナイト"],
        ["ホンマタカシ", "川内倫子", "上田義彦", "藤井保"],
        "#f5f5f5", "#999999",
    ),
]

TITLE = "写真史の転換点と、それを担った写真家"
SUBTITLE = (
    "★ はニューカラーの中心人物（別記事で詳述）。"
    "広告・ファッションを独立した列にしたのは、正典がこの系列をほぼ省くため"
)
BAND = (
    "同じ時代に同じ技術で撮っていても、発注者が企業だと写真史の教科書に載らない。\n"
    "スタイケンはコンデナストの首席写真家、クラインは『The Americans』と同時期に『Vogue』、"
    "エヴァンズは 1945 年から『Fortune』の専属だった。"
)

# Column geometry: (x, width, chips per row, header label)
COLS = [
    (30, 180, 1, None),      # era label
    (222, 560, 3, "欧米（芸術・報道）"),
    (794, 420, 2, "広告・ファッション"),
    (1226, 400, 2, "日本"),
]
PAGE_W = 1656
CHIP_H = 34
CHIP_GAP = 8
ROW_PITCH = CHIP_H + CHIP_GAP
BAND_PAD_TOP = 12
BAND_PAD_BOTTOM = 12
ERA_GAP = 12
HEADER_Y = 76
FIRST_BAND_Y = 108


def build() -> str:
    lines: list[str] = []

    def cell(cid, value, style, x, y, w, h):
        # Escape first, then map real newlines onto drawio's line-break entity;
        # doing it the other way round would turn the entity's & into &amp;.
        text = html.escape(value).replace("\n", "&#10;")
        lines.append(
            f'        <mxCell id="{cid}" value="{text}" style="{style}" vertex="1" parent="1">'
        )
        lines.append(
            f'          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>'
        )
        lines.append("        </mxCell>")

    def rows_needed(names, per_row):
        return -(-len(names) // per_row) if names else 0

    # --- measure every band first so the page height is known up front
    band_heights = []
    for _, _, west, ads, jp, _, _ in ERAS:
        rows = max(
            rows_needed(west, COLS[1][2]),
            rows_needed(ads, COLS[2][2]),
            rows_needed(jp, COLS[3][2]),
        )
        band_heights.append(BAND_PAD_TOP + rows * ROW_PITCH - CHIP_GAP + BAND_PAD_BOTTOM)

    table_bottom = FIRST_BAND_Y + sum(band_heights) + ERA_GAP * (len(ERAS) - 1)
    band_y = table_bottom + 20
    page_h = band_y + 88

    lines.append('<mxfile host="app.diagrams.net" agent="Claude Code" version="26.0.0">')
    lines.append('  <diagram id="photographers-by-era" name="Photographers by Era">')
    lines.append(
        f'    <mxGraphModel dx="1200" dy="900" grid="1" gridSize="10" guides="1" tooltips="1"'
        f' connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{PAGE_W}"'
        f' pageHeight="{page_h}" math="0" shadow="0">'
    )
    lines.append("      <root>")
    lines.append('        <mxCell id="0"/>')
    lines.append('        <mxCell id="1" parent="0"/>')
    lines.append("")

    cell("ttl", TITLE,
         "text;html=1;align=center;verticalAlign=middle;whiteSpace=wrap;fontSize=19;"
         "fontStyle=1;fontColor=#333333;",
         (PAGE_W - 600) // 2, 16, 600, 30)
    cell("sub", SUBTITLE,
         "text;html=1;align=center;verticalAlign=middle;whiteSpace=wrap;fontSize=12;"
         "fontColor=#666666;",
         (PAGE_W - 1000) // 2, 46, 1000, 22)

    for ci, (cx, cw, _, label) in enumerate(COLS):
        if label:
            cell(f"h{ci}", label,
                 "text;html=1;align=center;verticalAlign=middle;whiteSpace=wrap;fontSize=13;"
                 "fontStyle=1;fontColor=#666666;",
                 cx, HEADER_Y, cw, 24)

    y = FIRST_BAND_Y
    for ei, (label, years, west, ads, jp, fill, stroke) in enumerate(ERAS):
        h = band_heights[ei]
        cell(f"e{ei}", f"{label}\n{years}",
             f"rounded=1;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;fontSize=12;"
             f"fontStyle=1;fillColor={fill};strokeColor={stroke};",
             COLS[0][0], y, COLS[0][1], h)

        for ci, (names, prefix) in enumerate(
            ((west, "w"), (ads, "a"), (jp, "j")), start=1
        ):
            cx, cw, per_row, _ = COLS[ci]
            cell(f"b{prefix}{ei}", "",
                 f"rounded=1;whiteSpace=wrap;html=1;verticalAlign=top;align=left;fontSize=13;"
                 f"dashed=1;dashPattern=6 4;fillColor={fill};strokeColor={stroke};opacity=45;",
                 cx, y, cw, h)

            inner_pad = 12
            chip_w = (cw - inner_pad * 2 - CHIP_GAP * (per_row - 1)) // per_row
            for ni, name in enumerate(names):
                r, c = divmod(ni, per_row)
                cell(f"{prefix}{ei}_{ni}", name,
                     "rounded=1;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;"
                     "fontSize=11;fillColor=#ffffff;strokeColor=" + stroke + ";",
                     cx + inner_pad + c * (chip_w + CHIP_GAP),
                     y + BAND_PAD_TOP + r * ROW_PITCH,
                     chip_w, CHIP_H)

        y += h + ERA_GAP

    cell("band", BAND,
         "rounded=1;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;fontSize=13;"
         "fontStyle=1;fillColor=#f5f5f5;strokeColor=#999999;dashed=1;dashPattern=5 5;",
         COLS[0][0], band_y, PAGE_W - COLS[0][0] * 2, 72)

    lines.append("")
    lines.append("      </root>")
    lines.append("    </mxGraphModel>")
    lines.append("  </diagram>")
    lines.append("</mxfile>")
    return "\n".join(lines) + "\n"


def main() -> None:
    default_out = (
        Path(__file__).resolve().parent.parent
        / "static/images/photographers-by-era-map.drawio"
    )
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=default_out, help="output .drawio path")
    args = parser.parse_args()

    args.out.write_text(build(), encoding="utf-8")
    print(f"wrote {args.out}")
    total = sum(len(e[2]) + len(e[3]) + len(e[4]) for e in ERAS)
    print(f"eras={len(ERAS)} names={total}")


if __name__ == "__main__":
    main()
