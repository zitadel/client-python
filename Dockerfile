FROM python:3.13-slim@sha256:9ed09f78253eb4f029f3d99e07c064f138a6f1394932c3807b3d0738a674d33b

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-root

COPY . .

RUN poetry install

CMD ["poetry", "run", "python"]
