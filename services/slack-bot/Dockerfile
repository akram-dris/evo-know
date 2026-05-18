FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY services/slack-bot/requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install --default-timeout=1000 -r requirements.txt

COPY shared/ /app/shared/
COPY services/slack-bot/app/ /app/app/

EXPOSE 3000
CMD ["uvicorn", "app.main:api", "--host", "0.0.0.0", "--port", "3000"]
