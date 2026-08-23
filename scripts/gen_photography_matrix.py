#!/usr/bin/env python3
"""Generate the photography turning-points matrix diagram as drawio XML.

The matrix scores each turning point on the four axes used in
content/posts/2026/08/2026-08-23-photography-history-turning-points.md.
Hand-editing 16 rows x 4 columns of mxCell geometry is unmaintainable, so the
scoring table lives here as data and the XML is generated from it.

Usage:
    python3 scripts/gen_photography_matrix.py [--out PATH]

Then export the PNG the post references:
    /Applications/draw.io.app/Contents/MacOS/draw.io --export --format png --scale 2 \
        --output static/images/photography-history-turning-points-matrix.png \
        static/images/photography-history-turning-points-matrix.drawio
"""

import argparse
import html
from pathlib import Path

# (year, label, [technical, institutional, circulation, commission], highlight)
ROWS = [
    ("1888", "コダック No.1 — スナップショットの誕生", ["大", "小", "大", "小"], False),
    ("1890s", "ピクトリアリズム / フォト・セセッション", ["中", "大", "小", "ほぼゼロ"], False),
    ("1920s", "広告・ファッション写真の職業化", ["小", "小", "大", "極大"], True),
    ("1932", "ストレート・フォトグラフィ / f/64 グループ", ["小", "大", "小", "ほぼゼロ"], False),
    ("1935", "FSA とグラフ誌の時代", ["小", "中", "大", "極大"], True),
    ("1955", "The Family of Man（MoMA 企画 / USIA 巡回）", ["小", "大", "大", "大"], False),
    ("1958", "ロバート・フランク『The Americans』", ["小", "大", "小", "小"], False),
    ("1967", "New Documents（MoMA）", ["小", "大", "小", "ほぼゼロ"], False),
    ("1975", "ニュー・トポグラフィックス", ["小", "大", "小", "ほぼゼロ"], False),
    ("1976", "ニューカラー", ["小", "大", "ほぼゼロ", "ほぼゼロ"], True),
    ("1977", "ピクチャーズ・ジェネレーション", ["小", "大", "小", "ほぼゼロ"], False),
    ("1990", "デジタル化（Photoshop / DCS）", ["大", "中", "中", "中"], False),
    ("1993", "インターネット流通 / ストックフォト", ["中", "小", "大", "大"], False),
    ("2007", "スマートフォン — カメラの常時携帯化", ["大", "小", "極大", "小"], False),
    ("2010", "SNS（Instagram / Snapchat）※ アルゴリズムを含む", ["小", "中", "極大", "大"], False),
    ("2022", "生成 AI（DALL·E 2 / Stable Diffusion）", ["大", "大", "大", "極大"], True),
]

HEADERS = [
    ("① 技術", "#dae8fc", "#6c8ebf"),
    ("② 制度・美学", "#ffe6cc", "#d79b00"),
    ("③ 流通・受容", "#d5e8d4", "#82b366"),
    ("④ 発注", "#e1d5e7", "#9673a6"),
]

# score -> (fill, stroke, fontColor, bold)
SCALE = {
    "ほぼゼロ": ("#f5f5f5", "#cccccc", "#999999", False),
    "小": ("#eef3fb", "#9db8dd", "#4a6f9e", False),
    "中": ("#d5e8d4", "#82b366", "#3d6b33", False),
    "大": ("#ffe6cc", "#d79b00", "#8a6400", True),
    "極大": ("#f8cecc", "#b85450", "#8f3a36", True),
}

NOTE = (
    "ニューカラーは制度・美学軸でのみ大きく、流通と発注はほぼ何も動かしていない。\n"
    "逆に 1920 年代の広告写真と 1935 年の FSA は、正典がほとんど記述しない発注軸で極大に振れる。\n"
    "4 軸すべてが大きいのは生成 AI だけである。"
)

PAGE_W = 1120
YEAR_X, YEAR_W = 40, 70
NAME_X, NAME_W = 118, 330
COL_X = [456, 614, 772, 930]
COL_W = 150
ROW_H = 42
HEAD_Y = 86
ROW_Y0 = 130


def build() -> str:
    lines: list[str] = []

    def cell(cid, value, style, x, y, w, h):
        # Real newlines in `value` become drawio's line break entity. Escape
        # first, or html.escape turns the entity's own & into &amp;.
        text = html.escape(value).replace("\n", "&#10;")
        lines.append(
            f'        <mxCell id="{cid}" value="{text}" style="{style}" vertex="1" parent="1">'
        )
        lines.append(
            f'          <mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/>'
        )
        lines.append("        </mxCell>")

    table_bottom = ROW_Y0 + len(ROWS) * ROW_H
    legend_y = table_bottom + 18
    note_y = legend_y + 48
    page_h = note_y + 76

    lines.append('<mxfile host="app.diagrams.net" agent="Claude Code" version="26.0.0">')
    lines.append(
        '  <diagram id="photo-turning-points-matrix" name="Photography Turning Points Matrix">'
    )
    lines.append(
        f'    <mxGraphModel dx="1200" dy="800" grid="1" gridSize="10" guides="1" tooltips="1"'
        f' connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="{PAGE_W}"'
        f' pageHeight="{page_h}" math="0" shadow="0">'
    )
    lines.append("      <root>")
    lines.append('        <mxCell id="0"/>')
    lines.append('        <mxCell id="1" parent="0"/>')
    lines.append("")

    cell(
        "ttl",
        "写真史の転換点 — 4 軸評価マトリクス",
        "text;html=1;align=center;verticalAlign=middle;whiteSpace=wrap;fontSize=18;"
        "fontStyle=1;fontColor=#333333;",
        (PAGE_W - 400) // 2, 18, 400, 30,
    )
    cell(
        "sub",
        "各転換点が「技術」「制度・美学」「流通・受容」「発注」のどの軸をどれだけ動かしたか",
        "text;html=1;align=center;verticalAlign=middle;whiteSpace=wrap;fontSize=12;"
        "fontColor=#666666;",
        (PAGE_W - 760) // 2, 48, 760, 24,
    )

    cell(
        "h0", "年",
        "text;html=1;align=center;verticalAlign=middle;whiteSpace=wrap;fontSize=12;"
        "fontStyle=1;fontColor=#666666;",
        YEAR_X, HEAD_Y, YEAR_W, 36,
    )
    cell(
        "h1", "転換点",
        "text;html=1;align=left;verticalAlign=middle;whiteSpace=wrap;fontSize=12;"
        "fontStyle=1;fontColor=#666666;spacingLeft=10;",
        NAME_X, HEAD_Y, NAME_W, 36,
    )
    for i, (label, fill, stroke) in enumerate(HEADERS):
        cell(
            f"h{i + 2}", label,
            f"rounded=1;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;fontSize=12;"
            f"fillColor={fill};strokeColor={stroke};fontStyle=1;",
            COL_X[i], HEAD_Y, COL_W, 36,
        )

    for r, (year, label, scores, hl) in enumerate(ROWS):
        y = ROW_Y0 + r * ROW_H
        cell(
            f"y{r}", year,
            "text;html=1;align=center;verticalAlign=middle;whiteSpace=wrap;fontSize=12;"
            + ("fontStyle=1;fontColor=#8a6400;" if hl else "fontColor=#666666;"),
            YEAR_X, y, YEAR_W, ROW_H,
        )
        cell(
            f"n{r}", label,
            "rounded=1;whiteSpace=wrap;html=1;align=left;verticalAlign=middle;spacingLeft=10;"
            + (
                "fontSize=13;fontStyle=1;fillColor=#fff2cc;strokeColor=#d6b656;" if hl
                else "fontSize=12;fillColor=#ffffff;strokeColor=#d6d6d6;"
            ),
            NAME_X, y, NAME_W, ROW_H,
        )
        for c, score in enumerate(scores):
            fill, stroke, font_color, bold = SCALE[score]
            cell(
                f"c{r}_{c}", score,
                f"rounded=1;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;"
                f"fontSize=12;fillColor={fill};strokeColor={stroke};fontColor={font_color};"
                + ("fontStyle=1;" if bold else ""),
                COL_X[c], y, COL_W, ROW_H,
            )

    cell(
        "lg", "凡例",
        "text;html=1;align=center;verticalAlign=middle;whiteSpace=wrap;fontSize=12;"
        "fontStyle=1;fontColor=#666666;",
        YEAR_X, legend_y, YEAR_W, 32,
    )
    for i, score in enumerate(["ほぼゼロ", "小", "中", "大", "極大"]):
        fill, stroke, font_color, bold = SCALE[score]
        cell(
            f"lg{i}", score,
            f"rounded=1;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;fontSize=12;"
            f"fillColor={fill};strokeColor={stroke};fontColor={font_color};"
            + ("fontStyle=1;" if bold else ""),
            NAME_X + i * 110, legend_y, 100, 32,
        )

    cell(
        "note", NOTE,
        "rounded=1;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;fontSize=13;"
        "fontStyle=1;fillColor=#f5f5f5;strokeColor=#999999;dashed=1;dashPattern=5 5;",
        YEAR_X, note_y, PAGE_W - 80, 68,
    )

    lines.append("")
    lines.append("      </root>")
    lines.append("    </mxGraphModel>")
    lines.append("  </diagram>")
    lines.append("</mxfile>")
    return "\n".join(lines) + "\n"


def main() -> None:
    default_out = (
        Path(__file__).resolve().parent.parent
        / "static/images/photography-history-turning-points-matrix.drawio"
    )
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=default_out, help="output .drawio path")
    args = parser.parse_args()

    args.out.write_text(build(), encoding="utf-8")
    print(f"wrote {args.out}")
    print(f"rows={len(ROWS)} axes={len(HEADERS)}")


if __name__ == "__main__":
    main()
