/**
 * Swiss skin — design token source.
 *
 * Light canvas, big bold labels, pastel color bands, line icons, thin precise rules.
 * Editorial and documentation-oriented: high contrast on near-white, strict grids,
 * hairline strokes everywhere. C4 nesting is expressed via increasing left indent
 * and lightening blue bands rather than nested boxes.
 *
 * This file is the TOKEN SOURCE ONLY — it is never imported by emitted MDX.
 * Instead, the orchestrator serializes the relevant subset into a `const T = {...}`
 * at the top of each MDX file. Every diagram reads from `T`, not from this file.
 *
 * Conforms to the §6 `T` shape from the frozen contract (CONTRACT.md §6).
 */
export const theme = {
  skin: 'swiss' as const,

  font: {
    sans: "'Helvetica Neue',Helvetica,Arial,sans-serif",
    mono: "'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,monospace",
  },

  surface: {
    canvas: '#ECEBE7',
    panel:  '#ECEBE7',
    shadow: '0 2px 14px rgba(0,0,0,.10)',
  },

  ink: {
    heading: '#141414',
    body:    '#3A3A38',
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
    color:    '#141414',
    width:    1.8,
    style:    'straight' as const,
    label:    '#6C6B66',
    lifeline: '#B8B6AE',  // dashed 4 4 — used for sequence diagram lifelines
  },

  c4: {
    // Indented color bands; border none; right-aligned mono L1/L2/L3 tag
    l1: { bg: '#9CAFE7', border: 'none', label: '#26345E', indent: 0  },
    l2: { bg: '#A6C6E2', border: 'none', label: '#27465A', indent: 18 },
    l3: { bg: '#C9DAEA', border: 'none', label: '#48586A', indent: 36 },
  },

  style: {
    nodeRadius:     8,
    nodeBorder:     'none' as const,
    iconMode:       'line' as const,
    nodeLayout:     'band' as const,
    showTag:        false,
    dashedExternal: false,
    groupBoundary:  'indent' as const,
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
