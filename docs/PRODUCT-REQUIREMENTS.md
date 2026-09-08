# Accepted ClipForge product direction

## User requirements

- Cheap automated content creation with local and cloud choices per job.
- Two workflows: repurpose an uploaded/downloaded video; create an original video from an idea, article or story.
- Prioritize code-rendered motion templates, then generated still images, then full AI motion video.
- Skill discovery precedes model output. Users can add/import/edit instructions, pin skills, combine compatible instructions, disable skills, and see the version used.
- Separate writing, narration, images and transcription providers. One model may serve several agent roles; multiple large models need not run simultaneously.
- Original neo-brutalist visual design inspired by RiddleUI. No paid RiddleUI files/assets have been copied.
- GRANDMA-PROOF UI COPY RULEBOOK governs all labels, helper text, consequences, recommendations and examples.
- Code-based scheduling and durable jobs, without requiring Windows Task Scheduler. Running somewhere is still required.
- Users eventually connect social accounts through official OAuth and delegate posting where each platform permits it.
- Sell a public SaaS with private customer workspaces, billing, metered usage and accessible friendly UX.

## 0.3 implementation boundary

The private studio and portable local maker establish the skill-to-script-to-motion workflow. Online writing supports OpenRouter/Groq with a session-only key. Local writing/narration/rendering uses exported tasks. Browser export accepts a finished script plus an optional uploaded narration.

The v0.2 clipping engine is retained separately for source downloads, transcription and clip extraction. Its MCP tools remain available to an external agent, but neither the legacy engine nor a Hermes supervisor is yet integrated into the web studio.

## Public SaaS gates

1. Public auth, organisation membership, passwordless/OAuth lifecycle, session controls, invitations and deletion/export of account data.
2. Encrypted provider secrets and scoped worker pairing; outbound local/cloud bridge with leases and checkpoints. Keep secrets out of model context.
3. Transactional usage reservations and settlement, idempotent payment webhooks, cancellation and refunds; confirm payment-provider availability for the business country.
4. Hosted CPU/GPU containers with concurrency limits, retention policies, cleanup, abuse controls and resource budgets.
5. Video upload/download UI wired to the retained clipping engine, with per-customer isolation and bounded ingestion.
6. Platform-specific OAuth publishing integrations, app reviews/audits, refresh/revocation, required user consent, disclosure controls and duplicate-post protection.
7. Browser/device/assistive-technology QA, real-model evaluations, narration-language tests and representative performance/cost benchmarks.
8. Review font, codec, model and source-content licences for the chosen commercial distribution.

## Skills are application data

Customer skill files guide writing. They are not trusted system instructions. They cannot grant tools access to accounts, change budgets, execute scripts, or override output validation. Automatically selected skills are deterministic and inspectable; pinned order is authoritative within the user's writing guidance. Do not claim a semantic quality guarantee from schema validation.

## UI acceptance

- Users can start the main activity immediately; no marketing landing page in front of the editor.
- Use clear everyday language; technical model IDs/addresses appear only where needed to connect a chosen service, with an example.
- Explain on/off outcomes, units, defaults and trade-offs. Essential consequences stay visible; longer help may expand.
- Show truthful loading, unavailable, empty and failure states. No fake connection or publishing buttons.
- Display model/skill provenance and plain-language local/cloud limitations.
