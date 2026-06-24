# Node Glyphs — Copy-Paste SVG Reference

All glyphs use a `24×24` viewBox. Two modes:

- **fill** (`T.style.iconMode === 'fill'`): used by `candy-os` and `blueprint`. Set `fill="#111"` on the `<svg>` or individual elements.
- **line** (`T.style.iconMode === 'line'`): used by `swiss`. Set `fill="none" stroke="#111" stroke-width="1.8"` on the `<svg>`.

The `external` glyph is always `fill="none" stroke="#111"` regardless of mode; only `stroke-width` differs (`2.6` fill-mode / `1.8` line-mode).

## Glyph table

| Type | Fill variant | Line variant |
|------|-------------|-------------|
| `person` | `<circle cx="12" cy="7" r="4"/><path d="M3 22a9 9 0 0 1 18 0Z"/>` | `<circle cx="12" cy="8" r="3.6"/><path d="M5 21a7 7 0 0 1 14 0"/>` |
| `external` | `fill="none" stroke="#111" stroke-width="2.6"` → `<path d="M8 16 17 7"/><path d="M9 7h8v8"/>` | `fill="none" stroke="#111" stroke-width="1.8"` → `<path d="M8 16 17 7"/><path d="M9 7h8v8"/>` |
| `container` | `<rect x="3" y="6" width="13" height="12" rx="2.5"/><rect x="9" y="2" width="13" height="12" rx="2.5" opacity=".45"/>` | `<rect x="3" y="5" width="13" height="11" rx="2"/><rect x="8" y="9" width="13" height="11" rx="2"/>` |
| `database` | `<ellipse cx="12" cy="5.5" rx="8" ry="3.2"/><path d="M4 5.5v13c0 1.8 3.6 3.2 8 3.2s8-1.4 8-3.2v-13" fill="none" stroke="#111" stroke-width="2.2"/>` | `<ellipse cx="12" cy="6" rx="7" ry="2.8"/><path d="M5 6v12c0 1.5 3.1 2.8 7 2.8s7-1.3 7-2.8V6"/>` |
| `queue` | `<rect x="3" y="5" width="4" height="14" rx="1.5"/><rect x="10" y="5" width="4" height="14" rx="1.5"/><rect x="17" y="5" width="4" height="14" rx="1.5"/>` | `<path d="M5 6v12M11 6v12M17 6v12"/>` |

## Full SVG snippets (ready to paste)

### person — fill

```svg
<svg viewBox="0 0 24 24" width="20" height="20" fill="#111">
  <circle cx="12" cy="7" r="4"/>
  <path d="M3 22a9 9 0 0 1 18 0Z"/>
</svg>
```

### person — line

```svg
<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#111" stroke-width="1.8">
  <circle cx="12" cy="8" r="3.6"/>
  <path d="M5 21a7 7 0 0 1 14 0"/>
</svg>
```

### external — fill-mode (stroke-width 2.6)

```svg
<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#111" stroke-width="2.6">
  <path d="M8 16 17 7"/>
  <path d="M9 7h8v8"/>
</svg>
```

### external — line-mode (stroke-width 1.8)

```svg
<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#111" stroke-width="1.8">
  <path d="M8 16 17 7"/>
  <path d="M9 7h8v8"/>
</svg>
```

### container — fill

```svg
<svg viewBox="0 0 24 24" width="20" height="20" fill="#111">
  <rect x="3" y="6" width="13" height="12" rx="2.5"/>
  <rect x="9" y="2" width="13" height="12" rx="2.5" opacity=".45"/>
</svg>
```

### container — line

```svg
<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#111" stroke-width="1.8">
  <rect x="3" y="5" width="13" height="11" rx="2"/>
  <rect x="8" y="9" width="13" height="11" rx="2"/>
</svg>
```

### database — fill

```svg
<svg viewBox="0 0 24 24" width="20" height="20" fill="#111">
  <ellipse cx="12" cy="5.5" rx="8" ry="3.2"/>
  <path d="M4 5.5v13c0 1.8 3.6 3.2 8 3.2s8-1.4 8-3.2v-13"
        fill="none" stroke="#111" stroke-width="2.2"/>
</svg>
```

### database — line

```svg
<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#111" stroke-width="1.8">
  <ellipse cx="12" cy="6" rx="7" ry="2.8"/>
  <path d="M5 6v12c0 1.5 3.1 2.8 7 2.8s7-1.3 7-2.8V6"/>
</svg>
```

### queue — fill

```svg
<svg viewBox="0 0 24 24" width="20" height="20" fill="#111">
  <rect x="3"  y="5" width="4" height="14" rx="1.5"/>
  <rect x="10" y="5" width="4" height="14" rx="1.5"/>
  <rect x="17" y="5" width="4" height="14" rx="1.5"/>
</svg>
```

### queue — line

```svg
<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#111" stroke-width="1.8">
  <path d="M5 6v12M11 6v12M17 6v12"/>
</svg>
```

## Which skins use which mode

| Skin | `iconMode` | Variant |
|------|-----------|---------|
| `candy-os` | `fill` | Fill variant for person/container/database/queue; `external` at stroke-width 2.6 |
| `swiss` | `line` | Line variant for all; `external` at stroke-width 1.8 |
| `blueprint` | `fill` | Fill variant for person/container/database/queue; `external` at stroke-width 2.6 |

Check `T.style.iconMode` at runtime to branch:

```js
const isFill = T.style.iconMode === 'fill'
// then use isFill to pick fill vs line SVG paths (see canon.md glyph helper)
```
