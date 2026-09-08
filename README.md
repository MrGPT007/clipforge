# ClipForge Studio 0.4

A private working alpha for turning stories into narrated motion videos. NeoBrutal Soft components and plain-language copy; no RiddleUI paid assets are included.

## What works

- Private, user-owned project, skill and model-profile storage in Cloudflare D1.
- Original responsive studio with source, script/voice and export steps.
- Skill discovery **before** script generation. Automatic tag/style matching, explicit ordered selection, disable switches, instruction text, and version snapshots.
- Create, edit and import Markdown writing instructions. Imported files are treated as text, never executable code.
- OpenRouter and Groq writing through OpenAI-compatible requests using a key entered for the current request. Keys are not stored in the database or browser storage.
- Editable scene headings and narration, three motion styles and a playable preview.
- Private narration uploads in R2 (20 MB per file; 100 MB workspace cap).
- Browser WebM export at 720 × 1280, with an uploaded recording when supplied. Browser export requires a visible tab and takes real time.
- Python local maker: LM Studio or a selected online writer, skill discovery, schema validation/one repair attempt, optional Kokoro narration, animated ASS captions and H.264/AAC MP4.
- Local folder watching with a persistent SQLite queue, retry limits, content deduplication and script/audio checkpoints. No operating-system scheduler is required.
- Public HTTPS article extraction in the local maker using checked, pinned DNS and bounded redirects. This does not bypass paywalls, logins or site restrictions.
- The previous video clipping/download engine is retained in `engine-v02/`, including its separate CLI/MCP workflow. It is **not yet wired into the new web editor**.

## First run: no paid model needed

1. Open the private studio.
2. Choose **Try an example**, then **Use this script**.
3. Edit the scenes under **Script & voice**.
4. Add a narration recording if you want voice.
5. Choose **Make the video → Download video**. The file is WebM. Keep the tab visible.

For an MP4 without AI setup, use the included finished script:

```sh
python worker/maker.py worker/example-task.json --silent --out output
```

Python 3.10+ and FFmpeg/FFprobe with libass/libx264 are required. See [worker/README.md](worker/README.md) for narration, model setup and unattended processing.

## Online writing

Add a writing model in **Models & voices**, selecting OpenRouter or Groq. Copy the exact model ID from that service. Choose it in a project, paste your own key and choose **Write my script**. Source text and selected instructions are sent to that provider. The service can charge your account even if the response fails validation. There is no automatic provider fallback or invisible retry in the web editor.

The local maker supports the same providers and local OpenAI-compatible servers. Its environment variables are described in `worker/README.md`. The v0.4 browser adapter can attempt direct LM Studio access when browser/CORS policy allows it. Task/result files remain the fallback for the Python maker.

## Run the web application

This checkout uses the Vinext/React starter with Cloudflare Workers, D1 and R2. Node 22.13+ is required. Preserve the included lockfile.

```sh
npm ci
npm run db:generate
npm run build
```

In the current private deployment, identity is supplied by the trusted Sites dispatcher through `oai-authenticated-user-id`. Do not expose the Worker directly with client-spoofable identity headers. Public SaaS deployment requires an actual public authentication boundary and account lifecycle, not merely allowing arbitrary callers to supply this header.

The `.openai/hosting.json` manifest selects logical `DB` and `BUCKET` bindings. D1 schema migrations are in `drizzle/` and must be applied before running the server. All data queries are scoped to the authenticated owner. Records use optimistic revisions to prevent overwriting changes from another tab.

## Validation

```sh
node --test tests-product/core.test.mjs
python -m unittest discover -s tests-product -p 'test_*.py' -v
```

`docs/VALIDATION.md` records what was actually checked. Automated tests do not claim successful calls to a user's local model, paid provider, or social platform.

## Not a finished public SaaS

This release does **not** implement subscription billing, public customer signup, OAuth social connections, automatic social posting, always-on hosted GPU workers, a live local/cloud job bridge, AI image generation or full AI video generation. The accounts screen states that posting is unavailable and collects no social credentials.

Captions are paced proportionally within each scene, not forced-aligned word by word. The Python local maker measures actual per-scene narration duration. Browser preview uses the requested video length; an uploaded recording determines browser-export duration.

Model and voice downloads are not included. Kokoro defaults to English CPU inference with `af_heart`; other languages need a tested language/voice configuration. FFmpeg codecs/fonts and model licences must be reviewed before a public commercial rollout. No third-party UI kit is redistributed.

See `docs/PRODUCT-REQUIREMENTS.md` for the accepted product direction and launch gates.

## 0.4 makeover and model routing

The active UI now uses the canonical **NeoBrutal Soft** CSS snapshot in `vendor/neobrutal-soft`, with shallow compression on hover/press, semantic colors, fluid spacing and a light/dark switch. Older `design-system/` assets remain historical; see `docs/SOFT-MIGRATION.md`.

**Models & voices** saves separate model choices on each project for writing, finding moments and narration. Existing writing profiles still load. A capability check prevents speech services from being used as text models or LM Studio from being presented as TTS.

- **LM Studio:** the browser checks `http://localhost:1234/v1/models`; users select returned model IDs. Start the server and enable browser access (CORS) in LM Studio. Browser local-network permission or browser policy may also affect access. There is no address field for this default path. No successful connection is implied before discovery succeeds. Local inference stays local, but saving a project sends its source/script to the private hosted workspace.
- **Cloud text:** OpenAI, OpenRouter and Groq adapters, live model discovery with a request-only key, and validated script or timestamped-moment output. Model lists do not guarantee every returned model supports JSON output; unsupported calls surface provider errors. No invisible provider fallback.
- **Voice:** OpenAI speech and ElevenLabs speech adapters, plus a separate OpenAI-compatible local TTS server at `http://localhost:8880/v1`. Voice model and voice ID are independent from writing. Generated audio is saved through the existing owner-scoped audio route and can be previewed/exported. Local API speech requires its own running service; LM Studio does not supply it.
- **Moments:** paste timestamped transcript segments and select a dedicated local or cloud model. Clip boundaries must match real segment boundaries and last 10–120 seconds. Download the choices as JSON. This does not yet connect the video-URL engine to the web editor.
- **Agent MCP:** `worker/agent_server.py` exposes `list_tasks`, `discover_skills`, `list_local_models`, and `write_script` via stdio. Generation returns the selected instruction versions. External MCP servers are connected through the user's agent harness, not executed by the web editor.

### Connect an agent

```sh
python -m pip install -r worker/requirements-agent.txt
mkdir tasks
python worker/agent_server.py
```

Download a project task from the editor and place it in `tasks/`. Configure the agent's MCP command as `python`, with the **absolute path** to `worker/agent_server.py` as its argument. Start it from this repository, or set `CLIPFORGE_TASKS_DIR` to the desired task folder. `CLIPFORGE_SKILLS_DIR` can point to additional Markdown instructions. These paths are configured by the operator, not read from model output. Cloud writing uses `CLIPFORGE_API_KEY`; local writing discovers LM Studio without an API key. A cloud request can use credit and the maker permits one format-repair attempt.

The MCP interface has no shell-execution or social-publishing tool. Connect third-party MCPs separately in Hermes or another harness and apply their permissions there.

### Current limits

This update is still an alpha. It does not include managed cloud billing/credentials, zero-install local voice services, generated images, a hosted GPU worker, or the end-to-end video-URL clipping UI. Cloud accounts need a key unless a future managed-service layer provides one. Browser-to-local access is best effort and must be tried on the user's actual browser/host. Windows, GPU inference, paid provider calls and visual/browser QA have not been verified in this update.

Validation commands:

```sh
npm run typecheck
npm test
python -m pip install -r worker/requirements-agent.txt
python -m unittest discover -s tests-product -p 'test_*.py' -v
npm run build
```
