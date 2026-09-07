# ClipForge Design System v1

## Purpose

ClipForge needs to feel approachable enough for a first-time creator and systematic enough that an LLM can build new screens without inventing a second visual language. The system uses a friendly neo-brutalist grammar: warm paper surfaces, strong ink borders, lavender and lime accents, modest rounding and crisp offset shadows.

The visual direction is inspired by the broad neo-brutalist foundation model visible in Riddle UI, but the ClipForge tokens, component skin, behavior, copy rules and implementation are original to this codebase.

## Foundations

### Color
Product code uses semantic roles rather than literal colors: Background, Foreground, Card, Popover, Primary (lavender), Secondary (lime), Muted, Accent, Destructive, Border, Ring, Success, Warning and Info. Each role has light and dark values.

### Typography
The type scale is fluid from `--text-2xs` through `--text-3xl`. Headings use tight tracking and strong weight; body copy favors legibility.

### Spacing and sizing
The fluid scale (`--space-1` through `--space-12`) plus page padding, controls and icon sizes uses `clamp()` so interfaces adapt smoothly without breakpoint-heavy sizing.

### Radius
ClipForge uses modest radii. UI objects should feel crisp rather than like soft floating capsules. Status chips and avatars may use full rounding.

### Borders and shadows
Borders are core identity, usually 1.5px or 2px. Elevation is expressed primarily with a hard offset ink shadow. `--shadow-soft` exists only where spatial depth is more useful than the printed effect.

### Motion
Motion is fast and purposeful. Hover raises a pressable object away from its hard shadow; active moves it toward the shadow. Overlays enter with subtle fade/scale. Reduced-motion users receive near-instant state changes.

## Component coverage

The UI library covers navigation, forms, overlays, content surfaces, data display, feedback and layout primitives. Shared styling targets each primitive's `data-slot` attribute, keeping theme, elevation, focus and motion consistent.

## State model

Interactive components should account for default, hover, focus-visible, active, disabled and invalid states. Async work should expose loading/busy state. Selection components visually distinguish selected/checked/on from hover.

## Light and dark

Dark mode is a semantic remap, not a filter. Lavender, lime, peach, blue and coral retain the ClipForge character while ink borders become light so hard shadows remain visible.

## Copy

UI copy follows `GRANDMA-PROOF-UI-COPY-RULEBOOK.md`: labels describe the user's goal, help text answers the next obvious question, and destructive/publishing/external-service actions explain consequences before commitment.

## LLM implementation protocol

A coding model should read, in order: `AGENTS.md`, `design-system/LLM-GUIDE.md`, `design-system/manifest.json`, the specific component files it intends to use, and the Grandma-proof copy rulebook for user-facing copy.
