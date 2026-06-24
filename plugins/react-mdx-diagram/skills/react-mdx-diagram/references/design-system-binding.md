# Design-system binding

How to turn whatever the user provides at setup into (a) resolved theme tokens
and (b) — if they gave a component library — a component-name map. This is
reasoning work; there's no script for it because every design system is shaped
differently.

Remember the output is always **self-contained inline React**. So "binding a
design system" never means importing their components. It means two things:

1. **Token extraction** — pull their colors/radius/typography/spacing into the
   profile `theme.ts`, mapped onto the canon *semantic roles*.
2. **Name adapting** — record what they call the building blocks so the inline
   helpers we emit are named in their vocabulary (canon `Node` → their `Card`),
   making generated code read native. Stored in `binding.json` `componentNames`.

## Mapping onto semantic roles

The canon palette is semantic (`problem`/`solution`/`info`/`neutral`/`warn`/
`primary`), but design systems ship by name/intent (`brand`, `danger`,
`success`, `gray-100…900`). Map intent → role:

| Their token (typical) | Canon role |
|----------------------|-----------|
| danger / error / red | `problem` |
| success / positive / green | `solution` |
| brand / primary | `primary` |
| info / accent / blue | `info` |
| warning / caution / amber | `warn` |
| gray / neutral / surface | `neutral`, `surface`, `ink` |

For each role fill `{bg, border, text, accent}` from their scale (e.g. accent =
the 500/600 step, bg = the 50/100 step, border = 200/300, text = 700/800). If
they only give one hex for a role, derive bg/border by lightening — keep it
legible (dark text on light bg).

## Per-input-type handling

### Design tokens / theme file (CSS vars, JSON, TS)
The cleanest input. Read it, find the color scale, radius, font family, spacing.
Map onto roles as above. Copy radius/font/spacing into `theme.ts` directly. No
`componentNames` unless a component library also came with it.

### A component library in the repo (a path / import)
Read the library to learn two things:
- **Vocabulary** → build `componentNames` (what do they call a card, a tag, a
  container, a divider/arrow?). Look at exported component names and their
  props. This is the "adapting" the user cares about.
- **Visual tokens** → if components hardcode colors/radius or read from a theme,
  extract those into `theme.ts`.
Don't import or render their components — just mirror their look and naming.

### Figma link / screenshots (visual reference)
Read the image(s). Sample the palette (eyedrop the key fills/borders/text),
estimate radius (sharp vs. rounded vs. pill), corner/shadow style, and the font
character (geometric sans, humanist, mono accents). Map colors onto roles by
how they're used in the design (the alert/error color → `problem`, etc.).
Record uncertainty in `profile.md`; it's fine to approximate and refine later.

### Written style spec
Parse the prose for concrete values (hex codes, radius in px, font names,
spacing rhythm) and qualitative cues ("rounded and friendly", "high-contrast,
boxy"). Translate cues into token choices (friendly → larger radius, softer
borders; boxy → `radius.sm`, `thick` borders). Fill gaps from the default.

### Design-system repo URL
Fetch it (WebFetch) to find the tokens file, theme config, or component docs,
then treat it like the matching case above (tokens file → tokens; component docs
→ vocabulary). If it's a known system (Material, Chakra, Ant, shadcn, Radix,
Mantine), you likely know its palette and primitive names already — confirm key
values from the source rather than guessing.

## Adapting when names differ

The user's core ask: *if the design system's component names differ from canon,
adapt.* Mechanics:

- Build `componentNames` mapping each canon primitive used in output (`Node`,
  `Group`, `Lane`, `Edge`, `Badge`, `Note`) to the project's term **only when a
  real equivalent exists**. No equivalent → keep the canon name.
- When authoring, name the **lowercase helper function** after the DS component
  (camelCase) and invoke it as a **call**, never a JSX tag (see the renderability
  contract in `canon.md` — nested capitalized tags break the VS Code MDX
  preview). Example: DS calls cards `Panel` and tags `Chip` → inside
  `DomainModelBeforeAfter` write `const panel = (...) => (...)` and
  `const chip = (...) => (...)`, used as `{panel(...)}` / `{chip(...)}` instead of
  `node`/`badge`. The archetype component keeps its descriptive PascalCase name
  and is the only `export const` for the diagram.
- If a DS distinguishes variants (e.g. `Panel` vs `Card` vs `Surface`), pick the
  closest by role and note the choice. Don't multiply helpers needlessly — a
  diagram needs a handful of primitives, not their whole catalog.

The point is legibility to that team, not perfect fidelity to their API. We're
emitting standalone inline JSX that merely *looks and reads* like their system.
