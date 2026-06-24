# Canon — component vocabulary, theme pattern, and archetypes

This is the visual and structural vocabulary every diagram shares so a document
full of them reads as one coherent set. Read this before authoring.

The guiding constraint: **self-contained inline-style React, no external
libraries and no imports**. No React Flow, Mermaid, chart libs, or icon
packages; no importing the project's own components either. Everything is plain
JSX with inline `style={{}}` objects laid out with flexbox or SVG, so it renders
in any MDX host (Astro, Next, Docusaurus) with zero setup.

## Table of contents
- [The theme-const pattern](#the-theme-const-pattern) — how a skin's theme reaches the MDX
- [Renderability contract](#renderability-contract) — the hard rule, the linter, why it matters
- [Node taxonomy primitives](#node-taxonomy-primitives) — the 5-type system + glyph helpers
- [C4 method per skin](#c4-method-per-skin) — L1→L2→L3 expressed differently by skin
- [Canon archetypes](#canon-archetypes) — all 11 diagram shapes
- [The data-driven rule](#the-data-driven-rule)
- [Naming](#naming)

---

## The theme-const pattern

Because output is self-contained, a diagram can't `import` the profile's
`theme.ts`. Instead, **serialize the theme into the MDX once** as a module-scope
const, and have every diagram component read from it. This is the mechanism
that makes a re-theme restyle the whole document: change the const, every
diagram follows.

### The `T` shape (exact key names — do not rename)

At the very top of the MDX file (module scope, hoisted by MDX):

```js
export const T = {
  skin: 'blueprint',           // 'candy-os' | 'swiss' | 'blueprint'
  font: {
    sans: "'Helvetica Neue',Helvetica,Arial,sans-serif",
    mono: "'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,monospace",
  },
  surface: { canvas:'#F4F3F0', panel:'#F4F3F0', shadow:'0 2px 14px rgba(0,0,0,.10)' },
  ink:     { heading:'#111111', body:'#33312E', muted:'#6C6B66', tag:'#9A988F' },
  palette: {
    orange:'#EE7B4D', purple:'#C5B6EE', pink:'#F0C5DA', yellow:'#E7E058',
    blue:'#A6C6E2',   green:'#87B79A',  brown:'#A98C7E', periwinkle:'#9CAFE7',
  },
  node: {
    person:    { fill:'#C5B6EE', tag:'[person]' },
    external:  { fill:'#EE7B4D', tag:'[external]' },
    container: { fill:'#87B79A', tag:'[container]' },
    database:  { fill:'#A6C6E2', tag:'[datastore]' },
    queue:     { fill:'#E7E058', tag:'[queue]' },
  },
  edge:  { color:'#111111', width:3, style:'orthogonal', label:'#555', lifeline:null },
  c4: {
    l1:{ bg:'#E4EAF4', border:'3px solid #111', label:'#555', indent:0 },
    l2:{ bg:'#CFDDEC', border:'2px solid #111', label:'#555', indent:0 },
    l3:{ bg:'#ffffff', border:'1.4px solid #111', label:'#888', indent:0 },
  },
  style: {
    nodeRadius:14, nodeBorder:'2.5px solid #111', iconMode:'fill',
    nodeLayout:'tile', showTag:true, dashedExternal:true, groupBoundary:'keyline',
  },
  semantic: {
    problem:  { bg:'#EE7B4D', text:'#111', accent:'#7A3B1E' },
    solution: { bg:'#87B79A', text:'#111', accent:'#2C4A3A' },
    info:     { bg:'#A6C6E2', text:'#111', accent:'#27465A' },
    neutral:  { bg:'#A98C7E', text:'#111', accent:'#3E2F28' },
    warn:     { bg:'#E7E058', text:'#111', accent:'#5E5A1E' },
    primary:  { bg:'#C5B6EE', text:'#111', accent:'#3A3550' },
    data:     { bg:'#F0C5DA', text:'#111', accent:'#7A3F58' },
    second:   { bg:'#9CAFE7', text:'#111', accent:'#26345E' },
  },
  step: ['#C5B6EE','#A6C6E2','#87B79A','#E7E058'],
  radius: { sm:8, md:14, lg:16, pill:9999 },
  type:   { caption:10, tag:9, label:11, body:12, title:14, big:30 },
  weight: { normal:400, bold:700 },
  letterSpacing: { mono:'1.5px', tight:'-1px', label:'-.5px' },
}
```

### Per-skin overrides

**candy-os** (dark canvas, solid vivid tiles, fill glyphs, bright connectors):
- `surface.canvas/panel` → `#0B0B0B`; `shadow` → `0 2px 14px rgba(0,0,0,.18)`
- `ink.heading` → `#F1F0ED`; `body` → `#C9C9C6`; `muted` → `#9A9A97`; `tag` → `#6E6E6B`
- `edge.color` → `#EDEBE6`; `width` → `3.4`; `style` → `straight`
- `style.nodeRadius` → `16`; `nodeBorder` → `none`; `iconMode` → `fill`; `nodeLayout` → `tile`; `showTag` → `false`; `dashedExternal` → `false`; `groupBoundary` → `soft`
- `c4.l1` → `{bg:'rgba(156,175,231,.18)', border:'1px solid #3A3A3A', label:'#9CAFE7', indent:0}`
- `c4.l2` → `{bg:'rgba(166,198,226,.42)', border:'none', label:'#A6C6E2', indent:0}`
- `c4.l3` → `{bg:'#A6C6E2', border:'none', label:'#21323F', indent:0}`

**swiss** (light canvas, color bands, line glyphs, thin rules):
- `surface.canvas/panel` → `#ECEBE7`; `shadow` → `0 2px 14px rgba(0,0,0,.10)`
- `ink.heading` → `#141414`; `body` → `#3A3A38`; `muted` → `#6C6B66`; `tag` → `#9A988F`
- `edge.color` → `#141414`; `width` → `1.8`; `style` → `straight`; `lifeline` → `#B8B6AE`
- `style.nodeRadius` → `8`; `nodeBorder` → `none`; `iconMode` → `line`; `nodeLayout` → `band`; `showTag` → `false`; `groupBoundary` → `indent`
- `c4.l1` → `{bg:'#9CAFE7', border:'none', label:'#26345E', indent:0}`
- `c4.l2` → `{bg:'#A6C6E2', border:'none', label:'#27465A', indent:18}`
- `c4.l3` → `{bg:'#C9DAEA', border:'none', label:'#48586A', indent:36}`

**blueprint** (light canvas, bold keylines, fill glyphs, orthogonal arrows, `[type-tags]`, dashed group):
- The literal values shown in the shape above are the blueprint defaults.

---

## Renderability contract

Capitalized JSX tags are the source of two host-dependent breakages:
- Standard MDX throws `Expected component 'X' to be defined` for a capitalized
  tag not in scope.
- Some hosts (notably the **VS Code MDX preview**) inject a component binding
  for *every* capitalized tag they see — including nested ones — which collides
  with a local `const X` and throws `Identifier 'X' has already been declared`
  at compile time.

One portable rule avoids both:

> **The ONLY capitalized JSX tags in the file are the top-level archetype
> `export const`s used at column 0 in the markdown body as `<Foo/>`. Inside
> a diagram, use lowercase HTML elements (`<div>`, `<span>`, `<svg>`, etc.)
> and call lowercase helper functions as `{fn(...)}`. `<svg>` and all its
> lowercase children (`<rect>`, `<path>`, `<text>`, `<marker>`, etc.) are
> fully allowed.**

Run `scripts/check_mdx.py <file>` after writing. It fails on:
1. Any capitalized JSX tag used **nested** (inside a component body).
2. A column-0 body usage with no matching top-level `export const`.

The shape of every diagram file:

```mdx
export const T = { /* theme */ }

export const SomeDiagram = () => {
  const node = (type, label) => (<div style={{…}}>{label}</div>)
  const data = [{…}, {…}]
  return (<div>{data.map((d,i) => <div key={i}>{node(d.type, d.label)}</div>)}</div>)
}

## Heading

<SomeDiagram/>
```

---

## Node taxonomy primitives

Five node types with constant fills across all skins. The glyph changes between
`fill` and `line` mode depending on `T.style.iconMode`.

### Fills (constant, all skins)

| type        | fill hex    | tag label    |
|-------------|-------------|--------------|
| `person`    | `#C5B6EE`   | `[person]`   |
| `external`  | `#EE7B4D`   | `[external]` |
| `container` | `#87B79A`   | `[container]`|
| `database`  | `#A6C6E2`   | `[datastore]`|
| `queue`     | `#E7E058`   | `[queue]`    |

Node label text is always `#111` (black) — the "black glyph/black label on
pastel" rule holds in every skin, including dark `candy-os` (the tile is a
light pastel).

### Skin-branching on `T.style`

| property             | candy-os       | swiss          | blueprint          |
|----------------------|----------------|----------------|--------------------|
| `iconMode`           | `fill`         | `line`         | `fill`             |
| `nodeLayout`         | `tile` (96×88) | `band` (full-width row) | `tile` (96×88) |
| `nodeBorder`         | `none`         | `none`         | `2.5px solid #111` |
| `showTag`            | `false`        | `false`        | `true`             |
| `dashedExternal`     | `false`        | `false`        | `true`             |
| `groupBoundary`      | `soft`         | `indent`       | `keyline`          |

### Glyph helper skeleton (inline in each archetype)

```jsx
// Inside NodeTaxonomy or C4Container:
const glyph = (type) => {
  const fill = T.style.iconMode === 'fill'
  const s = { fill: fill ? '#111' : 'none', stroke: '#111',
               strokeWidth: fill ? 0 : 1.8, overflow:'visible' }
  if (type === 'person')    return (<svg viewBox="0 0 24 24" width="20" height="20" style={s}>
    {fill
      ? [<circle key="c" cx="12" cy="7" r="4"/>,<path key="p" d="M3 22a9 9 0 0 1 18 0Z"/>]
      : [<circle key="c" cx="12" cy="8" r="3.6"/>,<path key="p" d="M5 21a7 7 0 0 1 14 0"/>]}
  </svg>)
  if (type === 'external')  return (<svg viewBox="0 0 24 24" width="20" height="20" style={{fill:'none',stroke:'#111',strokeWidth:fill?2.6:1.8,overflow:'visible'}}>
    <path d="M8 16 17 7"/><path d="M9 7h8v8"/>
  </svg>)
  if (type === 'container') return (<svg viewBox="0 0 24 24" width="20" height="20" style={s}>
    {fill
      ? [<rect key="a" x="3" y="6" width="13" height="12" rx="2.5"/>,<rect key="b" x="9" y="2" width="13" height="12" rx="2.5" opacity=".45"/>]
      : [<rect key="a" x="3" y="5" width="13" height="11" rx="2"/>,<rect key="b" x="8" y="9" width="13" height="11" rx="2"/>]}
  </svg>)
  if (type === 'database')  return (<svg viewBox="0 0 24 24" width="20" height="20" style={s}>
    {fill
      ? [<ellipse key="e" cx="12" cy="5.5" rx="8" ry="3.2"/>,<path key="p" d="M4 5.5v13c0 1.8 3.6 3.2 8 3.2s8-1.4 8-3.2v-13" fill="none" stroke="#111" strokeWidth="2.2"/>]
      : [<ellipse key="e" cx="12" cy="6" rx="7" ry="2.8"/>,<path key="p" d="M5 6v12c0 1.5 3.1 2.8 7 2.8s7-1.3 7-2.8V6"/>]}
  </svg>)
  if (type === 'queue')     return (<svg viewBox="0 0 24 24" width="20" height="20" style={s}>
    {fill
      ? [<rect key="a" x="3" y="5" width="4" height="14" rx="1.5"/>,<rect key="b" x="10" y="5" width="4" height="14" rx="1.5"/>,<rect key="c" x="17" y="5" width="4" height="14" rx="1.5"/>]
      : <path key="p" d="M5 6v12M11 6v12M17 6v12"/>}
  </svg>)
  return null
}
```

For `external`, the `dashedExternal` flag applies to the **node border** in
blueprint (dashed `2.5px`), not the glyph itself. The glyph is always the
arrow-out-of-box pair of paths.

---

## C4 method per skin

All three skins render L1 (Context) → L2 (Container) → L3 (Component), but the
visual nesting mechanism differs:

### candy-os — saturation/opacity nesting

Outer-to-inner uses the blue palette family at increasing opacity/solidity:

```js
// L1 wrapper
{ background:'rgba(156,175,231,.18)', border:'1px solid #3A3A3A', borderRadius:T.style.nodeRadius }
// L2 wrapper (nested inside L1)
{ background:'rgba(166,198,226,.42)', border:'none', borderRadius:T.style.nodeRadius }
// L3 items (solid fill)
{ background:'#A6C6E2', border:'none', borderRadius:T.style.nodeRadius }
// Level labels colored: L1=#9CAFE7, L2=#A6C6E2, L3=#21323F
```

### swiss — indented color bands

Each level shifts indent and lightens the blue:

```js
// L1 band (ml 0, bg #9CAFE7)
{ background: T.c4.l1.bg, marginLeft: T.c4.l1.indent, padding:'8px 12px', borderRadius:T.style.nodeRadius }
// L2 band (ml 18, bg #A6C6E2)
{ background: T.c4.l2.bg, marginLeft: T.c4.l2.indent, … }
// L3 band (ml 36, bg #C9DAEA)
{ background: T.c4.l3.bg, marginLeft: T.c4.l3.indent, … }
// Right-aligned mono L1/L2/L3 tag: colors L1=#26345E, L2=#27465A, L3=#48586A
```

### blueprint — nested boxes with decreasing border width

```js
// L1 box: bg #E4EAF4, border '3px solid #111'
{ background: T.c4.l1.bg, border: T.c4.l1.border, borderRadius: T.style.nodeRadius, padding:16 }
// L2 box nested inside: bg #CFDDEC, border '2px solid #111'
{ background: T.c4.l2.bg, border: T.c4.l2.border, … }
// L3 items: bg #fff, border '1.4px solid #111'
{ background: T.c4.l3.bg, border: T.c4.l3.border, … }
// Mono captions like "L1 · CONTEXT · border 3" in T.ink.muted color
```

---

## Canon archetypes

All 11 archetypes. Names 1–6 are generic (concept diagrams); 7–11 are
architecture/system-design archetypes.

---

### 1. `BeforeAfter`

Two columns: `semantic.problem` node(s) left, `semantic.solution` node(s) right,
horizontal arrow between. Footer summarizes the win.

```jsx
export const BeforeAfter = () => {
  const nb = T.style.nodeBorder === 'none' ? 'none' : T.style.nodeBorder
  const col = (sem, items) => (
    <div style={{flex:1, display:'flex', flexDirection:'column', gap:8}}>
      {items.map((t,i) => (
        <div key={i} style={{background:sem.bg, border:nb, borderRadius:T.style.nodeRadius,
          padding:'10px 14px', fontFamily:T.font.sans, color:'#111', fontSize:T.type.body}}>
          {t}
        </div>
      ))}
    </div>
  )
  return (
    <div style={{fontFamily:T.font.sans, background:T.surface.canvas, padding:24,
      borderRadius:T.style.nodeRadius, boxShadow:T.surface.shadow}}>
      <div style={{display:'flex', gap:16, alignItems:'center'}}>
        {col(T.semantic.problem, ['Before item A','Before item B'])}
        <div style={{fontSize:22, color:T.edge.color}}>→</div>
        {col(T.semantic.solution, ['After item A','After item B'])}
      </div>
    </div>
  )
}
```

---

### 2. `LayerStack`

Nodes stacked vertically joined by vertical arrows with relationship labels.

```jsx
export const LayerStack = () => {
  const layers = [
    {label:'UI Layer', sem:T.semantic.primary},
    {label:'API Layer', sem:T.semantic.info},
    {label:'DB Layer', sem:T.semantic.data},
  ]
  const nb = T.style.nodeBorder === 'none' ? 'none' : T.style.nodeBorder
  return (
    <div style={{fontFamily:T.font.sans, background:T.surface.canvas, padding:24,
      borderRadius:T.style.nodeRadius, boxShadow:T.surface.shadow, display:'flex',
      flexDirection:'column', alignItems:'center', gap:0}}>
      {layers.map((l,i) => (
        <div key={i} style={{width:'100%', display:'flex', flexDirection:'column', alignItems:'center'}}>
          <div style={{width:'100%', background:l.sem.bg, border:nb,
            borderRadius:T.style.nodeRadius, padding:'12px 16px', textAlign:'center',
            fontWeight:T.weight.bold, color:'#111', fontSize:T.type.title}}>{l.label}</div>
          {i < layers.length-1 && (
            <div style={{display:'flex', flexDirection:'column', alignItems:'center', padding:'4px 0', gap:2}}>
              <div style={{width:2, height:16, background:T.edge.color}}/>
              <div style={{color:T.edge.color, fontSize:14}}>▼</div>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
```

---

### 3. `FlowSteps`

Numbered steps left-to-right, color cycling through `T.step`.

```jsx
export const FlowSteps = () => {
  const steps = ['Define','Build','Test','Deploy']
  return (
    <div style={{fontFamily:T.font.sans, background:T.surface.canvas, padding:24,
      borderRadius:T.style.nodeRadius, boxShadow:T.surface.shadow, display:'flex',
      alignItems:'center', gap:8, flexWrap:'wrap'}}>
      {steps.map((s,i) => (
        <div key={i} style={{display:'flex', alignItems:'center', gap:8}}>
          <div style={{background:T.step[i%T.step.length], padding:'10px 18px',
            borderRadius:T.style.nodeRadius, fontWeight:T.weight.bold, color:'#111',
            fontSize:T.type.body}}>
            <span style={{fontFamily:T.font.mono, marginRight:6}}>{i+1}.</span>{s}
          </div>
          {i < steps.length-1 && <div style={{color:T.edge.color, fontSize:20}}>→</div>}
        </div>
      ))}
    </div>
  )
}
```

---

### 4. `Architecture`

Actors in a row connected by labeled directional arrows.

```jsx
export const Architecture = () => {
  const actors = [
    {label:'Client', sem:T.semantic.primary},
    {label:'API Gateway', sem:T.semantic.info},
    {label:'Database', sem:T.semantic.data},
  ]
  const nb = T.style.nodeBorder === 'none' ? 'none' : T.style.nodeBorder
  return (
    <div style={{fontFamily:T.font.sans, background:T.surface.canvas, padding:24,
      borderRadius:T.style.nodeRadius, boxShadow:T.surface.shadow, display:'flex',
      alignItems:'center', gap:8, flexWrap:'wrap'}}>
      {actors.map((a,i) => (
        <div key={i} style={{display:'flex', alignItems:'center', gap:8}}>
          <div style={{background:a.sem.bg, border:nb, borderRadius:T.style.nodeRadius,
            padding:'12px 16px', fontWeight:T.weight.bold, color:'#111',
            fontSize:T.type.body}}>{a.label}</div>
          {i < actors.length-1 && (
            <div style={{display:'flex', flexDirection:'column', alignItems:'center'}}>
              <div style={{fontFamily:T.font.mono, fontSize:T.type.caption, color:T.ink.muted,
                marginBottom:2}}>GET /data</div>
              <div style={{color:T.edge.color, fontSize:20}}>→</div>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
```

---

### 5. `CardSet`

A labeled group of semantic cards — for feature lists, success/limit blocks.

```jsx
export const CardSet = () => {
  const cards = [
    {sem:T.semantic.solution, label:'Outcome A', detail:'Detail text'},
    {sem:T.semantic.warn,     label:'Limit B',   detail:'Detail text'},
    {sem:T.semantic.problem,  label:'Risk C',    detail:'Detail text'},
  ]
  const nb = T.style.nodeBorder === 'none' ? 'none' : T.style.nodeBorder
  return (
    <div style={{fontFamily:T.font.sans, background:T.surface.canvas, padding:24,
      borderRadius:T.style.nodeRadius, boxShadow:T.surface.shadow}}>
      <div style={{display:'flex', gap:12, flexWrap:'wrap'}}>
        {cards.map((c,i) => (
          <div key={i} style={{flex:1, minWidth:140, background:c.sem.bg, border:nb,
            borderRadius:T.style.nodeRadius, padding:'12px 14px'}}>
            <div style={{fontWeight:T.weight.bold, color:'#111', fontSize:T.type.body,
              marginBottom:4}}>{c.label}</div>
            <div style={{fontSize:T.type.label, color:'#111'}}>{c.detail}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
```

---

### 6. `Matrix`

2×2 quadrant with axis labels.

```jsx
export const Matrix = () => {
  const quads = [
    {label:'High Value / Low Effort',  sem:T.semantic.solution, pos:'tl'},
    {label:'High Value / High Effort', sem:T.semantic.warn,     pos:'tr'},
    {label:'Low Value / Low Effort',   sem:T.semantic.neutral,  pos:'bl'},
    {label:'Low Value / High Effort',  sem:T.semantic.problem,  pos:'br'},
  ]
  const nb = T.style.nodeBorder === 'none' ? 'none' : T.style.nodeBorder
  return (
    <div style={{fontFamily:T.font.sans, background:T.surface.canvas, padding:24,
      borderRadius:T.style.nodeRadius, boxShadow:T.surface.shadow}}>
      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap:8}}>
        {quads.map((q,i) => (
          <div key={i} style={{background:q.sem.bg, border:nb,
            borderRadius:T.style.nodeRadius, padding:'16px', fontSize:T.type.body,
            fontWeight:T.weight.bold, color:'#111'}}>{q.label}</div>
        ))}
      </div>
    </div>
  )
}
```

---

### 7a. `Palette` (the 8-color swatch strip)

Every frame in the prototype shows a `PALETTE · 8` strip so the shared DNA is
visible at a glance. Render all 8 palette colors read from `T.palette.*` as
34×34 rounded swatches, in the fixed order
orange → purple → pink → yellow → blue → green → brown → periwinkle. Per
CONTRACT §1, swatches carry a `2px solid #111` keyline in `blueprint` and are
borderless in `candy-os` / `swiss`.

```jsx
export const Palette = () => {
  const order = ['orange','purple','pink','yellow','blue','green','brown','periwinkle']
  const swBorder = T.skin === 'blueprint' ? '2px solid #111' : 'none'
  return (
    <div style={{fontFamily:T.font.sans, background:T.surface.canvas, padding:24,
      borderRadius:T.style.nodeRadius, boxShadow:T.surface.shadow}}>
      <div style={{fontFamily:T.font.mono, fontSize:T.type.caption, color:T.ink.muted,
        letterSpacing:T.letterSpacing.mono, textTransform:'uppercase', marginBottom:16}}>
        PALETTE · 8
      </div>
      <div style={{display:'flex', gap:10, flexWrap:'wrap'}}>
        {order.map((k,i) => (
          <div key={i} style={{width:34, height:34, background:T.palette[k],
            border:swBorder, borderRadius:T.radius.sm}}/>
        ))}
      </div>
    </div>
  )
}
```

### 7. `NodeTaxonomy`

The 5-type legend. In `tile` layout (candy-os / blueprint) each node is a fixed
96×88 tile; in `band` layout (swiss) each is a full-width row.

```jsx
export const NodeTaxonomy = () => {
  const types = ['person','container','database','queue','external']
  const isTile = T.style.nodeLayout === 'tile'
  const isFill = T.style.iconMode === 'fill'
  const nb = T.style.nodeBorder === 'none' ? 'none' : T.style.nodeBorder

  const glyph = (type) => {
    const s = { fill: isFill ? '#111' : 'none', stroke:'#111',
                 strokeWidth: isFill ? 0 : 1.8, overflow:'visible' }
    if (type==='person')    return (<svg viewBox="0 0 24 24" width="20" height="20" style={s}>
      {isFill ? [<circle key="c" cx="12" cy="7" r="4"/>,<path key="p" d="M3 22a9 9 0 0 1 18 0Z"/>]
               : [<circle key="c" cx="12" cy="8" r="3.6"/>,<path key="p" d="M5 21a7 7 0 0 1 14 0"/>]}</svg>)
    if (type==='external')  return (<svg viewBox="0 0 24 24" width="20" height="20"
      style={{fill:'none',stroke:'#111',strokeWidth:isFill?2.6:1.8,overflow:'visible'}}>
      <path d="M8 16 17 7"/><path d="M9 7h8v8"/></svg>)
    if (type==='container') return (<svg viewBox="0 0 24 24" width="20" height="20" style={s}>
      {isFill ? [<rect key="a" x="3" y="6" width="13" height="12" rx="2.5"/>,<rect key="b" x="9" y="2" width="13" height="12" rx="2.5" opacity=".45"/>]
               : [<rect key="a" x="3" y="5" width="13" height="11" rx="2"/>,<rect key="b" x="8" y="9" width="13" height="11" rx="2"/>]}</svg>)
    if (type==='database')  return (<svg viewBox="0 0 24 24" width="20" height="20" style={s}>
      {isFill ? [<ellipse key="e" cx="12" cy="5.5" rx="8" ry="3.2"/>,<path key="p" d="M4 5.5v13c0 1.8 3.6 3.2 8 3.2s8-1.4 8-3.2v-13" fill="none" stroke="#111" strokeWidth="2.2"/>]
               : [<ellipse key="e" cx="12" cy="6" rx="7" ry="2.8"/>,<path key="p" d="M5 6v12c0 1.5 3.1 2.8 7 2.8s7-1.3 7-2.8V6"/>]}</svg>)
    if (type==='queue')     return (<svg viewBox="0 0 24 24" width="20" height="20" style={s}>
      {isFill ? [<rect key="a" x="3" y="5" width="4" height="14" rx="1.5"/>,<rect key="b" x="10" y="5" width="4" height="14" rx="1.5"/>,<rect key="c" x="17" y="5" width="4" height="14" rx="1.5"/>]
               : <path key="p" d="M5 6v12M11 6v12M17 6v12"/>}</svg>)
    return null
  }

  const tileNode = (type) => {
    const n = T.node[type]
    const extBorder = (type==='external' && T.style.dashedExternal)
      ? '2.5px dashed #111' : nb
    return (
      <div style={{width:96, height:88, background:n.fill, border:extBorder,
        borderRadius:T.style.nodeRadius, display:'flex', flexDirection:'column',
        alignItems:'center', justifyContent:'center', gap:4}}>
        {glyph(type)}
        <div style={{fontSize:T.type.label, fontWeight:T.weight.bold, color:'#111',
          fontFamily:T.font.sans, textAlign:'center', lineHeight:1.2,
          textTransform:'capitalize'}}>{type}</div>
        {T.style.showTag && <div style={{fontFamily:T.font.mono, fontSize:T.type.tag,
          color:T.ink.tag, letterSpacing:T.letterSpacing.mono,
          textTransform:'uppercase'}}>{n.tag}</div>}
      </div>
    )
  }

  const bandNode = (type) => {
    const n = T.node[type]
    return (
      <div style={{display:'flex', alignItems:'center', gap:12, background:n.fill,
        border:nb, borderRadius:T.style.nodeRadius, padding:'10px 16px'}}>
        {glyph(type)}
        <div style={{fontSize:T.type.body, fontWeight:T.weight.bold, color:'#111',
          fontFamily:T.font.sans, flex:1, textTransform:'capitalize'}}>{type}</div>
        {T.style.showTag && <div style={{fontFamily:T.font.mono, fontSize:T.type.tag,
          color:T.ink.tag, letterSpacing:T.letterSpacing.mono}}>{n.tag}</div>}
      </div>
    )
  }

  return (
    <div style={{fontFamily:T.font.sans, background:T.surface.canvas, padding:24,
      borderRadius:T.style.nodeRadius, boxShadow:T.surface.shadow}}>
      <div style={{fontFamily:T.font.mono, fontSize:T.type.caption, color:T.ink.muted,
        letterSpacing:T.letterSpacing.mono, textTransform:'uppercase', marginBottom:16}}>
        NODE TAXONOMY
      </div>
      <div style={{display:'flex', gap:12,
        flexDirection: isTile ? 'row' : 'column', flexWrap: isTile ? 'wrap' : 'nowrap'}}>
        {types.map((t,i) => (
          <div key={i}>{isTile ? tileNode(t) : bandNode(t)}</div>
        ))}
      </div>
    </div>
  )
}
```

---

### 8. `C4Hierarchy`

Nested L1→L2→L3 rendered via the per-skin method.

```jsx
export const C4Hierarchy = () => {
  const isCandy    = T.skin === 'candy-os'
  const isSwiss    = T.skin === 'swiss'
  const isBluepr   = T.skin === 'blueprint'
  const nb = T.style.nodeBorder === 'none' ? 'none' : T.style.nodeBorder

  const levelLabel = (lv, text, color) => (
    <div style={{fontFamily:T.font.mono, fontSize:T.type.caption, color:color,
      letterSpacing:T.letterSpacing.mono, textTransform:'uppercase',
      marginBottom:6, display:'flex', justifyContent:'space-between'}}>
      <span>{text}</span><span>{lv}</span>
    </div>
  )

  if (isSwiss) {
    return (
      <div style={{fontFamily:T.font.sans, background:T.surface.canvas, padding:24,
        borderRadius:T.style.nodeRadius, boxShadow:T.surface.shadow,
        display:'flex', flexDirection:'column', gap:8}}>
        <div style={{background:T.c4.l1.bg, marginLeft:T.c4.l1.indent, padding:'12px 16px',
          borderRadius:T.style.nodeRadius}}>
          {levelLabel('L1','Context System',T.c4.l1.label)}
          <div style={{fontWeight:T.weight.bold, color:'#111', fontSize:T.type.body}}>
            E-Commerce Platform
          </div>
        </div>
        <div style={{background:T.c4.l2.bg, marginLeft:T.c4.l2.indent, padding:'12px 16px',
          borderRadius:T.style.nodeRadius}}>
          {levelLabel('L2','Container',T.c4.l2.label)}
          <div style={{fontWeight:T.weight.bold, color:'#111', fontSize:T.type.body}}>
            Web Application
          </div>
        </div>
        <div style={{background:T.c4.l3.bg, marginLeft:T.c4.l3.indent, padding:'12px 16px',
          borderRadius:T.style.nodeRadius}}>
          {levelLabel('L3','Component',T.c4.l3.label)}
          <div style={{fontWeight:T.weight.bold, color:'#111', fontSize:T.type.body}}>
            Auth Service
          </div>
        </div>
      </div>
    )
  }

  if (isBluepr) {
    return (
      <div style={{fontFamily:T.font.sans, background:T.surface.canvas, padding:24,
        borderRadius:T.style.nodeRadius, boxShadow:T.surface.shadow}}>
        <div style={{background:T.c4.l1.bg, border:T.c4.l1.border,
          borderRadius:T.style.nodeRadius, padding:16}}>
          {levelLabel('L1','Context · border 3',T.c4.l1.label)}
          <div style={{fontWeight:T.weight.bold, color:'#111', marginBottom:12,
            fontSize:T.type.body}}>E-Commerce Platform</div>
          <div style={{background:T.c4.l2.bg, border:T.c4.l2.border,
            borderRadius:T.style.nodeRadius, padding:12}}>
            {levelLabel('L2','Container · border 2',T.c4.l2.label)}
            <div style={{fontWeight:T.weight.bold, color:'#111', marginBottom:12,
              fontSize:T.type.body}}>Web Application</div>
            <div style={{background:T.c4.l3.bg, border:T.c4.l3.border,
              borderRadius:T.style.nodeRadius, padding:10}}>
              {levelLabel('L3','Component · border 1.4',T.c4.l3.label)}
              <div style={{fontWeight:T.weight.bold, color:'#111',
                fontSize:T.type.body}}>Auth Service</div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // candy-os: opacity/saturation nesting
  return (
    <div style={{fontFamily:T.font.sans, background:T.surface.canvas, padding:24,
      borderRadius:T.style.nodeRadius, boxShadow:T.surface.shadow}}>
      <div style={{background:T.c4.l1.bg, border:T.c4.l1.border,
        borderRadius:T.style.nodeRadius, padding:16}}>
        {levelLabel('L1','Context',T.c4.l1.label)}
        <div style={{fontWeight:T.weight.bold, color:T.ink.heading, marginBottom:12,
          fontSize:T.type.body}}>E-Commerce Platform</div>
        <div style={{background:T.c4.l2.bg, borderRadius:T.style.nodeRadius, padding:12}}>
          {levelLabel('L2','Container',T.c4.l2.label)}
          <div style={{fontWeight:T.weight.bold, color:T.ink.heading, marginBottom:12,
            fontSize:T.type.body}}>Web Application</div>
          <div style={{background:T.c4.l3.bg, borderRadius:T.style.nodeRadius, padding:10}}>
            {levelLabel('L3','Component',T.c4.l3.label)}
            <div style={{fontWeight:T.weight.bold, color:T.ink.heading,
              fontSize:T.type.body}}>Auth Service</div>
          </div>
        </div>
      </div>
    </div>
  )
}
```

---

### 9. `C4Container`

SVG diagram: system boundary + node boxes + directional labeled edges.
Edges drawn first (behind nodes). Uses `<marker>` arrowheads.

The layout is a fixed-size SVG canvas; colors read from `T`. In blueprint:
system boundary is a dashed rectangle + mono label; external nodes get dashed
border; type-tags shown. In candy-os/swiss: simpler boundaries.

```jsx
export const C4Container = () => {
  const W = 560, H = 320
  const ec = T.edge.color
  const ew = T.edge.width
  const isDashed = T.style.dashedExternal
  const markerId = 'arr-' + T.skin

  const nodes = [
    { id:'user',  x:40,  y:130, w:90,  h:72, type:'person',    label:'User',      detail:'Web Browser' },
    { id:'web',   x:200, y:50,  w:110, h:72, type:'container',  label:'Web App',   detail:'React SPA' },
    { id:'api',   x:200, y:190, w:110, h:72, type:'container',  label:'API',       detail:'REST / Node' },
    { id:'db',    x:390, y:190, w:110, h:72, type:'database',   label:'Database',  detail:'PostgreSQL' },
    { id:'ext',   x:390, y:50,  w:110, h:72, type:'external',   label:'Auth Svc',  detail:'OAuth2' },
  ]

  const edges = [
    { from:'user', to:'web',  label:'HTTPS', fx:130, fy:166, tx:200, ty:86,  mx:165, my:116 },
    { from:'user', to:'api',  label:'uses',  fx:130, fy:170, tx:200, ty:226, mx:165, my:200 },
    { from:'web',  to:'api',  label:'calls', fx:255, fy:122, tx:255, ty:190, mx:265, my:156 },
    { from:'api',  to:'db',   label:'r/w',   fx:310, fy:226, tx:390, ty:226, mx:350, my:216 },
    { from:'api',  to:'ext',  label:'auth',  fx:255, fy:190, tx:255, ty:122, mx:330, my:86  },
  ]

  return (
    <div style={{fontFamily:T.font.sans, background:T.surface.canvas, padding:24,
      borderRadius:T.style.nodeRadius, boxShadow:T.surface.shadow}}>
      <div style={{fontFamily:T.font.mono, fontSize:T.type.caption, color:T.ink.muted,
        letterSpacing:T.letterSpacing.mono, textTransform:'uppercase', marginBottom:12}}>
        C4 CONTAINER
      </div>
      <svg width={W} height={H} viewBox={'0 0 '+W+' '+H}
        style={{width:'100%', maxWidth:W, display:'block'}}>
        <defs>
          <marker id={markerId} markerWidth="8" markerHeight="8"
            refX="6" refY="3" orient="auto">
            <path d="M0 0 L6 3 L0 6 Z" fill={ec}/>
          </marker>
        </defs>
        {T.skin==='blueprint' && (
          <rect x="170" y="20" width="370" height="280" rx={T.style.nodeRadius}
            fill="none" stroke="#111" strokeWidth="1.5" strokeDasharray="6 4"/>
        )}
        {edges.map((e,i) => (
          <g key={i}>
            <line x1={e.fx} y1={e.fy} x2={e.tx} y2={e.ty}
              stroke={ec} strokeWidth={ew}
              markerEnd={'url(#'+markerId+')'}/>
            <text x={e.mx} y={e.my} textAnchor="middle"
              style={{fontFamily:T.font.mono, fontSize:T.type.caption,
                fill:T.edge.label, letterSpacing:T.letterSpacing.mono}}>{e.label}</text>
          </g>
        ))}
        {nodes.map((n,i) => {
          const fill = T.node[n.type].fill
          const bStroke = n.type==='external' && isDashed ? '#111' : ec
          const bDash   = n.type==='external' && isDashed ? '5 3' : undefined
          const bWidth  = T.style.nodeBorder==='none' ? 0 : parseFloat(T.style.nodeBorder)
          return (
            <g key={i}>
              <rect x={n.x} y={n.y} width={n.w} height={n.h}
                rx={T.style.nodeRadius} fill={fill}
                stroke={bStroke} strokeWidth={bWidth}
                strokeDasharray={bDash}/>
              <text x={n.x+n.w/2} y={n.y+28} textAnchor="middle"
                style={{fontFamily:T.font.sans, fontSize:T.type.label,
                  fontWeight:T.weight.bold, fill:'#111'}}>{n.label}</text>
              <text x={n.x+n.w/2} y={n.y+44} textAnchor="middle"
                style={{fontFamily:T.font.sans, fontSize:T.type.caption,
                  fill:T.ink.muted}}>{n.detail}</text>
              {T.style.showTag && (
                <text x={n.x+n.w/2} y={n.y+60} textAnchor="middle"
                  style={{fontFamily:T.font.mono, fontSize:T.type.tag,
                    fill:T.ink.tag, letterSpacing:T.letterSpacing.mono}}>
                  {T.node[n.type].tag}
                </text>
              )}
            </g>
          )
        })}
        {T.skin==='blueprint' && (
          <text x="545" y="36" textAnchor="end"
            style={{fontFamily:T.font.mono, fontSize:T.type.caption,
              fill:T.ink.muted, letterSpacing:T.letterSpacing.mono}}>
            SYSTEM BOUNDARY
          </text>
        )}
      </svg>
    </div>
  )
}
```

---

### 10. `Flowchart`

SVG: rect/diamond/cylinder nodes + `yes`/`no` labeled arrows. Edges drawn
first, then nodes on top. Uses `<marker>` arrowheads. Colors from `T`.

```jsx
export const Flowchart = () => {
  const W = 480, H = 360
  const ec = T.edge.color
  const ew = T.edge.width
  const markerId = 'fc-arr-' + T.skin

  const nodes = [
    { id:'start', x:190, y:20,  w:100, h:40,  shape:'rect',     label:'Start',        fill:T.node.container.fill },
    { id:'req',   x:160, y:100, w:160, h:44,  shape:'rect',     label:'HTTP Request',  fill:T.node.container.fill },
    { id:'auth',  x:165, y:186, w:150, h:48,  shape:'diamond',  label:'Authenticated?',fill:T.node.queue.fill },
    { id:'ok',    x:320, y:272, w:120, h:40,  shape:'rect',     label:'Return 200 OK', fill:T.node.database.fill },
    { id:'deny',  x:30,  y:272, w:120, h:40,  shape:'rect',     label:'Return 401',    fill:T.node.external.fill },
    { id:'db',    x:320, y:186, w:120, h:44,  shape:'cylinder', label:'Lookup DB',     fill:T.node.database.fill },
  ]

  const edges = [
    { x1:240, y1:60,  x2:240, y2:100, label:null,  lx:250, ly:80,  dash:false },
    { x1:240, y1:144, x2:240, y2:186, label:null,  lx:250, ly:165, dash:false },
    { x1:315, y1:210, x2:380, y2:186, label:'yes', lx:355, ly:195, dash:false },
    { x1:380, y1:230, x2:380, y2:272, label:null,  lx:390, ly:251, dash:false },
    { x1:165, y1:210, x2:90,  y2:272, label:'no',  lx:110, ly:238, dash:false },
  ]

  const nodeShape = (n) => {
    if (n.shape === 'diamond') {
      const cx=n.x+n.w/2, cy=n.y+n.h/2, hw=n.w/2, hh=n.h/2
      return (<polygon points={`${cx},${cy-hh} ${cx+hw},${cy} ${cx},${cy+hh} ${cx-hw},${cy}`}
        fill={n.fill} stroke={ec} strokeWidth={T.style.nodeBorder==='none'?0:parseFloat(T.style.nodeBorder)}/>)
    }
    if (n.shape === 'cylinder') {
      const rx=n.w/2, ry=8
      return (<g>
        <ellipse cx={n.x+rx} cy={n.y+ry} rx={rx} ry={ry} fill={n.fill}
          stroke={ec} strokeWidth={T.style.nodeBorder==='none'?0:parseFloat(T.style.nodeBorder)}/>
        <rect x={n.x} y={n.y+ry} width={n.w} height={n.h-ry} fill={n.fill}
          stroke={ec} strokeWidth={T.style.nodeBorder==='none'?0:parseFloat(T.style.nodeBorder)}
          strokeTop="none"/>
        <ellipse cx={n.x+rx} cy={n.y+n.h} rx={rx} ry={ry} fill={n.fill}
          stroke={ec} strokeWidth={T.style.nodeBorder==='none'?0:parseFloat(T.style.nodeBorder)}/>
      </g>)
    }
    return (<rect x={n.x} y={n.y} width={n.w} height={n.h} rx={T.style.nodeRadius}
      fill={n.fill} stroke={ec} strokeWidth={T.style.nodeBorder==='none'?0:parseFloat(T.style.nodeBorder)}/>)
  }

  const textY = (n) => {
    if (n.shape === 'diamond') return n.y + n.h/2 + 5
    if (n.shape === 'cylinder') return n.y + n.h/2 + 16
    return n.y + n.h/2 + 5
  }

  return (
    <div style={{fontFamily:T.font.sans, background:T.surface.canvas, padding:24,
      borderRadius:T.style.nodeRadius, boxShadow:T.surface.shadow}}>
      <div style={{fontFamily:T.font.mono, fontSize:T.type.caption, color:T.ink.muted,
        letterSpacing:T.letterSpacing.mono, textTransform:'uppercase', marginBottom:12}}>
        FLOWCHART SAMPLE
      </div>
      <svg width={W} height={H} viewBox={'0 0 '+W+' '+H}
        style={{width:'100%', maxWidth:W, display:'block'}}>
        <defs>
          <marker id={markerId} markerWidth="8" markerHeight="8"
            refX="6" refY="3" orient="auto">
            <path d="M0 0 L6 3 L0 6 Z" fill={ec}/>
          </marker>
        </defs>
        {edges.map((e,i) => (
          <g key={i}>
            <line x1={e.x1} y1={e.y1} x2={e.x2} y2={e.y2}
              stroke={ec} strokeWidth={ew} markerEnd={'url(#'+markerId+')'}
              strokeDasharray={e.dash?'6 3':undefined}/>
            {e.label && <text x={e.lx} y={e.ly} textAnchor="middle"
              style={{fontFamily:T.font.mono, fontSize:T.type.caption,
                fill:T.edge.label, letterSpacing:T.letterSpacing.mono}}>{e.label}</text>}
          </g>
        ))}
        {nodes.map((n,i) => (
          <g key={i}>
            {nodeShape(n)}
            <text x={n.x+n.w/2} y={textY(n)} textAnchor="middle"
              style={{fontFamily:T.font.sans, fontSize:T.type.label,
                fontWeight:T.weight.bold, fill:'#111'}}>{n.label}</text>
          </g>
        ))}
      </svg>
    </div>
  )
}
```

---

### 11. `Sequence`

SVG: actor header boxes + dashed lifelines + solid/dashed message arrows with
mono labels. Colors from `T`. The `lifeline` color is `T.edge.lifeline` (swiss
uses `#B8B6AE` dashed; others fall back to a muted tone).

```jsx
export const Sequence = () => {
  const W = 520, H = 300
  const ec = T.edge.color
  const ew = T.edge.width
  const lc = T.edge.lifeline || T.ink.muted
  const markerId = 'seq-arr-' + T.skin
  const markRetId = 'seq-ret-' + T.skin

  const actors = [
    { id:'browser', x:40,  label:'Browser' },
    { id:'api',     x:200, label:'API' },
    { id:'auth',    x:360, label:'Auth' },
  ]
  const AW = 100, AH = 36

  const messages = [
    { from:0, to:1, y:90,  label:'POST /login',      dashed:false },
    { from:1, to:2, y:130, label:'verify token',      dashed:false },
    { from:2, to:1, y:170, label:'token valid',       dashed:true  },
    { from:1, to:0, y:210, label:'200 OK + session',  dashed:true  },
    { from:0, to:1, y:250, label:'GET /data',         dashed:false },
  ]

  const ax = (i) => actors[i].x + AW/2

  return (
    <div style={{fontFamily:T.font.sans, background:T.surface.canvas, padding:24,
      borderRadius:T.style.nodeRadius, boxShadow:T.surface.shadow}}>
      <div style={{fontFamily:T.font.mono, fontSize:T.type.caption, color:T.ink.muted,
        letterSpacing:T.letterSpacing.mono, textTransform:'uppercase', marginBottom:12}}>
        SEQUENCE DIAGRAM
      </div>
      <svg width={W} height={H} viewBox={'0 0 '+W+' '+H}
        style={{width:'100%', maxWidth:W, display:'block'}}>
        <defs>
          <marker id={markerId} markerWidth="8" markerHeight="8"
            refX="6" refY="3" orient="auto">
            <path d="M0 0 L6 3 L0 6 Z" fill={ec}/>
          </marker>
          <marker id={markRetId} markerWidth="8" markerHeight="8"
            refX="6" refY="3" orient="auto">
            <path d="M0 0 L6 3 L0 6 Z" fill={lc}/>
          </marker>
        </defs>
        {actors.map((a,i) => (
          <g key={i}>
            <rect x={a.x} y={10} width={AW} height={AH} rx={T.style.nodeRadius}
              fill={T.node.container.fill}
              stroke={T.style.nodeBorder==='none'?'none':ec}
              strokeWidth={T.style.nodeBorder==='none'?0:parseFloat(T.style.nodeBorder)}/>
            <text x={ax(i)} y={10+AH/2+5} textAnchor="middle"
              style={{fontFamily:T.font.sans, fontSize:T.type.label,
                fontWeight:T.weight.bold, fill:'#111'}}>{a.label}</text>
            <line x1={ax(i)} y1={10+AH} x2={ax(i)} y2={H-10}
              stroke={lc} strokeWidth="1.5" strokeDasharray="4 4"/>
          </g>
        ))}
        {messages.map((m,i) => {
          const x1=ax(m.from), x2=ax(m.to), dir=x2>x1
          const mColor = m.dashed ? lc : ec
          const mMark  = m.dashed ? ('url(#'+markRetId+')') : ('url(#'+markerId+')')
          return (
            <g key={i}>
              <line x1={x1} y1={m.y} x2={x2} y2={m.y}
                stroke={mColor} strokeWidth={m.dashed?1.5:ew}
                strokeDasharray={m.dashed?'5 3':undefined}
                markerEnd={mMark}/>
              <text x={(x1+x2)/2} y={m.y-5} textAnchor="middle"
                style={{fontFamily:T.font.mono, fontSize:T.type.caption,
                  fill:T.edge.label, letterSpacing:T.letterSpacing.mono}}>{m.label}</text>
            </g>
          )
        })}
      </svg>
    </div>
  )
}
```

---

## The data-driven rule

Declare content as arrays of plain objects at the top of each component, then
`.map()`. This keeps JSX short, makes every node consistent, and makes edits
trivial.

```jsx
export const PipelineDiagram = () => {
  const stages = [
    { label:'Ingest',  fill:T.step[0] },
    { label:'Process', fill:T.step[1] },
    { label:'Emit',    fill:T.step[2] },
  ]
  return (
    <div style={{…}}>
      {stages.map((s,i) => (
        <div key={i} style={{background:s.fill,…}}>{s.label}</div>
      ))}
    </div>
  )
}
```

For SVG archetypes: declare `nodes` and `edges` arrays, render edges first
(so they appear behind nodes), then nodes.

---

## Naming

Component names are PascalCase and describe the **concept** derived from the
request — e.g. `LoginFlowchart`, `PaymentC4Container`, `NodeTypeLegend`.
Avoid generic `Diagram1`.

When a design system is bound, apply the binding to **lowercase helper function
names** (e.g. if their system calls a card a `Panel`, name the helper `panel`
and call it `{panel(...)}`). The top-level export name stays PascalCase.

The 11 canon archetype names (`NodeTaxonomy`, `C4Hierarchy`, `C4Container`,
`Flowchart`, `Sequence`, `BeforeAfter`, `LayerStack`, `FlowSteps`,
`Architecture`, `CardSet`, `Matrix`) are reserved for reference samples and
skill-generated outputs. Authored diagrams should use descriptive names.
