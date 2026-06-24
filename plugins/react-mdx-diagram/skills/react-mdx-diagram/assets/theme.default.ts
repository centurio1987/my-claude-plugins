/**
 * Default diagram theme tokens.
 *
 * This is the *source of truth* for the look of every diagram the skill emits
 * before a project is customized. During per-project setup, this object is
 * copied into the project's profile as `theme.ts` and then adjusted to match
 * whatever the user provides (design tokens, a repo component library, a Figma
 * reference, a written spec, or a design-system repo URL).
 *
 * Diagrams are always emitted as self-contained inline-style React, so this
 * object never gets imported by the MDX. Instead, the relevant subset is
 * serialized into a `const T = {...}` at the top of each MDX file and the
 * diagram components read from `T`. That keeps every diagram in a document
 * visually identical without coupling the document to any external file.
 *
 * Colors are organized *semantically*, not by hue — a diagram uses `problem`
 * because something is a problem, not because it wants red. This is what lets a
 * re-theme (swap the hexes) restyle every diagram coherently.
 */
export const theme = {
  font: {
    sans: '-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif',
    mono: 'ui-monospace,SFMono-Regular,Menlo,"Fira Code",monospace',
  },

  // The diagram canvas + the neutral card surface that holds content.
  surface: {
    canvas: '#f8fafc', // outer framed background
    card: '#ffffff', // default card fill
    border: '#e2e8f0', // hairline borders, frame outline
  },

  // Semantic color families. Each is a {bg, border, text, accent} quad:
  //   bg     fills a card/box
  //   border outlines it
  //   text   body text inside it
  //   accent labels, badges, emphasis
  semantic: {
    problem: { bg: '#fff1f2', border: '#fca5a5', text: '#7f1d1d', accent: '#dc2626' }, // rose — before / bad / warning
    solution: { bg: '#f0fdf4', border: '#86efac', text: '#14532d', accent: '#16a34a' }, // green — after / good / result
    info: { bg: '#eff6ff', border: '#93c5fd', text: '#1e3a8a', accent: '#2563eb' }, // blue — data / secondary
    neutral: { bg: '#f1f5f9', border: '#cbd5e1', text: '#334155', accent: '#475569' }, // slate — structure / default
    warn: { bg: '#fffbeb', border: '#fcd34d', text: '#78350f', accent: '#d97706' }, // amber — attention / limits
    primary: { bg: '#eef2ff', border: '#a5b4fc', text: '#312e81', accent: '#6366f1' }, // indigo — primary / step 1
  },

  // Ordered ramp for sequences/steps (indigo → sky → green → amber). Cycle
  // across N steps so a flow reads as forward motion rather than random color.
  stepRamp: ['#6366f1', '#0ea5e9', '#16a34a', '#d97706'],

  // Muted text/line colors for captions, connectors, arrows.
  ink: { heading: '#1e293b', body: '#475569', muted: '#94a3b8', line: '#cbd5e1' },

  radius: { sm: 6, md: 10, lg: 12, pill: 9999 },
  border: { thin: 1, thick: 2 },
  space: { xs: 6, sm: 10, md: 16, lg: 24 },
  type: { caption: 10, label: 11, body: 12, title: 14, big: 22 },
  weight: { normal: 400, bold: 700 },
  letterSpacing: { label: '0.08em' },
} as const

export type DiagramTheme = typeof theme
export default theme
