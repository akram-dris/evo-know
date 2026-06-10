FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/backend

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY services/orchestrator/requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install --default-timeout=3600 -r requirements.txt

COPY . /app/backend/

CMD ["python", "-m", "backend.services.orchestrator.app.main"]
