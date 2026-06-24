#!/usr/bin/env python3
"""Lint an authored MDX diagram file for the render-time failure modes.

Why this exists: capitalized JSX tags are the source of two distinct breakages
across MDX hosts:

  1. Standard MDX resolves a capitalized tag that isn't in scope via
     `_missingMdxReference`, throwing `Expected component 'X' to be defined`.
  2. Some hosts (notably the VS Code MDX preview, ggfincke.vsc-mdx-preview)
     inject a component binding for EVERY capitalized tag they see — including
     nested ones — which then collides with a local `const X` you defined,
     throwing `Identifier 'X' has already been declared`. Standard
     `@mdx-js/mdx` does NOT reproduce this, so "it compiles for me" is not
     enough — the output has to survive the picky hosts too.

Both are avoided by one simple, portable rule (the pattern the predecessor
skill used everywhere without trouble):

    The ONLY capitalized JSX tags in the file are the top-level archetype
    components (`export const Foo = () => …`), used at COLUMN 0 in the markdown
    body as `<Foo/>`. Everything *inside* a diagram is built from lowercase HTML
    elements (`<div>`, `<span>`, `<pre>`) and `.map()`. For a reusable piece,
    define a lowercase helper FUNCTION and invoke it as a call — `{panel(a)}` —
    never as a JSX tag `<Panel/>`.

It also enforces the icon rule (principle 1): diagrams use **inline SVG vector
glyphs**, never emoji/pictographs. The rewritten design system (see
references/node-glyphs.md and the canon `glyph` helper) draws every semantic icon
as an `<svg>`; an emoji like ✅ / ⚠️ / 💡 / 🔁 standing in for an icon is exactly
what the prototype was meant to avoid. Geometric connector marks (→ ↓ ▼ and the
like) are NOT emoji and are allowed.

So this linter flags:
  - any capitalized JSX tag used NESTED (inside a component) — these are the
    sub-components that break hosts; convert them to lowercase function calls.
  - a column-0 body tag that has no matching top-level `export const`.
  - any emoji/pictograph on an indented (diagram-JSX) line — replace it with an
    inline SVG glyph.

Detection uses indentation: a nested tag has non-empty leading text on its line;
a body usage sits at column 0. Emoji are only flagged on indented lines (diagram
JSX), so emoji in column-0 prose of a content doc don't trip the gate.

Usage:
    python3 check_mdx.py <file.mdx> [more.mdx ...]

Exit code 0 = clean, 1 = violations found (printed with line numbers).
"""
import re
import sys
from pathlib import Path

TOPLEVEL_RE = re.compile(r"^export\s+const\s+([A-Za-z_]\w*)\s*=")
JSX_TAG_RE = re.compile(r"<([A-Z]\w*)[\s/>]")

# Pictographic emoji ranges only. Deliberately EXCLUDES arrows (U+2190–21FF) and
# geometric shapes (U+25A0–25FF) so connector marks like → ↓ ▼ ▶ are allowed.
#   U+1F000–1FAFF  emoji & supplemental symbols/pictographs (💡 🔁 📦 🚀 …)
#   U+2600–27BF    misc symbols + dingbats (⚠ ✅ ✔ ☀ …)
#   U+2B00–2BFF    misc symbols & arrows used as emoji (⭐ ⬛ …)
#   U+FE0F         emoji variation selector
EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF☀-➿⬀-⯿️]"
)


def check_file(path):
    text = Path(path).read_text(encoding="utf-8")
    lines = text.splitlines()
    top_names = {m.group(1) for ln in lines if (m := TOPLEVEL_RE.match(ln))}

    problems = []
    for i, ln in enumerate(lines, start=1):
        for m in JSX_TAG_RE.finditer(ln):
            tag = m.group(1)
            prefix = ln[: m.start()]
            at_col0 = prefix == ""  # tag is the very first thing on its line
            if at_col0:
                if tag not in top_names:
                    problems.append(
                        (i, f"body uses <{tag}/> but there is no top-level "
                            f"`export const {tag}`.")
                    )
            else:
                problems.append(
                    (i, f"<{tag}/> is a capitalized component used inside a diagram. "
                        f"Nested capitalized tags break some MDX hosts (e.g. VS Code "
                        f"preview: 'Identifier {tag} has already been declared'). Use a "
                        f"lowercase helper invoked as {{{tag[0].lower() + tag[1:]}(...)}} "
                        f"or inline lowercase HTML instead.")
                )

        # Emoji icon check — only on indented lines (diagram JSX). Emoji in
        # column-0 prose of a content doc are left alone.
        if ln[:1] in (" ", "\t"):
            found = {m.group(0) for m in EMOJI_RE.finditer(ln)}
            if found:
                emo = " ".join(sorted(c for c in found if c != "️"))
                problems.append(
                    (i, f"emoji/pictograph ({emo}) used inside diagram JSX. Icons must "
                        f"be inline SVG vector glyphs, not emoji — draw it as an <svg> "
                        f"(see references/node-glyphs.md / the canon `glyph` helper). "
                        f"Geometric connector marks like → ↓ ▼ are fine.")
                )
    return sorted(set(problems))


def main():
    if len(sys.argv) < 2:
        print("usage: check_mdx.py <file.mdx> [...]", file=sys.stderr)
        return 2
    total = 0
    for path in sys.argv[1:]:
        problems = check_file(path)
        if problems:
            print(f"\n✗ {path}")
            for line, msg in problems:
                print(f"  L{line}: {msg}")
            total += len(problems)
        else:
            print(f"✓ {path} — renderable (no nested capitalized components, no emoji icons)")
    if total:
        print(f"\n# {total} issue(s). Fix before considering the diagram done.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
