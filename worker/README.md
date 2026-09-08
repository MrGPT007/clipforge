# Make a video on your computer

This program turns a task downloaded from the studio into an MP4. Your machine must stay on while it works. It does not post to social accounts.

## 1. Install the basics

Use Python 3.10 or newer. Install FFmpeg with FFprobe, libass and libx264, and make both commands available on PATH. Install the DejaVu Sans font (or substitute a font in the subtitle styles). The Docker option below includes FFmpeg, fonts and speech dependencies.

First test a finished script without a model or voice download:

```sh
python worker/maker.py worker/example-task.json --silent --out output
```

A new output folder contains `video.mp4`, `captions.srt`, `captions.ass`, `script.json`, `project.json` and `run.json`. No writing model is called when scenes or a finished script are supplied.

## 2. Add generated narration

Install the speech dependencies into a virtual environment:

```sh
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r worker/requirements-voice.txt
```

macOS/Linux:

```sh
. .venv/bin/activate
python -m pip install -r worker/requirements-voice.txt
```

Kokoro may also require the eSpeak NG system package. The first narrated run downloads model/voice files. After those downloads, the local narration step can work without a cloud API. CPU inference is intentional, leaving the RTX 2060's GPU available for the writing model.

```sh
python worker/maker.py worker/example-task.json --out output --voice af_heart
```

The current maker is configured for American English. `af_heart` is the default. Do not assume an arbitrary voice name supports another language.

## 3. Use LM Studio for writing

Download a model that fits your hardware, start LM Studio's local server and copy the exact loaded model ID into the studio's **Models & voices** page. A quantized small model is a reasonable first experiment for 6 GB VRAM; performance has not been benchmarked on your PC.

Default server address: `http://localhost:1234/v1`.

Download your task from the studio, then run:

```sh
python worker/maker.py clipforge-task.json --out output
```

For another local server address, set `CLIPFORGE_MODEL_URL` yourself. If it needs a key, set `CLIPFORGE_LOCAL_KEY`. These override task-file addresses; never put private keys in a task or commit them to Git.

For OpenRouter or Groq, choose that provider in your studio profile and set `CLIPFORGE_API_KEY` in your own shell. The maker uses fixed provider addresses. A model-generated malformed script gets one repair attempt, which may incur another provider charge. Transport failures are left to the bounded queue retry.

## 4. Automatically read available skills

Task files include the selected writing instructions and their versions. You can additionally point the maker at a local directory:

```sh
python worker/maker.py clipforge-task.json --skills-dir my-instructions --out output
```

Each Markdown file can have simple front matter with `name`, `description`, `tags` (comma-separated), `version` and `enabled`. The body is writing guidance. The maker never executes imported instructions.

Automatic discovery scores topic words and the selected video style, then chooses up to three enabled skills. Pinned mode preserves your selected order. Earlier skills win conflicts. Unmatched requests use the basic writing instructions and say so in the console.

## 5. Read a source article

```sh
python worker/maker.py clipforge-task.json --source-url https://example.org/your-article --out output
```

Use an article you may adapt. Only public HTTPS HTML/plain text is accepted, with a 2 MB download cap. Private addresses, credentials in URLs, custom ports and excessive redirects are rejected. Existing scene scripts are reused; clear the task's `scenes` array and use `story` mode when you want the article rewritten.

## 6. Watch a folder continuously

```sh
python worker/maker.py --watch tasks --out output --skills-dir my-instructions
```

Drop downloaded task files into `tasks`. The maker waits until files appear stable, handles one at a time, saves its queue in SQLite, and retries a failed task at most three times. It resumes when you restart it. Press Ctrl+C to stop. Repeated task content is not processed again in the same queue. Use a different output folder when changing voice/silent settings for a whole queue. Only one watcher can own an output folder.

It runs while the Python process is running. Automatically starting a process after a machine reboot still requires a host/container supervisor; code cannot run on a powered-off machine.

## Docker option

From the worker directory:

```sh
docker compose up --build -d
```

Put tasks in `worker/tasks`. Outputs appear in `worker/output`. Model downloads are cached in a named volume. This setup uses CPU narration and connects to the host model server through `host.docker.internal`. For Linux or a different model host, adjust `CLIPFORGE_MODEL_URL`. Docker itself and any required host virtualization must be installed and running.

## Bring results back

Use **Script & voice → Import local result** to open `project.json` in the studio. Add `narration.wav` as the recording. Or simply use the finished local `video.mp4` directly.

A task and its outputs contain your story and instructions. Keep them private when needed. No credentials are bundled. Keep your original source files; the maker does not delete them.
