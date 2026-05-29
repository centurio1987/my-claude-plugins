---
name: greeting
description: >
  This skill should be used when the user asks to "test the marketplace",
  "say hello from the plugin", "greeting 스킬 실행", or wants to confirm that a
  plugin installed from the centurio87-plugins marketplace is working. It is an
  example/template skill demonstrating the minimal plugin layout.
metadata:
  version: "0.1.0"
---

# Greeting (example skill)

This is a minimal example skill shipped inside the `hello-marketplace` plugin to
demonstrate the marketplace structure. Use it as a starting template for real skills.

## What to do

When this skill triggers, greet the user and confirm the plugin chain is working:

1. Reply with a short greeting that names the marketplace and plugin, e.g.
   "centurio87-plugins → hello-marketplace 플러그인이 정상 동작합니다. 👋".
2. If the user asked how to make their own plugin, point them to the
   `publish-to-marketplace` skill, which packages an existing skill / MCP server /
   command / hook / agent into a plugin and registers it in `marketplace.json`.

## Using this as a template

To create a real skill, copy this `skills/greeting/` directory, rename it, and:

- Update the `name` (kebab-case, matches the directory) and `description`
  (third-person, with concrete trigger phrases in quotes) in the frontmatter.
- Replace this body with imperative instructions for Claude (verb-first).
- Add `references/` files for long-form content to keep the body lean.
