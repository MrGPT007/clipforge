FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg espeak-ng fonts-dejavu-core && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements-voice.txt .
RUN pip install --no-cache-dir -r requirements-voice.txt
COPY maker.py .
ENV HF_HOME=/models
ENTRYPOINT ["python", "maker.py"]
CMD ["--watch", "/tasks", "--out", "/output"]
