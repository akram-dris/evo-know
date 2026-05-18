FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY services/t2-report-generation/requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install --default-timeout=1000 -r requirements.txt

COPY shared/ /app/shared/
COPY services/t2-report-generation/app/ /app/app/

CMD ["python", "-m", "app.main"]
