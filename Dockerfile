# Stage 1: Build stage
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml .
COPY uv.lock . 
RUN uv sync --locked

# Stage 2: Runtime stage
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /app/.venv ./.venv
COPY src/ ./src/
EXPOSE 8003
CMD ["./.venv/bin/fastapi", "run", "src/api/server.py", "--port", "8003", "--forwarded-allow-ips='*'", "--root-path", "/95e222ef-c637-42d3-a81e-955beeeb0ba2"]