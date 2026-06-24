# Quality Checklist — react-mdx-diagram Rewrite

Rubric derived from CONTRACT §9. Total = 100 pts.
**PASS = total ≥ 85 AND no CRITICAL dimension scored 0 AND playwright green AND check_mdx green.**

See `scripts/score.py` for the automated scorer (supply a `score-input.json`).

---

## Dimension 1 · DNA Fidelity — 25 pts · **CRITICAL**

Verifies that the shared visual DNA (palette, taxonomy fills, typography) is intact and
identical across all three skins.

| # | Item | Pts | Pass condition |
|---|------|-----|----------------|
| 1.1 | All 8 palette hexes present and unaltered (§1): `#EE7B4D` `#C5B6EE` `#F0C5DA` `#E7E058` `#A6C6E2` `#87B79A` `#A98C7E` `#9CAFE7` | 8 | Every hex appears verbatim in `T.palette` in all 3 theme files and in the 3 MDX samples |
| 1.2 | 5 node taxonomy fills correct and constant across skins (§2): person `#C5B6EE`, external `#EE7B4D`, container `#87B79A`, database `#A6C6E2`, queue `#E7E058` | 7 | `T.node.<type>.fill` matches §2 in every theme file; Playwright confirms tile fill colors |
| 1.3 | `font.sans` stack is `'Helvetica Neue',Helvetica,Arial,sans-serif` (§4) in all 3 themes | 5 | Exact string match in each `T.font.sans` |
| 1.4 | `font.mono` stack is `'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,monospace` (§4) in all 3 themes | 3 | Exact string match in each `T.font.mono` |
| 1.5 | Node label text and glyphs use `#111` (black) in every skin including dark candy-os (§2) | 2 | Glyph fill or stroke `#111` present in rendered samples |

**Subtotal: 25 pts. Earned = sum of passed items (capped at 25).**

---

## Dimension 2 · Skin Completeness & Distinctness — 20 pts · **CRITICAL**

Verifies that all three presets are implemented, each faithfully matches §5 token table,
and the C4 nesting method differs per skin (§3).

| # | Item | Pts | Pass condition |
|---|------|-----|----------------|
| 2.1 | All 3 skin theme files exist: `assets/theme.candy-os.ts`, `assets/theme.swiss.ts`, `assets/theme.blueprint.ts` + `assets/theme.default.ts` re-exports blueprint (§8) | 3 | All 4 files present; `theme.default.ts` re-exports blueprint |
| 2.2 | `canvas` / `panel` tokens per skin (§5): candy-os `#0B0B0B`, swiss `#ECEBE7`, blueprint `#F4F3F0` | 3 | `T.surface.canvas` matches in each file |
| 2.3 | `node.border` token: `none` in candy-os & swiss, `2.5px solid #111` in blueprint (§5) | 3 | `T.style.nodeBorder` matches; Playwright confirms border present in blueprint, absent in candy/swiss |
| 2.4 | Edge tokens differ: candy-os width `3.4` / color `#EDEBE6` / style `straight`; swiss width `1.8` / color `#141414` / style `straight`; blueprint width `3` / color `#111` / style `orthogonal` (§5) | 3 | `T.edge.*` values match per-skin |
| 2.5 | C4 nesting method differs by skin (§3): blueprint = nested boxes with 3 decreasing border widths (`3px`→`2px`→`1.4px`); swiss = increasing indent (`0`/`18px`/`36px`); candy-os = opacity ramp on blue | 5 | `T.c4.l1/l2/l3` border/indent values match §3; Playwright confirms distinct nesting patterns |
| 2.6 | `icon.mode` per skin (§5): candy-os `fill`, swiss `line`, blueprint `fill`; glyph SVG paths differ accordingly (§2) | 3 | `T.style.iconMode` matches; MDX samples use correct SVG path variants |

**Subtotal: 20 pts. Earned = sum of passed items (capped at 20).**

---

## Dimension 3 · Render Portability — 20 pts · **CRITICAL**

Verifies that all MDX files compile and are safe on all hosts per the renderability contract (§0).

| # | Item | Pts | Pass condition |
|---|------|-----|----------------|
| 3.1 | `check_mdx.py` exits 0 on all 3 sample files (`assets/samples/reference.candy-os.mdx`, `reference.swiss.mdx`, `reference.blueprint.mdx`) | 8 | `python3 scripts/check_mdx.py assets/samples/reference.*.mdx` returns exit code 0 |
| 3.2 | No nested Capitalized JSX tags inside any component (§0) — only lowercase HTML / helper function calls inside archetypes | 5 | `check_mdx.py` clean (covered by 3.1); manual inspection confirms no `<PascalCase>` inside diagram bodies |
| 3.3 | All MDX samples compile via `@mdx-js/mdx` `evaluate` without error (§8 TEST AGENT) | 4 | `tests/render.mjs` produces `.out/*.html` without throwing for all 3 skins |
| 3.4 | No import statements in any MDX sample (§0 — inline-style React only, no imports/libraries) | 3 | Grep for `^import ` in MDX samples returns empty |

**Subtotal: 20 pts. Earned = sum of passed items (capped at 20).**

---

## Dimension 4 · Prototype Fidelity — 15 pts · not critical

Verifies faithful reproduction of the `Directions.dc.html` prototype details.

| # | Item | Pts | Pass condition |
|---|------|-----|----------------|
| 4.1 | Correct glyph SVG paths used for both `fill` and `line` variants per §2 (all 5 node types: person, external, container, database, queue) | 5 | Exact SVG path strings from §2 appear in MDX samples or archetype source |
| 4.2 | Blueprint nodes carry `2.5px solid #111` keyline; external nodes in blueprint are dashed (`dashedExternal: true`) (§5) | 3 | `T.style.nodeBorder` = `2.5px solid #111`; `T.style.dashedExternal` = `true`; rendered blueprint shows dashed border on external nodes |
| 4.3 | `[type-tags]` mono labels appear in blueprint samples (`showTag: true`) and are absent in candy-os / swiss (`showTag: false`) (§5) | 3 | `T.style.showTag` values correct; Playwright checks presence/absence of tag text |
| 4.4 | Group boundary treatment per skin (§5): blueprint = dashed `#111` + label (`keyline`), swiss = indent only, candy-os = subtle rounded bg (`soft`) | 2 | `T.style.groupBoundary` values match: `keyline`, `indent`, `soft` |
| 4.5 | `swiss` skin has dashed lifeline `#B8B6AE` (edge.lifeline token) and `band` node layout; candy-os and blueprint have `tile` layout (§5) | 2 | `T.edge.lifeline` set in swiss, null in others; `T.style.nodeLayout` correct per skin |

**Subtotal: 15 pts. Earned = sum of passed items (capped at 15).**

---

## Dimension 5 · Playwright Tests — 15 pts · **CRITICAL**

Verifies that the test suite exists, is wired up correctly, and all assertions pass for all 3 skins.

| # | Item | Pts | Pass condition |
|---|------|-----|----------------|
| 5.1 | Test infrastructure files exist: `tests/package.json`, `tests/playwright.config.ts`, `tests/render.mjs`, `tests/dna.spec.ts` (§8 TEST AGENT) | 3 | All 4 files present under `tests/` |
| 5.2 | Playwright canvas/panel background assertion passes for all 3 skins (§8): candy-os `#0B0B0B`, swiss `#ECEBE7`, blueprint `#F4F3F0` | 3 | `dna.spec.ts` bg assertion green for all 3 |
| 5.3 | All 8 palette hexes detected in rendered output for each skin (§8) | 2 | `dna.spec.ts` palette assertion green for all 3 |
| 5.4 | 5 taxonomy labels present and fills map correctly in rendered output (§8) | 2 | `dna.spec.ts` taxonomy assertion green for all 3 |
| 5.5 | C4 three nested levels (L1/L2/L3) present and nesting method matches skin (§8) | 2 | `dna.spec.ts` C4 assertion green for all 3 |
| 5.6 | Font stack assertions pass: Helvetica Neue element and JetBrains Mono element both present (§8) | 1 | `dna.spec.ts` font assertion green |
| 5.7 | Skin-distinctness assertion: rendered canvases are NOT identical across the 3 skins (§8) | 1 | `dna.spec.ts` distinctness assertion green |
| 5.8 | `cd tests && npm i && npx playwright test` exits 0 (all assertions pass) | 1 | Full Playwright run green |

**Subtotal: 15 pts. Earned = sum of passed items (capped at 15).**

---

## Dimension 6 · Docs & Integration — 5 pts · not critical

Verifies human documentation and SKILL.md wiring are in place.

| # | Item | Pts | Pass condition |
|---|------|-----|----------------|
| 6.1 | `references/style-guide.md` exists and covers: palette, taxonomy, C4 method per skin, §5 token table, when-to-pick-which, T serialization (§8 THEME AGENT) | 2 | File present; contains sections for DNA, all 3 skins, token table |
| 6.2 | `references/canon.md` exists and covers: new T shape, renderability contract, node-taxonomy primitives + glyphs, C4 method per skin, all 11 archetypes with skin-branching (§8 CANON AGENT) | 2 | File present; all 11 archetypes documented |
| 6.3 | `SKILL.md` preset-selection wiring present (§8 ORCHESTRATOR) | 1 | `SKILL.md` references the 3 skin presets (candy-os / swiss / blueprint) |

**Subtotal: 5 pts. Earned = sum of passed items (capped at 5).**

---

## GATE Rule

```
PASS  iff  total ≥ 85
       AND  dim-1 earned > 0  (DNA Fidelity not zeroed)
       AND  dim-2 earned > 0  (Skin Completeness not zeroed)
       AND  dim-3 earned > 0  (Render Portability not zeroed)
       AND  dim-5 earned > 0  (Playwright Tests not zeroed)
       AND  playwright_green == true
       AND  check_mdx_green  == true
```

On FAIL: `scripts/score.py` emits the per-dimension gap and every failed item
grouped by dimension. The orchestrator dispatches parallel fix agents by dimension,
then re-runs the scorer. Maximum 3 fix rounds.

---

## How to Score

1. Run the test suite and check_mdx, collect results into `score-input.json`
   (see `scripts/score-input.example.json` for the expected shape).
2. Run the scorer:
   ```
   python3 scripts/score.py score-input.json
   ```
   Or with a custom threshold:
   ```
   python3 scripts/score.py score-input.json --threshold 90
   ```
3. Read the PASS/FAIL verdict and the list of failed items. Feed failures to
   the appropriate fix agent (by dimension).
