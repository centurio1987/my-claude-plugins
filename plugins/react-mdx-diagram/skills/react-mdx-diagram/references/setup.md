# Per-project setup

The skill keeps a **profile** per project — its customized theme and (optionally)
a design-system binding — stored inside the skill/plugin, not in the user's
project tree. Setup is the one-time act of creating that profile. After it
exists, authoring just reads it.

## When setup runs

Before authoring anything, run:

```bash
python3 <skill>/scripts/profile.py status
```

- `set_up: true` → a profile exists. Skip setup; go author (read `canon.md`,
  `profile.py show` for the theme/binding).
- `set_up: false` → no profile yet. Do setup **once**, then author.

Don't force a heavy interview when the user just wants a quick diagram. If they
provided no style material and don't want to, create a **default profile**
(copy `assets/theme.default.ts` into the profile dir as `theme.ts`, no
`binding.json`) and proceed. The default already looks good; setup only gets
elaborate when the user supplies material.

## What setup produces

Write these into the profile directory (`profile.py path` prints it):

| File | Required | Contents |
|------|----------|----------|
| `theme.ts` | yes | the resolved theme token object (same shape as `assets/theme.default.ts`), adjusted to the project |
| `binding.json` | only if a design system was provided | component-name map + theme overrides + freeform notes |
| `profile.md` | recommended | short human note: what material was used, decisions made, anything the author pass should know |

`theme.ts` existing is what flips `set_up` to true.

## The setup flow

1. **Detect first use** (`profile.py status`).

2. **Ask what's available** — but lightly, offering the default as the easy out.
   The material can be any of: design tokens / a theme file, a path to a
   component library in the repo, a Figma link or screenshots, a written style
   spec, or a design-system repo URL. Whatever they give, the job is to turn it
   into theme tokens (and, if it's a component library, a name binding).

3. **Ingest the material** → see `design-system-binding.md` for how to handle
   each input type. The output of this step is: a set of resolved token values
   (palette, radius, typography, spacing) and, if applicable, a `componentNames`
   map.

4. **Write `theme.ts`.** Start from `assets/theme.default.ts`, overwrite the
   values the material specifies, keep sensible defaults for the rest. Preserve
   the **semantic structure** (`problem`/`solution`/`info`/`neutral`/`warn`/
   `primary`) — map the project's brand colors onto these roles rather than
   renaming the roles. A design system rarely ships a "problem" color, so infer:
   their danger/error → `problem`, success → `solution`, brand/primary →
   `primary`, etc.

5. **Write `binding.json`** if a component library was provided:
   ```json
   {
     "componentNames": { "Node": "Panel", "Group": "Section", "Badge": "Tag", "Edge": "Connector", "Note": "Callout" },
     "themeOverrides": { "radius": { "md": 8 }, "font": { "sans": "Pretendard, sans-serif" } },
     "notes": "DS uses 8px radius everywhere, Pretendard, brand primary #5B21B6, danger #E11D48."
   }
   ```
   Only include names that genuinely exist in their system; leave the rest as
   canon. The author pass applies this map when naming emitted helpers (see
   `canon.md` → Naming).

6. **Write `profile.md`** — a couple of sentences for future runs.

7. **Confirm briefly** with the user (show the palette / key decisions), then
   proceed to author.

## Re-setup / updating a profile

If the user later says "the diagrams should use our new brand color" or "we
switched design systems," just edit the profile files — don't make a second
profile for the same project. The project key is stable, so editing in place is
correct. Mention what changed in `profile.md`.

## Keeping it out of the project tree

Never write theme/binding files into the user's repo unless they explicitly ask.
The whole point of the profile living in the skill/plugin is that the project
stays clean and the diagrams stay self-contained (the theme is serialized inline
into each MDX, per `canon.md`).
