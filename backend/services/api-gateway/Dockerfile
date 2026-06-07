FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
# هنا السر: أعطينا بايثون خريطة للمسارين معاً
ENV PYTHONPATH=/app/backend/services/api-gateway:/app/backend

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY services/api-gateway/requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install --default-timeout=3000 --retries=20 -r requirements.txt
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"

# Copy the entire backend directory
COPY . /app/backend/

EXPOSE 8000

# قمنا بتبسيط أمر الإقلاع لأن بايثون أصبح يعرف مسار app مباشرة
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]