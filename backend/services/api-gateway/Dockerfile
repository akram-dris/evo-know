FROM python:3.12-slim

WORKDIR /app

# ضفنا هذا السطر لإجبار بايثون على إظهار السجلات فوراً وقراءة المجلد المشترك
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY services/api-gateway/requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install --default-timeout=3000 --retries=20 -r requirements.txt

COPY shared/ /app/shared/
COPY services/api-gateway/app/ /app/app/

EXPOSE 8000

# أصلحنا الأمر ليعمل الخادم بشكل سليم
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
