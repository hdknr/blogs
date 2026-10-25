// slides.json → dist/ai-harness-for-executives.pptx
//
// The slide text lives in slides.json; this file only decides where it goes.
// Each slide names a `layout`, and each layout has one renderer below.
// Usage: npm install && npm run build

import { mkdir, readFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import pptxgen from "pptxgenjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const OUT = join(HERE, "dist", "ai-harness-for-executives.pptx");

// --- design tokens ---------------------------------------------------------

// BIZ UDPGothic ships with Windows 10 (1809) and later. Where it is missing,
// PowerPoint falls back to the system's Japanese gothic face.
const FONT = "BIZ UDPGothic";

const C = {
  navy: "1F2A44",
  navy2: "2E3B5A",
  bg: "F7F5F0",
  bg2: "ECE8DF",
  card: "FFFDF9",
  border: "E2DCCF",
  row: "F3EFE6",
  text: "3D4656",
  orange: "B5561A",
  accent: "F2A65A",
  teal: "2F6F73",
  tealTint: "E3EEED",
  peach: "F6E3D3",
  onDark: "C9D2E3",
  onTeal: "DCEBEA",
  arrow: "C9C2B3",
};

const TONE = { teal: C.teal, orange: C.orange, navy: C.navy, accentLight: C.accent, neutral: C.navy };
const TINT = { teal: C.tealTint, orange: C.peach, neutral: C.bg2 };

// Type scale in points.
const T = { title: 32, lead: 16, head: 20, body: 15, small: 14, emphasis: 18 };

// 16:9 wide canvas in inches; margins match the 128px margins of the web deck.
const W = 13.333;
const H = 7.5;
const M = 0.89;
const CW = W - 2 * M;
const TOP = 0.75;
const CT = 1.8; // first content row under a title
const CB = H - 0.8; // lowest content edge
const GAP = 0.25;

// --- text measuring ---------------------------------------------------------

// Japanese glyphs are about 1em wide, ASCII about 0.55em.
function emWidth(s) {
  let w = 0;
  for (const ch of s) w += /[\x00-\x7F]/.test(ch) ? 0.55 : 1;
  return w;
}

function lines(text, pt, wIn) {
  const perLine = (wIn * 72) / pt;
  return String(text)
    .split("\n")
    .reduce((n, seg) => n + Math.max(1, Math.ceil((emWidth(seg) * 1.05) / perLine)), 0);
}

// A line is font-size × line-spacing × the face's own leading (about 1.25 for
// Japanese gothics). Leaving out that last factor is what made text overlap.
function height(text, pt, wIn, spacing = 1.2) {
  return (lines(text, pt, wIn) * pt * spacing * 1.25) / 72;
}

// --- drawing helpers --------------------------------------------------------

function text(slide, body, opts) {
  slide.addText(body, {
    isTextBox: true,
    fontFace: FONT,
    lang: "ja-JP",
    margin: 0,
    valign: "top",
    lineSpacingMultiple: 1.2,
    ...opts,
  });
}

function box(pres, slide, { x, y, w, h, fill, line, lineWidth = 0.75, radius = 0.12 }) {
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x,
    y,
    w,
    h,
    fill: { color: fill },
    line: line ? { color: line, width: lineWidth } : { type: "none" },
    rectRadius: radius,
  });
}

// Several differently styled paragraphs in one text box, so they flow into
// each other instead of being pinned at estimated offsets.
function paragraphs(parts) {
  const runs = [];
  parts.forEach((p, i) => {
    const last = i === parts.length - 1;
    runs.push({
      text: p.text,
      options: { fontSize: p.size, bold: p.bold, color: p.color, breakLine: !last, paraSpaceAfter: last ? 0 : p.after ?? 6 },
    });
  });
  return runs;
}

function partsHeight(parts, wIn) {
  return parts.reduce((a, p, i) => a + height(p.text, p.size, wIn) + (i < parts.length - 1 ? (p.after ?? 6) / 72 : 0), 0);
}

function footer(slide, f, y) {
  if (!f) return 0;
  const h = height(f.text, T.emphasis, CW);
  text(slide, f.text, { x: M, y, w: CW, h, fontSize: T.emphasis, bold: true, color: TONE[f.tone] ?? C.navy });
  return h;
}

function noteBox(pres, slide, note, { x = M, y, w = CW, size = T.body }) {
  const pad = 0.24;
  const h = height((note.label ?? "") + note.text, size, w - 2 * pad) + 2 * pad;
  box(pres, slide, { x, y, w, h, fill: TINT[note.tone ?? "neutral"] ?? C.bg2, radius: 0.1 });
  const runs = [];
  if (note.label) runs.push({ text: note.label, options: { bold: true } });
  runs.push({ text: note.text });
  text(slide, runs, { x: x + pad, y: y + pad, w: w - 2 * pad, h: h - 2 * pad, fontSize: size, color: C.navy, valign: "middle" });
  return h;
}

function eyebrow(slide, label, y, color = C.orange) {
  text(slide, label, { x: M, y, w: CW, h: 0.35, fontSize: T.small, bold: true, color, charSpacing: 2 });
}

function title(slide, s) {
  slide.addText(s.title, { placeholder: "title" });
}

// --- slide masters (one per frame) -------------------------------------------

function defineMasters(pres) {
  const slideNumber = { x: W - M - 0.8, y: H - 0.5, w: 0.8, h: 0.3, fontFace: FONT, fontSize: 10, color: "8A8F99", align: "right" };
  const titlePh = (y, h, color) => ({
    placeholder: {
      options: { name: "title", type: "title", x: M, y, w: CW, h, fontFace: FONT, fontSize: T.title, bold: true, color, align: "left", valign: "top", margin: 0 },
      text: "",
    },
  });
  pres.defineSlideMaster({ title: "LIGHT", background: { color: C.bg }, objects: [titlePh(TOP, 0.75, C.navy)], slideNumber });
  pres.defineSlideMaster({ title: "LIGHT_ALT", background: { color: C.bg2 }, objects: [titlePh(TOP, 0.75, C.navy)], slideNumber });
  pres.defineSlideMaster({ title: "LIGHT_EYEBROW", background: { color: C.bg }, objects: [titlePh(1.15, 1.35, C.navy)], slideNumber });
  pres.defineSlideMaster({ title: "DARK", background: { color: C.navy }, objects: [titlePh(TOP, 0.75, C.bg)], slideNumber: { ...slideNumber, color: C.onDark } });
  pres.defineSlideMaster({ title: "PLAIN_ALT", background: { color: C.bg2 }, objects: [], slideNumber });
  pres.defineSlideMaster({ title: "COVER", background: { color: C.navy }, objects: [] });
}

// --- layouts -----------------------------------------------------------------

const layouts = {
  cover: {
    master: () => "COVER",
    render(pres, slide, s) {
      const size = 50;
      const titleH = (s.title.length * size * 1.1 * 1.25) / 72;
      const parts = [0.35, 0.3, titleH, 0.35, 0.5, 0.25, 0.35];
      let y = (H - parts.reduce((a, b) => a + b, 0)) / 2;
      eyebrow(slide, s.eyebrow, y, C.accent);
      y += parts[0] + parts[1];
      text(slide, s.title.join("\n"), { x: M, y, w: CW, h: titleH, fontSize: size, bold: true, color: C.bg, lineSpacingMultiple: 1.1 });
      y += parts[2] + parts[3];
      text(slide, s.subtitle, { x: M, y, w: CW, h: parts[4], fontSize: 20, color: C.onDark });
      y += parts[4] + parts[5];
      text(slide, s.meta, { x: M, y, w: CW, h: parts[6], fontSize: T.small, color: C.onDark });
    },
  },

  statement: {
    master: () => "PLAIN_ALT",
    render(pres, slide, s) {
      const size = 44;
      const titleH = (s.title.length * size * 1.25 * 1.25) / 72;
      const bodyH = height(s.body, 17, CW, 1.4);
      let y = (H - (0.35 + 0.4 + titleH + 0.45 + bodyH)) / 2;
      eyebrow(slide, s.eyebrow, y);
      y += 0.75;
      const runs = [];
      s.title.forEach((line, i) => {
        line.forEach((run, j) => {
          const breakLine = j === line.length - 1 && i < s.title.length - 1;
          runs.push({ text: run.text, options: { color: run.accent ? C.orange : C.navy, breakLine } });
        });
      });
      text(slide, runs, { x: M, y, w: CW, h: titleH, fontSize: size, bold: true, lineSpacingMultiple: 1.25 });
      y += titleH + 0.45;
      text(slide, s.body, { x: M, y, w: CW, h: bodyH, fontSize: 17, color: C.text, lineSpacingMultiple: 1.4 });
    },
  },

  cards: {
    master: (s) => (s.background === "alt" ? "LIGHT_ALT" : "LIGHT"),
    render(pres, slide, s) {
      title(slide, s);
      let y = CT;
      if (s.intro) {
        const h = height(s.intro, T.lead, CW, 1.35);
        text(slide, s.intro, { x: M, y, w: CW, h, fontSize: T.lead, color: C.text, lineSpacingMultiple: 1.35 });
        y += h + 0.3;
      }
      const cols = s.columns;
      const rows = Math.ceil(s.cards.length / cols);
      const cw = (CW - (cols - 1) * GAP) / cols;
      const horizontal = cols === 2 && s.cards.some((c) => c.number);
      const numW = 0.6;
      const reserve = s.footer ? height(s.footer.text, T.emphasis, CW) + 0.35 : 0;
      const room = (CB - reserve - y - (rows - 1) * GAP) / rows;

      // Four narrow columns cannot hold the full-size heading on one line.
      // When the cards still do not fit the room, step down one size, no
      // further than the 14pt body floor.
      const sizes = cols >= 4 ? [{ head: 16, body: T.small, pad: 0.2 }] : [
        { head: T.head, body: T.body, pad: cols === 3 ? 0.26 : 0.3 },
        { head: 18, body: T.small, pad: 0.24 },
      ];
      let pad, inner, blocks;
      for (const sz of sizes) {
        pad = sz.pad;
        inner = cw - 2 * pad - (horizontal ? numW : 0);
        blocks = s.cards.map((card) => {
          const parts = [];
          if (card.number && !horizontal) parts.push({ text: card.number, size: 28, bold: true, color: C.orange, after: 4 });
          parts.push({ text: card.heading, size: horizontal && !card.text ? 22 : sz.head, bold: true, color: TONE[card.tone] ?? C.navy });
          if (card.sub) parts.push({ text: card.sub, size: sz.body, bold: true, color: C.teal });
          if (card.text) parts.push({ text: card.text, size: sz.body, color: C.text });
          return { card, parts, natural: partsHeight(parts, inner) };
        });
        if (Math.max(...blocks.map((b) => b.natural)) + 2 * pad <= room) break;
      }
      const ch = Math.min(room, Math.max(...blocks.map((b) => b.natural)) + 2 * pad + 0.2);
      const headingOnly = blocks.every((b) => !b.card.text && !b.card.sub);

      blocks.forEach((b, i) => {
        const x = M + (i % cols) * (cw + GAP);
        const top = y + Math.floor(i / cols) * (ch + GAP);
        box(pres, slide, { x, y: top, w: cw, h: ch, fill: C.card, line: C.border });
        const valign = headingOnly ? "middle" : "top";
        if (horizontal) {
          text(slide, b.card.number, { x: x + pad, y: top + pad, w: numW, h: ch - 2 * pad, fontSize: 28, bold: true, color: C.orange, valign });
        }
        text(slide, paragraphs(b.parts), { x: x + pad + (horizontal ? numW : 0), y: top + pad, w: inner, h: ch - 2 * pad, valign });
      });
      footer(slide, s.footer, y + rows * ch + (rows - 1) * GAP + 0.35);
    },
  },

  // A numbered list where each step is one row: number, heading, description.
  rows: {
    master: () => "LIGHT",
    render(pres, slide, s) {
      title(slide, s);
      const y = CT;
      const gap = 0.14;
      const n = s.items.length;
      const reserve = s.footer ? height(s.footer.text, T.emphasis, CW) + 0.3 : 0;
      const rh = Math.min((CB - reserve - y - (n - 1) * gap) / n, 0.8);
      const headW = 3.9;
      const textX = M + 0.95 + headW + 0.2;
      const textW = M + CW - 0.3 - textX;
      s.items.forEach((it, i) => {
        const top = y + i * (rh + gap);
        box(pres, slide, { x: M, y: top, w: CW, h: rh, fill: C.card, line: C.border, radius: 0.1 });
        text(slide, it.number, { x: M + 0.3, y: top, w: 0.5, h: rh, fontSize: 26, bold: true, color: C.orange, valign: "middle" });
        text(slide, it.heading, { x: M + 0.95, y: top, w: headW, h: rh, fontSize: T.emphasis, bold: true, color: C.navy, valign: "middle" });
        text(slide, it.text, { x: textX, y: top, w: textW, h: rh, fontSize: T.small, color: C.text, valign: "middle" });
      });
      footer(slide, s.footer, y + n * rh + (n - 1) * gap + 0.3);
    },
  },

  equation: {
    master: () => "LIGHT_EYEBROW",
    render(pres, slide, s) {
      eyebrow(slide, s.eyebrow, TOP);
      title(slide, s);
      let y = 2.7;
      const bodyH = height(s.body, T.lead, CW, 1.35);
      text(slide, s.body, { x: M, y, w: CW, h: bodyH, fontSize: T.lead, color: C.text, lineSpacingMultiple: 1.35 });
      y += bodyH + 0.4;
      const opW = 0.7;
      const bw = (CW - s.operators.length * opW) / s.terms.length;
      const bh = 1.5;
      const style = {
        light: { fill: C.card, line: C.border, label: C.navy, sub: C.text },
        teal: { fill: C.teal, label: C.bg, sub: C.onTeal },
        dark: { fill: C.navy, label: C.accent, sub: C.onDark },
      };
      let x = M;
      s.terms.forEach((t, i) => {
        const st = style[t.style];
        box(pres, slide, { x, y, w: bw, h: bh, fill: st.fill, line: st.line });
        text(
          slide,
          paragraphs([
            { text: t.label, size: 28, bold: true, color: st.label, after: 6 },
            { text: t.sub, size: T.body, color: st.sub },
          ]),
          { x, y, w: bw, h: bh, align: "center", valign: "middle" },
        );
        x += bw;
        if (i < s.operators.length) {
          text(slide, s.operators[i], { x, y, w: opW, h: bh, fontSize: 36, bold: true, color: C.text, align: "center", valign: "middle" });
          x += opW;
        }
      });
      footer(slide, s.footer, y + bh + 0.45);
    },
  },

  lists: {
    master: () => "LIGHT",
    render(pres, slide, s) {
      title(slide, s);
      const y = CT;
      const cw = (CW - GAP) / 2;
      const pad = 0.3;
      const inner = cw - 2 * pad - 0.3; // bullets indent
      const listH = (l) => l.items.reduce((a, it) => a + height(it, T.body, inner, 1.2) + 6 / 72, 0);
      const headH = height("見出し", T.head, cw) + 0.12;
      const ch = Math.max(...s.lists.map(listH)) + headH + 2 * pad;
      s.lists.forEach((l, i) => {
        const x = M + i * (cw + GAP);
        box(pres, slide, { x, y, w: cw, h: ch, fill: TINT[l.tone] });
        text(slide, l.heading, { x: x + pad, y: y + pad, w: cw - 2 * pad, h: headH, fontSize: T.head, bold: true, color: TONE[l.tone] });
        const items = l.items.map((it, j) => ({ text: it, options: { bullet: true, breakLine: j < l.items.length - 1 } }));
        text(slide, items, { x: x + pad, y: y + pad + headH, w: cw - 2 * pad, h: ch - 2 * pad - headH, fontSize: T.body, color: C.text, paraSpaceAfter: 6 });
      });
      let ny = y + ch + 0.3;
      ny += footer(slide, s.footer, ny) + 0.25;
      noteBox(pres, slide, s.note, { y: ny, size: T.small });
    },
  },

  table: {
    master: (s) => (s.eyebrow ? "LIGHT_EYEBROW" : "LIGHT"),
    render(pres, slide, s) {
      if (s.eyebrow) eyebrow(slide, s.eyebrow, TOP);
      title(slide, s);
      let y = s.eyebrow ? 2.05 : CT;
      if (s.intro) {
        const h = height(s.intro, T.lead, CW, 1.35);
        text(slide, s.intro, { x: M, y, w: CW, h, fontSize: T.lead, color: C.text, lineSpacingMultiple: 1.35 });
        y += h + 0.25;
      }
      // The table estimate runs a little tall, so a box under it may sit
      // higher than estimated, but never below the bottom margin.
      y += drawTable(slide, s.table, { x: M, y, w: CW }) + 0.3;
      if (s.note) {
        const nh = height((s.note.label ?? "") + s.note.text, T.body, CW - 0.48) + 0.48;
        noteBox(pres, slide, s.note, { y: Math.min(y, CB - nh) });
      }
      if (s.tips) {
        const tw = (CW - GAP) / s.tips.length;
        const pad = 0.24;
        const th = Math.max(...s.tips.map((t) => height(t.label + t.text, T.body, tw - 2 * pad))) + 2 * pad;
        y = Math.min(y, CB - th);
        s.tips.forEach((t, i) => {
          const x = M + i * (tw + GAP);
          box(pres, slide, { x, y, w: tw, h: th, fill: C.tealTint, radius: 0.1 });
          text(slide, [{ text: t.label, options: { bold: true } }, { text: t.text }], { x: x + pad, y: y + pad, w: tw - 2 * pad, h: th - 2 * pad, fontSize: T.body, color: C.navy, valign: "middle" });
        });
      }
      if (s.footer) footer(slide, s.footer, y);
    },
  },

  boundary: {
    master: () => "LIGHT",
    render(pres, slide, s) {
      title(slide, s);
      const colW = (CW - 0.4) / 2;
      const rx = M + colW + 0.4;
      const pad = 0.26;

      let ly = CT;
      const bodyH = height(s.body, T.body, colW, 1.3);
      text(slide, s.body, { x: M, y: ly, w: colW, h: bodyH, fontSize: T.body, color: C.text, lineSpacingMultiple: 1.3 });
      ly += bodyH + 0.2;
      for (const c of s.callouts) {
        const parts = [
          { text: c.heading, size: T.body, bold: true, color: TONE[c.tone], after: 4 },
          { text: c.text, size: T.body, color: C.navy },
        ];
        const h = partsHeight(parts, colW - 2 * pad) + 2 * pad;
        box(pres, slide, { x: M, y: ly, w: colW, h, fill: TINT[c.tone], radius: 0.1 });
        text(slide, paragraphs(parts), { x: M + pad, y: ly + pad, w: colW - 2 * pad, h: h - 2 * pad, valign: "middle" });
        ly += h + 0.15;
      }

      let ry = CT;
      for (const z of s.zones) {
        const parts = [
          { text: z.heading, size: 17, bold: true, color: TONE[z.tone], after: 6 },
          { text: z.text, size: T.body, color: C.navy },
        ];
        const h = partsHeight(parts, colW - 2 * pad) + 2 * pad + 0.1;
        box(pres, slide, { x: rx, y: ry, w: colW, h, fill: TINT[z.tone], line: TONE[z.tone], lineWidth: 2 });
        text(slide, paragraphs(parts), { x: rx + pad, y: ry + pad, w: colW - 2 * pad, h: h - 2 * pad, valign: "middle" });
        ry += h + 0.18;
      }
      noteBox(pres, slide, s.note, { y: Math.max(ly, ry) + 0.1, size: T.small });
    },
  },

  flow: {
    master: () => "LIGHT",
    render(pres, slide, s) {
      title(slide, s);
      const y = CT + 0.1;
      const gapW = 0.55;
      const bw = (CW - (s.steps.length - 1) * gapW) / s.steps.length;
      const bh = 1.3;
      s.steps.forEach((st, i) => {
        const x = M + i * (bw + gapW);
        box(pres, slide, { x, y, w: bw, h: bh, fill: st.dark ? C.navy : C.card, line: st.dark ? undefined : C.border });
        text(
          slide,
          paragraphs([
            { text: st.label, size: T.small, bold: true, color: st.dark ? C.accent : C.orange, after: 6 },
            { text: st.heading, size: T.head, bold: true, color: st.dark ? C.bg : C.navy },
          ]),
          { x: x + 0.26, y, w: bw - 0.52, h: bh, valign: "middle" },
        );
        if (i < s.steps.length - 1) {
          slide.addShape(pres.shapes.RIGHT_ARROW, { x: x + bw + 0.12, y: y + bh / 2 - 0.12, w: gapW - 0.24, h: 0.24, fill: { color: C.arrow }, line: { type: "none" } });
        }
      });
      let ny = y + bh + 0.4;
      const loopH = height(s.loop, T.emphasis, CW);
      text(slide, s.loop, { x: M, y: ny, w: CW, h: loopH, fontSize: T.emphasis, bold: true, color: C.teal });
      ny += loopH + 0.45;
      const pad = 0.3;
      const parts = [
        { text: s.example.heading, size: T.lead, bold: true, color: C.navy, after: 8 },
        { text: s.example.text, size: T.lead, color: C.text },
      ];
      const exH = partsHeight(parts, CW - 2 * pad) + 2 * pad;
      box(pres, slide, { x: M, y: ny, w: CW, h: exH, fill: C.bg2 });
      text(slide, paragraphs(parts), { x: M + pad, y: ny + pad, w: CW - 2 * pad, h: exH - 2 * pad, valign: "middle" });
    },
  },

  stairs: {
    master: () => "DARK",
    render(pres, slide, s) {
      title(slide, s);
      const base = 5.8;
      const heights = [1.9, 2.7, 3.5];
      const style = {
        muted: { fill: C.navy2, head: C.bg, body: C.onDark },
        teal: { fill: C.teal, head: C.bg, body: C.onTeal },
        accent: { fill: C.accent, head: C.navy, body: C.navy },
      };
      const bw = (CW - 2 * GAP) / 3;
      const pad = 0.28;
      s.bars.forEach((b, i) => {
        const st = style[b.style];
        const h = heights[i];
        const x = M + i * (bw + GAP);
        box(pres, slide, { x, y: base - h, w: bw, h, fill: st.fill });
        text(
          slide,
          paragraphs([
            { text: b.heading, size: 24, bold: true, color: st.head, after: 8 },
            { text: b.text, size: T.body, color: st.body },
          ]),
          { x: x + pad, y: base - h + pad, w: bw - 2 * pad, h: h - 2 * pad, valign: "bottom" },
        );
      });
      footer(slide, s.footer, base + 0.35);
    },
  },

  measure: {
    master: () => "LIGHT",
    render(pres, slide, s) {
      title(slide, s);
      const y = CT;
      const lw = 3.7;
      const rx = M + lw + 0.35;
      const rw = CW - lw - 0.35;
      const headH = height("測るもの", T.head, rw) + 0.15;
      text(slide, s.tableHeading, { x: rx, y, w: rw, h: headH, fontSize: T.head, bold: true, color: C.teal });
      const tableH = drawTable(slide, { ...s.table, fontSize: T.lead }, { x: rx, y: y + headH, w: rw });

      const pad = 0.3;
      box(pres, slide, { x: M, y, w: lw, h: headH + tableH, fill: C.bg2 });
      text(
        slide,
        paragraphs([
          { text: s.callout.heading, size: T.head, bold: true, color: C.orange, after: 12 },
          { text: s.callout.text, size: T.lead, color: C.text },
        ]),
        { x: M + pad, y: y + pad, w: lw - 2 * pad, h: headH + tableH - 2 * pad, lineSpacingMultiple: 1.35 },
      );
    },
  },
};

// Draws a header-row table with banded rows; returns its estimated height.
function drawTable(slide, t, { x, y, w }) {
  const size = t.fontSize ?? T.body;
  const colW = t.widths.map((p) => (w * p) / 100);
  const padV = 0.1;
  const padH = 0.14;
  const cell = (txt, opts = {}) => ({ text: txt, options: { margin: [padV, padH, padV, padH], valign: "middle", ...opts } });
  const rows = [t.headers.map((h) => cell(h, { bold: true, color: C.bg, fill: { color: C.navy } }))];
  t.rows.forEach((r, i) => rows.push(r.map((c) => cell(c, { fill: { color: i % 2 ? C.row : C.card } }))));
  const rowH = (r) => Math.max(...r.map((c, i) => height(c, size, colW[i] - 2 * padH))) + 2 * padV;
  const total = [t.headers, ...t.rows].reduce((a, r) => a + rowH(r), 0);
  slide.addTable(rows, {
    x,
    y,
    w,
    colW,
    fontFace: FONT,
    fontSize: size,
    color: C.navy,
    border: { type: "solid", pt: 0.75, color: C.border },
    autoPage: false,
  });
  return total;
}

// --- build ------------------------------------------------------------------

async function main() {
  const deck = JSON.parse(await readFile(join(HERE, "slides.json"), "utf8"));
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
  pres.title = deck.title;
  pres.subject = deck.subject;
  pres.theme = { headFontFace: FONT, bodyFontFace: FONT };
  defineMasters(pres);

  const starts = new Map(deck.sections.map((s) => [s.start, s.title]));
  let section;
  for (const s of deck.slides) {
    const layout = layouts[s.layout];
    if (!layout) throw new Error(`slide ${s.id}: unknown layout "${s.layout}"`);
    if (starts.has(s.id)) {
      section = starts.get(s.id);
      pres.addSection({ title: section });
    }
    const slide = pres.addSlide({ masterName: layout.master(s), sectionTitle: section });
    layout.render(pres, slide, s);
    if (s.notes) slide.addNotes(s.notes);
  }

  await mkdir(dirname(OUT), { recursive: true });
  await pres.writeFile({ fileName: OUT });
  console.log(`wrote ${OUT} (${deck.slides.length} slides)`);
}

await main();
