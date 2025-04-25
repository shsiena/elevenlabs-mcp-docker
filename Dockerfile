# syntax=docker/dockerfile:1

FROM python:3.12-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      curl \
 && rm -rf /var/lib/apt/lists/*
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
WORKDIR /app
COPY pyproject.toml setup.py uv.lock ./
COPY . .
RUN uv sync
EXPOSE 8000
ENV ELEVENLABS_API_KEY=
CMD ["/app/.venv/bin/python", "/app/elevenlabs_mcp/server.py"]

