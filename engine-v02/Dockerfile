FROM denoland/deno:bin AS deno
FROM python:3.11-slim-bookworm
COPY --from=deno /deno /usr/local/bin/deno
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml ./
COPY clipforge ./clipforge
RUN python -m pip install --no-cache-dir '.[all]'
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["python", "-m", "clipforge"]
CMD ["--config", "/config/config.json", "run"]
