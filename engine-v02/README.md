# ClipForge 0.2 — files, video URLs and agent control

A working source-code starter for a local-first clipping application. Its own Python process watches an inbox, downloads queued video URLs, keeps durable SQLite queues, selects moments using an OpenAI-compatible model endpoint, and renders captioned vertical clips. Windows Task Scheduler, cron, Hermes and LM Studio are **not required** by the application.

This is an initial implementation, not a verified replacement for every feature or the editorial quality of WayinVideo. It has no web dashboard or installer yet.

## New in 0.2

- Paste a **single video URL or a local video path** using the same `enqueue` command, or the interactive `add` prompt.
- Put one URL per line in `inbox/urls.txt` for unattended intake alongside local files.
- Choose named AI profiles and query available model IDs. Model choices persist in the application database.
- Start, pause, resume, stop and inspect the worker from code or commands.
- Connect Hermes or another MCP-capable harness through the included stdio MCP server.

The application and agent adapter are Python. FFmpeg, speech/text inference engines and the optional Deno runtime are native dependencies; this is not a pure-Python video codec implementation.

## What independence means

- Scheduling, duplicate detection, request limits, retries and checkpoints live in application code.
- The same core code is intended for Windows, Linux and macOS. The current automated tests were run on Linux, not on the user's Windows PC.
- It still requires a running host, Python and FFmpeg, or a container runtime that packages those dependencies. Software cannot run while every host is off.
- To continue with your PC switched off, deploy the stack to an always-on server. CPU-only operation is available but speed and hosting cost depend on the machine and video volume.
- Automatic launch after a machine reboot necessarily belongs to the host/container runtime. The supplied containers have a restart policy; they start when Docker starts. No application can launch itself before a runtime is running.

## Implemented

1. Watch a local/mounted `inbox` directory for MP4, MKV, MOV, WebM and M4V files.
2. Wait for each file's size and modification time to settle. Prefer copying under a temporary extension, then renaming to `.mp4` after copying completes.
3. Copy the source into application storage and deduplicate by SHA-256 content, regardless of the filename.
4. Run Faster-Whisper in a child process, caching speech text and word timestamps. The child exits after transcription to release its model memory.
5. Split the transcript into overlapping sections. Ask the configured text model for contiguous segment IDs, hooks, titles and editorial scores.
6. Validate IDs, durations and scores. Select up to three nonoverlapping clips across the source.
7. Render a vertical MP4 with a blurred background, full-frame foreground, timed word-highlighting captions, AAC audio and loudness normalization.
8. Verify output duration, dimensions and audio-stream presence. Save the result manifest, captions and clips.
9. Retry failures with bounded exponential delays; resume from completed checkpoints when restarted.

These are technical validation checks, not a guarantee that captions are accurate, framing is attractive, clips preserve all needed context, or content will perform well. Review a representative first batch before relying on unattended output.

## Quick start — native Python, any supported desktop OS

Prerequisites: Python 3.11+; FFmpeg and ffprobe on PATH, with the `subtitles` filter/libass; and a running OpenAI-compatible text-model server. For sites requiring JavaScript extraction, install a supported Deno runtime on PATH; the Dockerfile includes one. Use a Python virtual environment if you normally do so. No OS scheduling setup is needed.

From the extracted project folder:

```text
python -m pip install -e ".[all]"
python -m clipforge init
```

For LM Studio, the default endpoint is `http://127.0.0.1:1234/v1`. Start its API server, list its models and choose an exact ID:

```text
python -m clipforge models
python -m clipforge set-model "EXACT_MODEL_ID"
```

An external provider or headless local server works too: set its endpoint in `config.json`, or use the profile example below.

```text
python -m clipforge doctor
python -m clipforge run
```

Place complete source videos you have permission to use in `inbox`. Keep the worker process running. First transcription downloads the selected Whisper weights unless already cached. A model download and the initial Python installation require network access.

For a background worker instead of a foreground terminal:

```text
python -m clipforge start
python -m clipforge add
```

The second command prompts for a URL or file path. This is a terminal prompt, not a web form. Background logs go to `data/worker.log`. In Docker, use the main `run` process already started by Compose, rather than launching another detached worker inside the container.

An alternative is to enqueue a complete file explicitly, which avoids the inbox settling delay:

```text
python -m clipforge enqueue "path/to/video.mp4"
python -m clipforge run --once
python -m clipforge status
```

`run --once` drains currently due queued work and exits. It does not wait for newly copied inbox files to settle, future retries, or tomorrow's quota. Use continuous `run` for unattended operation.

## Both input options

```text
python -m clipforge enqueue "C:/Videos/creator-episode.mp4"
python -m clipforge enqueue "https://example.com/creator-episode.mp4"
python -m clipforge enqueue "https://www.youtube.com/watch?v=VIDEO_ID"
```

Replace these examples with real authorized sources. URLs enter a separate persistent download queue and return a `download_id` immediately. The worker downloads with yt-dlp, verifies the media, then puts it into the editing queue. `status` contains both queues and links a completed download to its editing `job_id`.

For unattended batch intake, create `inbox/urls.txt` with one complete HTTP(S) video URL per line. Blank lines and lines beginning with `#` are ignored. Previously accepted lines and unchanged local files are remembered across worker restarts. Changing the active profile does not replay old inbox entries. To deliberately process the same source under a different profile, submit it explicitly with `--profile`.

Support is limited to sites/URLs supported by the installed yt-dlp version and accessible without bypassing access controls. Direct public video links are supported. YouTube and other platforms can change or restrict downloads; authenticated, private, DRM-protected and paywalled sources are not promised. This version has no login/cookie-import flow. Channel URLs, playlists and ongoing live streams are rejected. It does not discover new channel uploads automatically.

Defaults request up to 1080p, limit completed downloads to 2 GiB and videos to four hours, and set a two-hour download timeout. These are configurable. When a direct URL lacks resolution metadata, the downloader accepts its available file and the renderer scales it; the height preference is not a strict bandwidth limit. Unknown sizes or separate audio/video tracks can temporarily use more disk than the completed-file limit. Downloaded media is retained alongside a source copy for recovery.

For troubleshooting, update the downloader deliberately:

```text
python -m pip install --upgrade "yt-dlp[default]"
python -m clipforge doctor
python -m clipforge retry-download FULL_DOWNLOAD_ID
```

Retries are bounded. The application does not update itself automatically or endlessly retry blocked URLs.

## Entire stack as code — no LM Studio application

The optional Compose stack runs the worker and a headless llama.cpp model server. It exposes no external HTTP port by default.

1. Install a compatible Docker/Compose runtime.
2. Create `models`, `inbox` and `data` directories beside the Compose file.
3. Put a compatible instruction-tuned GGUF model at `models/model.gguf`. A 4-bit Qwen3-4B-Instruct-2507 conversion is a conservative candidate; small-model selection quality must be tested.
4. Start both services:

```text
docker compose -f compose.local-model.yaml up --build -d
docker compose -f compose.local-model.yaml logs -f worker
```

This sample uses **CPU inference and CPU transcription** for portability. It does not claim GPU passthrough on every OS. Model-server startup is asynchronous; the queue retries an initial connection failure if the model is still loading. If startup exceeds the configured retry window, use the retry command after the server is ready.

The model image currently uses the upstream `server` tag. Pin it to a tested digest and lock Python dependencies before a production rollout. Container builds and the actual model server were not executed in the supplied test environment.

To use an existing LM Studio server instead, edit `config.docker.json`, then run:

```text
docker compose up --build -d
```

The `host.docker.internal` address refers to the container host, not to an arbitrary PC. LM Studio must listen on an interface reachable from Docker; its loopback-only binding may not be reachable from a container. A model server on another machine needs its reachable hostname and appropriate network access. For the fully contained option, use `compose.local-model.yaml`.

## Your Ryzen 5 3600 / 16 GB RAM / RTX 2060 6 GB

The screenshot shows **6 GB dedicated VRAM**, with roughly 2.4 GB occupied at capture time. The 14 GB aggregate figure includes shared system memory and is not 14 GB of fast GPU memory.

Start with the CPU defaults so the text model can use the GPU. Use a small 4-bit text model with a modest context window. Increase model size only after measuring memory use and result quality on your own content.

For a native NVIDIA transcription trial, after installing the CUDA/cuDNN dependencies required by your Faster-Whisper/CTranslate2 version, change:

```json
{
  "whisper_model": "small",
  "whisper_device": "cuda",
  "whisper_compute_type": "int8_float16"
}
```

These keys are edits to `config.json`, not a complete replacement file. A compatible GPU-enabled FFmpeg build can optionally use `video_encoder: "h264_nvenc"`. GPU mode is opt-in; the application will report errors rather than silently claim acceleration.

The transcription child releases **its own** model memory. An external LM Studio/llama.cpp server can keep its text model resident independently. The application does not automatically unload external models; use CPU transcription or configure the model server's lifecycle to avoid memory contention. The supplied CPU container does not contain a CUDA runtime.

Your earlier CPU screenshot showed virtualization disabled. Docker Desktop/WSL-based setups on Windows may need virtualization enabled; native Python avoids that dependency. No BIOS change is needed for native operation.

## AI endpoint configuration

For multiple model choices, copy `config.profiles.example.json` to a new config file, replace the endpoint/model placeholders, and use that file with `--config`. It demonstrates `local`, `cloud-free` and `custom` profiles. The name `cloud-free` does not make a model free: you must select a currently free model from that provider. No paid fallback is enabled.

```text
python -m clipforge --config config.profiles.example.json profiles
python -m clipforge --config config.profiles.example.json --profile local models
python -m clipforge --config config.profiles.example.json --profile local set-model "EXACT_MODEL_ID"
python -m clipforge --config config.profiles.example.json use-profile local
python -m clipforge --config config.profiles.example.json --profile local enqueue "https://example.com/video.mp4"
```

Put global options such as `--config` and `--profile` **before** the subcommand. `use-profile` selects a preconfigured profile for future intake; an editing/download job retains the profile name chosen at submission. `set-model` changes that profile's text-model ID for its next processing jobs, including queued jobs. It takes effect without rewriting Python or restarting the worker. Provider settings and transcription-model changes in the JSON file require a worker restart.

Profiles can choose `whisper_model`, `whisper_device`, `whisper_compute_type` and `language` as well as the text-model endpoint. Transcription still runs locally; a cloud text profile does not send audio to a cloud transcription API.

| Setting | Purpose |
| --- | --- |
| `llm_base_url` | OpenAI-compatible API root ending in `/v1`, or the provider's documented equivalent |
| `llm_model` | Exact model ID supplied by the server/provider |
| `llm_api_key_env` | Environment variable containing the API key; defaults to `CLIPFORGE_API_KEY` |
| `llm_response_format` | `json_schema` by default; use `json_object` or `none` if the provider does not support schemas |
| `llm_daily_request_limit` | App-wide persistent request cap per UTC day; default 30; 0 disables it for local inference |
| `chunk_characters` | Transcript request-size budget; lower it for small model context windows |
| `llm_max_output_tokens` | Output budget; default 1000 |

Configure secrets in the process/container environment, not inside source files. The program never picks a paid model automatically. A request-count cap is **not a monetary spending cap**: a paid endpoint can still charge for allowed requests. For zero API charges, use local inference or explicitly select a currently free provider/model with its own limits.

OpenAI-compatible describes an interface. It does not guarantee identical JSON-schema support, model quality, context length or free availability across providers. The app validates returned segment IDs even when schema mode is disabled.

Transcript text is sent to the configured model endpoint. With a remote provider, that text leaves your machine. Actual video and audio are processed locally by this starter.

## Scheduling, recovery and control

The internal loop scans between processing jobs, so a long render or transcription delays the next scan. This single-worker design keeps RAM use manageable. It is not a distributed queue.

SQLite holds job states `queued`, `running`, `retry`, `failed` and `done`. One process owns the worker lock for each data directory. A killed worker's lock is released by the runtime, and previously running jobs return to the queue on the next start. Completed transcription, AI-section selection and rendered-output metadata are cached.

```text
python -m clipforge status
python -m clipforge retry FULL_JOB_ID
```

`retry` accepts failed/deferred editing jobs; `retry-download` accepts failed/deferred downloads. Configuration-file changes apply on worker restart. Identical video bytes are deduplicated within the same named profile; explicit submission under a different profile creates a separate editing job. To rerun a completed job under changed settings in the same profile, use a separate `data_dir` for that experiment. Changing settings during a retry invalidates the relevant stage caches.

```text
python -m clipforge pause
python -m clipforge resume
python -m clipforge stop
python -m clipforge start
```

Pause/resume/stop requests persist in the database and are checked between processing steps/jobs; they do not interrupt an active render, model call or download. Pause state survives restarts. `start` starts the worker, but an already-paused worker also needs `resume`. The built-in controller costs no LLM tokens for polling or scheduling. The text model is called only for clip selection.

Ctrl+C/SIGTERM requests a stop after the current job. A forced shutdown can interrupt a child operation; restart recovers through checkpoints. Keep the data directory on a local disk with working SQLite file locks, not an unreliable network filesystem. Preserve the source files and data volume when moving hosts; paths in previously written result manifests reflect the original host, while assets remain beneath `data/jobs`.

## Hermes and other agent harnesses

The built-in worker is the default automation controller. Hermes can operate it through the included MCP server. Any harness supporting local stdio MCP can use the same interface; actual compatibility must be checked with that harness.

Install `.[agent]` or `.[all]` in the Python environment used by your agent. Merge `hermes-mcp.example.yaml` into the Hermes MCP configuration after replacing the Python executable and config paths. The adapter runs as:

```text
python -m clipforge --config /absolute/path/to/config.json mcp
```

It exposes `submit_video`, `processing_status`, `model_profiles`, `available_models`, `select_profile`, `select_model`, `worker_control` and `retry_failed`. The adapter uses the maintained v1 MCP SDK with a `<2` bound; a future SDK migration should be tested deliberately.

Hermes can submit a URL, start/resume the worker, and inspect resulting files without doing the editing through browser clicks. The processing worker and MCP server are separate processes. A running worker does not need an active agent conversation. Host or harness process-management rules can terminate child processes when an app exits; use the supplied Compose service on an always-on host for durable unattended operation.

The stdio adapter is for a trusted local agent and has the same filesystem/network access as its process. It does not expose an unauthenticated web API. Only configured model profiles are selectable; the tool does not execute arbitrary shell commands. Credentials needed for cloud inference must be present in the environment of the worker or MCP-launched worker. Hermes's own model usage is separate from ClipForge's request cap.

## Output layout

```text
data/jobs/FULL_CONTENT_HASH/source.video
data/jobs/FULL_CONTENT_HASH/transcript.json
data/jobs/FULL_CONTENT_HASH/selected-clips.json
data/jobs/FULL_CONTENT_HASH/result.json
data/jobs/FULL_CONTENT_HASH/outputs/RENDER_ID/clip.mp4
data/jobs/FULL_CONTENT_HASH/outputs/RENDER_ID/captions.ass
```

Source copies are retained so the worker can recover after restarts. No automatic deletion is implemented. Monitor free disk space and archive/delete completed job folders deliberately; deleting active folders breaks recovery.

## Not implemented yet

- Automatic channel/feed discovery or campaign discovery.
- Active-speaker tracking, scene-aware face cropping, B-roll or animated motion graphics.
- Social publishing, Whop submission, account login, campaign-rule validation or payout tracking.
- A web dashboard, multi-server coordination, signed desktop installer or built-in updates.
- Guaranteed good hooks, transcript accuracy or viral performance.

This version implements the portable **download/editing/transcription core and agent-control adapter**. The social and campaign integrations discussed earlier remain separate work. From supplied files/URLs to exported clips, the queue runs automatically once dependencies and a working model are configured; this is not yet an automated Whop business.

## Validation

Run the bundled tests from the project directory:

```text
python -m unittest discover -s tests -v
```

The integration test uses a real FFmpeg-generated source, real FFmpeg subtitle rendering and ffprobe checks, plus a controlled HTTP model server and supplied transcript fixture. It checks checkpoint reuse so cached work does not issue another model request or rerender.

See `VALIDATION.md` for the executed checks and exact limitations. No large speech/text weights are bundled.

## Reference documentation

- [Faster-Whisper installation, CPU/GPU execution and timestamps](https://github.com/SYSTRAN/faster-whisper)
- [LM Studio OpenAI-compatible API](https://lmstudio.ai/docs/developer/openai-compat)
- [LM Studio structured output and model limitations](https://lmstudio.ai/docs/developer/openai-compat/structured-output)
- [llama.cpp official container images](https://github.com/ggml-org/llama.cpp/blob/master/docs/docker.md)
- [FFmpeg filter reference](https://ffmpeg.org/ffmpeg-filters.html)
- [Docker GPU requirements](https://docs.docker.com/compose/how-tos/gpu-support/)
- [Hermes scheduling and script-only jobs](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron)
- [Hermes MCP integration](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp)
- [MCP Python SDK v1](https://github.com/modelcontextprotocol/python-sdk/tree/v1.x)
- [yt-dlp source, supported options and runtime requirements](https://github.com/yt-dlp/yt-dlp)
