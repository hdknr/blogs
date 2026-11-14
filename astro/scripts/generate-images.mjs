#!/usr/bin/env node
/**
 * Produces the WebP and resized-PNG renditions that rehypePicture.mjs points at.
 *
 * Runs after `astro build`, writing into dist/images/ alongside the originals
 * that publicDir copied there. The names are deterministic (`<name>-640.webp`),
 * which is what lets the rewriting and the generation stay independent.
 *
 * `q90` and lanczos because these are drawio diagrams -- line art and small
 * kanji, not photographs. Thin strokes fall apart at the quality levels that
 * look fine on a photo. Never upscales: a 700px-wide diagram blown up to 1600
 * is a bigger file with no more detail in it.
 *
 * IMAGE_CACHE_DIR (optional): reuse renditions across runs. Entries are keyed by
 * the SHA-256 of the source PNG, not its name, so a redrawn diagram misses the
 * cache and an unchanged one hits it no matter what else moved. CI restores this
 * directory with actions/cache; the key there also hashes this script, so a
 * change to widths or quality starts from an empty cache rather than serving
 * renditions made by the old settings. An entry counts only once its `.complete`
 * marker exists, so a run killed halfway through writing it is regenerated.
 */
import { createHash } from "node:crypto";
import { copyFile, mkdir, readdir, readFile, stat, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { join } from "node:path";
import sharp from "sharp";

const WIDTHS = [640, 1024, 1600];
const dir = join(process.cwd(), "dist", "images");
const cacheDir = process.env.IMAGE_CACHE_DIR || "";

const files = (await readdir(dir)).filter(f => /\.png$/i.test(f) && !/-\d+\.png$/.test(f));

let written = 0;
let cached = 0;

async function render(path, name) {
  const image = sharp(path);
  const { width } = await image.metadata();
  const outputs = [];

  for (const w of WIDTHS) {
    if (width && w > width) continue;
    const resized = sharp(path).resize({ width: w, kernel: "lanczos3" });
    const webpPath = join(dir, `${name}-${w}.webp`);
    const pngPath = join(dir, `${name}-${w}.png`);
    await Promise.all([
      resized.clone().webp({ quality: 90 }).toFile(webpPath),
      resized.clone().png().toFile(pngPath),
    ]);
    outputs.push(`${w}.webp`, `${w}.png`);
  }

  // Narrower than the smallest step: one rendition at the source width, which
  // is the only width rehypePicture.mjs will ask for in that case.
  if (width && width < WIDTHS[0]) {
    await sharp(path).webp({ quality: 90 }).toFile(join(dir, `${name}-${width}.webp`));
    await sharp(path).png().toFile(join(dir, `${name}-${width}.png`));
    outputs.push(`${width}.webp`, `${width}.png`);
  }
  return outputs;
}

await Promise.all(
  files.map(async file => {
    const path = join(dir, file);
    const name = file.replace(/\.png$/i, "");

    if (!cacheDir) {
      // Await first, then add: `written += await …` reads `written` before the
      // await and writes it back after, losing every other file's increment.
      const outputs = await render(path, name);
      written += outputs.length;
      return;
    }

    const hash = createHash("sha256").update(await readFile(path)).digest("hex");
    const entry = join(cacheDir, hash);

    if (existsSync(join(entry, ".complete"))) {
      const suffixes = (await readdir(entry)).filter(f => f !== ".complete");
      await Promise.all(suffixes.map(s => copyFile(join(entry, s), join(dir, `${name}-${s}`))));
      cached += suffixes.length;
      return;
    }

    const suffixes = await render(path, name);
    written += suffixes.length;
    await mkdir(entry, { recursive: true });
    await Promise.all(suffixes.map(s => copyFile(join(dir, `${name}-${s}`), join(entry, s))));
    await writeFile(join(entry, ".complete"), "");
  })
);

// Size the results by reading the directory back, rather than accumulating
// during generation -- the totals are what a reader actually downloads, and
// they should come from the files on disk, not from bookkeeping that can drift.
const sum = async names =>
  (await Promise.all(names.map(n => stat(join(dir, n))))).reduce((a, s) => a + s.size, 0);

const after = await readdir(dir);
const originalBytes = await sum(files);
const webpBytes = await sum(after.filter(f => f.endsWith("-640.webp")));

const mb = n => (n / 1024 / 1024).toFixed(1);
console.log(
  `generate-images: ${files.length} sources, ${written} renditions` +
    (cacheDir ? `, ${cached} from cache` : "")
);
console.log(
  `  originals ${mb(originalBytes)}MB -> 640w webp ${mb(webpBytes)}MB ` +
    `(-${(100 * (1 - webpBytes / originalBytes)).toFixed(0)}%)`
);
