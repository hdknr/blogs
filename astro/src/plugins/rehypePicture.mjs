import { readFileSync } from "node:fs";
import { join } from "node:path";
import { visit } from "unist-util-visit";

/**
 * Rewrites markdown images into a `<picture>` with WebP sources, the Astro
 * equivalent of the Hugo render hook added in hdknr/blogs#648.
 *
 * Astro does not optimise images referenced by absolute URL -- those are public
 * assets, copied verbatim. Every one of the 122 image references in content is
 * written that way (`![alt](/blogs/images/x.png)`), and moving them into
 * src/assets to get the pipeline would mean editing 92 posts. So the rewriting
 * happens here and the WebP files are produced by scripts/generate-images.mjs,
 * which uses the same deterministic names.
 *
 * Measured on the Hugo side: a reader on a phone went from 45.2MB of PNG across
 * the site to 3.1MB of WebP. Dropping this on the way to Astro would have
 * quietly undone that.
 */
const WIDTHS = [640, 1024, 1600];
const IMAGE_PREFIX = "/blogs/images/";
const SOURCE_DIR = join(process.cwd(), "..", "static", "images");

const widthCache = new Map();

/**
 * Intrinsic width straight out of the PNG header: bytes 16-20 of the IHDR
 * chunk. Cheap, synchronous and dependency-free, which matters because rehype
 * transformers run per document and this is called for all 122 images.
 *
 * Needed because the generator must not upscale -- a 700px-wide diagram blown
 * up to 1600 is a bigger file with no more detail. Emitting a srcset entry for
 * a width that was never generated is worse still: the browser picks it and
 * gets a 404. That is exactly what scripts/check_assets.py caught.
 */
function intrinsicWidth(name) {
  if (widthCache.has(name)) return widthCache.get(name);
  let width = null;
  try {
    const header = readFileSync(join(SOURCE_DIR, `${name}.png`)).subarray(0, 24);
    if (header.length >= 24) width = header.readUInt32BE(16);
  } catch {
    width = null;
  }
  widthCache.set(name, width);
  return width;
}

export function rehypePicture() {
  return tree => {
    visit(tree, "element", (node, index, parent) => {
      if (node.tagName !== "img" || !parent || index === null) return;

      const src = node.properties?.src;
      if (typeof src !== "string" || !src.startsWith(IMAGE_PREFIX)) return;
      if (!/\.png$/i.test(src)) return; // SVG is vector; leave it alone.

      const name = src.slice(IMAGE_PREFIX.length).replace(/\.png$/i, "");
      const source = intrinsicWidth(name);
      // Only widths that were actually generated. Falls back to the full set
      // when the header could not be read, so a new image still renders.
      const widths = source ? WIDTHS.filter(w => w <= source) : WIDTHS;
      if (source && widths.length === 0) widths.push(source);

      const webp = widths.map(w => `${IMAGE_PREFIX}${name}-${w}.webp ${w}w`).join(", ");
      const png = widths.map(w => `${IMAGE_PREFIX}${name}-${w}.png ${w}w`).join(", ");
      const largest = widths[widths.length - 1];
      const sizes = "(max-width: 720px) 100vw, 720px";

      const img = {
        type: "element",
        tagName: "img",
        properties: {
          src: `${IMAGE_PREFIX}${name}-${largest}.png`,
          srcset: png,
          sizes,
          alt: node.properties.alt ?? "",
          loading: "lazy",
          decoding: "async",
        },
        children: [],
      };

      const picture = {
        type: "element",
        tagName: "picture",
        properties: {},
        children: [
          {
            type: "element",
            tagName: "source",
            properties: { type: "image/webp", srcset: webp, sizes },
            children: [],
          },
          img,
        ],
      };

      // Wrap in a link to the untouched original. These diagrams are 2000-2600px
      // wide and readers pinch-zoom to read the small labels; a downscaled
      // rendition alone takes that away.
      parent.children[index] = {
        type: "element",
        tagName: "a",
        properties: {
          href: src,
          target: "_blank",
          rel: "noopener",
          class: "diagram-link",
        },
        children: [picture],
      };
    });
  };
}
