# ClipForge 0.4 validation

Executed on September 8, 2026:

- TypeScript typecheck.
- 17 JavaScript tests: skill discovery/order, schema validation, legacy model compatibility, per-task routing, timestamp integrity, fixed cloud destinations and provider authentication/redirect behavior.
- 10 Python tests: existing maker checks plus a real stdio MCP client/server initialization, tool discovery, skill loading, finished-script result and path-traversal rejection.
- Production build including the model-list, speech and moment-selection routes.

No paid provider requests were made. LM Studio inference, local speech, GPU execution, Windows, browser permission/CORS behavior, visual QA, and a public SaaS authentication boundary were not tested. Mocked provider transport tests do not establish live API availability. Existing FFmpeg functionality was not changed or newly benchmarked.
