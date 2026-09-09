FROM python:3.10

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY app/services/bot/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app /app/app

CMD ["python", "-m", "app.services.bot.main"]