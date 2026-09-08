# Validation — ClipForge Studio 0.3

Checked during implementation:

- 8 JavaScript tests passed for automatic skill discovery, instruction injection into the writing prompt, disabled/pinned skills, malformed response rejection, fenced JSON parsing, paragraph handling, duration validation and stripping keys from saved model profiles.
- 9 Python tests passed for local skill discovery/order, prompt assembly, scene validation, subtitle escaping/timing, Markdown instruction imports, blocking private article addresses and the finished-script path.
- A real FFmpeg render of `worker/example-task.json` produced a 15-second, 720 × 1280 H.264 MP4. FFprobe confirmed the codec, dimensions and duration. This smoke render was explicitly silent.
- D1 migrations were generated and inspected: two tables with owner indexes, schema-only statements and no seed data.
- Server queries scope records/files to the authenticated owner. Updates and deletes require matching revisions. Script requests use fixed online-provider origins; no provider keys are persisted.

The production build and TypeScript check passed. These notes do not imply successful external inference.

Not exercised here:

- A live OpenRouter/Groq request or the user's LM Studio model.
- Actual Kokoro model download or narrated generation.
- Browser recording/audio playback and mobile/assistive-technology UI interaction; no browser QA was requested.
- Windows/macOS installation, Docker execution, sustained queue load or public multi-tenant operation.
- Social posting or billing: not implemented.

The private deployed editor is an alpha, not a production SaaS launch. Follow `PRODUCT-REQUIREMENTS.md` before monetizing it publicly.
