/**
 * render.mjs
 * Compiles each reference MDX fixture using @mdx-js/mdx evaluate(),
 * renders to static HTML via react-dom/server renderToStaticMarkup(),
 * wraps in a full HTML document with inline font-stack styles,
 * and writes to tests/.out/<skin>.html.
 *
 * Run: node render.mjs
 */

import { evaluate } from '@mdx-js/mdx';
import * as runtime from 'react/jsx-runtime';
import { renderToStaticMarkup } from 'react-dom/server';
import { readFileSync, mkdirSync, writeFileSync, existsSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SKILL_ROOT = resolve(__dirname, '..');
const SAMPLES_DIR = resolve(SKILL_ROOT, 'assets', 'samples');
const OUT_DIR = resolve(__dirname, '.out');

const SKINS = ['candy-os', 'swiss', 'blueprint'];

// Inline font-stack style injected into every HTML doc.
// Google Fonts link is included for online environments, but tests rely
// on the fallback stack so they pass fully offline.
const FONT_STYLE = `
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
  /* Fallback font stack — must degrade gracefully when offline */
  :root {
    --font-sans: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    --font-mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
  }
  body {
    margin: 0;
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
  }
  code, pre, .mono {
    font-family: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
  }
</style>
`.trim();

function wrapHtml(skin, bodyContent) {
  return `<!DOCTYPE html>
<html lang="en" data-skin="${skin}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>react-mdx-diagram · ${skin}</title>
  ${FONT_STYLE}
</head>
<body style="margin:0">
${bodyContent}
</body>
</html>`;
}

async function renderSkin(skin) {
  const mdxPath = resolve(SAMPLES_DIR, `reference.${skin}.mdx`);

  if (!existsSync(mdxPath)) {
    throw new Error(
      `Missing fixture: ${mdxPath}\n` +
      `The CANON AGENT sample files must be present before rendering.\n` +
      `Expected: assets/samples/reference.${skin}.mdx`
    );
  }

  const mdxSource = readFileSync(mdxPath, 'utf-8');

  // evaluate() compiles + evaluates MDX; returns { default: Component, ...exports }
  const { default: Content } = await evaluate(mdxSource, {
    ...runtime,
    // Pass Fragment so MDX can wrap multi-root returns
    Fragment: runtime.Fragment,
    baseUrl: import.meta.url,
  });

  // Render the MDX default export to static HTML
  const markup = renderToStaticMarkup(
    runtime.jsx(Content, {})
  );

  const html = wrapHtml(skin, markup);

  const outPath = resolve(OUT_DIR, `${skin}.html`);
  writeFileSync(outPath, html, 'utf-8');
  console.log(`[render] wrote ${outPath} (${html.length} bytes)`);
}

async function main() {
  mkdirSync(OUT_DIR, { recursive: true });

  const errors = [];
  for (const skin of SKINS) {
    try {
      await renderSkin(skin);
    } catch (err) {
      console.error(`[render] ERROR for skin "${skin}": ${err.message}`);
      errors.push({ skin, error: err.message });
    }
  }

  if (errors.length > 0) {
    console.error('\n[render] Failed skins:');
    for (const { skin, error } of errors) {
      console.error(`  ${skin}: ${error}`);
    }
    process.exit(1);
  }

  console.log('[render] All skins rendered successfully.');
}

main();
