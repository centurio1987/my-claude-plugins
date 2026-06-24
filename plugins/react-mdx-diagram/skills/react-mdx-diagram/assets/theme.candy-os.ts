/**
 * Candy-OS skin — design token source.
 *
 * Dark canvas, solid vivid pastel tiles, black glyphs, bright bold straight connectors.
 * Paste fills are light so the "black glyph/black label on pastel" rule holds even on
 * the dark #0B0B0B canvas: each tile is a light island over the dark sea.
 *
 * This file is the TOKEN SOURCE ONLY — it is never imported by emitted MDX.
 * Instead, the orchestrator serializes the relevant subset into a `const T = {...}`
 * at the top of each MDX file. Every diagram reads from `T`, not from this file.
 *
 * Conforms to the §6 `T` shape from the frozen contract (CONTRACT.md §6).
 */
export const theme = {
  skin: 'candy-os' as const,

  font: {
    sans: "'Helvetica Neue',Helvetica,Arial,sans-serif",
    mono: "'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,monospace",
  },

  surface: {
    canvas: '#0B0B0B',
    panel:  '#0B0B0B',
    shadow: '0 2px 14px rgba(0,0,0,.18)',
  },

  ink: {
    heading: '#F1F0ED',
    body:    '#C9C9C6',
    muted:   '#9A9A97',
    tag:     '#6E6E6B',
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
    color:    '#EDEBE6',
    width:    3.4,
    style:    'straight' as const,
    label:    '#9A9A97',
    lifeline: null,
  },

  c4: {
    l1: { bg: 'rgba(156,175,231,.18)', border: '1px solid #3A3A3A', label: '#9CAFE7', indent: 0 },
    l2: { bg: 'rgba(166,198,226,.42)', border: 'none',              label: '#A6C6E2', indent: 0 },
    l3: { bg: '#A6C6E2',              border: 'none',              label: '#21323F', indent: 0 },
  },

  style: {
    nodeRadius:     16,
    nodeBorder:     'none' as const,
    iconMode:       'fill' as const,
    nodeLayout:     'tile' as const,
    showTag:        false,
    dashedExternal: false,
    groupBoundary:  'soft' as const,
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
