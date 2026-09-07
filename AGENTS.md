# ClipForge agent instructions

Before generating or changing UI, read `design-system/LLM-GUIDE.md` and `design-system/manifest.json`. Reuse `components/ui` primitives. Use semantic design tokens and fluid `clamp()` scale; do not introduce arbitrary product colors or one-off responsive sizes. All new UI must support light/dark, focus-visible, keyboard use and reduced motion. User-facing copy must follow `docs/GRANDMA-PROOF-UI-COPY-RULEBOOK.md`.

For product logic, keep user content and credentials explicit. Do not imply a model, voice, publisher, integration, or background process is connected unless the code actually connects it.
