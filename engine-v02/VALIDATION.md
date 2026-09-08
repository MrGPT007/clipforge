# Validation — ClipForge 0.2.0

Validated in the provided Linux workspace with Python 3.12.13 and installed FFmpeg/ffprobe.

## Executed checks

- The original twelve core unittest cases passed, plus ten new URL/profile/agent cases.
- A real yt-dlp 2026.8.19 download from a controlled HTTP video server completed and entered the editing queue. Repeating the operation reused the download checkpoint.
- Actual MCP 1.29.1 stdio initialization, tool discovery, URL submission and status calls passed with an SDK client.
- URL queues survive restart and deduplicate repeated URLs; failed downloads have bounded retries.
- Inbox files and URL lines are not replayed after restart or merely switching the active profile.
- Profile choices bind to submissions; model-ID overrides persist without rewriting the config file.
- Pause and resume controls persist and affect the internal worker.
- A real background worker was started through the control command, paused, resumed and stopped on Linux; no orphan worker remained after the smoke check.
- Content hashes deduplicate renamed copies while preserving original input files.
- A second worker cannot acquire the same data-directory lock; interrupted running jobs recover on restart.
- Failed jobs wait for their retry time and stop after the configured attempt limit.
- Daily model-request counts persist across database connections; quota exhaustion defers work without consuming a processing attempt.
- The inbox watcher waits for file metadata to settle before enqueueing.
- Service errors are recorded and configured API-key values are redacted.
- Unknown segment IDs, nonfinite scores, invalid durations and overlapping clip choices are rejected/filtered.
- Transcript sectioning covers the full source, and subtitle text cannot inject ASS override tags.
- Integration: a real generated 8-second audiovisual source was sent through a controlled HTTP model adapter and real FFmpeg subtitle/vertical rendering. The exported 6-second MP4 had the expected dimensions and an audio stream.
- Repeating the processing function reused checkpoints: no second transcription, model call or render occurred.
- CLI initialization, dependency reporting and empty-queue single-run operation were exercised.

## Not executed

- Real Faster-Whisper transcription: model weights and the inference package were not installed in the execution environment. The integration test supplies a transcript fixture.
- Real LM Studio/llama.cpp or cloud-model inference: the HTTP integration uses a controlled local test server.
- Live YouTube/platform extraction, authenticated downloads and Deno execution were not exercised; the URL integration uses a real local HTTP media endpoint.
- An actual Hermes session was not launched. The MCP interface was tested using the official SDK client.
- NVIDIA CUDA, NVENC, RTX 2060 performance or memory use.
- Windows/macOS execution, Docker image builds or Compose deployment.
- Editorial quality, caption accuracy, visual suitability for real creator footage, or throughput on long videos.

These limits mean this is a tested portable core, not a production-certified service or a benchmarked replacement for a commercial editor. First-use checks should include one representative creator video on the target machine, model-response reliability, caption timing and available GPU memory.
