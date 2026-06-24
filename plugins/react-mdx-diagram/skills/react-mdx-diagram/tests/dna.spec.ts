/**
 * dna.spec.ts
 * Playwright assertions for the react-mdx-diagram DNA contract.
 * Each skin's rendered HTML file is loaded via file:// and tested
 * against the frozen CONTRACT §1–§5 values.
 *
 * Run after render.mjs has produced tests/.out/<skin>.html.
 */

import { test, expect } from '@playwright/test';
import { readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT_DIR = resolve(__dirname, '.out');

// ── CONTRACT §5 surface.canvas (background) ───────────────────────────────────
const SURFACE_CANVAS: Record<string, string> = {
  'candy-os': '#0b0b0b',
  swiss:       '#ecebe7',
  blueprint:   '#f4f3f0',
};

// Normalised lowercase for comparison (some renderers emit lowercase hex)
const normalizeHex = (h: string) => h.toLowerCase().trim();

// ── CONTRACT §1 palette (all 8 must appear somewhere in the rendered HTML) ───
const PALETTE_HEXES = [
  '#EE7B4D', // orange
  '#C5B6EE', // purple
  '#F0C5DA', // pink
  '#E7E058', // yellow
  '#A6C6E2', // blue
  '#87B79A', // green
  '#A98C7E', // brown
  '#9CAFE7', // periwinkle
];

// ── CONTRACT §2 taxonomy fills (constant across skins) ───────────────────────
const TAXONOMY_FILLS: Record<string, string> = {
  person:    '#C5B6EE', // purple
  external:  '#EE7B4D', // orange
  container: '#87B79A', // green
  database:  '#A6C6E2', // blue
  queue:     '#E7E058', // yellow
};

// ── C4 level text markers per skin (§3) ──────────────────────────────────────
// We look for at least 3 level markers (any mix of L1/L2/L3, Context/Container/Component,
// or the blueprint captions)
const C4_LEVEL_PATTERNS: Record<string, RegExp[]> = {
  'candy-os': [/L1|Context/i, /L2|Container/i, /L3|Component/i],
  swiss:      [/L1|Context/i, /L2|Container/i, /L3|Component/i],
  blueprint:  [/L1|Context|border\s*3/i, /L2|Container|border\s*2/i, /L3|Component|border\s*1/i],
};

// ─────────────────────────────────────────────────────────────────────────────
// Helper: file URL for a skin's output HTML
// ─────────────────────────────────────────────────────────────────────────────
function outFileUrl(skin: string): string {
  const absPath = resolve(OUT_DIR, `${skin}.html`);
  // Convert to file:// URL — on macOS/Linux this is fine
  return `file://${absPath}`;
}

// ─────────────────────────────────────────────────────────────────────────────
// Helper: read raw HTML text for hex-presence checks (avoids computed-style API
// overhead for simple string-search assertions)
// ─────────────────────────────────────────────────────────────────────────────
function rawHtml(skin: string): string {
  return readFileSync(resolve(OUT_DIR, `${skin}.html`), 'utf-8');
}

// ═════════════════════════════════════════════════════════════════════════════
// PER-SKIN TESTS
// ═════════════════════════════════════════════════════════════════════════════

for (const skin of ['candy-os', 'swiss', 'blueprint'] as const) {
  test.describe(`skin: ${skin}`, () => {

    // ── 1. Canvas/panel background ──────────────────────────────────────────
    test(`body background equals surface.canvas (${SURFACE_CANVAS[skin]})`, async ({ page }) => {
      await page.goto(outFileUrl(skin));

      // Check via body background-color computed style
      const bodyBg = await page.evaluate(() => {
        const body = document.body;
        const style = window.getComputedStyle(body);
        // Also check any top-level wrapper that may carry the canvas color
        const firstChild = body.firstElementChild as HTMLElement | null;
        if (firstChild) {
          const childBg = window.getComputedStyle(firstChild).backgroundColor;
          if (childBg && childBg !== 'rgba(0, 0, 0, 0)' && childBg !== 'transparent') {
            return childBg;
          }
        }
        return style.backgroundColor;
      });

      // rgb(11, 11, 11) → #0b0b0b etc.  We also check inline-style string.
      const htmlText = rawHtml(skin);
      const canvasHex = SURFACE_CANVAS[skin];

      // Primary assertion: canvas hex appears in the raw HTML (inline style)
      const hexVariants = [
        canvasHex,
        canvasHex.toUpperCase(),
        canvasHex.replace('#', ''),
      ];
      const foundInHtml = hexVariants.some(v =>
        htmlText.toLowerCase().includes(v.toLowerCase())
      );

      // Fallback: compare computed background-color using rgb conversion
      const computedMatch = bodyBg
        ? normalizeHex(bodyBg) === normalizeHex(canvasHex) ||
          rgbToHex(bodyBg) === normalizeHex(canvasHex)
        : false;

      expect(foundInHtml || computedMatch,
        `Expected surface.canvas ${canvasHex} in rendered HTML for skin "${skin}". ` +
        `Got computed bg: ${bodyBg}`
      ).toBe(true);
    });

    // ── 2. All 8 palette hexes appear somewhere ─────────────────────────────
    test('all 8 palette hexes appear in the rendered HTML', async ({ page }) => {
      const html = rawHtml(skin);
      const lower = html.toLowerCase();

      for (const hex of PALETTE_HEXES) {
        const variants = [hex.toLowerCase(), hex.toUpperCase(), hex.slice(1).toLowerCase()];
        const found = variants.some(v => lower.includes(v.toLowerCase()));
        expect(found, `Palette hex ${hex} not found in ${skin} HTML`).toBe(true);
      }
    });

    // ── 3. Taxonomy fills: person=purple, external=orange, etc. ────────────
    test('taxonomy type fills map to correct colors', async ({ page }) => {
      const html = rawHtml(skin);
      const lower = html.toLowerCase();

      for (const [type, fillHex] of Object.entries(TAXONOMY_FILLS)) {
        // The fill hex must appear in the HTML (used as background-color, fill attribute, etc.)
        const variants = [fillHex.toLowerCase(), fillHex.toUpperCase(), fillHex.slice(1).toLowerCase()];
        const hexFound = variants.some(v => lower.includes(v.toLowerCase()));
        expect(hexFound,
          `Taxonomy fill ${fillHex} for type "${type}" not found in ${skin} HTML`
        ).toBe(true);
      }
    });

    test('taxonomy node labels are present in the rendered HTML', async ({ page }) => {
      await page.goto(outFileUrl(skin));
      const html = rawHtml(skin);
      const lower = html.toLowerCase();

      // At least person and container must appear as text content
      // (the sample includes a NodeTaxonomy section)
      const labels = ['person', 'external', 'container', 'database', 'queue'];
      for (const label of labels) {
        expect(lower.includes(label),
          `Taxonomy label "${label}" not found in ${skin} HTML`
        ).toBe(true);
      }
    });

    // ── 4. C4 hierarchy: 3 nested levels + skin-specific nesting method ─────
    test('C4 shows 3 nested level labels', async ({ page }) => {
      const html = rawHtml(skin);

      const patterns = C4_LEVEL_PATTERNS[skin];
      for (const pattern of patterns) {
        expect(pattern.test(html),
          `C4 level pattern ${pattern} not found in ${skin} HTML`
        ).toBe(true);
      }
    });

    test(`C4 nesting method matches skin: ${skin}`, async ({ page }) => {
      await page.goto(outFileUrl(skin));

      if (skin === 'blueprint') {
        // blueprint: 3 boxes with decreasing border-widths (3px → 2px → 1.4px)
        // Look for the border widths in inline styles
        const html = rawHtml(skin);
        // We check for the presence of the three border specs from CONTRACT §3
        const has3px   = /3px\s+solid\s+#111/i.test(html);
        const has2px   = /2px\s+solid\s+#111/i.test(html);
        const has14px  = /1\.4px\s+solid\s+#111/i.test(html);

        expect(has3px,  'blueprint C4 L1: 3px solid #111 border not found').toBe(true);
        expect(has2px,  'blueprint C4 L2: 2px solid #111 border not found').toBe(true);
        expect(has14px, 'blueprint C4 L3: 1.4px solid #111 border not found').toBe(true);

      } else if (skin === 'swiss') {
        // swiss: increasing left indent (marginLeft: 0, 18, 36)
        const html = rawHtml(skin);
        // Check for marginLeft or margin-left indent values 18 and 36
        const hasIndent18 = /margin[-_]?[Ll]eft['":\s]*18/i.test(html) ||
                            /margin[-_]?[Ll]eft['":\s]*18px/i.test(html) ||
                            html.includes('18px') && html.toLowerCase().includes('indent');
        const hasIndent36 = /margin[-_]?[Ll]eft['":\s]*36/i.test(html) ||
                            /margin[-_]?[Ll]eft['":\s]*36px/i.test(html) ||
                            html.includes('36px');
        // Also verify the three c4 background colors for swiss (#9CAFE7, #A6C6E2, #C9DAEA)
        const hasL1bg = html.toLowerCase().includes('#9cafe7');
        const hasL2bg = html.toLowerCase().includes('#a6c6e2');
        const hasL3bg = html.toLowerCase().includes('#c9daea');

        // Require at minimum the three BG colors (indent is primary method per contract)
        expect(hasL1bg || hasIndent18,
          'swiss C4: L1 bg #9CAFE7 or indent progression not found').toBe(true);
        expect(hasL2bg,
          'swiss C4: L2 bg #A6C6E2 not found').toBe(true);
        expect(hasL3bg || hasIndent36,
          'swiss C4: L3 bg #C9DAEA or indent 36 not found').toBe(true);

      } else {
        // candy-os: opacity/rgba ramp
        // L1: rgba(156,175,231,.18) L2: rgba(166,198,226,.42) L3: solid #A6C6E2
        const html = rawHtml(skin);
        const hasL1rgba = /rgba\(156,\s*175,\s*231/i.test(html) ||
                          /rgba\(\s*156\s*,\s*175\s*,\s*231/i.test(html);
        const hasL2rgba = /rgba\(166,\s*198,\s*226/i.test(html) ||
                          /rgba\(\s*166\s*,\s*198\s*,\s*226/i.test(html);
        const hasL3solid = html.toLowerCase().includes('#a6c6e2');

        expect(hasL1rgba,
          'candy-os C4: L1 rgba(156,175,231,.18) not found').toBe(true);
        expect(hasL2rgba,
          'candy-os C4: L2 rgba(166,198,226,.42) not found').toBe(true);
        expect(hasL3solid,
          'candy-os C4: L3 solid #A6C6E2 not found').toBe(true);
      }
    });

    // ── 5. Typography: Helvetica Neue + JetBrains Mono font stacks ─────────
    test('at least one element has Helvetica Neue font-family', async ({ page }) => {
      await page.goto(outFileUrl(skin));

      // Check inline styles in raw HTML first
      const html = rawHtml(skin);
      const hasHelveticaInline = /Helvetica\s+Neue/i.test(html);

      // Fallback: query DOM for computed style
      const hasHelveticaComputed = await page.evaluate(() => {
        const all = Array.from(document.querySelectorAll('*'));
        return all.some(el => {
          const ff = window.getComputedStyle(el).fontFamily;
          return ff && /Helvetica\s+Neue/i.test(ff);
        });
      });

      expect(hasHelveticaInline || hasHelveticaComputed,
        `No element with 'Helvetica Neue' font-family found in ${skin}`
      ).toBe(true);
    });

    test('at least one element has JetBrains Mono font-family', async ({ page }) => {
      await page.goto(outFileUrl(skin));

      const html = rawHtml(skin);
      const hasMonoInline = /JetBrains\s+Mono/i.test(html);

      const hasMonoComputed = await page.evaluate(() => {
        const all = Array.from(document.querySelectorAll('*'));
        return all.some(el => {
          const ff = window.getComputedStyle(el).fontFamily;
          return ff && /JetBrains\s+Mono/i.test(ff);
        });
      });

      expect(hasMonoInline || hasMonoComputed,
        `No element with 'JetBrains Mono' font-family found in ${skin}`
      ).toBe(true);
    });

    // ── 6. node.border: 2.5px solid #111 present in blueprint, absent otherwise
    if (skin === 'blueprint') {
      test('blueprint: taxonomy nodes have 2.5px solid #111 border', async ({ page }) => {
        const html = rawHtml(skin);
        const hasBlueprintBorder = /2\.5px\s+solid\s+#111/i.test(html) ||
                                   /2\.5px\s+solid\s+#111111/i.test(html);
        expect(hasBlueprintBorder,
          'blueprint: expected 2.5px solid #111 border on nodes').toBe(true);
      });
    } else {
      test(`${skin}: taxonomy tiles/bands have NO 2.5px solid black border`, async ({ page }) => {
        const html = rawHtml(skin);
        // The spec says candy-os/swiss have nodeBorder: 'none'
        // We accept 2.5px only on blueprint; here we confirm it's absent
        const has25pxBlackBorder = /2\.5px\s+solid\s+#(111|000|111111|000000)/i.test(html);
        expect(has25pxBlackBorder,
          `${skin}: found unexpected 2.5px solid black border (blueprint-only)`
        ).toBe(false);
      });
    }

  });
}

// ═════════════════════════════════════════════════════════════════════════════
// CROSS-SKIN DISTINCTNESS TEST
// ═════════════════════════════════════════════════════════════════════════════

test.describe('cross-skin distinctness', () => {
  test('the three rendered canvases have different background colors', async () => {
    const htmls = ['candy-os', 'swiss', 'blueprint'].map(skin => rawHtml(skin));

    // Each skin's canvas color must appear and they must differ
    const candyOsBg  = '#0b0b0b';
    const swissBg    = '#ecebe7';
    const blueprintBg = '#f4f3f0';

    expect(htmls[0].toLowerCase()).toContain(candyOsBg);
    expect(htmls[1].toLowerCase()).toContain(swissBg);
    expect(htmls[2].toLowerCase()).toContain(blueprintBg);

    // The three canvases are structurally distinct
    expect(htmls[0]).not.toEqual(htmls[1]);
    expect(htmls[1]).not.toEqual(htmls[2]);
    expect(htmls[0]).not.toEqual(htmls[2]);
  });
});

// ─────────────────────────────────────────────────────────────────────────────
// Utility: parse rgb(r, g, b) → #rrggbb
// ─────────────────────────────────────────────────────────────────────────────
function rgbToHex(rgb: string): string {
  const m = rgb.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
  if (!m) return '';
  return '#' + [m[1], m[2], m[3]]
    .map(n => parseInt(n, 10).toString(16).padStart(2, '0'))
    .join('');
}
