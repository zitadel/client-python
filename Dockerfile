FROM python:3.14-slim@sha256:a2b82f3c48559aa0a8446d9af49826b6e2b2016f4cd2afabfe6013ec53729170

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

RUN apt-get update \
    && apt-get install --yes --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv /usr/local/bin/uv \
    && rm -rf /root/.local

ENV UV_PROJECT_ENVIRONMENT=/app/.venv
ENV PATH="/app/.venv/bin:/usr/local/bin:${PATH}"

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --all-extras

COPY . .
RUN uv sync --frozen --no-dev --all-extras

CMD ["uv", "run", "python"]
