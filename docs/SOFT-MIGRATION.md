# Active design and integration contract

The user's September 8 makeover request selects NeoBrutal-Soft in place of the original ClipForge/RiddleUI-inspired palette. For active product UI, use `vendor/neobrutal-soft/src/index.css` and its `--nbs-*` tokens. This supersedes the old visual grammar in `design-system/LLM-GUIDE.md`, while preserving its accessibility, primitive reuse and plain-language-copy requirements.

Buttons map to `.nbs-button`; common React Button variants map to upstream Soft modifier classes. NativeSelect, Input, Textarea, Sidebar, Tabs, Switch, Checkbox and dialogs reuse the existing primitives. Product-specific layout remains in `app/globals.css`. Reduced motion and forced-colors rules remain active. Only actual drag interactions may rise; ordinary buttons compress.

## New product patterns

| Pattern | Source | Behavior |
|---|---|---|
| Model routing | app/model-workbench.tsx | Three independent task choices saved on projects |
| Local connection status | lib/local-ai.ts | Actual discovery, bounded timeout, explicit failure guidance |
| Speech adapter | app/api/speech/route.ts | Owner-scoped saved profile, allowlisted destination, no redirects |
| Moment validation | lib/moments.ts | Ordered transcript; exact timestamp boundaries; duration limits |
| Skill-first agent tools | worker/agent_server.py | Discover instructions before writing; preserve versions |

## Interface copy requirements

The recovered source includes `docs/GRANDMA-PROOF-UI-COPY-RULEBOOK.md`. Follow that rulebook: explain what each setting changes, use action-specific buttons, explain choices, show units/ranges for numbers, and state spending/data-sharing effects before actions. Keep short summaries visible and put longer help in expandable sections.
