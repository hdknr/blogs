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
 */
import { readdir, stat } from "node:fs/promises";
import { join } from "node:path";
import sharp from "sharp";

const WIDTHS = [640, 1024, 1600];
const dir = join(process.cwd(), "dist", "images");

const files = (await readdir(dir)).filter(f => /\.png$/i.test(f) && !/-\d+\.png$/.test(f));

let written = 0;

await Promise.all(
  files.map(async file => {
    const path = join(dir, file);
    const image = sharp(path);
    const { width } = await image.metadata();
    const name = file.replace(/\.png$/i, "");

    for (const w of WIDTHS) {
      if (width && w > width) continue;
      const resized = sharp(path).resize({ width: w, kernel: "lanczos3" });
      const webpPath = join(dir, `${name}-${w}.webp`);
      const pngPath = join(dir, `${name}-${w}.png`);
      await Promise.all([
        resized.clone().webp({ quality: 90 }).toFile(webpPath),
        resized.clone().png().toFile(pngPath),
      ]);
      written += 2;
    }

    // Narrower than the smallest step: one rendition at the source width, which
    // is the only width rehypePicture.mjs will ask for in that case.
    if (width && width < WIDTHS[0]) {
      await sharp(path).webp({ quality: 90 }).toFile(join(dir, `${name}-${width}.webp`));
      await sharp(path).png().toFile(join(dir, `${name}-${width}.png`));
      written += 2;
    }
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
console.log(`generate-images: ${files.length} sources, ${written} renditions`);
console.log(
  `  originals ${mb(originalBytes)}MB -> 640w webp ${mb(webpBytes)}MB ` +
    `(-${(100 * (1 - webpBytes / originalBytes)).toFixed(0)}%)`
);
