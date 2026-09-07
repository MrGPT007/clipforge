# ClipForge Design System

A reusable, code-first UI system for ClipForge and future projects. It is optimized for humans building deliberately and LLMs generating UI consistently.

## Included

- `tokens.css` — light/dark semantic colors, fluid typography, spacing, sizing, radius, shadows, charts and motion values.
- `components.css` — shared skin for `data-slot` primitives.
- `motion.css` — named motion primitives and reduced-motion handling.
- `utilities.css` — stable layout and semantic utility classes.
- `tokens.ts` — typed token references.
- `manifest.json` — machine-readable inventory of UI primitives.
- `LLM-GUIDE.md` — generation contract for coding agents.
- `../docs/DESIGN-SYSTEM.md` — human-facing design guidance.

## Theme model

`next-themes` applies `.dark` on the root. Product code should never branch on theme to pick colors. System theme is the default and a manual toggle may be provided.

## Reuse

Copy `design-system/`, the required `components/ui/` primitives, and the theme provider. For an LLM-driven project, include `AGENTS.md` and `design-system/LLM-GUIDE.md` in model context before generating screens.
