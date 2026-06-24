# Canon — component vocabulary, theme pattern, and archetypes

This is the visual and structural vocabulary every diagram shares so a document
full of them reads as one coherent set. Read this before authoring.

The guiding constraint: **self-contained inline-style React, no external
libraries and no imports**. No React Flow, Mermaid, chart libs, or icon
packages; no importing the project's own components either. Everything is plain
JSX with inline `style={{}}` objects laid out with flexbox, so it renders in any
MDX host (Astro, Next, Docusaurus) with zero setup. Unicode glyphs stand in for
icons (`▼ → ↓ ✅ ⚠️ 💡 🔁 📄 ❗`).

Even when a project has a real design system bound, the output stays inline —
the binding changes the *token values* and the *component names*, never the
"no-import" rule. See `design-system-binding.md` for why.

## Table of contents
- [The theme-const pattern](#the-theme-const-pattern) — how a profile's theme reaches the MDX
- [Canon primitives](#canon-primitives) — the named building blocks
- [Canon archetypes](#canon-archetypes) — the diagram shapes you actually author
- [The data-driven rule](#the-data-driven-rule)
- [Naming](#naming) — and how design-system binding renames things

## The theme-const pattern

Because output is self-contained, a diagram can't `import` the profile's
`theme.ts`. Instead, **serialize the theme into the MDX once** as a module-scope
const, and have every diagram component read from it. This is the mechanism that
makes a re-theme restyle the whole document: change the const, every diagram
follows.

At the very top of the MDX file (module scope, hoisted by MDX):

```mdx
export const T = {
  font: { sans: '-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif' },
  surface: { canvas: '#f8fafc', card: '#fff', border: '#e2e8f0' },
  problem:  { bg: '#fff1f2', border: '#fca5a5', text: '#7f1d1d', accent: '#dc2626' },
  solution: { bg: '#f0fdf4', border: '#86efac', text: '#14532d', accent: '#16a34a' },
  neutral:  { bg: '#f1f5f9', border: '#cbd5e1', text: '#334155', accent: '#475569' },
  ink: { heading: '#1e293b', body: '#475569', muted: '#94a3b8', line: '#cbd5e1' },
  step: ['#6366f1', '#0ea5e9', '#16a34a', '#d97706'],
}
```

Copy the values from the project's profile `theme.ts` (run
`scripts/profile.py show`). Include only the families a document actually uses —
don't dump the whole token set if three diagrams need three colors. Every
diagram component below then references `T.problem.bg` etc. instead of literal
hexes, so the values live in exactly one place.

## Renderability contract (read this — it's the #1 way diagrams break)

Capitalized JSX tags are the source of two host-dependent breakages:
- Standard MDX throws `Expected component 'X' to be defined` for a capitalized
  tag not in scope.
- Some hosts (notably the **VS Code MDX preview**) inject a component binding for
  *every* capitalized tag they see — including nested ones — which collides with
  a local `const X` and throws `Identifier 'X' has already been declared` at
  compile time. Standard `@mdx-js/mdx` does NOT reproduce this, so "it compiled
  for me" doesn't prove portability.

One portable rule avoids both (it's exactly what the predecessor skill did
everywhere without trouble):

- The **only** capitalized JSX tags in the file are the top-level archetype
  components, used at **column 0** in the markdown body as `<Foo/>`.
- **Inside** a diagram, build with **lowercase HTML elements** (`<div>`,
  `<span>`, `<pre>`) and `.map()`. For a reusable piece, define a **lowercase
  helper function** and **call** it — `{panel(a)}` — never a `<Panel/>` tag.
- The value object `T` is fine at module scope (read as `T.x`, never `<T>`).

So the shape of every diagram is:
```mdx
export const T = { /* theme */ }

export const SomeDiagram = () => {
  const node  = (c, title) => (<div style={{ /* uses T */ }}>{title}</div>)
  const badge = (c, label) => (<span style={{ /* uses T */ }}>{label}</span>)
  const data = [ /* ... */ ]
  return (<div>{data.map((d, i) => <div key={i}>{node(d.c, d.title)}</div>)}</div>)
}
```
Run `scripts/check_mdx.py <file>` after writing — it fails on any nested
capitalized tag. (If you have node, `@mdx-js/mdx`'s `compile()` is a bonus check,
but it won't catch the VS Code-preview collision — the static lint is the gate.)

## Canon primitives

These are the named building blocks — a **vocabulary to think in**, realized as
**lowercase helper functions** (called as `{node(...)}`) or inlined directly, per
the renderability contract above. When a project binds a design system, these
names are what get re-mapped (e.g. `Node`→`Card`, `Badge`→`Tag`) — applied to the
lowercase helper names (`card`, `tag`). Keeping the vocabulary stable is what
makes "adapting" mechanical rather than a guess.

| Canon name | What it is | Default shape |
|-----------|-----------|---------------|
| `node` | the atomic box/card holding a label + optional detail | `2px` solid border, `radius.md`, `padding 12–14px`, semantic bg |
| `group` | a labeled container that visually clusters nodes | dashed/solid frame, small uppercase title chip top-left |
| `lane` | a swimlane / vertical column region grouping a flow | flex column, neutral header band, children stacked |
| `edge` | a labeled connector between nodes | thin line (`ink.line`) + optional centered label chip + arrow glyph |
| `badge` | a small status/label pill | `radius.pill`, `caption`/`label` size, accent-tinted bg |
| `note` | a callout / annotation aside | left accent border, muted bg, small body text |

Default implementations as lowercase helpers (read values from `T`; `c` is a
semantic family like `T.problem`):

**node**
```jsx
const node = (c, title, detail) => (
  <div style={{ border: `2px solid ${c.border}`, borderRadius: 10, padding: '12px 14px', background: c.bg }}>
    <div style={{ fontSize: 14, fontWeight: 700, color: T.ink.heading }}>{title}</div>
    {detail && <div style={{ fontSize: 11, color: c.text, marginTop: 6 }}>{detail}</div>}
  </div>
)
```

**badge**
```jsx
const badge = (c, label) => (
  <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 9999, background: `${c.accent}22`, color: c.accent, whiteSpace: 'nowrap', fontWeight: 700 }}>{label}</span>
)
```

**Edge — vertical** (between stacked Nodes): thin line, optional label chip, `▼`.
```jsx
<div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '4px 0', gap: 2 }}>
  <div style={{ width: 2, height: 10, background: T.ink.line }} />
  {label && <div style={{ fontSize: 10, color: T.ink.muted, background: T.surface.canvas, padding: '2px 10px', borderRadius: 4, border: `1px solid ${T.surface.border}` }}>{label}</div>}
  <div style={{ width: 2, height: 10, background: T.ink.line }} />
  <div style={{ color: T.ink.line, fontSize: 14, lineHeight: 1 }}>▼</div>
</div>
```

**Edge — horizontal** (between side-by-side Nodes):
```jsx
<div style={{ display: 'flex', alignItems: 'center', color: T.ink.muted, fontSize: 22, padding: '0 10px' }}>→</div>
```

**Note**
```jsx
<div style={{ borderLeft: `3px solid ${c.accent}`, background: c.bg, padding: '8px 12px', fontSize: 12, color: c.text, borderRadius: 4 }}>{children}</div>
```

**Wrapper** (the frame around a whole diagram):
```jsx
<div style={{ fontFamily: T.font.sans, margin: '2rem 0', padding: 24, background: T.surface.canvas, borderRadius: 12, border: `1px solid ${T.surface.border}` }}>…</div>
```

## Canon archetypes

Read the request (or `(( ))` placeholder), pick the archetype matching its
intent, build it from primitives. These cover the large majority of cases;
combine and adapt freely.

1. **`BeforeAfter`** — two columns; `problem` Node(s) left, `solution` Node(s)
   right, horizontal Edge between, a footer line summarizing the win. For
   `before → after`, `기존 vs 개선`, refactor stories.

2. **`LayerStack`** — Nodes stacked vertically, joined by vertical Edges
   carrying the relationship label (a prop, a ref, a call). For abstraction
   layers, wrapper → abstract → concrete, request pipelines.

3. **`FlowSteps`** — numbered Nodes left-to-right joined by `→`, color cycling
   through `T.step`, often a result banner underneath. For procedures, 단계,
   pipelines, registration flows.

4. **`Architecture`** — Nodes for actors (client, BFF, server, chunks)
   positioned in a small grid/row, connected by labeled directional Edges
   showing what flows between them. For 개념도, 서빙, request routing.

5. **`CardSet`** — when the request *is* content rather than a description (a
   성과/한계 block, a feature list), render a labeled Group of Nodes: a
   `solution` "성과" Node, then `warn`/`problem` "한계" Nodes. Match the structure
   of the content; don't invent a flow where the source is a list.

6. **`Matrix`** (optional) — a 2×2 quadrant with axis labels, for trade-off /
   positioning content.

## The data-driven rule

Declare the content as an array of plain objects at the top of the component,
then `.map()`. This keeps JSX short, makes every Node consistent, and makes
edits trivial (change data, not markup).

```jsx
export const DomainModelBeforeAfter = () => {
  const before = ['거대 LCA Aggregate', '메서드 폭증', 'Row flooding']
  const after  = ['LCA / Process / Data 분리', '도메인 서비스로 상호작용', '프로파일 + CQRS']
  // render two columns from these arrays, reading colors from T.problem / T.solution
}
```

## Naming

Component names are PascalCase and describe the **concept**, derived from the
request — `DomainModelBeforeAfter`, `BffChunkServingDiagram`, `OutcomeAndLimits`.
Avoid generic `Diagram1`.

When a design system is bound, the profile's `binding.json` carries a
`componentNames` map (canon → project vocabulary). Apply it to the **lowercase
helper function names** (per the renderability contract) so the generated code
reads native to that codebase — if their system calls a card a `Panel`, name the
helper `panel` (camelCase) and call it `{panel(...)}`, not `node`. The
concept-level archetype name (`DomainModelBeforeAfter`) stays PascalCase and is
the only thing at module scope as `export const`. If no binding exists, use the
canon names. Fidelity to the source content (labels, numbers, relationships must
be traceable to the document) always overrides style — never invent steps or
figures to look impressive.
