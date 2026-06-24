/**
 * Blueprint skin — design token source.
 *
 * Light canvas, pastel fills with bold black keylines, thick right-angle arrows,
 * mono [type-tags] on every node, dashed group boundary + label. The reference skin
 * for architecture and C4 diagrams: borders signal hierarchy, tags identify roles,
 * orthogonal routing makes structure explicit.
 *
 * C4 nesting uses nested boxes with decreasing border weight:
 *   L1 — #E4EAF4  3px solid #111  (system context)
 *   L2 — #CFDDEC  2px solid #111  (container boundary)
 *   L3 — #ffffff  1.4px solid #111 (component boundary)
 *
 * This file is the TOKEN SOURCE ONLY — it is never imported by emitted MDX.
 * Instead, the orchestrator serializes the relevant subset into a `const T = {...}`
 * at the top of each MDX file. Every diagram reads from `T`, not from this file.
 *
 * Conforms to the §6 `T` shape from the frozen contract (CONTRACT.md §6).
 * Blueprint is also the DEFAULT skin (see theme.default.ts).
 */
export const theme = {
  skin: 'blueprint' as const,

  font: {
    sans: "'Helvetica Neue',Helvetica,Arial,sans-serif",
    mono: "'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,monospace",
  },

  surface: {
    canvas: '#F4F3F0',
    panel:  '#F4F3F0',
    shadow: '0 2px 14px rgba(0,0,0,.10)',
  },

  ink: {
    heading: '#111111',
    body:    '#33312E',
    muted:   '#6C6B66',
    tag:     '#9A988F',
  },

  palette: {
    orange:     '#EE7B4D',
    purple:     '#C5B6EE',
    pink:       '#F0C5DA',
    yellow:     '#E7E058',
    blue:       '#A6C6E2',
    green:      '#87B79A',
    brown:      '#A98C7E',
    periwinkle: '#9CAFE7',
  },

  node: {
    person:    { fill: '#C5B6EE', tag: '[person]' },
    external:  { fill: '#EE7B4D', tag: '[external]' },
    container: { fill: '#87B79A', tag: '[container]' },
    database:  { fill: '#A6C6E2', tag: '[datastore]' },
    queue:     { fill: '#E7E058', tag: '[queue]' },
  },

  edge: {
    color:    '#111111',
    width:    3,
    style:    'orthogonal' as const,
    label:    '#555555',
    lifeline: null,
  },

  c4: {
    l1: { bg: '#E4EAF4', border: '3px solid #111',   label: '#555555', indent: 0 },
    l2: { bg: '#CFDDEC', border: '2px solid #111',   label: '#555555', indent: 0 },
    l3: { bg: '#ffffff', border: '1.4px solid #111', label: '#888888', indent: 0 },
  },

  style: {
    nodeRadius:     14,
    nodeBorder:     '2.5px solid #111' as const,
    iconMode:       'fill' as const,
    nodeLayout:     'tile' as const,
    showTag:        true,
    dashedExternal: true,
    groupBoundary:  'keyline' as const,
  },

  semantic: {
    problem:  { bg: '#EE7B4D', text: '#111', accent: '#7A3B1E' },
    solution: { bg: '#87B79A', text: '#111', accent: '#2C4A3A' },
    info:     { bg: '#A6C6E2', text: '#111', accent: '#27465A' },
    neutral:  { bg: '#A98C7E', text: '#111', accent: '#3E2F28' },
    warn:     { bg: '#E7E058', text: '#111', accent: '#5E5A1E' },
    primary:  { bg: '#C5B6EE', text: '#111', accent: '#3A3550' },
    data:     { bg: '#F0C5DA', text: '#111', accent: '#7A3F58' },
    second:   { bg: '#9CAFE7', text: '#111', accent: '#26345E' },
  },

  step: ['#C5B6EE', '#A6C6E2', '#87B79A', '#E7E058'] as const,

  radius: { sm: 8, md: 14, lg: 16, pill: 9999 },

  type: { caption: 10, tag: 9, label: 11, body: 12, title: 14, big: 30 },

  weight: { normal: 400, bold: 700 },

  letterSpacing: { mono: '1.5px', tight: '-1px', label: '-.5px' },
} as const

export type DiagramTheme = typeof theme
export default theme
