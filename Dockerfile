# Base Image
# TODO: реализуй меня
FROM ghcr.io/astral-sh/uv:python3.14-trixie-slim AS base

WORKDIR /app


# Python byte-code caching
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Testing
FROM base AS testing

COPY pyproject.toml uv.lock .python-version ./

RUN uv sync --frozen --no-install-project

COPY src/ ./src/
COPY tests/ ./test/
COPY README.md/ ./
COPY .envs/.env.docker.tests .envs/.env.tests

RUN uv sync --frozen

CMD ["uv", "run", "pytest"]



# Building
FROM base AS builder

WORKDIR /build

COPY pyproject.toml uv.lock .python-version README.md ./
COPY src/ ./src/

RUN uv build --wheel --out-dir /dist


# Runtime 
FROM base AS runtime
WORKDIR /app

COPY --from=builder /dist/*.whl  /tmp/

RUN uv pip install --system /tmp/*.whl && rm -rf /tmp/*.whl

COPY .envs/.env.docker.prod .envs/.env.prod

COPY --chmod=755 entrypoint.sh /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
