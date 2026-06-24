# react-mdx-diagram — Style Guide

> Human-facing reference for the design system used by all diagram archetypes.
> The frozen source of truth is `CONTRACT.md`. This document reproduces the
> key tables for day-to-day authoring. If anything conflicts, the contract wins.

---

## Part A — Shared DNA

Everything that does NOT change between skins.

### A1. Palette · 8 exact hexes

| Name       | Hex       | Role / node type        |
|------------|-----------|-------------------------|
| orange     | `#EE7B4D` | `external` node fill    |
| purple     | `#C5B6EE` | `person` node fill      |
| pink       | `#F0C5DA` | `data` semantic         |
| yellow     | `#E7E058` | `queue` node fill       |
| blue       | `#A6C6E2` | `database` node fill    |
| green      | `#87B79A` | `container` node fill   |
| brown      | `#A98C7E` | `neutral` semantic      |
| periwinkle | `#9CAFE7` | `second` semantic / C4  |

> In **blueprint** skin, palette swatches carry a `2px solid #111` keyline.
> In **candy-os** and **swiss**, swatches are borderless.

Node label text and glyph strokes are always `#111` (black) in every skin.
The tile is always a light pastel island — this holds even on the dark candy-os canvas.

### A2. Node taxonomy · 5 types

Fills are CONSTANT across all three skins. The mono tag is shown only in **blueprint**
(`style.showTag = true`). Glyphs use `fill="#111"` in fill-mode skins (candy-os, blueprint)
and `fill="none" stroke="#111" stroke-width="1.8"` line variants in **swiss**.

| Type        | Fill hex    | Mono tag       | Glyph shape (24×24 viewBox)      |
|-------------|-------------|----------------|----------------------------------|
| `person`    | `#C5B6EE`   | `[person]`     | Head circle + shoulder path      |
| `external`  | `#EE7B4D`   | `[external]`   | Diagonal arrow out of box        |
| `container` | `#87B79A`   | `[container]`  | Two offset stacked rects         |
| `database`  | `#A6C6E2`   | `[datastore]`  | Cylinder (ellipse cap + path)    |
| `queue`     | `#E7E058`   | `[queue]`      | Three vertical bars              |

For copy-pasteable SVG path data for each glyph (fill and line variants), see
`references/node-glyphs.md`.

### A3. C4 level hierarchy (L1 Context → L2 Container → L3 Component)

All three skins carry three C4 levels. The **method** of expressing nesting differs:

| Skin       | Method                  | L1                                | L2                                | L3                                 |
|------------|-------------------------|-----------------------------------|-----------------------------------|------------------------------------|
| candy-os   | Saturation/opacity ramp | `rgba(156,175,231,.18)` 1px #3A3A3A | `rgba(166,198,226,.42)` none    | `#A6C6E2` solid, no border         |
| swiss      | Indented color bands    | `#9CAFE7` indent 0                | `#A6C6E2` indent 18px             | `#C9DAEA` indent 36px              |
| blueprint  | Nested boxes, shrinking border | `#E4EAF4` 3px solid #111  | `#CFDDEC` 2px solid #111          | `#ffffff` 1.4px solid #111         |

C4 level label colors per skin:

| Level | candy-os   | swiss     | blueprint |
|-------|-----------|-----------|-----------|
| L1    | `#9CAFE7` | `#26345E` | `#555555` |
| L2    | `#A6C6E2` | `#27465A` | `#555555` |
| L3    | `#21323F` | `#48586A` | `#888888` |

### A4. Typography

Two font stacks, used consistently:

| Role              | Stack                                                              | Weight | Size range  | Letter-spacing  |
|-------------------|--------------------------------------------------------------------|--------|-------------|-----------------|
| Sans (display/labels) | `'Helvetica Neue',Helvetica,Arial,sans-serif`                 | 700    | 11–30px     | `-1px` / `-.5px` |
| Mono (tags/captions)  | `'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,monospace` | 400    | 9–13px      | `1.5px`          |

Mono is used for: section labels (`PALETTE · 8`), type-tags (`[person]`), C4 level
captions, edge labels (`yes` / `no` / `uses` / `GET /data`), and step numbers.

JetBrains Mono is loaded via Google Fonts `<link>` when the host allows it; the
fallback stack degrades gracefully without it.

Type scale (`T.type`):

| Key       | px |
|-----------|----|
| `caption` | 10 |
| `tag`     | 9  |
| `label`   | 11 |
| `body`    | 12 |
| `title`   | 14 |
| `big`     | 30 |

---

## Part B — The Three Skins

### B1. candy-os

**Character:** Night-mode design tool aesthetic. A near-black canvas dotted with vivid
pastel tiles — each node pops as a colourful island. Bold straight strokes connect them.
Energy and playfulness without sacrificing legibility; the pastel-on-dark contrast is
deliberately high. C4 nesting is visible but subtle: opacity and saturation shift the
blue family from barely-there at L1 to solid periwinkle at L3.

### B2. swiss

**Character:** Swiss International Typographic Style meets a documentation site. A warm
off-white canvas, maximum type contrast, hairline rules. Nodes are not tiles but full-width
colour bands, giving the layout a grid-like rigour. Icons are line-art only. Sequence and
flow diagrams feel native here. C4 hierarchy reads as progressively indented blue bands —
spatial rhythm over box-drawing.

### B3. blueprint

**Character:** Architecture whiteboard / C4 specification sheet. Bold black keylines on
pastel fills make every boundary unmistakable. Orthogonal routing and thick right-angle
arrows enforce structural reading. Mono `[type-tags]` label every node's role. Dashed
boundary + caption marks system groups. The most information-dense skin; use it when the
diagram IS the spec.

### B4. Skin differentiation table (§5)

| Token                | candy-os                         | swiss                            | blueprint                        |
|----------------------|----------------------------------|----------------------------------|----------------------------------|
| `surface.canvas`     | `#0B0B0B`                        | `#ECEBE7`                        | `#F4F3F0`                        |
| `surface.panel`      | `#0B0B0B`                        | `#ECEBE7`                        | `#F4F3F0`                        |
| `surface.shadow`     | `rgba(0,0,0,.18)`                | `rgba(0,0,0,.10)`                | `rgba(0,0,0,.10)`                |
| `ink.heading`        | `#F1F0ED`                        | `#141414`                        | `#111111`                        |
| `ink.body`           | `#C9C9C6`                        | `#3A3A38`                        | `#33312E`                        |
| `ink.muted`          | `#9A9A97`                        | `#6C6B66`                        | `#6C6B66`                        |
| `ink.tag`            | `#6E6E6B`                        | `#9A988F`                        | `#9A988F`                        |
| `edge.color`         | `#EDEBE6`                        | `#141414`                        | `#111111`                        |
| `edge.width`         | `3.4`                            | `1.8`                            | `3`                              |
| `edge.style`         | `straight`                       | `straight`                       | `orthogonal`                     |
| `edge.lifeline`      | —                                | `#B8B6AE` dashed `4 4`           | —                                |
| `style.nodeRadius`   | `16`                             | `8`                              | `14`                             |
| `style.nodeBorder`   | `none`                           | `none`                           | `2.5px solid #111`               |
| `style.dashedExternal` | `false`                        | `false`                          | `true`                           |
| `style.iconMode`     | `fill`                           | `line`                           | `fill`                           |
| `style.nodeLayout`   | `tile` (96×88)                   | `band` (full-width row)          | `tile` (96×88)                   |
| `style.showTag`      | `false`                          | `false`                          | `true`                           |
| `style.groupBoundary` | `soft` (subtle rounded bg)      | `indent` (indent only)           | `keyline` (dashed #111 + label)  |
| Panel `box-shadow`   | `0 2px 14px rgba(0,0,0,.18)`     | `0 2px 14px rgba(0,0,0,.10)`     | `0 2px 14px rgba(0,0,0,.10)`     |

---

## Part C — Which Skin When

| Situation                                              | Reach for   |
|--------------------------------------------------------|-------------|
| Dark-mode slide deck, keynote, visual explainer        | `candy-os`  |
| Published docs, blog post, editorial walkthrough       | `swiss`     |
| Architecture review, C4 model, technical specification | `blueprint` |
| Default when uncertain                                 | `blueprint` |

`theme.default.ts` re-exports `blueprint`. Changing the default is a one-line edit
in that file.

---

## Part D — Serializing a Skin's `T` into MDX

Each MDX file begins with an inline `const T = {...}` block that contains the token
subset relevant to that diagram. This is how a diagram stays self-contained (no
imports, no external CSS, no libraries).

The orchestrator picks the active skin's `theme.{skin}.ts`, extracts the values, and
writes them verbatim as:

```mdx
export const T = {
  skin: 'blueprint',
  font: { ... },
  surface: { canvas: '#F4F3F0', panel: '#F4F3F0', shadow: '...' },
  ink:     { ... },
  palette: { ... },
  node:    { ... },
  edge:    { ... },
  c4:      { ... },
  style:   { ... },
  semantic: { ... },
  step:    [...],
  radius:  { ... },
  type:    { ... },
  weight:  { ... },
  letterSpacing: { ... },
}
```

Archetype components (e.g. `<Architecture/>`, `<C4Container/>`) close over `T` via
the MDX module scope. They read `T.style.iconMode`, `T.palette.green`, etc. — never
hardcoded hex values.

For the exact canonical component signatures, data-driven rules, and skin-branching
helpers, see `references/canon.md`.
