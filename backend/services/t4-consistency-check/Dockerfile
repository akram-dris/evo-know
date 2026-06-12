FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY services/t4-consistency-check/requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install torch==2.3.0 --index-url https://download.pytorch.org/whl/cpu
RUN --mount=type=cache,target=/root/.cache/pip pip install --default-timeout=3600 -r requirements.txt

COPY shared/ /app/shared/
COPY services/t4-consistency-check/app/ /app/app/

CMD ["python", "-m", "app.main"]
