// Render a BPMN 2.0 diagram (as saved by Camunda Modeler) to PNG.
//
// Usage (from scripts/bpmn/):
//   npm ci
//   node render.cjs ../../static/images/<name>.bpmn ../../static/images/<name>.png [scale]
//
// The diagram is drawn by bpmn-js (the same renderer Camunda Modeler uses) in a local
// Chrome via puppeteer-core, exported as SVG, then screenshotted at `scale` (default 2).
// Set CHROME_PATH if Chrome is not at the default macOS location.
const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer-core');

const CHROME =
  process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

(async () => {
  const [input, output, scaleArg] = process.argv.slice(2);
  if (!input || !output) {
    console.error('usage: node render.cjs <in.bpmn> <out.png> [scale]');
    process.exit(2);
  }
  const scale = Number(scaleArg || 2);
  const xml = fs.readFileSync(input, 'utf8');
  const dist = path.join(__dirname, 'node_modules/bpmn-js/dist');
  const viewerJs = fs.readFileSync(path.join(dist, 'bpmn-viewer.production.min.js'), 'utf8');
  const css = ['diagram-js.css', 'bpmn-js.css']
    .map((f) => fs.readFileSync(path.join(dist, 'assets', f), 'utf8'))
    .join('\n');

  const browser = await puppeteer.launch({ executablePath: CHROME, headless: true });
  try {
    const page = await browser.newPage();
    await page.setContent(
      `<html><head><meta charset="utf-8"><style>${css}
       body{margin:0;font-family:"Hiragino Sans","Hiragino Kaku Gothic ProN",sans-serif}
       #canvas{width:2400px;height:1600px}</style></head>
       <body><div id="canvas"></div></body></html>`
    );
    await page.addScriptTag({ content: viewerJs });
    const { svg, warnings } = await page.evaluate(async (diagramXml) => {
      const viewer = new BpmnJS({ container: '#canvas' });
      const { warnings } = await viewer.importXML(diagramXml);
      const { svg } = await viewer.saveSVG();
      return { svg, warnings: warnings.map((w) => w.message) };
    }, xml);
    // A diagram that imports with warnings may render with missing or misplaced shapes.
    console.log(`import warnings: ${warnings.length}`);
    warnings.forEach((w) => console.log(`  - ${w}`));

    // Render the exported SVG on a white background and screenshot it at the requested scale.
    const svgPage = await browser.newPage();
    const m = svg.match(/width="([\d.]+)" height="([\d.]+)"/);
    const width = Math.ceil(Number(m[1]));
    const height = Math.ceil(Number(m[2]));
    await svgPage.setViewport({ width, height, deviceScaleFactor: scale });
    await svgPage.setContent(
      `<html><head><meta charset="utf-8"><style>
       body{margin:0;background:#fff;font-family:"Hiragino Sans","Hiragino Kaku Gothic ProN",sans-serif}
       </style></head><body>${svg}</body></html>`
    );
    const el = await svgPage.$('svg');
    await el.screenshot({ path: output, omitBackground: false });
    console.log(`${input} -> ${output} (${width}x${height} @${scale}x)`);
    if (warnings.length) process.exitCode = 1;
  } finally {
    await browser.close();
  }
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
